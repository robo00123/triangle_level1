import math, os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "common"))
import cairosvg
from multiprocessing import Pool
from make_video import arrow, text, it, col, clamp, fade, ease, card, DEFS, NAVY, GREEN, RED, BLUE, GOLD, W, H, FPS
from lesson import (Cues, window, label, header, divider, footer, caption, qblock, gold_box, answer_box, pop,
                    section_card, cta_card, dashed, darrow, PUR, INK)
import impact_script

OUT = HERE + "/frames_impact"
os.makedirs(OUT, exist_ok=True)
CUES = Cues(impact_script, HERE + "/impact_cues.json")
S, DUR = CUES.S, CUES.dur

# colour code: u green, v blue, along the wall (w) orange, perpendicular to the wall (I) red, e purple
UC, VC, WC, IC, EC = GREEN, BLUE, "#e8650a", RED, PUR
GREY, BGREY, HATCH, BALL = "#9aa3b2", "#5b6b8c", "#8a8f99", "#f6c995"

def bold(s, c=NAVY): return f'<tspan font-weight="bold" fill="{c}">{s}</tspan>'
U_, V_, W_, WH, I_, IH = bold("u", UC), bold("v", VC), bold("w", WC), bold("ŵ", WC), bold("I", IC), bold("Î", IC)
A_, B_ = bold("a"), bold("b", BGREY)
u_, v_, e_ = col(it("u"), UC), col(it("v"), VC), col(it("e"), EC)
AL, BE, TH = it("α"), it("β"), it("θ")
i_, j_ = bold("i"), bold("j")
D = " · "
MS = 'm s<tspan font-size="0.6em" dy="-0.7em">−1</tspan><tspan dy="0.42em"></tspan>'
def mag(x): return f"|{x}|"

def scene(t, first, nxt):
    """a slide stays still through the pause after its last line, then crossfades into the next slide"""
    return window(t, S(first) - 0.55, S(nxt) - 0.55)

def grow(t, start, dur=0.6):
    return ease(clamp((t - start) / dur))

# ------------------------------------------------------------------ the collision, in the wall's own directions
ALPHA, E = 35.0, 0.6
BETA = math.degrees(math.atan(E * math.tan(math.radians(ALPHA))))
ca, sa = math.cos(math.radians(ALPHA)), math.sin(math.radians(ALPHA))
cb, sb = math.cos(math.radians(BETA)), math.sin(math.radians(BETA))
UL = 300.0                              # drawn length of u
VL = UL * ca / cb                       # v has the same component along the wall
UA = (-UL * ca, UL * sa)                # tail of u, whose head is at the point of impact
VB = (VL * cb, VL * sb)                 # head of v
UT = (UL * ca, -UL * sa)                # head of u once it is slid to start at the point of impact
RB = 20                                 # radius of the sphere

class Frame:
    """points (a, b): a along the wall, b away from it, scaled by k, with the wall turned phi degrees and the point of
    impact at C"""
    def __init__(self, C, phi=0.0, k=1.0):
        self.C, self.phi, self.k = C, math.radians(phi), k

    def P(self, a, b=0.0):
        c, s = math.cos(self.phi), math.sin(self.phi)
        a, b = a * self.k, b * self.k
        return (self.C[0] + a * c - b * s, self.C[1] - a * s - b * c)

    def at(self, p, r, d):
        """the point r from frame point p in direction d (degrees from along the wall)"""
        x, y = self.P(*p)
        a = math.radians(d) + self.phi
        return (x + r * math.cos(a), y - r * math.sin(a))

def line(p0, p1, c, w=3, op=1.0, dash=None):
    if op <= 0: return ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" stroke="{c}" stroke-width="{w}" '
            f'stroke-linecap="round" opacity="{op}"{d}/>')

def vec(p0, p1, c, op=1.0, w=6, k=1.0):
    """an arrow from p0 to p1, drawn k of the way so that it can grow"""
    if op <= 0 or k <= 0.05: return ""
    q = (p0[0] + (p1[0] - p0[0]) * k, p0[1] + (p1[1] - p0[1]) * k)
    return arrow(p0[0], p0[1], q[0], q[1], c, w=w, op=op)

def mid_label(p0, p1, inner, c, op=1.0, gap=30, size=40, side=1):
    """a label beside the middle of the arrow p0 -> p1 (side 1 is to the arrow's left)"""
    if op <= 0: return ""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    n = math.hypot(dx, dy) or 1
    m = ((p0[0] + p1[0]) / 2 + side * gap * dy / n, (p0[1] + p1[1]) / 2 - side * gap * dx / n)
    return label(m[0], m[1] + size * 0.35, inner, size, c, "middle", op)

def wall(F, a0, a1, op=1.0):
    if op <= 0: return ""
    s = [f'<g opacity="{op}">']
    q = 1 / F.k                         # the hatching is the same size at any scale
    a = a0 + 16 * q
    while a < a1 - 4 * q:
        s.append(line(F.P(a, -3 * q), F.P(a - 14 * q, -22 * q), HATCH, 3))
        a += 20 * q
    s.append(line(F.P(a0), F.P(a1), INK, 6))
    s.append('</g>')
    return "".join(s)

def arc(F, p, r, d0, d1, c=NAVY, op=1.0, w=3):
    """arc of radius r round frame point p, from direction d0 to d1 (degrees from along the wall)"""
    if op <= 0: return ""
    n = max(4, int(abs(d1 - d0) / 3))
    pts = " ".join("%.1f,%.1f" % F.at(p, r, d0 + (d1 - d0) * i / n) for i in range(n + 1))
    return f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="{w}" opacity="{op}"/>'

def arc_label(F, p, r, d, inner, size=36, c=NAVY, op=1.0):
    if op <= 0: return ""
    x, y = F.at(p, r, d)
    return label(x, y + size * 0.35, inner, size, c, "middle", op)

def right_angle(F, p, d0, size=22, c=INK, op=1.0):
    if op <= 0: return ""
    a, b, q = F.at(p, size, d0), F.at(p, size * math.sqrt(2), d0 + 45), F.at(p, size, d0 + 90)
    return (f'<polyline points="{a[0]:.1f},{a[1]:.1f} {b[0]:.1f},{b[1]:.1f} {q[0]:.1f},{q[1]:.1f}" fill="none" '
            f'stroke="{c}" stroke-width="3" opacity="{op}"/>')

def ball(p, op=1.0, r=RB):
    if op <= 0: return ""
    return f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r}" fill="{BALL}" stroke="#222" stroke-width="3" opacity="{op}"/>'

def flash(p, t, t_hit, op=1.0):
    if not (t_hit <= t < t_hit + 0.7) or op <= 0: return ""
    k = (t - t_hit) / 0.7
    out = []
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        r0, r1 = RB + 8 + 26 * k, RB + 30 + 26 * k
        out.append(line((p[0] + r0 * math.cos(a), p[1] + r0 * math.sin(a)), (p[0] + r1 * math.cos(a), p[1] + r1 * math.sin(a)),
                        GOLD, 5, op * (1 - k)))
    return "".join(out)

def place(t, items):
    """text that eases in: (start, x, y, inner, size, colour, weight)"""
    s = []
    for start, x, y, inner, size, c, wgt in items:
        o = ease(fade(t, start, 0.5))
        if o > 0:
            s.append(f'<g transform="translate(0,{14 * (1 - o):.1f})">' + text(x, y, inner, size, c, op=o, weight=wgt) + '</g>')
    return "".join(s)

def outline(t, start, x, y, w, h, c=GOLD, end=None):
    o = fade(t, start) * (1 - fade(t, end) if end else 1)
    if o <= 0: return ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" stroke="{c}" stroke-width="5" opacity="{o}"/>'

def glow(t, start, end, x, y, w, h):
    """a soft gold highlight behind something being talked about"""
    o = window(t, start, end, 0.4)
    if o <= 0: return ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{GOLD}" opacity="{0.3 * o:.3f}"/>'

def ij_icon(x, y, deg, op=1.0, glow_op=0.0):
    """the i and j directions, turned deg degrees"""
    if op <= 0: return ""
    a = math.radians(deg)
    pi = (x + 95 * math.cos(a), y - 95 * math.sin(a))
    pj = (x - 95 * math.sin(a), y - 95 * math.cos(a))
    s = [f'<g opacity="{op}">']
    if glow_op > 0:
        s.append(f'<circle cx="{x + 30}" cy="{y - 30}" r="95" fill="{GOLD}" opacity="{0.25 * glow_op:.3f}"/>')
    s.append(arrow(x, y, pi[0], pi[1], NAVY, w=4) + arrow(x, y, pj[0], pj[1], NAVY, w=4))
    s.append(label(pi[0] + 22 * math.cos(a), pi[1] - 22 * math.sin(a) + 12, i_, 34, NAVY, "middle"))
    s.append(label(pj[0] - 22 * math.sin(a), pj[1] - 22 * math.cos(a) + 12, j_, 34, NAVY, "middle"))
    s.append('</g>')
    return "".join(s)

def shadow(p0, p1, c, op=1.0, w=12, head=False):
    """the projection of a vector onto a line: a thick translucent bar"""
    if op <= 0 or math.hypot(p1[0] - p0[0], p1[1] - p0[1]) < 3: return ""
    if head and math.hypot(p1[0] - p0[0], p1[1] - p0[1]) > 30:
        return arrow(p0[0], p0[1], p1[0], p1[1], c, w=w, op=0.55 * op)
    return line(p0, p1, c, w, 0.55 * op)

# ------------------------------------------------------------------ the set-up
SET_C, PHI0 = (1385, 560), 20.0
L_IN, L_OUT = 360.0, 300.0

def setup_ball(t):
    """(frame point of the sphere's centre, opacity, time of impact) as it moves in, hits the wall and bounces off"""
    t0, t1 = S("s1", "towards"), S("s1", "It hits")
    v_in = L_IN / max(1.0, t1 - t0)
    t2 = t1 + 0.1
    t3 = t2 + L_OUT / (v_in * VL / UL)
    if t < t1:
        d = L_IN * (1 - clamp((t - t0) / (t1 - t0)))
        p = (-d * ca, RB + d * sa)
    elif t < t2:
        p = (0, RB)
    else:
        d = L_OUT * clamp((t - t2) / (t3 - t2))
        p = (d * cb, RB + d * sb)
    return p, fade(t, S("s1", "sphere")) * (1 - fade(t, S("s2", "is u"))), t1, (t0, t3)

def scene_setup(t):
    op = scene(t, "s1", "p1")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("A sphere bouncing off a wall"), divider()]
    s.append(place(t, [
        (S("s1"), 80, 200, "Looking down on a smooth sphere moving", 32, NAVY, "normal"),
        (S("s1", "towards"), 80, 245, "towards a smooth vertical wall", 32, NAVY, "normal"),
        (S("s2", "is u"), 80, 320, f"Velocity before the impact:  {U_}", 34, NAVY, "normal"),
        (S("s2", "its velocity"), 80, 370, f"Velocity after the impact:  {V_}", 34, NAVY, "normal"),
        (S("s3", "alpha with"), 80, 440, f"{U_} makes an angle {AL} with the wall", 32, NAVY, "normal"),
        (S("s3", "beta with"), 80, 485, f"{V_} makes an angle {BE} with the wall", 32, NAVY, "normal"),
        (S("s3", "coefficient"), 80, 530, f"Coefficient of restitution:  {e_}", 32, NAVY, "normal"),
        (S("s4", "Notice"), 80, 620, f"The wall is not in the {i_} or {j_} direction,", 32, NAVY, "normal"),
        (S("s4", "So splitting"), 80, 665, f"so {i_} and {j_} components don't help.", 32, NAVY, "normal"),
        (S("s5", "w points"), 80, 755, f"{W_}  points along the wall", 34, NAVY, "normal"),
        (S("s5", "I is"), 80, 805, f"{I_}  is perpendicular to the wall, pointing away", 34, NAVY, "normal"),
        (S("s5", "So w and I"), 80, 870, f"{W_} and {I_} are perpendicular", 36, NAVY, "bold"),
    ]))
    k = ease(clamp((t - S("s6", "Let's turn")) / 2.2))
    phi = PHI0 * (1 - k)
    F = Frame(SET_C, phi)
    O = F.P(0, 0)
    s.append(wall(F, -330, 330, fade(t, S("s1") - 0.3)))
    # the i and j directions, which don't line up with the wall
    s.append(ij_icon(1000, 240, phi - PHI0, fade(t, S("s1") - 0.3) * (1 - fade(t, S("s6", "We're just") + 0.5)),
                     window(t, S("s4", "Notice"), S("s4", "So splitting") + 1.5)))
    for start, d in (("i direction", -PHI0), ("j direction", 90 - PHI0)):
        o = window(t, S("s4", start), S("s5"), 0.4)
        s.append(line(F.at((0, 0), -260, d), F.at((0, 0), 260, d), BGREY, 3, o, "10,8"))
    # the sphere moves in, hits the wall and bounces off, leaving its path behind
    p, bo, t_hit, (t0, t3) = setup_ball(t)
    po = fade(t, t0) * (1 - fade(t, S("s2", "its velocity") + 0.4))
    if po > 0:
        start = F.P(-L_IN * ca, RB + L_IN * sa)
        if t < t_hit:
            s.append(line(start, F.P(*p), GREY, 3, po, "8,8"))
        else:
            s.append(line(start, F.P(0, RB), GREY, 3, po, "8,8") + line(F.P(0, RB), F.P(*p), GREY, 3, po, "8,8"))
    s.append(ball(F.P(*p), bo))
    s.append(flash(F.P(0, RB), t, t_hit))
    # velocities and angles
    ku, kv = grow(t, S("s2", "is u")), grow(t, S("s2", "its velocity"))
    A, B = F.P(*UA), F.P(*VB)
    s.append(vec(A, O, UC, k=ku) + mid_label(A, O, U_, UC, fade(t, S("s2", "is u") + 0.3)))
    s.append(vec(O, B, VC, k=kv) + mid_label(O, B, V_, VC, fade(t, S("s2", "its velocity") + 0.3)))
    ao, bo2 = fade(t, S("s3", "alpha with")), fade(t, S("s3", "beta with"))
    s.append(arc(F, (0, 0), 70, 180 - ALPHA, 180, NAVY, ao) + arc_label(F, (0, 0), 98, 180 - ALPHA / 2, AL, 38, NAVY, ao))
    s.append(arc(F, (0, 0), 92, 0, BETA, NAVY, bo2) + arc_label(F, (0, 0), 122, BETA / 2, BE, 38, NAVY, bo2))
    # the wall's own directions
    wo, io = fade(t, S("s5", "w points")), fade(t, S("s5", "I is"))
    s.append(vec(O, F.P(150, 0), WC, w=7, k=grow(t, S("s5", "w points"))) + label(*F.P(182, 14), W_, 40, WC, "middle", wo))
    s.append(vec(O, F.P(0, 150), IC, w=7, k=grow(t, S("s5", "I is"))) + label(*F.at((0, 150), 30, 90), I_, 40, IC, "middle", io))
    s.append(right_angle(F, (0, 0), 0, 24, INK, fade(t, S("s5", "So w and I"))))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ what happens in the collision
def scene_physics(t):
    op = scene(t, "p1", "d1")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("What happens in the collision"), divider()]
    s.append(glow(t, S("p4", "There's no"), S("p5"), 270, 293, 230, 120))
    s.append(glow(t, S("p5", "The speed away"), S("p6"), 570, 293, 210, 120))
    s.append(place(t, [
        (S("p1", "split"), 80, 200, "Split each velocity into two components:", 34, NAVY, "bold"),
        (S("p1", "one along"), 285, 265, "along the wall", 30, WC, "bold"),
        (S("p1", "perpendicular"), 585, 265, "perpendicular", 30, IC, "bold"),
        (S("p2"), 80, 335, "Before", 32, NAVY, "bold"),
        (S("p2", "u cos"), 290, 335, f"{u_} cos {AL}", 38, NAVY, "normal"),
        (S("p2", "u sine"), 590, 335, f"{u_} sin {AL}", 38, NAVY, "normal"),
        (S("p2", "u sine"), 730, 335, "towards", 26, BGREY, "normal"),
        (S("p3"), 80, 400, "After", 32, NAVY, "bold"),
        (S("p3", "v cos"), 290, 400, f"{v_} cos {BE}", 38, NAVY, "normal"),
        (S("p3", "v sine"), 590, 400, f"{v_} sin {BE}", 38, NAVY, "normal"),
        (S("p3", "v sine"), 730, 400, "away", 26, BGREY, "normal"),
        (S("p4"), 80, 485, "Smooth wall: the impulse is perpendicular to the wall,", 30, NAVY, "normal"),
        (S("p4", "There's no"), 80, 527, "so the velocity along the wall doesn't change.", 30, NAVY, "normal"),
        (S("p4", "u cos alpha equals"), 120, 607, f"{u_} cos {AL} = {v_} cos {BE}", 46, NAVY, "normal"),
        (S("p4", "u cos alpha equals"), 790, 605, "(1)", 34, NAVY, "bold"),
        (S("p5", "Newton's"), 80, 700, "Newton's law of restitution:", 30, NAVY, "normal"),
        (S("p5", "The speed away"), 80, 742, f"speed away from the wall = {e_} × speed towards it", 30, NAVY, "normal"),
        (S("p5", "So v sine"), 120, 822, f"{v_} sin {BE} = {e_}{u_} sin {AL}", 46, NAVY, "normal"),
        (S("p5", "So v sine"), 790, 820, "(2)", 34, NAVY, "bold"),
    ]))
    s.append(outline(t, S("p6"), 96, 556, 770, 74) + outline(t, S("p6"), 96, 771, 770, 74))
    F = Frame(SET_C, 0)
    O, A, B = F.P(0, 0), F.P(*UA), F.P(*VB)
    s.append(wall(F, -420, 420))
    s.append(vec(A, O, UC) + mid_label(A, O, U_, UC) + vec(O, B, VC) + mid_label(O, B, V_, VC))
    s.append(arc(F, (0, 0), 70, 180 - ALPHA, 180) + arc_label(F, (0, 0), 98, 180 - ALPHA / 2, AL, 38))
    s.append(arc(F, (0, 0), 92, 0, BETA) + arc_label(F, (0, 0), 122, BETA / 2, BE, 38))
    # the components of u, then of v
    o1, o2 = fade(t, S("p2", "u cos")), fade(t, S("p2", "u sine"))
    s.append(line(A, F.P(UA[0], -62), GREY, 2, o1, "6,6") + line(O, F.P(0, -62), GREY, 2, o1, "6,6"))
    s.append(darrow(F.P(UA[0], -62), F.P(-4, -62), UC, 5, o1) + label(*F.P(UA[0] / 2, -108), f"{u_} cos {AL}", 34, NAVY, "middle", o1))
    s.append(darrow(F.P(UA[0] - 34, UA[1]), F.P(UA[0] - 34, 4), UC, 5, o2)
             + label(*F.P(UA[0] - 52, UA[1] / 2 - 12), f"{u_} sin {AL}", 34, NAVY, "end", o2))
    o3, o4 = fade(t, S("p3", "v cos")), fade(t, S("p3", "v sine"))
    s.append(line(B, F.P(VB[0], -62), GREY, 2, o3, "6,6"))
    s.append(darrow(F.P(4, -62), F.P(VB[0], -62), VC, 5, o3) + label(*F.P(VB[0] / 2, -108), f"{v_} cos {BE}", 34, NAVY, "middle", o3))
    s.append(darrow(F.P(VB[0] + 34, 4), F.P(VB[0] + 34, VB[1]), VC, 5, o4)
             + label(*F.P(VB[0] + 52, VB[1] / 2 - 12), f"{v_} sin {BE}", 34, NAVY, "start", o4))
    # the impulse from a smooth wall is perpendicular to it, so only the perpendicular parts change
    io = window(t, S("p4", "impulse"), S("p6"))
    s.append(vec(F.P(0, 4), F.P(0, 130), IC, io, 7) + label(*F.P(0, 150), "impulse", 30, IC, "middle", io))
    s.append(glow(t, S("p4", "doesn't change"), S("p5"), F.P(UA[0], -62)[0] - 10, F.P(0, -80)[1], VB[0] - UA[0] + 20, 82))
    s.append(glow(t, S("p5", "The speed away"), S("p6"), F.P(UA[0] - 175, 0)[0], F.P(0, UA[1] / 2 + 30)[1], 160, 64))
    s.append(glow(t, S("p5", "The speed away"), S("p6"), F.P(VB[0] + 42, 0)[0], F.P(0, VB[1] / 2 + 30)[1], 160, 64))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ the scalar product
REC_O = (1290, 640)

def recap_theta(t):
    k1 = ease(clamp((t - S("d3", "Watch")) / max(0.8, S("d3", "At 90") - S("d3", "Watch"))))
    k2 = ease(clamp((t - S("d3", "Past 90")) / 2.4))
    return 50 + 40 * k1 + 50 * k2

def scene_recap(t):
    op = scene(t, "d1", "w1")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Reminder: the scalar product"), divider()]
    s.append(gold_box(t, S("d1", "is the magnitude"), 76, 160, 830, 120, [f"{A_}{D}{B_} = {mag(A_)} {mag(B_)} cos {TH}"], 52))
    s.append(place(t, [
        (S("d1", "That angle"), 80, 345, f"{TH} is the angle between {A_} and {B_},", 32, NAVY, "normal"),
        (S("d1", "tail to tail"), 80, 390, "with the vectors tail to tail.", 32, NAVY, "normal"),
        (S("d2", "unit vector"), 80, 480, f"{WH} is a unit vector, so  {mag(WH)} = 1", 32, NAVY, "normal"),
        (S("d2", "That's the component"), 80, 650, f"the component of {A_} in the direction of {WH}", 30, NAVY, "normal"),
        (S("d3", "At 90"), 80, 750, f"{TH} = 90°:   {A_}{D}{WH} = 0", 34, NAVY, "normal"),
        (S("d3", "the cosine is negative"), 80, 810, f"{TH} &gt; 90°:   cos {TH} &lt; 0,  so  {A_}{D}{WH} &lt; 0", 34, NAVY, "normal"),
        (S("d3", "pointing backwards"), 80, 865, f"{A_} points backwards, against {WH}", 30, RED, "normal"),
    ]))
    s.append(gold_box(t, S("d2", "So a dot"), 76, 510, 830, 100, [f"{A_}{D}{WH} = {mag(A_)} cos {TH}"], 48))
    F = Frame(REC_O, 0)
    O = F.P(0, 0)
    th = recap_theta(t)
    s.append(line(F.P(-330, 0), F.P(480, 0), GREY, 3, fade(t, S("d2", "unit vector")), "10,8"))
    # b turns into the unit vector w hat
    m = ease(fade(t, S("d2", "unit vector"), 0.8))
    blen = 230 - 70 * m
    s.append(vec(O, F.P(blen, 0), BGREY, 1 - m) + label(*F.P(blen - 4, 24), B_, 42, BGREY, "middle", 1 - m))
    s.append(vec(O, F.P(blen, 0), WC, m, 7) + label(*F.P(blen - 4, 24), WH, 42, WC, "middle", m))
    tip = F.at((0, 0), 300, th)
    s.append(vec(O, tip, NAVY, w=7) + label(*F.at((0, 0), 340, th), A_, 42, NAVY, "middle"))
    s.append(arc(F, (0, 0), 70, 0, th, NAVY, fade(t, S("d1", "That angle"))))
    s.append(arc_label(F, (0, 0), 100, th / 2, TH, 38, NAVY, fade(t, S("d1", "That angle"))))
    # the shadow of a on the line of w hat
    so = fade(t, S("d2", "That's the component"))
    c = math.cos(math.radians(th))
    foot = F.P(300 * c, 0)
    sc = GOLD if c > 0.03 else RED if c < -0.03 else GREY
    s.append(line(tip, foot, GREY, 3, so, "8,7"))
    s.append(shadow(O, foot, sc, so, 14))
    if c > 0.03:
        lab = f"{mag(A_)} cos {TH}"
    elif c < -0.03:
        lab = col("negative", RED, True)
    else:
        lab = f"{A_}{D}{WH} = 0"
    s.append(label(F.P(150 * c, 0)[0], O[1] + 58, lab, 34, NAVY, "middle", so))
    # live readout as the angle opens up
    ro = fade(t, S("d3", "Watch"))
    if ro > 0:
        cs = f"{c:.2f}".replace("-", "−")
        if cs in ("−0.00", "0.00"): cs = "0"
        s.append(f'<g opacity="{ro}"><rect x="1500" y="170" width="300" height="130" rx="14" fill="#f3f6fb"/>'
                 + text(1530, 222, f"{TH} = {th:.0f}°", 36, NAVY)
                 + text(1530, 275, f"cos {TH} = {col(cs, RED if c < -0.03 else NAVY, True)}", 36, NAVY) + '</g>')
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ along the wall
ALG_C = (1360, 540)

def slid(t, start):
    """u slides along its own line until its tail is at the point of impact: (tail, head) in frame points"""
    k = ease(clamp((t - start) / 1.6))
    tail = (UA[0] * (1 - k), UA[1] * (1 - k))
    return tail, (tail[0] + UL * ca, tail[1] - UL * sa), k

def scene_along(t):
    op = scene(t, "w1", "n1")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header(f"Along the wall:  {U_}{D}{WH}  and  {V_}{D}{WH}"), divider()]
    s.append(place(t, [
        (S("w1", "u dot w hat"), 80, 190, f"{WH} = unit vector along the wall", 30, NAVY, "normal"),
        (S("w3", "So u dot"), 80, 270, f"{U_}{D}{WH} = {mag(U_)} {mag(WH)} cos {AL}", 40, NAVY, "normal"),
        (S("w3", "its magnitude is 1"), 168, 340, f"= {mag(U_)} × 1 × cos {AL}", 40, NAVY, "normal"),
        (S("w3", "That leaves"), 168, 410, f"= {u_} cos {AL}", 40, NAVY, "normal"),
        (S("w3", "That leaves"), 440, 408, f"({u_} is the speed)", 28, BGREY, "normal"),
        (S("w4", "So v dot"), 80, 500, f"{V_}{D}{WH} = {mag(V_)} {mag(WH)} cos {BE} = {v_} cos {BE}", 40, NAVY, "normal"),
        (S("w5", "We know"), 80, 590, f"{u_} cos {AL} = {v_} cos {BE}", 40, NAVY, "normal"),
        (S("w5", "We know"), 470, 588, "from (1)", 28, BGREY, "normal"),
        (S("w5", "So u dot w hat equals"), 80, 660, f"so  {U_}{D}{WH} = {V_}{D}{WH}", 40, NAVY, "normal"),
        (S("w6", "w is w hat"), 80, 740, f"{W_} = {mag(W_)} {WH}:   multiply both sides by {mag(W_)}", 30, NAVY, "normal"),
    ]))
    s.append(gold_box(t, S("w6", "first result"), 76, 780, 520, 120, [f"{U_}{D}{W_} = {V_}{D}{W_}"], 58))
    F = Frame(ALG_C, 0, 1.35)
    O, A, B = F.P(0, 0), F.P(*UA), F.P(*VB)
    s.append(wall(F, -315, 315))
    # w hat, which later stretches into w
    kw = ease(clamp((t - S("w6", "w is w hat")) / 1.2))
    tip = (O[0] + 170 + 110 * kw, O[1])
    uo, vo = fade(t, S("w3", "It's the shadow")), fade(t, S("w4", "which is v cos"))
    s.append(shadow(O, F.P(UT[0], 0), UC, uo, 18) + shadow(O, F.P(VB[0], 0), VC, vo, 10))
    s.append(vec(O, tip, WC, w=7) + label(tip[0] - 8, tip[1] - 18, WH if kw < 0.5 else W_, 38, WC, "end"))
    s.append(vec(O, B, VC) + mid_label(O, B, V_, VC))
    # slide u until it is tail to tail with w hat
    t_sl = S("w2", "slide")
    s.append(line(A, F.P(*UT), GREY, 2, window(t, t_sl - 0.3, S("w3"), 0.4), "8,8"))
    tail, head, k = slid(t, t_sl)
    if k > 0:
        s.append(vec(A, O, UC, 0.25))
    s.append(vec(F.P(*tail), F.P(*head), UC) + mid_label(F.P(*tail), F.P(*head), U_, UC, side=-1 if k > 0.5 else 1))
    ao = fade(t, S("w2", "Now we can see"))
    s.append(arc(F, (0, 0), 70, -ALPHA, 0, NAVY, ao) + arc_label(F, (0, 0), 98, -ALPHA / 2, AL, 38, NAVY, ao))
    bo = fade(t, S("w4", "angle beta"))
    s.append(arc(F, (0, 0), 84, 0, BETA, NAVY, bo) + arc_label(F, (0, 0), 110, BETA / 2, BE, 36, NAVY, bo))
    # the two shadows on the wall finish at the same point
    s.append(line(F.P(*UT), F.P(UT[0], 0), GREY, 3, uo, "8,7"))
    s.append(label(F.P(UT[0], 0)[0] + 22, O[1] + 54, f"{u_} cos {AL}", 34, NAVY, "start", uo))
    s.append(line(B, F.P(VB[0], 0), GREY, 3, vo, "8,7"))
    s.append(label(F.P(VB[0], 0)[0] + 22, O[1] - 16, f"{v_} cos {BE}", 34, NAVY, "start", vo))
    go = window(t, S("w5", "exactly the same"), S("w6"), 0.4)
    s.append(line(F.P(UT[0], UT[1] - 20), F.P(VB[0], VB[1] + 20), GOLD, 8, go))
    s.append(pop(t, S("w5", "exactly the same"), F.P(UT[0], 0)[0], F.P(0, UT[1] - 70)[1], "same length", 2.6, 40))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ perpendicular to the wall: u
PU_C = (1250, 420)
UCIRC, UR = (1385, 600), 210

def unit_circle(t):
    """the point at angle alpha, turned through another 90 degrees: its x coordinate becomes -sin alpha"""
    o = window(t, S("n4") - 0.2, S("n5"), 0.5)
    if o <= 0: return ""
    cx, cy = UCIRC
    s = [f'<g opacity="{o}">', line((cx - 260, cy), (cx + 280, cy), BGREY, 3), line((cx, cy + 250), (cx, cy - 270), BGREY, 3),
         label(cx + 296, cy + 11, it("x"), 34, BGREY, "start"), label(cx, cy - 284, it("y"), 34, BGREY, "middle"),
         f'<circle cx="{cx}" cy="{cy}" r="{UR}" fill="none" stroke="{NAVY}" stroke-width="3"/>']
    rot = 90 * ease(clamp((t - S("n4", "Now turn")) / 1.8))
    to = fade(t, S("n4", "the point at"))
    def R(x, y):                         # turn a point of the original triangle through rot degrees
        r = math.radians(rot)
        return (cx + x * math.cos(r) - y * math.sin(r), cy - (x * math.sin(r) + y * math.cos(r)))
    P, Fo = R(UR * ca, UR * sa), R(UR * ca, 0)
    s.append(f'<polygon points="{cx},{cy} {Fo[0]:.1f},{Fo[1]:.1f} {P[0]:.1f},{P[1]:.1f}" fill="#fff2cc" stroke="{WC}" '
             f'stroke-width="3" opacity="{to}"/>')
    s.append(line((cx, cy), P, NAVY, 5, to) + f'<circle cx="{P[0]:.1f}" cy="{P[1]:.1f}" r="9" fill="{NAVY}" opacity="{to}"/>')
    lo = to * (1 - fade(t, S("n4", "Now turn"), 0.4))
    s.append(label(cx + UR * ca / 2, cy + 42, f"cos {AL}", 32, NAVY, "middle", lo))
    s.append(label(cx + UR * ca + 14, cy - UR * sa / 2 + 11, f"sin {AL}", 32, NAVY, "start", lo))
    s.append(label(P[0] + 10, P[1] - 24, f"(cos {AL}, sin {AL})", 32, NAVY, "middle", fade(t, S("n4", "has coordinates")) * lo))
    s.append(label((P[0] + Fo[0]) / 2, P[1] - 18, f"sin {AL}", 32, NAVY, "middle", fade(t, S("n4", "The triangle turns"))))
    # the angle from the x axis
    ang = ALPHA + rot
    s.append(arc(Frame((cx, cy)), (0, 0), 55, 0, ang, NAVY, to))
    s.append(arc_label(Frame((cx, cy)), (0, 0), 84, ALPHA / 2, AL, 32, NAVY, to * (1 - fade(t, S("n4", "Now turn"), 0.4))))
    s.append(label(cx + 22, cy - 66, f"90° + {AL}", 32, NAVY, "start", fade(t, S("n4", "Now turn") + 1.8, 0.4)))
    # its x coordinate is negative sine alpha
    xo = fade(t, S("n4", "x coordinate"))
    s.append(line(P, (P[0], cy), GREY, 3, xo, "8,7") + line((cx, cy), (P[0], cy), WC, 10, xo))
    s.append(label((cx + P[0]) / 2, cy + 46, col(f"−sin {AL}", WC, True), 36, NAVY, "middle", xo))
    s.append('</g>')
    return "".join(s)

def scene_perp_u(t):
    op = scene(t, "n1", "n6")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header(f"Perpendicular to the wall:  {U_}{D}{IH}"), divider()]
    s.append(place(t, [
        (S("n1", "where I hat"), 80, 190, f"{IH} = unit vector perpendicular to the wall, away from it", 28, NAVY, "normal"),
        (S("n2", "That's 90"), 80, 270, f"Angle between {U_} and {IH}:  90° + {AL}", 34, NAVY, "normal"),
        (S("n3", "So u dot"), 80, 360, f"{U_}{D}{IH} = {mag(U_)} {mag(IH)} cos(90° + {AL})", 40, NAVY, "normal"),
        (S("n3", "times 1"), 168, 430, f"= {u_} cos(90° + {AL})", 40, NAVY, "normal"),
        (S("n4", "So cos of 90"), 80, 530, f"cos(90° + {AL}) = −sin {AL}", 38, WC, "bold"),
        (S("n5", "The shadow of u"), 80, 780, f"The shadow points against {IH}, so it is negative:", 30, NAVY, "normal"),
        (S("n5", "The sphere is"), 80, 822, "the sphere is moving towards the wall.", 30, NAVY, "normal"),
    ]))
    s.append(gold_box(t, S("n5", "That means"), 76, 600, 600, 120, [f"{U_}{D}{IH} = −{u_} sin {AL}"], 52))
    F = Frame(PU_C, 0)
    O, A = F.P(0, 0), F.P(*UA)
    s.append(f'<g opacity="{1 - 0.95 * window(t, S("n4") - 0.2, S("n5"), 0.5):.3f}">')
    s.append(wall(F, -300, 300))
    s.append(line(F.P(0, 210), F.P(0, -235), GREY, 2, fade(t, S("n1", "where I hat")), "8,8"))
    s.append(vec(O, F.P(0, 130), IC, w=7, k=grow(t, S("n1", "where I hat")))
             + label(*F.P(-18, 112), IH, 40, IC, "end", fade(t, S("n1", "where I hat"))))
    t_sl = S("n2", "Put u")
    tail, head, k = slid(t, t_sl)
    if k > 0:
        s.append(vec(A, O, UC, 0.25))
    s.append(vec(F.P(*tail), F.P(*head), UC) + mid_label(F.P(*tail), F.P(*head), U_, UC, side=-1 if k > 0.5 else 1))
    # a right angle, plus alpha
    ro, ao, bo = fade(t, S("n2", "a right angle")), fade(t, S("n2", "plus alpha")), fade(t, S("n2", "That's 90"))
    s.append(right_angle(F, (0, 0), 0, 26, NAVY, ro * (1 - bo)))
    s.append(arc(F, (0, 0), 50, -ALPHA, 0, NAVY, ao * (1 - bo)) + arc_label(F, (0, 0), 72, -ALPHA / 2, AL, 32, NAVY, ao * (1 - bo)))
    s.append(arc(F, (0, 0), 70, -ALPHA, 90, NAVY, bo) + arc_label(F, (0, 0), 132, (90 - ALPHA) / 2, f"90° + {AL}", 34, NAVY, bo))
    # the shadow of u on the line of I hat points down, against I hat
    so = fade(t, S("n5", "The shadow of u"))
    s.append(line(F.P(*UT), F.P(0, UT[1]), GREY, 3, so, "8,7"))
    s.append(shadow(F.P(-12, 0), F.P(-12, UT[1]), UC, so, 12, head=True))
    s.append(label(*F.P(-30, UT[1] / 2 - 10), f"−{u_} sin {AL}", 34, NAVY, "end", so))
    s.append('</g>')
    s.append(unit_circle(t))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ perpendicular to the wall: v
PV_C = (1300, 640)
VL2 = 400.0
VB2 = (VL2 * cb, VL2 * sb)

def scene_perp_v(t):
    op = scene(t, "n6", "r1")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header(f"Perpendicular to the wall:  {V_}{D}{IH}"), divider()]
    s.append(place(t, [
        (S("n6", "So the angle"), 80, 200, f"Angle between {V_} and {IH}:  90° − {BE}", 34, NAVY, "normal"),
        (S("n7", "So v dot"), 80, 290, f"{V_}{D}{IH} = {mag(V_)} {mag(IH)} cos(90° − {BE})", 40, NAVY, "normal"),
        (S("n7", "cos of 90"), 168, 360, f"= {v_} cos(90° − {BE})", 40, NAVY, "normal"),
        (S("n8", "Its angles"), 80, 450, f"Right-angled triangle: angles {BE} and 90° − {BE}", 30, NAVY, "normal"),
        (S("n8", "The side opposite"), 80, 495, f"the side opposite {BE} is next to 90° − {BE}", 30, NAVY, "normal"),
        (S("n8", "So cos of 90"), 80, 565, f"cos(90° − {BE}) = sin {BE}", 38, WC, "bold"),
        (S("n9", "the shadow points"), 80, 790, f"The shadow points the same way as {IH}, so it is", 30, NAVY, "normal"),
        (S("n9", "The sphere is"), 80, 832, "positive: the sphere is moving away from the wall.", 30, NAVY, "normal"),
    ]))
    s.append(gold_box(t, S("n9", "So v dot"), 76, 625, 560, 120, [f"{V_}{D}{IH} = {v_} sin {BE}"], 52))
    F = Frame(PV_C, 0)
    O, B, Fp = F.P(0, 0), F.P(*VB2), F.P(VB2[0], 0)
    s.append(wall(F, -320, 400))
    s.append(line(F.P(0, 300), F.P(0, -60), GREY, 2, 1, "8,8"))
    s.append(vec(O, F.P(0, 130), IC, w=7) + label(*F.P(-18, 112), IH, 40, IC, "end"))
    # the right-angled triangle under v
    to = fade(t, S("n8", "Look at"))
    s.append(f'<polygon points="{O[0]},{O[1]} {Fp[0]:.1f},{Fp[1]:.1f} {B[0]:.1f},{B[1]:.1f}" fill="#fff2cc" opacity="{0.9 * to:.3f}"/>')
    s.append(line(Fp, B, GREY, 3, to * (1 - fade(t, S("n8", "The side opposite"))), "8,7"))
    s.append(line(Fp, B, GOLD, 8, fade(t, S("n8", "The side opposite"))))
    s.append(label(Fp[0] + 18, (Fp[1] + B[1]) / 2 + 10, f"opposite {BE}", 30, NAVY, "start", fade(t, S("n8", "The side opposite"))))
    s.append(right_angle(F, (VB2[0], 0), 90, 22, INK, to))
    s.append(arc(F, VB2, 46, 180 + BETA, 270, NAVY, fade(t, S("n8", "Its angles"))))
    s.append(label(Fp[0] - 16, B[1] + 80, f"90° − {BE}", 28, NAVY, "end", fade(t, S("n8", "Its angles"))))
    s.append(vec(O, B, VC) + mid_label(O, B, V_, VC, gap=34))
    s.append(arc(F, (0, 0), 70, 0, BETA) + arc_label(F, (0, 0), 96, BETA / 2, BE, 34))
    ao = fade(t, S("n6", "So the angle"))
    s.append(arc(F, (0, 0), 112, BETA, 90, NAVY, ao) + arc_label(F, (0, 0), 150, (BETA + 90) / 2, f"90° − {BE}", 34, NAVY, ao))
    # the shadow of v on the line of I hat points up, with I hat
    so = fade(t, S("n9", "the shadow points"))
    s.append(line(B, F.P(0, VB2[1]), GREY, 3, so, "8,7"))
    s.append(shadow(F.P(-16, 0), F.P(-16, VB2[1]), VC, so, 12, head=True))
    s.append(label(*F.P(-34, VB2[1] / 2 - 30), f"{v_} sin {BE}", 34, NAVY, "end", so))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ Newton's law of restitution
RS_C = (1390, 600)
SU, SV = UL * sa, VL * sb               # lengths of the two shadows on the line of I hat

def scene_restitution(t):
    op = scene(t, "r1", "sum1")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Bringing in Newton's law of restitution"), divider()]
    s.append(place(t, [
        (S("r1", "v sine beta equals"), 80, 210, f"{v_} sin {BE} = {e_}{u_} sin {AL}", 42, NAVY, "normal"),
        (S("r1", "v sine beta equals"), 600, 208, "from (2)", 28, BGREY, "normal"),
        (S("r2", "v sine beta is"), 80, 300, f"{v_} sin {BE} = {V_}{D}{IH}", 36, NAVY, "normal"),
        (S("r2", "and u sine alpha is"), 470, 300, f"{u_} sin {AL} = −{U_}{D}{IH}", 36, NAVY, "normal"),
        (S("r3", "Substituting"), 80, 400, f"{V_}{D}{IH} = {e_}(−{U_}{D}{IH})", 42, NAVY, "normal"),
        (S("r3", "That's negative"), 80, 480, f"{V_}{D}{IH} = −{e_} {U_}{D}{IH}", 42, NAVY, "normal"),
        (S("r5", "I is I hat"), 80, 580, f"{I_} = {mag(I_)} {IH}:   multiply both sides by {mag(I_)}", 30, NAVY, "normal"),
    ]))
    s.append(gold_box(t, S("r5", "second result"), 76, 630, 600, 120, [f"−{e_} {U_}{D}{I_} = {V_}{D}{I_}"], 58))
    F = Frame(RS_C, 0)
    s.append(wall(F, -300, 320))
    s.append(vec(F.P(-240, 0), F.P(-240, 120), IC, w=7) + label(*F.P(-258, 100), IH, 40, IC, "end"))
    xu, xv = F.P(-110, 0)[0], F.P(180, 0)[0]
    y0 = RS_C[1]
    s.append(vec((xu, y0), (xu, y0 + SU), UC, w=8) + label(xu, y0 + SU + 46, f"{U_}{D}{IH} = −{u_} sin {AL}", 32, NAVY, "middle"))
    s.append(vec((xv, y0), (xv, y0 - SV), VC, w=8) + label(xv, y0 - SV - 22, f"{V_}{D}{IH} = {v_} sin {BE}", 32, NAVY, "middle"))
    # reverse the shadow of u, multiply it by e, and it becomes the shadow of v
    t1, t2, t3 = S("r4", "Reverse"), S("r4", "multiply it by e"), S("r4", "and you get")
    co = window(t, t1 - 0.2, S("r5") + 0.4, 0.3)
    if co > 0:
        f1, f2, f3 = ease(clamp((t - t1) / 1.2)), ease(clamp((t - t2) / 1.0)), ease(clamp((t - t3) / 0.9))
        L = -SU + 2 * SU * f1                              # down, then up through zero
        L = L - (SU - SV) * f2                             # then e times as long
        x = xu + 145 + (xv - xu - 145) * f3
        c = UC if f2 < 0.5 else EC
        if abs(L) > 22:
            s.append(arrow(x, y0, x, y0 - L, c, w=8, op=co))
        s.append(label(x + 22, y0 - L / 2 + 10, "× (−1)", 30, NAVY, "start", co * window(t, t1 + 0.4, t2, 0.3)))
        s.append(label(x + 22, y0 - L / 2 + 10, f"× {e_}", 34, NAVY, "start", co * window(t, t2 + 0.3, t3, 0.3)))
    s.append(pop(t, t3 + 0.9, xv, y0 - SV - 80, "exactly", 2.4, 40))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ the two results
SUM_C = (1385, 600)

def scene_summary(t):
    op = scene(t, "sum1", "ex0")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("The two results"), divider()]
    s.append(gold_box(t, S("sum1", "u dot w equals"), 76, 160, 830, 250,
                      [f"{U_}{D}{W_} = {V_}{D}{W_}", f"−{e_} {U_}{D}{I_} = {V_}{D}{I_}"], 58))
    s.append(outline(t, S("sum1", "u dot w equals"), 70, 154, 842, 262, WC))
    s.append(place(t, [
        (S("sum2", "The first"), 80, 480, f"{col('Along the wall:', WC, True)} the velocity component is unchanged", 30, NAVY, "normal"),
        (S("sum2", "The second"), 80, 530, f"{col('Perpendicular:', IC, True)} it reverses and is multiplied by {e_}", 30, NAVY, "normal"),
        (S("sum3", "Because"), 80, 630, "They work for a wall in any direction:", 32, NAVY, "bold"),
        (S("sum3", "w can be"), 80, 685, f"{W_} is any vector along the wall", 30, NAVY, "normal"),
        (S("sum3", "and I can be"), 80, 735, f"{I_} is any vector perpendicular to it, either way", 30, NAVY, "normal"),
    ]))
    no = fade(t, S("sum3", "You never"))
    if no > 0:
        s.append(f'<rect x="76" y="790" width="560" height="100" rx="16" fill="#2b0f52" opacity="{no}"/>'
                 f'<text x="356" y="858" font-family="Montserrat" font-weight="800" font-size="46" fill="#ffc94d" '
                 f'text-anchor="middle" opacity="{no}">No angles needed</text>')
    k = ease(clamp((t - S("sum3", "Because")) / 2.2))
    F = Frame(SUM_C, 40 * k)
    O, A, B = F.P(0, 0), F.P(*UA), F.P(*VB)
    s.append(wall(F, -330, 330))
    s.append(vec(A, O, UC) + mid_label(A, O, U_, UC) + vec(O, B, VC) + mid_label(O, B, V_, VC))
    ango = 1 - fade(t, S("sum3", "You never"))
    s.append(arc(F, (0, 0), 70, 180 - ALPHA, 180, NAVY, ango) + arc_label(F, (0, 0), 98, 180 - ALPHA / 2, AL, 38, NAVY, ango))
    s.append(arc(F, (0, 0), 92, 0, BETA, NAVY, ango) + arc_label(F, (0, 0), 122, BETA / 2, BE, 38, NAVY, ango))
    wl = 150 + 80 * ease(clamp((t - S("sum3", "w can be")) / 1.0))
    s.append(vec(O, F.P(wl, 0), WC, w=7) + label(*F.P(wl + 4, 34), W_, 40, WC, "middle"))
    s.append(vec(O, F.P(0, 150), IC, w=7) + label(*F.at((0, 150), 30, 90), I_, 40, IC, "middle"))
    s.append(right_angle(F, (0, 0), 0, 24, INK))
    mo = fade(t, S("sum3", "pointing either way"))
    s.append(darrow(O, F.P(0, -150), IC, 6, mo) + label(*F.at((0, -150), 34, -90), f"−{I_}", 40, IC, "middle", mo))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ example
EX_C = (1400, 440)
EX_PHI = math.degrees(math.atan2(4, 3))     # the wall is parallel to 3i + 4j
PXV = 22                                     # pixels per m/s for the velocity arrows
PXW = 30                                     # pixels per unit for w and I

def ex_ball(t, F):
    """the sphere moves in with u, waits at the wall until v is found, then leaves with v"""
    t0, t1 = S("ex1", "with velocity"), S("ex1", "It hits")
    t2 = S("ex5", "So the sphere leaves")
    pc = F.P(0, RB)
    un, vn = (11 / math.hypot(11, 2), 2 / math.hypot(11, 2)), (-1 / math.hypot(1, 7), -7 / math.hypot(1, 7))
    if t < t1:
        d = 300 * (1 - clamp((t - t0) / max(1.0, t1 - t0)))
        return (pc[0] - d * un[0], pc[1] - d * un[1]), t1
    if t < t2:
        return pc, t1
    d = 300 * math.hypot(1, 7) / math.hypot(11, 2) * clamp((t - t2) / 2.2)
    return (pc[0] + d * vn[0], pc[1] + d * vn[1]), t1

def scene_example(t):
    op = scene(t, "ex1", "cta")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Example: the velocity after the impact")]
    a_, b_ = it("a"), it("b")
    s.append(qblock(t, [(S("ex1"), "A smooth sphere moves on a smooth horizontal surface"),
                        (S("ex1", "with velocity"), f"with velocity (11{i_} − 2{j_}) {MS}. It hits a smooth vertical"),
                        (S("ex1", "parallel"), f"wall which is parallel to 3{i_} + 4{j_}. The coefficient of"),
                        (S("ex1", "The coefficient"), "restitution between the sphere and the wall is ½.")],
                    ["Find the velocity of the sphere after the impact."], S("ex1", "Find")))
    s.append(place(t, [
        (S("ex2", "Let the velocity"), 80, 450, f"{V_} = {a_}{i_} + {b_}{j_}", 34, NAVY, "normal"),
        (S("ex2", "Along the wall"), 80, 505, f"{W_} = 3{i_} + 4{j_}", 32, NAVY, "normal"),
        (S("ex2", "which gives"), 330, 505, f"{I_} = 4{i_} − 3{j_}", 32, NAVY, "normal"),
        (S("ex2", "w dot I is"), 580, 505, f"{W_}{D}{I_} = 12 − 12 = 0", 32, NAVY, "normal"),
        (S("ex3"), 80, 580, "Along the wall", 30, WC, "bold"),
        (S("ex3"), 80, 630, f"{U_}{D}{W_} = {V_}{D}{W_}", 32, NAVY, "normal"),
        (S("ex3", "u dot w is"), 80, 685, f"{U_}{D}{W_} = 33 − 8 = 25", 32, NAVY, "normal"),
        (S("ex3", "And v dot w"), 80, 740, f"{V_}{D}{W_} = 3{a_} + 4{b_}", 32, NAVY, "normal"),
        (S("ex3", "So 3 a"), 80, 800, f"3{a_} + 4{b_} = 25", 36, NAVY, "bold"),
        (S("ex4"), 500, 580, "Perpendicular to the wall", 30, IC, "bold"),
        (S("ex4"), 500, 630, f"−{e_} {U_}{D}{I_} = {V_}{D}{I_}", 32, NAVY, "normal"),
        (S("ex4", "u dot I is"), 500, 685, f"{U_}{D}{I_} = 44 + 6 = 50", 32, NAVY, "normal"),
        (S("ex4", "Negative a half"), 500, 740, f"−½ × 50 = 4{a_} − 3{b_}", 32, NAVY, "normal"),
        (S("ex4", "So 4 a"), 500, 800, f"4{a_} − 3{b_} = −25", 36, NAVY, "bold"),
        (S("ex5", "Solving"), 80, 870, f"Solving:   {a_} = −1,   {b_} = 7", 34, NAVY, "normal"),
    ]))
    s.append(f'<line x1="470" y1="555" x2="470" y2="815" stroke="{NAVY}" stroke-opacity="0.15" stroke-width="3" opacity="{fade(t, S("ex4"))}"/>')
    s.append(answer_box(t, S("ex5", "So the sphere leaves"), 955, 420, f"{V_} = (−{i_} + 7{j_}) {MS}", 40))
    F = Frame(EX_C, EX_PHI)
    O = F.P(0, 0)
    s.append(wall(F, -300, 300, fade(t, S("ex1") - 0.3)))
    s.append(label(*F.P(-200, -50), f"parallel to 3{i_} + 4{j_}", 28, NAVY, "start", fade(t, S("ex1", "parallel"))))
    s.append(ij_icon(1010, 300, 0, fade(t, S("ex1") - 0.3)))
    p, t_hit = ex_ball(t, F)
    s.append(ball(p, fade(t, S("ex1") - 0.3) * (1 - fade(t, S("ex5", "So the sphere leaves") + 0.6, 1.6))) + flash(F.P(0, RB), t, t_hit))
    uo = fade(t, S("ex1", "with velocity"))
    A = (O[0] - 11 * PXV, O[1] - 2 * PXV)
    s.append(vec(A, O, UC, uo) + mid_label(A, O, f"{U_} = 11{i_} − 2{j_}", UC, uo, 34, 32))
    Bv = (O[0] - 1 * PXV, O[1] - 7 * PXV)
    vo = fade(t, S("ex5", "b equals 7"))
    s.append(vec(O, Bv, VC, vo) + label(Bv[0] - 18, Bv[1] + 14, f"{V_} = −{i_} + 7{j_}", 32, VC, "end", vo))
    s.append(label(O[0] - 40, O[1] - 120, f"{V_} = ?", 34, VC, "middle", window(t, S("ex1", "Find"), S("ex5", "b equals 7"), 0.4)))
    wo, io = fade(t, S("ex2", "Along the wall")), fade(t, S("ex2", "which gives"))
    Wt, It = (O[0] + 3 * PXW, O[1] - 4 * PXW), (O[0] + 4 * PXW, O[1] + 3 * PXW)
    s.append(vec(O, Wt, WC, wo, 7) + label(Wt[0] + 40, Wt[1] + 30, f"{W_} = 3{i_} + 4{j_}", 30, WC, "start", wo))
    s.append(vec(O, It, IC, io, 7) + label(It[0] + 16, It[1] + 24, f"{I_} = 4{i_} − 3{j_}", 30, IC, "start", io))
    s.append(right_angle(F, (0, 0), -90, 22, INK, fade(t, S("ex2", "so they are"))))
    s.append(caption(t, [
        (S("ex1"), S("ex2"), "The problem", f"The wall is parallel to 3{i_} + 4{j_}, not to {i_} or {j_}."),
        (S("ex2"), S("ex3"), f"Step 1: Choose {W_} and {I_}", "Swap the components and change one sign."),
        (S("ex3"), S("ex4"), "Step 2: Along the wall", f"{U_}{D}{W_} = {V_}{D}{W_}"),
        (S("ex4"), S("ex5"), "Step 3: Perpendicular to the wall", f"−{e_} {U_}{D}{I_} = {V_}{D}{I_}"),
        (S("ex5"), S("cta"), "Step 4: Solve", f"Simultaneous equations give {a_} and {b_}."),
    ]))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ frame
TITLE_SUB = "Proving  u · w = v · w  and  −e u · I = v · I"

def frame_svg(t):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         DEFS, f'<rect width="{W}" height="{H}" fill="white"/>']
    for sc in (scene_setup, scene_physics, scene_recap, scene_along, scene_perp_u, scene_perp_v, scene_restitution,
               scene_summary, scene_example):
        s.append(sc(t))
    if S("s1") - 0.6 <= t < S("cta"):
        s.append(footer())
    s.append(section_card(t, S("ex0") - 0.55, S("ex1") - 0.55, [("Using the", "white"), ("results", "#ffc94d")],
                          "A sphere hits a wall parallel to 3i + 4j"))
    s.append(cta_card(t, S("cta") - 0.55, S("cta", "You'll find"), S("cta", "the link")))
    top = 1 - fade(t, S("s1") - 0.55, 0.6)
    if top > 0:
        s.append(card([("Oblique impact", "white"), ("with a wall", "#ffc94d")], TITLE_SUB, top))
    s.append('</svg>')
    return "".join(s)

def render(i):
    cairosvg.svg2png(bytestring=frame_svg(i / FPS).encode(), write_to=f"{OUT}/f{i:05d}.png", output_width=W, output_height=H)
    return i

def encode(out=HERE + "/impact.mp4"):
    """frames (and impact_audio.mp3 if it is there) -> impact.mp4"""
    cmd = ["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{OUT}/f%05d.png"]
    audio = HERE + "/impact_audio.mp3"
    if os.path.exists(audio):
        cmd += ["-i", audio, "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        for tt in map(float, sys.argv[2:]):
            cairosvg.svg2png(bytestring=frame_svg(tt).encode(), write_to=f"{HERE}/itest_{tt:06.1f}.png", output_width=W, output_height=H)
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == "cues":
        for k, v in CUES.c.items(): print(f"{v[0]:7.2f} {v[1]:5.2f} {k}")
        print("DUR", DUR); sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == "encode":
        encode(); sys.exit()
    for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
    n = int(DUR * FPS)
    with Pool(os.cpu_count() or 2) as p:
        for _ in p.imap_unordered(render, range(n), chunksize=20): pass
    print("frames done", n)
