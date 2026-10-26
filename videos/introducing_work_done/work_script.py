SCRIPT = [
    # ---------------- part 1: what is work done?
    ("open",  "Welcome to this lesson, an introduction to work done. Work done is a way of measuring what a force achieves when it moves an object. By the end of this video, you'll be able to calculate the work done by a force, against gravity, and against friction."),
    ("i1",    "Let's start with the big idea."),
    ("i2",    "Work is done whenever a force makes an object move."),
    ("i3",    "Here, a force pushes a box along the floor. The box moves, so the force is doing work."),
    ("i4",    "Watch the bar. The further the box moves, the more work the force does."),
    ("i5",    "Now this force is pushing against a wall. However hard it pushes, the wall doesn't move."),
    ("i6",    "Think about leaning on a wall all lesson. You'd feel tired, but the wall hasn't moved, so you've done no work on it."),
    ("i7",    "No movement means no work."),
    ("h1",    "So how much work is done? It depends on two things."),
    ("h2",    "The first is the size of the force. Double the force over the same distance, and twice as much work is done."),
    ("h3",    "The second is how far the object moves in the direction of the force. Use the same force over twice the distance, and again, twice as much work is done."),
    ("h4",    "Putting those together, the work done is the force multiplied by the distance moved in the direction of the force."),
    ("h5",    "When the force acts in the same direction as the motion, this is simply force times distance. We write it as W equals F s, where s is the distance moved."),
    ("h6",    "Work is measured in joules. One joule is the work done when a force of 1 newton moves an object 1 metre."),
    # ---------------- part 2: by a force, and against gravity
    ("e1a",   "Let's try some examples."),
    ("e1b",   "A crate is pushed 12 metres across a horizontal floor by a constant horizontal force of 25 newtons."),
    ("e1c",   "Calculate the work done by the force."),
    ("e1s1",  "The force acts in the direction of motion, so the work done is the force multiplied by the distance."),
    ("e1s2",  "That's 25 times 12, which is 300. So the force does 300 joules of work."),
    ("gv1",   "Now let's lift something. Gravity pulls the box down with its weight, m g."),
    ("gv2",   "To lift it at a steady speed, we pull upwards with a force equal to that weight."),
    ("gv3",   "So when the box is lifted through a height h, the work done against gravity is m g multiplied by h."),
    ("e2a",   "A box of mass 12 kilograms is lifted vertically through a height of 5 metres. Calculate the work done against gravity."),
    ("e2s1",  "The lifting force equals the weight, which is 12 times 9.8. The distance is the height, 5 metres."),
    ("e2s2",  "12 times 9.8 times 5 is 588. So the work done against gravity is 588 joules."),
    ("e3a",   "This next one works backwards, to find a distance."),
    ("e3b",   "A cable is attached to a crate of mass 60 kilograms. The crate is lifted vertically at a constant speed, from the ground to the top of a tower."),
    ("e3c",   "The work done in raising the crate is 24 kilojoules. Calculate the height of the tower."),
    ("e3s1",  "First, convert to joules. 24 kilojoules is 24 thousand joules."),
    ("e3s2",  "The work done against gravity is m g h. So 24 thousand equals 60 times 9.8 times h."),
    ("e3s3",  "60 times 9.8 is 588. Dividing 24 thousand by 588 gives a height of 40.8 metres, to 3 significant figures."),
    ("e3chk", "Does that make sense? 40.8 metres is about the height of a 13 storey building, so it's a sensible height for a tower."),
    # ---------------- part 3: against friction
    ("fr1",   "Now let's look at friction. This time, the floor is rough."),
    ("fr2",   "Friction acts against the motion. To push the crate at a constant speed, the pushing force has to balance the friction exactly."),
    ("fr3",   "Friction is mu R. On a horizontal floor with a horizontal push, the normal reaction R balances the weight, so R equals m g."),
    ("fr4",   "So the work done against friction is mu m g, multiplied by the distance moved."),
    ("e4a",   "A crate of mass 8 kilograms is pushed a distance of 6 metres across a rough horizontal floor. The crate moves at a constant speed."),
    ("e4b",   "The work done against friction is 72 joules. Calculate the coefficient of friction between the crate and the floor."),
    ("e4s1",  "Work done is force times distance, so 72 equals the friction times 6. That makes the friction 12 newtons."),
    ("e4s2",  "The push is horizontal, so R equals m g. That's 8 times 9.8, which is 78.4 newtons."),
    ("e4s3",  "Friction equals mu R, so 12 equals mu times 78.4. Dividing, mu is 0.153 to 3 significant figures."),
    # ---------------- part 4: your turn
    ("q5a",   "Now it's your turn."),
    ("q5b",   "A crate of mass 5 kilograms is pushed across a rough horizontal floor, at a constant speed of 4 metres per second."),
    ("q5c",   "The coefficient of friction between the crate and the floor is 0.4. Calculate the work done against friction in 3 seconds."),
    ("q5p",   "Pause the video now and have a go. Think about how far the crate travels in 3 seconds. Press play when you're ready to check your answer."),
    ("q5r",   "Right, let's go through it."),
    ("s5a",   "First, the distance. At 4 metres per second for 3 seconds, the crate travels 4 times 3, which is 12 metres."),
    ("s5b",   "Next, the friction. On a horizontal floor, R equals m g, so the friction is 0.4 times 5 times 9.8. That's 19.6 newtons."),
    ("s5c",   "The work done against friction is the friction times the distance. 19.6 times 12 is 235.2, so the work done is 235.2 joules."),
    ("s5chk", "A common mistake is to multiply the friction by the time instead of the distance. That gives 58.8, which isn't work done at all. Work done is always force times distance."),
    ("cta",   "That's an introduction to work done. You'll find the full lesson and the worksheet at Mr Mathematics dot com, and the link to the worksheet is in the description below. Thanks for watching."),
]

PARTS = [("part1_what_is_work_done", "open", "e1a"), ("part2_force_and_gravity", "e1a", "fr1"),
         ("part3_friction", "fr1", "q5a"), ("part4_your_turn", "q5a", None)]

# Silence added to the narration after these lines (the sync puts it into the audio; the draft timing uses it too)
PAUSE_KEYS = ("q5p",)          # time to try the question
PAUSE_GAP = 6.0
SCENE_STARTS = ("i1", "h1", "e1a", "e1b", "gv1", "e2a", "e3a", "fr1", "e4a", "q5a", "q5b", "cta")
SCENE_GAP = 1.0                # a beat between slides
SLOW_KEYS = ("i1", "i2", "i3", "i4", "i5", "i6", "i7", "h1", "h2", "h3", "h4", "h5", "h6")
SLOW_GAP = 0.6                 # breathing space while the idea is introduced

def gaps():
    """seconds of silence to add after each line"""
    keys = [k for k, _ in SCRIPT]
    out = {}
    for i, k in enumerate(keys[:-1]):
        if k in PAUSE_KEYS: out[k] = PAUSE_GAP
        elif keys[i + 1] in SCENE_STARTS: out[k] = SCENE_GAP
        elif k in SLOW_KEYS: out[k] = SLOW_GAP
    return out


def estimated_cues(words_per_sec=2.5, gap=0.7, start=0.3):
    cues, t, g = {}, start, gaps()
    for key, line in SCRIPT:
        dur = len(line.split()) / words_per_sec
        cues[key] = (t, dur)
        t += dur + gap + g.get(key, 0.0)
    return cues, t


if __name__ == "__main__":
    # python work_script.py  ->  script.txt (whole narration) and one file per part, ready for ElevenLabs
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    keys = [k for k, _ in SCRIPT]
    with open(os.path.join(here, "script.txt"), "w") as f:
        f.write("\n\n".join(line for _, line in SCRIPT) + "\n")
    for name, a, b in PARTS:
        lines = SCRIPT[keys.index(a):keys.index(b) if b else None]
        body = "\n\n".join(line for _, line in lines) + "\n"
        with open(os.path.join(here, f"script_{name}.txt"), "w") as f:
            f.write(body)
        print(f"{name}: {len(body)} characters, {sum(len(l.split()) for _, l in lines)} words")
    cues, end = estimated_cues()
    print(f"total {sum(len(l) for _, l in SCRIPT)} characters, estimated length {end / 60:.1f} minutes")
