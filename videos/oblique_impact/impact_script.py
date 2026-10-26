SCRIPT = [
    # ---------------- part 1: the collision
    ("open",  "Welcome to this lesson on oblique impact with a wall. When a smooth sphere bounces off a smooth wall at an angle, there are two results that let you find its velocity after the impact, without working out a single angle. They're very useful, but they're rarely taught. In this video, we'll prove both of them using the scalar product."),
    ("s1",    "Imagine looking down on a smooth sphere moving across a smooth horizontal surface, towards a smooth vertical wall. It hits the wall at an angle, and bounces off."),
    ("s2",    "Before the impact, the velocity of the sphere is u. After the impact, its velocity is v."),
    ("s3",    "u makes an angle alpha with the wall, and v makes an angle beta with the wall. The coefficient of restitution between the sphere and the wall is e."),
    ("s4",    "Notice that the wall isn't in the i direction or the j direction. So splitting the velocities into i and j components won't help us here."),
    ("s5",    "Instead, we use two directions that suit the wall. w points along the wall, and I is perpendicular to the wall, pointing away from it. So w and I are perpendicular to each other."),
    ("s6",    "Let's turn the picture so that the wall is horizontal. The collision hasn't changed at all. We're just looking at it from a different angle."),
    ("p1",    "Now let's split each velocity into two parts, one along the wall and one perpendicular to it."),
    ("p2",    "Before the impact, the sphere moves along the wall at u cos alpha, and towards the wall at u sine alpha."),
    ("p3",    "After the impact, it moves along the wall at v cos beta, and away from the wall at v sine beta."),
    ("p4",    "The wall is smooth, so the impulse from the wall acts perpendicular to the wall. There's no impulse along the wall, so the velocity along the wall doesn't change. u cos alpha equals v cos beta."),
    ("p5",    "Perpendicular to the wall, we use Newton's law of restitution. The speed away from the wall is e times the speed towards it. So v sine beta equals e u sine alpha."),
    ("p6",    "These two equations are our starting point. Now let's write them using the scalar product."),
    # ---------------- part 2: the scalar product, and along the wall
    ("d1",    "First, a quick reminder. The scalar product of two vectors a and b is the magnitude of a, times the magnitude of b, times the cosine of the angle between them. That angle is measured with the vectors tail to tail."),
    ("d2",    "If one of the vectors is a unit vector, like w hat, its magnitude is 1. So a dot w hat is just the magnitude of a times cos theta. That's the component of a in the direction of w hat. You can think of it as the shadow of a on that line."),
    ("d3",    "Watch what happens as the angle gets bigger. At 90 degrees, there's no shadow, so the scalar product is zero. Past 90 degrees, the cosine is negative, so the component is negative. The vector is pointing backwards, against w hat."),
    ("w1",    "Let's start along the wall, with u dot w hat, where w hat is the unit vector along the wall."),
    ("w2",    "To find the angle between u and w hat, we need them tail to tail. So slide u along its line until its tail is at the point of impact. Now we can see that the angle between u and w hat is alpha."),
    ("w3",    "So u dot w hat is the magnitude of u, times the magnitude of w hat, times cos alpha. w hat is a unit vector, so its magnitude is 1. That leaves u cos alpha, where u is the speed. It's the shadow of u on the wall."),
    ("w4",    "v and w hat are already tail to tail, with an angle beta between them. So v dot w hat is v times 1 times cos beta, which is v cos beta."),
    ("w5",    "We know that u cos alpha equals v cos beta. You can see it in the shadows, which are exactly the same length. So u dot w hat equals v dot w hat."),
    ("w6",    "Finally, w is w hat multiplied by the magnitude of w. Multiply both sides by the magnitude of w, and we get our first result. u dot w equals v dot w, for any vector w along the wall."),
    # ---------------- part 3: perpendicular to the wall
    ("n1",    "Now for the direction perpendicular to the wall. This time we need u dot I hat, where I hat is the unit vector perpendicular to the wall, pointing away from it."),
    ("n2",    "Put u and I hat tail to tail. I hat points away from the wall, and u points into it. The angle between them is a right angle plus alpha. That's 90 degrees plus alpha."),
    ("n3",    "So u dot I hat is the magnitude of u, times 1, times cos of 90 plus alpha."),
    ("n4",    "What is cos of 90 plus alpha? On the unit circle, the point at an angle alpha has coordinates cos alpha, sine alpha. Now turn it through another 90 degrees. The triangle turns with it, and the x coordinate becomes negative sine alpha. So cos of 90 plus alpha is negative sine alpha."),
    ("n5",    "That means u dot I hat equals negative u sine alpha. You can see why in the shadow. The shadow of u on the line of I hat points the opposite way to I hat, so it's negative. The sphere is moving towards the wall."),
    ("n6",    "Now v dot I hat. v points away from the wall, at an angle beta above it. So the angle between v and I hat is 90 degrees minus beta."),
    ("n7",    "So v dot I hat is v times 1 times cos of 90 minus beta."),
    ("n8",    "Look at the right-angled triangle under v. Its angles are beta and 90 minus beta. The side opposite beta is next to the angle 90 minus beta. So cos of 90 minus beta is the same as sine beta."),
    ("n9",    "So v dot I hat equals v sine beta. This time, the shadow points the same way as I hat, so it's positive. The sphere is moving away from the wall."),
    ("r1",    "Now we bring in Newton's law of restitution. v sine beta equals e u sine alpha."),
    ("r2",    "We've just seen that v sine beta is v dot I hat, and u sine alpha is negative u dot I hat."),
    ("r3",    "Substituting, v dot I hat equals e times negative u dot I hat. That's negative e times u dot I hat."),
    ("r4",    "Here it is with the shadows. Reverse the shadow of u, multiply it by e, and you get the shadow of v exactly."),
    ("r5",    "Finally, I is I hat multiplied by the magnitude of I. Multiply both sides by the magnitude of I, and we get our second result. Negative e times u dot I equals v dot I, for any vector I perpendicular to the wall."),
    # ---------------- part 4: the results in use
    ("sum1",  "So here are the two results. u dot w equals v dot w. And negative e times u dot I equals v dot I."),
    ("sum2",  "The first says the component of the velocity along the wall doesn't change. The second says the component perpendicular to the wall reverses, and is multiplied by e."),
    ("sum3",  "Because they're written with scalar products, they work for a wall in any direction. w can be any vector along the wall, and I can be any vector perpendicular to it, pointing either way. You never need to find alpha or beta."),
    ("ex0",   "Let's see how useful that is."),
    ("ex1",   "A smooth sphere is moving on a smooth horizontal surface with velocity 11 i minus 2 j metres per second. It hits a smooth vertical wall, which is parallel to the vector 3 i plus 4 j. The coefficient of restitution is a half. Find the velocity of the sphere after the impact."),
    ("ex2",   "Let the velocity after the impact be a i plus b j. Along the wall, w is 3 i plus 4 j. For I, swap the components and change one sign, which gives 4 i minus 3 j. w dot I is 12 minus 12, which is zero, so they are perpendicular."),
    ("ex3",   "Along the wall, u dot w equals v dot w. u dot w is 11 times 3, plus negative 2 times 4, which is 25. And v dot w is 3 a plus 4 b. So 3 a plus 4 b equals 25."),
    ("ex4",   "Perpendicular to the wall, negative e times u dot I equals v dot I. u dot I is 11 times 4, plus negative 2 times negative 3, which is 50. Negative a half times 50 is negative 25. So 4 a minus 3 b equals negative 25."),
    ("ex5",   "Solving these simultaneous equations gives a equals negative 1, and b equals 7. So the sphere leaves the wall with velocity negative i plus 7 j metres per second, and we didn't need a single angle."),
    ("cta",   "That's oblique impact with a wall, using the scalar product. You'll find the full lesson and the worksheet at Mr Mathematics dot com, and the link to the worksheet is in the description below. Thanks for watching."),
]

PARTS = [("part1_the_collision", "open", "d1"), ("part2_along_the_wall", "d1", "n1"),
         ("part3_perpendicular", "n1", "sum1"), ("part4_using_the_results", "sum1", None)]

# Silence added to the narration after these lines (the sync puts it into the audio; the draft timing uses it too)
PAUSE_KEYS = ()
PAUSE_GAP = 6.0
SCENE_STARTS = ("s1", "p1", "d1", "w1", "n1", "n6", "r1", "sum1", "ex0", "ex1", "cta")
SCENE_GAP = 1.0                # a beat between slides
SLOW_KEYS = tuple(k for k, _ in SCRIPT if k[0] in "spdwnr" and not k.startswith("ex"))
SLOW_GAP = 0.6                 # time to take in each step of the proof

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
    # python impact_script.py  ->  script.txt (whole narration) and one file per part, ready for ElevenLabs
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
