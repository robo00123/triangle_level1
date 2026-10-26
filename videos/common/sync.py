"""Line a lesson video up with its ElevenLabs narration, word by word. Each video calls run() from a small wrapper:

    python sync_work.py narration.mp3                       # one file
    python sync_work.py part1.mp3 part2.mp3 part3.mp3 ...   # the script in parts

Uses pocketsphinx (pip install pocketsphinx). Its English model comes with the package, so nothing is downloaded.
1. Recognise the narration in chunks between pauses.
2. Match the recognised words to the script to find roughly where each line is spoken.
3. Snap each line to the pauses around it and force-align its text to that stretch of audio, which times every word.
4. Add the silences the script asks for (script.gaps(): the pause to try a question, a beat between slides, ...).

Writes <name>_audio.mp3 (the narration with the silences added) and <name>_cues.json:
    {key: [start, duration], "_words": {key: [start of each script word..., end of line]}, "_end": [length, 0]}
An optional <name>_cues_override.json moves whole lines by hand: {"e1s2": 0.5} plays that line's animation 0.5 s later.
"""
import difflib, json, os, re, subprocess, tempfile

SR = 16000
# pronunciations missing from the pocketsphinx dictionary, and the voice's readings of cos and mu
EXTRA_WORDS = {"frictional": "F R IH K SH AH N AH L", "hypotenuse": "HH AY P AA T AH N UW S", "newtons": "N UW T AH N Z",
               "resistances": "R IH Z IH S T AH N S AH Z", "kilojoules": "K IH L AH JH UW L Z", "storey": "S T AO R IY",
               "cosine": "K OW S AY N", "cos(2)": "K AA Z", "mu(2)": "M Y UW"}

# ------------------------------------------------------------------ the script as it is spoken
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = {2: "twenty", 3: "thirty", 4: "forty", 5: "fifty", 6: "sixty", 7: "seventy", 8: "eighty", 9: "ninety"}

def int_words(n):
    if n < 20: return [ONES[n]]
    if n < 100: return [TENS[n // 10]] + ([ONES[n % 10]] if n % 10 else [])
    if n < 1000: return [ONES[n // 100], "hundred"] + (int_words(n % 100) if n % 100 else [])
    return int_words(n // 1000) + ["thousand"] + (int_words(n % 1000) if n % 1000 else [])

def spoken(word):
    """one written word -> the dictionary words the narrator says, e.g. '51.88' -> fifty one point eight eight"""
    w = word.lower().replace("’", "'").strip(".,;:!?\"()")
    if re.fullmatch(r"\d+(\.\d+)?", w):
        a, _, b = w.partition(".")
        return int_words(int(a)) + (["point"] + [ONES[int(c)] for c in b] if b else [])
    if w == "mr": return ["mister"]
    return [t for t in (re.sub(r"[^a-z']", "", p) for p in w.split("-")) if t]

def line_tokens(line):
    """[(index of the written word, spoken token)] for one script line"""
    return [(i, tok) for i, wd in enumerate(line.split()) for tok in spoken(wd)]

# ------------------------------------------------------------------ audio
def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)

def join_parts(paths, out):
    if len(paths) == 1:
        ffmpeg("-i", paths[0], "-ar", "44100", "-ac", "1", out)
        return
    ins = [a for p in paths for a in ("-i", p)]
    graph = "".join(f"[{i}:a]" for i in range(len(paths))) + f"concat=n={len(paths)}:v=0:a=1[a]"
    ffmpeg(*ins, "-filter_complex", graph, "-map", "[a]", "-ar", "44100", "-ac", "1", out)

def silences(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "silencedetect=noise=-40dB:d=0.2", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]
    return list(zip(starts, ends))

def decoder(**kw):
    from pocketsphinx import Decoder
    d = Decoder(samprate=SR, **kw)
    for w, ph in EXTRA_WORDS.items():
        if d.lookup_word(w) is None:
            d.add_word(w, ph, True)
    return d

def words_of(d, offset):
    out = []
    for s in d.seg():
        w = re.sub(r"\(\d+\)$", "", s.word)
        if w in ("<s>", "</s>", "<sil>") or w.startswith("[") or w.startswith("+"): continue
        out.append((w, offset + s.start_frame / 100, offset + (s.end_frame + 1) / 100))
    return out

# ------------------------------------------------------------------ 1 and 2: recognise, then find each line
def recognise(raw, sil, total):
    d = decoder()
    edges = [0.0] + [(a + b) / 2 for a, b in sil if b - a >= 0.3] + [total]
    heard = []
    for a, b in zip(edges, edges[1:]):
        d.start_utt(); d.process_raw(raw[int(a * SR) * 2:int(b * SR) * 2], full_utt=True); d.end_utt()
        heard += words_of(d, a)
    return heard

def rough_lines(script, heard, total):
    """start and end of every line from the recognised words; lines that weren't heard are interpolated"""
    toks, owner = [], []
    for li, (_, line) in enumerate(script):
        for _, tok in line_tokens(line):
            toks.append(tok)
            owner.append(li)
    t = [None] * len(toks)
    sm = difflib.SequenceMatcher(None, toks, [w for w, _, _ in heard], autojunk=False)
    for a, b, n in sm.get_matching_blocks():
        if n >= 2:                                   # single-word matches are often coincidences
            for k in range(n):
                t[a + k] = heard[b + k][1:]
    known = [i for i, x in enumerate(t) if x]
    print(f"recognised {len(known)} of {len(toks)} script words")
    pts = [(-1, (0.0, 0.0))] + [(i, t[i]) for i in known] + [(len(toks), (total, total))]
    for (i0, (_, e0)), (i1, (s1, _)) in zip(pts, pts[1:]):
        gap = list(range(i0 + 1, i1))
        if not gap: continue
        w = [len(toks[i]) + 1 for i in gap]
        acc = 0
        for i, wi in zip(gap, w):
            st = e0 + (s1 - e0) * acc / sum(w)
            acc += wi
            t[i] = (st, e0 + (s1 - e0) * acc / sum(w))
    bounds = []
    for li in range(len(script)):
        idx = [i for i, o in enumerate(owner) if o == li]
        bounds.append([t[idx[0]][0], t[idx[-1]][1]])
    return bounds

def snap(bounds, sil, total):
    """lines start just after a pause and end just before one"""
    ends = [b for _, b in sil]
    starts = [a for a, _ in sil]
    out = []
    for s, e in bounds:
        cs = min(ends, key=lambda x: abs(x - s), default=s)
        ce = min(starts, key=lambda x: abs(x - e), default=e)
        s2 = cs if abs(cs - s) < 0.8 else s
        e2 = ce if abs(ce - e) < 0.8 and ce > s2 + 0.3 else e
        out.append([max(0.0, s2), min(total, e2)])
    for i in range(1, len(out)):
        out[i][0] = max(out[i][0], out[i - 1][0] + 0.05)
    return out

# ------------------------------------------------------------------ 3: force-align every line
def align_line(raw, line, s, e, total):
    toks = line_tokens(line)
    a, b = max(0.0, s - 0.08), min(total, e + 0.25)
    d = decoder(bestpath=False)
    d.set_align_text(" ".join(tok for _, tok in toks))
    d.start_utt(); d.process_raw(raw[int(a * SR) * 2:int(b * SR) * 2], full_utt=True); d.end_utt()
    got = words_of(d, a)
    if [w for w, _, _ in got] != [tok for _, tok in toks]:
        return None
    starts = [None] * len(line.split())
    for (wi, _), (_, st, _) in zip(toks, got):
        if starts[wi] is None: starts[wi] = st
    return starts + [got[-1][2]]

def time_words(script, raw, bounds, total):
    words = {}
    for (key, line), (s, e) in zip(script, bounds):
        ws = align_line(raw, line, s, e, total)
        if ws is None:
            n = len(line.split())
            ws = [s + (e - s) * i / n for i in range(n)] + [e]
            print(f"warning: could not force-align '{key}', spread its words evenly")
        words[key] = ws
    return words

# ------------------------------------------------------------------ 4: silences between lines
def insert_gaps(script, gaps, words, src, out):
    keys = [k for k, _ in script]
    cuts = []                                     # (time in the original audio, seconds of silence)
    for k, g in gaps.items():
        nxt = keys[keys.index(k) + 1]
        cuts.append(((words[k][-1] + words[nxt][0]) / 2, g))
    cuts.sort()
    for k in words:
        shift = sum(g for c, g in cuts if words[k][0] >= c)
        words[k] = [x + shift for x in words[k]]
    parts, edges = [], [0.0] + [c for c, _ in cuts] + [None]
    for i in range(len(edges) - 1):
        trim = f"atrim=start={edges[i]}" + (f":end={edges[i + 1]}" if edges[i + 1] is not None else "")
        pad = f",apad=pad_dur={cuts[i][1]}" if edges[i + 1] is not None else ""
        parts.append(f"[0:a]{trim},asetpts=PTS-STARTPTS{pad}[p{i}]")
    graph = ";".join(parts) + ";" + "".join(f"[p{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1[a]"
    ffmpeg("-i", src, "-filter_complex", graph, "-map", "[a]", "-c:a", "libmp3lame", "-b:a", "192k", out)
    return words

def run(script_module, paths, here, name):
    script = script_module.SCRIPT
    with tempfile.TemporaryDirectory() as tmp:
        joined, rawf = os.path.join(tmp, "joined.wav"), os.path.join(tmp, "joined.raw")
        join_parts(paths, joined)
        ffmpeg("-i", joined, "-ar", str(SR), "-ac", "1", "-f", "s16le", rawf)
        raw = open(rawf, "rb").read()
        total = len(raw) / (2 * SR)
        sil = silences(joined)
        bounds = snap(rough_lines(script, recognise(raw, sil, total), total), sil, total)
        words = time_words(script, raw, bounds, total)
        audio = os.path.join(here, f"{name}_audio.mp3")
        words = insert_gaps(script, script_module.gaps(), words, joined, audio)
    over = os.path.join(here, f"{name}_cues_override.json")
    if os.path.exists(over):
        for k, v in json.load(open(over)).items():
            words[k] = [x + v for x in words[k]]
    cues = {k: [words[k][0], words[k][-1] - words[k][0]] for k, _ in script}
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio],
                         capture_output=True, text=True, check=True)
    cues["_words"] = {k: [round(x, 3) for x in v] for k, v in words.items()}
    cues["_end"] = [float(out.stdout) + 1.0, 0]
    json.dump(cues, open(os.path.join(here, f"{name}_cues.json"), "w"), indent=1)
    for k, _ in script:
        print(f"{cues[k][0]:7.2f} {cues[k][1]:5.2f} {k}")
    print(f"wrote {name}_cues.json and {name}_audio.mp3 ({cues['_end'][0]:.1f} s)")
