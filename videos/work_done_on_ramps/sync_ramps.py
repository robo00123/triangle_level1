"""Line the animation up with the ElevenLabs narration.

    python sync_ramps.py narration.mp3                      # one file
    python sync_ramps.py part1.mp3 part2.mp3 part3.mp3 part4.mp3

Transcribes the audio with faster-whisper (word timestamps), matches every script line to the words heard,
inserts PAUSE_GAP seconds of silence after the pause line, and writes
    ramps_audio.mp3   the narration with the pause gap, used by `python make_ramps.py encode`
    ramps_cues.json   start and duration of every script line, used by make_ramps.py
An optional ramps_cues_override.json nudges cues by hand: {"wwf": 1.5} moves a cue 1.5 s later,
{"wwf": [350.2, 9.0]} sets its start and duration.
"""
import difflib, json, os, re, subprocess, sys, tempfile
from ramps_script import SCRIPT, PAUSE_KEYS, PAUSE_GAP

HERE = os.path.dirname(os.path.abspath(__file__))

NUMBERS = {w: str(i) for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
    "seventeen eighteen nineteen twenty".split())}
NUMBERS.update({"thirty": "30", "forty": "40", "fifty": "50", "hundred": "100"})

def norm(word):
    w = word.lower().replace("’", "'")
    w = re.sub(r"[^\w.']", "", w).strip(".'")
    return NUMBERS.get(w, w)

def tokens(line):
    return [t for t in (norm(w) for w in line.split()) if t]

def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())

def join_parts(paths, out):
    if len(paths) == 1:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", paths[0], "-ar", "44100", "-ac", "1", out], check=True)
        return
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for p in paths:
        cmd += ["-i", p]
    cmd += ["-filter_complex", "".join(f"[{i}:a]" for i in range(len(paths))) + f"concat=n={len(paths)}:v=0:a=1[a]",
            "-map", "[a]", "-ar", "44100", "-ac", "1", out]
    subprocess.run(cmd, check=True)

def transcribe(path):
    from faster_whisper import WhisperModel
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(path, word_timestamps=True)
    return [(w.word.strip(), w.start, w.end) for seg in segments for w in seg.words]

def align(words):
    """start and duration of every script line, from the words heard"""
    script, owner = [], []
    for i, (_, line) in enumerate(SCRIPT):
        for tok in tokens(line):
            script.append(tok)
            owner.append(i)
    heard, where = [], []
    for j, (w, _, _) in enumerate(words):
        n = norm(w)
        if n:
            heard.append(n)
            where.append(j)
    first, last = {}, {}
    sm = difflib.SequenceMatcher(None, script, heard, autojunk=False)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            i, (_, st, en) = owner[a + k], words[where[b + k]]
            first.setdefault(i, st)
            last[i] = en
    cues = {}
    known = sorted(first)
    for i, (key, line) in enumerate(SCRIPT):
        if i in first:
            cues[key] = [first[i], last[i] - first[i]]
            continue
        # not heard: share the gap between the neighbouring lines in proportion to the number of words
        prev = max((j for j in known if j < i), default=None)
        nxt = min((j for j in known if j > i), default=None)
        a = last[prev] if prev is not None else 0.0
        b = first[nxt] if nxt is not None else a + 3.0
        span = list(range((prev if prev is not None else -1) + 1, nxt if nxt is not None else len(SCRIPT)))
        wc = [len(SCRIPT[j][1].split()) for j in span]
        before = sum(wc[:span.index(i)])
        st = a + (b - a) * before / sum(wc)
        cues[key] = [st, (b - a) * wc[span.index(i)] / sum(wc)]
        print(f"warning: could not match line '{key}', placed it at {st:.1f} s")
    return cues

def insert_pauses(cues, src, out):
    """add PAUSE_GAP seconds of silence after each pause line and shift the later cues"""
    keys = [k for k, _ in SCRIPT]
    cuts = []
    for pk in PAUSE_KEYS:
        st, du = cues[pk]
        nxt = keys[keys.index(pk) + 1]
        cuts.append(min(st + du + 0.3, cues[nxt][0]))
    cuts.sort()
    for k in cues:
        cues[k][0] += PAUSE_GAP * sum(1 for c in cuts if cues[k][0] >= c)
    parts, edges = [], [0.0] + cuts + [None]
    for i in range(len(edges) - 1):
        trim = f"atrim=start={edges[i]}" + (f":end={edges[i + 1]}" if edges[i + 1] is not None else "")
        pad = f",apad=pad_dur={PAUSE_GAP}" if edges[i + 1] is not None else ""
        parts.append(f"[0:a]{trim},asetpts=PTS-STARTPTS{pad}[p{i}]")
    graph = ";".join(parts) + ";" + "".join(f"[p{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1[a]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", graph, "-map", "[a]",
                    "-c:a", "libmp3lame", "-b:a", "192k", out], check=True)
    return cues

def main(paths, words_json=None):
    with tempfile.TemporaryDirectory() as tmp:
        joined = os.path.join(tmp, "joined.wav")
        join_parts(paths, joined)
        words = [tuple(w) for w in json.load(open(words_json))] if words_json else transcribe(joined)
        cues = align(words)
        audio = os.path.join(HERE, "ramps_audio.mp3")
        cues = insert_pauses(cues, joined, audio)
    over = os.path.join(HERE, "ramps_cues_override.json")
    if os.path.exists(over):
        for k, v in json.load(open(over)).items():
            if isinstance(v, list): cues[k] = list(v)
            else: cues[k][0] += v
    cues["_end"] = [duration(audio) + 1.0, 0]
    json.dump(cues, open(os.path.join(HERE, "ramps_cues.json"), "w"), indent=1)
    for k, _ in SCRIPT:
        print(f"{cues[k][0]:7.2f} {cues[k][1]:5.2f} {k}")
    print(f"wrote ramps_cues.json and ramps_audio.mp3 ({cues['_end'][0]:.1f} s)")

if __name__ == "__main__":
    args = sys.argv[1:]
    wj = None
    if "--words" in args:          # testing: use a saved word list instead of transcribing
        i = args.index("--words"); wj = args[i + 1]; del args[i:i + 2]
    if not args:
        sys.exit(__doc__)
    main(args, wj)
