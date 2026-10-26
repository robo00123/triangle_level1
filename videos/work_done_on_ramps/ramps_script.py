SCRIPT = [
    # ---------------- part 1: work done and gravity
    ("open",  "Welcome to this lesson on work done on ramps. When we pull a box up a rough slope, the pulling force has two jobs to do. It lifts the box against gravity, and it overcomes friction. By the end of this video, you'll see exactly where each part of this formula comes from."),
    ("wd1",   "Let's start with a quick reminder. When a force moves an object, it does work. The work done is the force multiplied by the distance moved in the direction of the force."),
    ("wd2",   "Work done is measured in joules. Watch the bar fill up as the box moves. Twice the distance means twice the work."),
    ("g1",    "First, work done against gravity. Here's a box being pulled a distance d up a smooth slope."),
    ("g2",    "As the box moves along the slope, it also rises. The vertical height it gains is h."),
    ("g3",    "Gravity pulls straight down with the weight, m g. The box is moving along the slope, so let's resolve the weight into two components."),
    ("g4",    "One component, m g cos alpha, pushes into the slope. The other, m g sine alpha, acts down the slope, directly against the motion. That's the part we have to work against."),
    ("g5",    "So the work done against gravity is m g sine alpha, multiplied by the distance d."),
    ("g6",    "Now look at the triangle. Sine alpha is the opposite over the hypotenuse, which is h over d. Rearranging, d sine alpha is just h."),
    ("g7",    "So the work done against gravity is simply m g h. That's the weight multiplied by the vertical height gained."),
    ("g8",    "Here's why that's so useful. On the left, we lift the box straight up through a height h. On the right, we pull it up a slope to the same height."),
    ("g9",    "Lifting straight up takes the full weight, but over a short distance. Pulling up the slope takes a smaller force, but over a longer distance."),
    ("g10",   "Watch the work bars. They finish at exactly the same level. Only the vertical height matters, not the route the box takes."),
    # ---------------- part 2: friction and both together
    ("f1",    "Now let's look at friction. This time, the slope is rough."),
    ("f2",    "As the box moves up the slope, friction acts down the slope, against the motion. Friction stays the same size all the way up, so the work done against it grows steadily with every metre."),
    ("f3",    "To find the friction, we need the normal reaction, R. Resolve perpendicular to the slope. The box doesn't move into the slope or away from it, so R balances m g cos alpha."),
    ("f4",    "The box is moving, so friction is limiting. Friction equals mu R, which is mu m g cos alpha."),
    ("f5",    "The work done against friction is the friction multiplied by the distance moved. That's mu m g cos alpha, multiplied by d."),
    ("f6",    "Notice the difference. For gravity, we use the vertical height. For friction, we use the full distance along the slope, because friction acts the whole way."),
    ("c1",    "Now let's put them together. A force T pulls the box up the rough slope at a constant speed."),
    ("c2",    "Constant speed means there's no acceleration, so the forces along the slope balance. T equals the friction plus m g sine alpha."),
    ("c3",    "The work done by T is T multiplied by d. Multiplying out gives mu m g d cos alpha, plus m g d sine alpha."),
    ("c4",    "That's the work done against friction plus the work done against gravity. Watch the bars. The work done by T is exactly the two added together."),
    ("c5",    "And that's the formula from the start. T times d equals mu R times d, plus m g h."),
    ("tips",  "So when you solve a problem on a ramp, follow these four steps. Draw a force diagram. Find sine alpha and cos alpha from a right-angled triangle. Resolve perpendicular to the slope to find R. Then use the vertical height for gravity, and the full distance for friction."),
    # ---------------- part 3: worked example
    ("w0",    "Let's try an example together."),
    ("w1",    "A rough plane is inclined at an angle alpha to the horizontal, where tan alpha is 8 over 15."),
    ("w2",    "A box of mass 6 kilograms is pulled at a constant speed up a line of greatest slope. The coefficient of friction between the box and the plane is 0.4."),
    ("w3",    "First, we need the size of the frictional force. Then the box moves 20 metres up the plane, and we need the work done against friction and against gravity."),
    ("wtri",  "Tan alpha is 8 over 15, so let's draw a right-angled triangle with sides 8 and 15. Pythagoras gives a hypotenuse of 17. So sine alpha is 8 over 17, and cos alpha is 15 over 17."),
    ("wR",    "Resolve perpendicular to the plane. R equals 6 g cos alpha, which is 6 times 9.8 times 15 over 17. That's 51.88 newtons."),
    ("wF",    "The box is moving, so friction is limiting. Friction is 0.4 times 51.88, which is 20.8 newtons to 3 significant figures."),
    ("wmove", "Now let's watch the box move 20 metres up the slope."),
    ("wwf",   "Friction acts the whole way up, so the work done against friction is 20.75 times 20. That's 415 joules to 3 significant figures."),
    ("wh",    "For gravity, we need the height gained. The box rises 20 times sine alpha, which is 20 times 8 over 17. That's 9.41 metres."),
    ("wwg",   "So the work done against gravity is m g h. 6 times 9.8 times 9.41 is 553 joules to 3 significant figures."),
    ("wtot",  "Altogether, the pulling force does both jobs. That's 415 plus 553, which is 968 joules of work."),
    ("wchk",  "Does it make sense that more work goes against gravity than against friction? Yes. The component of the weight down the slope is about 27.7 newtons. That's bigger than the 20.8 newtons of friction."),
    # ---------------- part 4: your turn
    ("q2a",   "Now it's your turn."),
    ("q2b",   "A rough surface is inclined at an angle of arc tan 3 over 4 to the horizontal. A parcel of mass 1.5 kilograms is pulled 4 metres at a constant speed up the surface, by a force acting along a line of greatest slope."),
    ("q2c",   "The only resistances to the motion are friction and gravity. The work done by the force is 50 joules."),
    ("q2d",   "Find the coefficient of friction between the parcel and the surface."),
    ("q2p",   "Pause the video now and have a go. Think about how the 50 joules is shared between gravity and friction. Press play when you're ready to check your answer."),
    ("q2r",   "Right, let's go through it."),
    ("s2a",   "Tan alpha is 3 over 4, so this is a 3, 4, 5 triangle. Sine alpha is 3 fifths, and cos alpha is 4 fifths."),
    ("s2b",   "The parcel moves 4 metres along the slope, so it rises 4 times 3 fifths. That's 2.4 metres."),
    ("s2c",   "The work done against gravity is m g h. That's 1.5 times 9.8 times 2.4, which is 35.28 joules."),
    ("s2d",   "The force does 50 joules of work in total. Gravity takes 35.28 joules, so the other 14.72 joules goes into overcoming friction."),
    ("s2e",   "Now resolve perpendicular to the slope. R is 1.5 g cos alpha, which is 11.76 newtons."),
    ("s2f",   "The work done against friction is mu R multiplied by d. So 14.72 equals mu times 11.76 times 4, which is 47.04 mu."),
    ("s2g",   "Divide both sides by 47.04, and mu is 0.313 to 3 significant figures."),
    ("s2chk", "Does that make sense? A coefficient of friction of 0.313 is a sensible value for a rough surface. A common mistake is to use all 50 joules for friction. That gives a coefficient bigger than 1, which should make you suspicious. Always take away the work done against gravity first."),
    ("cta",   "That's work done on ramps. You'll find the full lesson and the worksheet at Mr Mathematics dot com, and the link to the worksheet is in the description below. Thanks for watching."),
]

PARTS = [("part1_work_and_gravity", "open", "f1"), ("part2_friction", "f1", "w0"),
         ("part3_worked_example", "w0", "q2a"), ("part4_your_turn", "q2a", None)]

PAUSE_KEYS = ("q2p",)
PAUSE_GAP = 6.0        # seconds of silence after the pause line, for the viewer to try the question


def estimated_cues(words_per_sec=2.5, gap=0.7, start=0.3):
    cues, t = {}, start
    for key, line in SCRIPT:
        dur = len(line.split()) / words_per_sec
        cues[key] = (t, dur)
        t += dur + gap + (PAUSE_GAP if key in PAUSE_KEYS else 0)
    return cues, t


if __name__ == "__main__":
    # python ramps_script.py  ->  script.txt (whole narration) and one file per part, ready for ElevenLabs
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
