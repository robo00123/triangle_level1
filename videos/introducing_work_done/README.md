# Introducing work done: video tutorial

The lesson before *Work done on ramps*, in the same style. The shared building blocks live in `../common`:
`make_video.py` (colours, arrows, text, title cards), `lesson.py` (cue timing, captions, working rows, bars, the pause
banner, section cards and the call to action) and `sync.py` (lines the animation up with the narration).

| File | What it is |
|---|---|
| `work_script.py` | The narration: one `(key, sentence)` pair per animation cue, and the pauses to add |
| `script.txt`, `script_part*.txt` | The narration as plain text for ElevenLabs (whole, and in four parts under 2,500 characters) |
| `make_work.py` | The animation |
| `sync_work.py` | Lines the animation up with the recorded narration, word by word |
| `work_title.png` | The lesson title slide, shown at the start |

## Structure

1. Opening: the lesson title slide
2. What is work done? A force that moves a box does work and the work bar fills; pushing on a wall does none
3. How much work is done? Double the force or double the distance and the work doubles, so *W* = *Fs*; one joule
4. Example 1: a crate pushed 12 m by 25 N (300 J)
5. Work done against gravity: lifting at a steady speed needs a force equal to the weight, so *W* = *mgh*
6. Example 2: a 12 kg box lifted 5 m (588 J)
7. Example 3: a 60 kg crate raised to the top of a tower with 24 kJ (40.8 m), checked against a 13 storey building
8. Work done against friction: push = friction at constant speed, friction = *μR* and *R* = *mg*, so *W* = *μmg* × *s*
9. Example 4: an 8 kg crate pushed 6 m with 72 J against friction (*μ* = 0.153)
10. Your turn: a 5 kg crate at 4 m s⁻¹ for 3 seconds with *μ* = 0.4 (235.2 J), with the pause banner and a common mistake
11. Call to action card

## Pacing

`work_script.py` sets the silences that `sync_work.py` adds to the narration (the silent draft uses them too):

- `SCENE_GAP` (1 s) after the last line of every slide: the finished slide stays on screen, then crossfades into the next
- `SLOW_GAP` (0.6 s) after each line that introduces the idea of work done
- `PAUSE_GAP` (6 s) after "Pause the video now", for the viewer to try the question

## Making the video

```bash
pip install cairosvg pocketsphinx              # Montserrat and Liberation Sans must be installed as system fonts

python work_script.py                          # writes script.txt and script_part1..4 for ElevenLabs
# record the narration in ElevenLabs, as one MP3 or as the four parts

python sync_work.py narration.mp3              # writes work_audio.mp3 and work_cues.json
python make_work.py cues                       # check the line timings
python make_work.py test 60 200 380            # single frames at those times, to check the layout
python make_work.py                            # render every frame
python make_work.py encode                     # work.mp4, with work_audio.mp3
```

In `make_work.py`, `S("e1s2", "300 joules")` is the moment the narrator starts saying "300 joules" in line `e1s2`.
Animation events are pinned to their words like this, so they stay in sync with any recording of the script. If the
wording of a line changes, update `work_script.py` to match. A phrase that no longer appears in its line stops the
render with an error naming the line.
