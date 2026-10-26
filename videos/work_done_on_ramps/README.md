# Work done on ramps: video tutorial

Built in the same style as the other Mr Mathematics lesson videos (`make_video.py` holds the shared colours,
arrows, text and title-card helpers, copied unchanged from the reference code).

| File | What it is |
|---|---|
| `ramps_script.py` | The narration: one `(key, sentence)` pair per animation cue |
| `script.txt`, `script_part*.txt` | The narration as plain text for ElevenLabs (whole, and in four parts under 2,500 characters) |
| `make_ramps.py` | The animation, synced to the cues |
| `sync_ramps.py` | Lines the animation up with the recorded narration, word by word |
| `narration.mp3` | The ElevenLabs narration |
| `ramps_audio.mp3`, `ramps_cues.json` | The narration with the pause gap, and the time of every script line and word (made by `sync_ramps.py`) |
| `ramps_title.png` | The lesson title slide, shown at the start |

## Structure

1. Opening: the lesson title slide
2. Work done: a quick reminder (work done = force × distance, the work bar)
3. Work done against gravity: the box rises *h* as it moves *d*, resolve the weight, then *mg* sin *α* × *d* = *mgh*
4. Only the vertical height matters: lifting straight up vs pulling up a slope, same work
5. Work done against friction: work grows steadily with distance, *R* = *mg* cos *α*, *Fr* = *μR*, then *μmg* cos *α* × *d*
6. Pulling at a constant speed: *T* = *Fr* + *mg* sin *α*, so *T* × *d* = *μR* × *d* + *mgh* (stacked work bars)
7. The four steps for ramp problems
8. Worked example (lesson Example 1): 6 kg box, tan *α* = 8/15, *μ* = 0.4, 20 m
9. Your turn (lesson Example 2): 1.5 kg parcel, arctan 3/4, 4 m, 50 J, find *μ*, with the pause banner
10. Call to action card

## Making the video

```bash
pip install cairosvg pocketsphinx              # Montserrat and Liberation Sans must be installed as system fonts

python ramps_script.py                         # writes script.txt and script_part1..4 for ElevenLabs
# record the narration in ElevenLabs, as one MP3 or as the four parts

python sync_ramps.py narration.mp3             # or: python sync_ramps.py part1.mp3 part2.mp3 part3.mp3 part4.mp3
python make_ramps.py cues                      # check the line timings
python make_ramps.py test 100 330 450          # single frames at those times, to check the layout
python make_ramps.py                           # render every frame
python make_ramps.py encode                    # ramps.mp4, with ramps_audio.mp3
```

### How the sync works

`sync_ramps.py` uses pocketsphinx, whose English model comes with the package, so nothing is downloaded. It recognises
the narration, matches the words it hears to the script to find each line, then force-aligns every line's text to its
stretch of audio. That gives the start of every word, typically to within a few hundredths of a second. It then adds 6
seconds of silence after the pause line.

In `make_ramps.py`, `S(key, ...)` gives a time in the narration:

- `S("wR")` is the start of line `wR`.
- `S("wR", "51.88")` is the moment the narrator starts saying "51.88" in that line. Animation events are pinned to the
  word they go with like this, so each line of working appears as it is read out.
- `S("wR", 0.5)` is halfway through the line's words.

Without `ramps_cues.json` the timings are estimated from a speaking rate of 2.5 words per second, which is how the
silent draft was made. If a new recording changes the wording of a line, update `ramps_script.py` to match; an
anchor phrase that no longer appears in its line stops the render with an error naming the line. To move a whole line's
animation by hand, add `ramps_cues_override.json`, for example `{"wwf": 0.5}` to play line `wwf` half a second later.
