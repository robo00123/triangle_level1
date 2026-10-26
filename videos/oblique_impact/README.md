# Oblique impact with a wall: proving the results with the scalar product

A proof video in the same style as the work done videos. It derives the two results for a smooth sphere bouncing off a
smooth wall that is not in the *i* or *j* direction:

- **u** · **w** = **v** · **w**, for any vector **w** along the wall
- −*e* **u** · **I** = **v** · **I**, for any vector **I** perpendicular to the wall

The shared building blocks live in `../common`: `make_video.py` (colours, arrows, text, title cards), `lesson.py` (cue
timing, captions, working rows, section cards and the call to action) and `sync.py` (lines the animation up with the
narration).

| File | What it is |
|---|---|
| `impact_script.py` | The narration: one `(key, sentence)` pair per animation cue, and the pauses to add |
| `script.txt`, `script_part*.txt` | The narration as plain text for ElevenLabs (whole, and in four parts under 2,500 characters) |
| `make_impact.py` | The animation |
| `sync_impact.py` | Lines the animation up with the recorded narration, word by word |
| `narration.mp3` | The ElevenLabs narration |
| `impact_audio.mp3`, `impact_cues.json` | The narration with the pauses added, and the time of every script line and word (made by `sync_impact.py`) |
| `impact_title.png` | The lesson title slide, *Rebounding particles against inclined walls*, shown at the start |
| `youtube.txt` | The YouTube title, tags, description, chapters and hashtags (chapter times are from the synced narration) |

## Structure

1. Opening: the lesson title slide
2. The set-up: the sphere moves in, hits the tilted wall and bounces off; **u**, **v**, *α*, *β* and *e*; the wall is
   not in the **i** or **j** direction, so **w** (along the wall) and **I** (perpendicular) are used instead; the
   picture turns so the wall is horizontal
3. What happens in the collision: each velocity split along and perpendicular to the wall; the smooth wall gives
   *u* cos *α* = *v* cos *β* (1), and restitution gives *v* sin *β* = *eu* sin *α* (2)
4. Reminder of the scalar product: **a** · **b** = |**a**||**b**| cos *θ*, tail to tail; with a unit vector it is the
   component (the shadow) of **a**, which shrinks to zero at 90° and turns negative past it
5. Along the wall: **u** slides along its line to sit tail to tail with **ŵ**, so **u** · **ŵ** = *u* cos *α*;
   **v** · **ŵ** = *v* cos *β*; the two shadows on the wall are the same length, so **u** · **w** = **v** · **w**
6. Perpendicular, **u**: the angle between **u** and **Î** is 90° + *α*; the unit circle shows
   cos(90° + *α*) = −sin *α*, so **u** · **Î** = −*u* sin *α*, a shadow pointing against **Î**
7. Perpendicular, **v**: the angle is 90° − *β*; the right-angled triangle under **v** shows cos(90° − *β*) = sin *β*,
   so **v** · **Î** = *v* sin *β*
8. Restitution: substituting into (2) gives **v** · **Î** = −*e* **u** · **Î**; the shadow of **u** is reversed and
   multiplied by *e* to land exactly on the shadow of **v**; so −*e* **u** · **I** = **v** · **I**
9. The two results, and why they work for a wall in any direction with **I** pointing either way
10. Example: a sphere with velocity (11**i** − 2**j**) m s⁻¹ hits a wall parallel to 3**i** + 4**j** with *e* = ½
    (answer −**i** + 7**j** m s⁻¹)
11. Call to action card

## Pacing

`impact_script.py` sets the silences that `sync_impact.py` adds to the narration (the silent draft uses them too):

- `SCENE_GAP` (1 s) after the last line of every slide: the finished slide stays on screen, then crossfades into the next
- `SLOW_GAP` (0.6 s) after each step of the proof, to take it in

## Making the video

```bash
pip install cairosvg pocketsphinx              # Montserrat and Liberation Sans must be installed as system fonts

python impact_script.py                        # writes script.txt and script_part1..4 for ElevenLabs
# record the narration in ElevenLabs, as one MP3 or as the four parts

python sync_impact.py narration.mp3            # writes impact_audio.mp3 and impact_cues.json
python make_impact.py cues                     # check the line timings
python make_impact.py test 60 200 380          # single frames at those times, to check the layout
python make_impact.py                          # render every frame
python make_impact.py encode                   # impact.mp4, with impact_audio.mp3
```

Until `impact_cues.json` exists, the animation uses timings estimated from the script, so `make_impact.py` renders a
silent draft.

In `make_impact.py`, `S("w5", "exactly the same")` is the moment the narrator starts saying "exactly the same" in line
`w5`. Animation events are pinned to their words like this, so they stay in sync with any recording of the script. If
the wording of a line changes, update `impact_script.py` to match. A phrase that no longer appears in its line stops
the render with an error naming the line.
