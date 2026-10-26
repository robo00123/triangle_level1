import math, os, sys, base64, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "common"))
import cairosvg
from multiprocessing import Pool
from make_video import arrow, text, it, col, clamp, fade, ease, card, DEFS, NAVY, GREEN, RED, BLUE, GOLD, W, H, FPS
from lesson import (Cues, window, NB, label, header, divider, footer, caption, notes, working, qblock, gold_box,
                    answer_box, pop, mistake, pause_banner, section_card, cta_card, title_image, dashed, darrow, track,
                    moving, bar, PUR, INK)
import work_script

OUT = HERE + "/frames_work"
os.makedirs(OUT, exist_ok=True)
IMG64 = base64.b64encode(open(HERE + "/work_title.png", "rb").read()).decode()
CUES = Cues(work_script, HERE + "/work_cues.json")
S, DUR = CUES.S, CUES.dur

# colour code, the same as the lesson slides: applied force green, distance blue, friction red, weight purple
F_ = col(it("F"), GREEN)
S_ = col(it("s"), BLUE)
H_ = col(it("h"), BLUE)
R_ = col(it("R"), BLUE)
MG = col(f'{it("m")}{it("g")}', PUR)
MU = it("μ")
FR_ = col(it("F"), RED)
MS = 'm s<tspan font-size="0.6em" dy="-0.7em">−1</tspan><tspan dy="0.42em"></tspan>'

def scene(t, first, nxt):
    """a slide stays still through the pause after its last line, then crossfades into the next slide"""
    return window(t, S(first) - 0.55, S(nxt) - 0.55)

# ------------------------------------------------------------------ drawing
def floor(x0, x1, y, rough=0.0, op=1.0):
    s = [f'<g opacity="{op}"><line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{INK}" stroke-width="4"/>']
    if rough > 0:
        x = x0 + 10
        while x < x1 - 4:
            s.append(f'<line x1="{x}" y1="{y + 2}" x2="{x - 12}" y2="{y + 18}" stroke="#555" stroke-width="3" opacity="{rough}"/>')
            x += 22
    s.append('</g>')
    return "".join(s)

def crate(x, yb, w=150, h=96, lab="", op=1.0, ghost=False, fs=34):
    """crate with its bottom-left corner at (x, yb)"""
    if op <= 0: return ""
    stroke = f'stroke="{PUR}" stroke-opacity="0.45" stroke-dasharray="12,8"' if ghost else f'stroke="{PUR}"'
    return (f'<g opacity="{op}"><rect x="{x}" y="{yb - h}" width="{w}" height="{h}" rx="18" fill="white" {stroke} stroke-width="5"/>'
            + (text(x + w / 2, yb - h / 2 + fs * 0.36, lab, fs, PUR, "middle") if lab else "") + '</g>')

def s_arrow(x0, x1, y, lab, op=1.0, c=BLUE, size=36):
    """distance moved: a tick at the start and an arrow to the current position, labelled above"""
    if op <= 0: return ""
    s = [f'<g opacity="{op}"><line x1="{x0}" y1="{y - 14}" x2="{x0}" y2="{y + 14}" stroke="{c}" stroke-width="4"/>']
    if x1 - x0 > 26:
        s.append(arrow(x0, y, x1, y, c, w=5))
    lo = clamp((x1 - x0 - 90) / 60)
    if lo > 0 and lab:
        s.append(label((x0 + x1) / 2, y - 18, lab, size, c, "middle", lo))
    s.append('</g>')
    return "".join(s)

def v_arrow(x, y0, y1, lab, op=1.0, c=BLUE, size=36, both=False):
    """vertical distance from y0 (bottom) up to y1"""
    if op <= 0 or y0 - y1 < 4: return ""
    s = [f'<g opacity="{op}"><line x1="{x - 14}" y1="{y0}" x2="{x + 14}" y2="{y0}" stroke="{c}" stroke-width="4"/>']
    if y0 - y1 > 26:
        s.append(arrow(x, y0, x, y1, c, w=5))
        if both:
            s.append(arrow(x, y1, x, y0, c, w=5))
    lo = clamp((y0 - y1 - 90) / 60)
    if lo > 0 and lab:
        s.append(text(x + 18, (y0 + y1) / 2 + 12, lab, size, c, op=lo))
    s.append('</g>')
    return "".join(s)

def speed_lines(x, y, op=1.0):
    if op <= 0: return ""
    return "".join(f'<line x1="{x - 16}" y1="{y + dy}" x2="{x - 16 - ln}" y2="{y + dy}" stroke="#999" stroke-width="4" '
                   f'stroke-linecap="round" opacity="{op}"/>' for dy, ln in ((-22, 46), (0, 66), (22, 46)))

def push(x, y, lab, op=1.0, length=130, size=34):
    """applied force arriving at the left side of a crate at (x, y)"""
    if op <= 0: return ""
    return arrow(x - length, y, x - 4, y, GREEN, w=6, op=op) + label(x - length, y - 16, lab, size, GREEN, "start", op)

def friction(x, y, lab, op=1.0, length=150, size=34):
    """friction under the floor, pointing back from x, labelled underneath"""
    if op <= 0: return ""
    return arrow(x, y, x - length, y, RED, w=6, op=op) + label(x - length / 2, y + 42, lab, size, RED, "middle", op)

def wall(x, y0, y1, op=1.0):
    s = [f'<g opacity="{op}"><rect x="{x}" y="{y0}" width="60" height="{y1 - y0}" fill="#e9edf3" stroke="{INK}" stroke-width="4"/>']
    for yy in range(int(y0) + 14, int(y1), 22):
        s.append(f'<line x1="{x + 4}" y1="{yy + 14}" x2="{x + 56}" y2="{yy - 8}" stroke="#777" stroke-width="2.5"/>')
    s.append('</g>')
    return "".join(s)

def clock(x, y, secs, op=1.0):
    """a stopwatch showing secs, with its hand going round once every 3 seconds"""
    if op <= 0: return ""
    a = 2 * math.pi * (secs / 3.0) - math.pi / 2
    return (f'<g opacity="{op}"><circle cx="{x}" cy="{y}" r="34" fill="white" stroke="{NAVY}" stroke-width="5"/>'
            f'<rect x="{x - 8}" y="{y - 50}" width="16" height="12" rx="3" fill="{NAVY}"/>'
            f'<line x1="{x}" y1="{y}" x2="{x + 26 * math.cos(a)}" y2="{y + 26 * math.sin(a)}" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>'
            + text(x + 52, y + 13, f'{it("t")} = {secs:.1f} s', 38, NAVY) + '</g>')

# ------------------------------------------------------------------ what is work done?
def scene_idea(t):
    op = scene(t, "i1", "h1")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("What is work done?"), divider()]
    s.append(notes(t, [
        (S("i2", "Work"), 240, "Work", 80, PUR, "bold"),
        (S("i2", "whenever"), 310, f'is done whenever a force makes an object {col("move", GOLD, True)}.', 36, NAVY, "normal"),
        (S("i3", "The box moves"), 400, "The box moves, so the force does work.", 34, NAVY, "normal"),
        (S("i4", "The further"), 455, "The further it moves, the more work is done.", 34, NAVY, "normal"),
        (S("i5", "However hard"), 560, "The wall doesn't move, so no work is done,", 34, NAVY, "normal"),
        (S("i5", "doesn't move"), 605, "however hard you push.", 34, NAVY, "normal"),
        (S("i6", "you've done"), 680, "Leaning on a wall all lesson is tiring,", 32, NAVY, "normal"),
        (S("i6", "you've done") + 0.3, 722, "but it does no work on the wall.", 32, NAVY, "normal"),
    ]))
    s.append(gold_box(t, S("i7"), 76, 780, 830, 120, [f"No movement  →  no work"], 50))
    # a force that moves a box does work
    G, X0, X1 = 400, 1110, 1600
    k = clamp((t - S("i3", "pushes")) / (S("i4", "does") - S("i3", "pushes")))
    x = X0 + (X1 - X0) * k
    o1 = fade(t, S("i3") - 0.2)
    s.append(floor(1000, 1840, G, op=o1))
    s.append(crate(x, G, 140, 90, op=o1))
    s.append(push(x, G - 45, F_, o1))
    if 0 < k < 1: s.append(speed_lines(x - 130, G - 45, 0.6))
    s.append(s_arrow(X0, x, G - 130, S_, o1))
    bo = fade(t, S("i4", "Watch"))
    s.append(text(1000, 470, "Work done", 30, NAVY, op=bo, weight="bold"))
    s.append(bar(1000, 485, 700, [(700 * k, GREEN)], bo, h=36))
    # pushing on a wall does none
    o2 = fade(t, S("i5", "Now"))
    if o2 > 0:
        Gw = 860
        strain = 0.5 + 0.5 * math.sin(2 * math.pi * 2.2 * t)
        grow = clamp((t - S("i5", "However hard")) / 2.0)
        ln = 110 + 70 * grow + 10 * strain * grow
        s.append(f'<g opacity="{o2}">' + floor(1000, 1840, Gw) + wall(1560, 610, Gw))
        s.append(arrow(1556 - ln, 740, 1556, 740, GREEN, w=6 + 4 * grow))
        s.append(text(1556 - ln, 722, F_, 36, GREEN))
        for i, dy in enumerate((-30, 0, 30)):
            s.append(f'<line x1="{1630 + 10 * strain}" y1="{740 + dy}" x2="{1650 + 10 * strain}" y2="{740 + dy * 1.4}" '
                     f'stroke="{GOLD}" stroke-width="4" stroke-linecap="round" opacity="{grow}"/>')
        s.append(text(1080, 820, f"{S_} = 0 m", 38, BLUE, op=fade(t, S("i5", "doesn't move"))))
        s.append(text(1000, 925, "Work done", 30, NAVY, weight="bold"))
        s.append(bar(1000, 940, 700, [], 1, h=36, value=None))
        s.append(text(1716, 970, "0 J", 32, GREEN, op=fade(t, S("i6", "no work")), weight="bold"))
        s.append('</g>')
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ how much work?
def comparison(t, y, t0, t1, force, dist, lab_f, lab_s, lab_w, op):
    """one row: a crate pushed `dist` px by an arrow `force` px long, filling a bar in proportion to force x dist"""
    if op <= 0: return ""
    k = clamp((t - t0) / (t1 - t0))
    x0 = 1260
    x = x0 + dist * k
    s = [f'<g opacity="{op}">', floor(1000, 1840, y)]
    s.append(crate(x, y, 90, 60))
    s.append(arrow(x - force, y - 30, x - 4, y - 30, GREEN, w=6))
    s.append(label(x - force - 10, y - 18, lab_f, 32, GREEN, "end"))
    if 0 < k < 1: s.append(speed_lines(x - force - 50, y - 30, 0.5))
    s.append(s_arrow(x0, x, y - 78, lab_s, 1, size=30))
    w = 200 * force * dist / (110 * 150) * k
    s.append(bar(1260, y + 18, 420, [(w, GREEN)], 1, h=30))
    if k >= 1:
        s.append(text(1260 + w + 14, y + 44, lab_w, 32, GREEN, weight="bold"))
    s.append('</g>')
    return "".join(s)

def scene_amount(t):
    op = scene(t, "h1", "e1a")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("How much work is done?"), divider()]
    s.append(notes(t, [
        (S("h1", "two things"), 205, "The work done depends on two things:", 36, NAVY, "bold"),
        (S("h2", "size of the force"), 268, f"1.  the size of the {col('force', GREEN, True)}", 34, NAVY, "normal"),
        (S("h3", "how far"), 323, f"2.  how far the object moves in the {col('direction', BLUE, True)}", 34, NAVY, "normal"),
        (S("h3", "direction"), 368, f"     {col('of the force', BLUE, True)}", 34, NAVY, "normal"),
    ]))
    bo = fade(t, S("h4", "the work done"))
    if bo > 0:
        s.append(f'<rect x="76" y="410" width="830" height="150" rx="14" fill="#dceaf7" opacity="{bo}"/>')
        s.append(text(100, 470, NB(f"Work done  =  {col('force in the direction of motion', GREEN)}"), 32, NAVY, op=bo))
        s.append(text(100, 525, NB(f"×  {col('distance moved in the direction of the force', BLUE)}"), 32, NAVY, op=bo))
    s.append(gold_box(t, S("h5", "W equals"), 76, 600, 400, 130, [f"{it('W')} = {F_}{S_}"], 64))
    s.append(notes(t, [(S("h5", "where s"), 650, f"{F_} = force (N)", 32, NAVY, "normal"),
                       (S("h5", "where s") + 0.4, 700, f"{S_} = distance moved (m)", 32, NAVY, "normal")], x=510))
    s.append(notes(t, [(S("h6", "joules"), 820, "Work done is measured in joules (J).", 34, NAVY, "normal"),
                       (S("h6", "One joule"), 880, col("1 J  =  work done when 1 N moves an object 1 m", GOLD, True), 31, NAVY, "normal")]))
    # double the force, double the distance
    s.append(notes(t, [(S("h2", "The first"), 165, f"Force {F_}, distance {S_}", 28, NAVY, "bold"),
                       (S("h2", "Double"), 375, f"Double the force: 2{F_}", 28, NAVY, "bold"),
                       (S("h3", "Use the same"), 585, f"Double the distance: 2{S_}", 28, NAVY, "bold")], x=1000))
    s.append(comparison(t, 290, S("h2", "The first"), S("h2", "Double") - 0.3, 110, 150, F_, S_, it("W"),
                        fade(t, S("h2", "The first") - 0.3)))
    s.append(comparison(t, 500, S("h2", "Double"), S("h2", "twice"), 220, 150, f"2{F_}", S_, f"2{it('W')}",
                        fade(t, S("h2", "Double") - 0.3)))
    s.append(comparison(t, 710, S("h3", "Use the same"), S("h3", "again"), 110, 300, F_, f"2{S_}", f"2{it('W')}",
                        fade(t, S("h3", "Use the same") - 0.3)))
    # one joule
    jo = fade(t, S("h6", "One joule") - 0.2)
    if jo > 0:
        k = clamp((t - S("h6", "One joule")) / max(0.5, S("h6", 1.0) - S("h6", "One joule")))
        G, x0 = 930, 1260
        x = x0 + 160 * k
        s.append(f'<g opacity="{jo}">' + floor(1000, 1840, G) + crate(x, G, 90, 60))
        s.append(arrow(x - 110, G - 30, x - 4, G - 30, GREEN, w=6) + label(x - 120, G - 18, "1 N", 32, GREEN, "end"))
        s.append(s_arrow(x0, x, G - 78, "1 m", 1, size=30))
        s.append(bar(1260, G + 18, 420, [(70 * k, GREEN)], 1, h=30))
        if k >= 1: s.append(text(1260 + 70 + 14, G + 44, "1 J", 32, GREEN, weight="bold"))
        s.append('</g>')
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ example 1: work done by a force
def scene_ex1(t):
    op = scene(t, "e1b", "gv1")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Example 1: work done by a force")]
    s.append(qblock(t, [(S("e1b"), "A crate is pushed 12 m across a horizontal floor by a"),
                        (S("e1b", "constant"), "constant horizontal force of magnitude 25 N.")],
                    ["Calculate the work done by the force."], S("e1c")))
    s.append(working(t, [(S("e1s1", "the work done"), "Work done = force × distance", 40),
                         (S("e1s1", "multiplied"), f"{it('W')} = {F_}{S_}", 40),
                         (S("e1s2", "25 times 12"), f"{it('W')} = 25 × 12", 40)], 410, 72))
    s.append(answer_box(t, S("e1s2", "300 joules"), 650, 330, f"{it('W')} = 300 J", 44))
    G, X0, X1 = 470, 1150, 1640
    k = clamp((t - S("e1b", "is pushed")) / (S("e1b", 1.0) - S("e1b", "is pushed")))
    x = X0 + (X1 - X0) * k
    s.append(floor(1000, 1840, G))
    s.append(crate(X1, G, 150, 96, ghost=True, op=1 - k))
    if k < 0.98: s.append(darrow((x + 165, G - 48), (X1 - 15, G - 48), INK, 4, 0.7))
    s.append(crate(x, G, 150, 96))
    s.append(push(x, G - 48, f"{F_} = 25 N", 1, 150, 32))
    if 0 < k < 1: s.append(speed_lines(x - 150, G - 48, 0.5))
    s.append(s_arrow(X0, x, G - 140, f"{S_} = 12 m"))
    bo = fade(t, S("e1b", "is pushed"))
    s.append(bar(1200, 590, 520, [(520 * k, GREEN)], bo, lab="Work done", labc=GREEN,
                 value="300 J" if t >= S("e1s2", "300 joules") else None, valc=GREEN))
    s.append(caption(t, [
        (S("e1b"), S("e1s1"), "The problem", "A constant force pushes a crate 12 m."),
        (S("e1s1"), S("e1s2"), "Step 1: Work done = force × distance", "The force acts in the direction of motion."),
        (S("e1s2"), S("gv1"), "Step 2: Substitute", "Force 25 N, distance 12 m"),
    ]))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ work done against gravity
def scene_lift(t):
    op = scene(t, "gv1", "e2a")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Work done against gravity"), divider()]
    s.append(notes(t, [(S("gv1", "Gravity"), 210, f"Weight:  {MG}  acting downwards", 36, NAVY, "normal"),
                       (S("gv2", "To lift"), 285, "To lift at a steady speed:", 34, NAVY, "normal"),
                       (S("gv2", "equal"), 335, f"lifting force  =  weight  =  {MG}", 36, NAVY, "bold")]))
    s.append(working(t, [(S("gv3", "the work done"), "Work done = force × distance", 40),
                         (S("gv3", "m g multiplied"), f"                = {MG} × {H_}", 40)], 440, 75))
    s.append(gold_box(t, S("gv3", "m g multiplied") + 1.2, 76, 620, 830, 120, [f"Work done against gravity  =  {it('m')}{it('g')}{H_}"], 44))
    G, TOP, X = 880, 470, 1330
    k = clamp((t - S("gv2", "To lift")) / (S("gv3", "the work done") - S("gv2", "To lift")))
    yb = G - (G - TOP) * k
    s.append(floor(1080, 1640, G))
    s.append(crate(X, yb, 150, 100))
    wo = fade(t, S("gv1", "weight"))
    s.append(arrow(X + 75, yb - 50, X + 75, yb + 70, PUR, w=6, op=wo))
    s.append(text(X + 90, yb + 60, MG, 36, PUR, op=wo))
    lo = fade(t, S("gv2", "equal"))
    s.append(arrow(X + 75, yb - 100, X + 75, yb - 220, GREEN, w=6, op=lo))
    s.append(text(X + 90, yb - 180, MG, 36, GREEN, op=lo))
    if 0 < k < 1:
        s.append("".join(f'<line x1="{X + 75 + dx}" y1="{yb + 16}" x2="{X + 75 + dx}" y2="{yb + 16 + ln}" stroke="#999" '
                         f'stroke-width="4" stroke-linecap="round" opacity="0.5"/>' for dx, ln in ((-40, 40), (0, 56), (40, 40))))
    s.append(v_arrow(1580, G, yb, H_))
    bo = fade(t, S("gv2", "To lift"))
    s.append(text(1080, 955, "Work done against gravity", 28, PUR, op=bo, weight="bold"))
    s.append(bar(1080, 970, 560, [(560 * k, PUR)], bo, h=30))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ example 2: lifting a box
def scene_ex2(t):
    op = scene(t, "e2a", "e3a")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Example 2: work done against gravity")]
    s.append(qblock(t, [(S("e2a"), "A box of mass 12 kg is lifted vertically through a"),
                        (S("e2a", "height"), "height of 5 m.")],
                    ["Calculate the work done against gravity."], S("e2a", "Calculate")))
    s.append(working(t, [(S("e2s1", "The lifting force"), f"Lifting force = weight = {MG} = 12 × 9.8", 36),
                         (S("e2s1", "The distance"), f"Distance = height = 5 m", 36),
                         (S("e2s2", "12 times"), f"{it('W')} = {F_}{S_} = 12 × 9.8 × 5", 36)], 410, 72))
    s.append(answer_box(t, S("e2s2", "588 joules"), 640, 330, f"{it('W')} = 588 J", 44))
    G, TOP, X = 660, 260, 1380
    k = clamp((t - S("e2a", "is lifted")) / (S("e2a", "Calculate") - S("e2a", "is lifted")))
    yb = G - (G - TOP) * k
    s.append(floor(1240, 1720, G))
    s.append(crate(X, TOP, 150, 96, ghost=True, op=1 - k))
    if k < 0.95: s.append(darrow((X + 75, yb - 110), (X + 75, TOP + 14), INK, 4, 0.7))
    s.append(crate(X, yb, 150, 96, "12 kg", fs=32))
    s.append(v_arrow(1640, G, yb, f"{S_} = 5 m"))
    # work bar, upright, filling with the height
    bo = fade(t, S("e2a", "is lifted"))
    if bo > 0:
        hb = 400 * k
        s.append(f'<g opacity="{bo}"><rect x="1060" y="{G - 400}" width="44" height="400" rx="6" fill="#eef1f7"/>'
                 f'<rect x="1060" y="{G - hb}" width="44" height="{hb}" rx="6" fill="{PUR}"/>'
                 + text(1082, G + 40, "Work done", 26, PUR, "middle", weight="bold")
                 + (text(1082, G - 415, "588 J", 30, PUR, "middle", weight="bold") if t >= S("e2s2", "588 joules") else "") + '</g>')
    s.append(caption(t, [
        (S("e2a"), S("e2s1"), "The problem", "A box is lifted straight up through 5 m."),
        (S("e2s1"), S("e2s2"), "Step 1: Force and distance", "Lifting force = weight, distance = height"),
        (S("e2s2"), S("e3a"), "Step 2: Work done = mgh", "12 × 9.8 × 5 = 588 J"),
    ]))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ example 3: the height of a tower
def scene_ex3(t):
    op = scene(t, "e3a", "fr1")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Example 3: finding the height of a tower")]
    s.append(qblock(t, [(S("e3b"), "A cable is attached to a crate of mass 60 kg. The crate"),
                        (S("e3b", "is lifted"), "is lifted vertically at a constant speed from the ground"),
                        (S("e3b", "to the top"), "to the top of a tower. The work done in raising the"),
                        (S("e3c"), "crate is 24 kJ.")],
                    ["Calculate the height of the tower."], S("e3c", "Calculate")))
    s.append(working(t, [(S("e3s1", "24 kilojoules"), "24 kJ = 24 000 J", 38),
                         (S("e3s2", "The work done"), f"{it('W')} = {MG}{H_}", 38),
                         (S("e3s2", "So 24"), f"24 000 = 60 × 9.8 × {H_}", 38),
                         (S("e3s3", "60 times"), f"24 000 = 588{H_}", 38),
                         (S("e3s3", "Dividing"), f"{H_} = 24 000 ÷ 588", 38)], 460, 62))
    s.append(answer_box(t, S("e3s3", "40.8"), 800, 420, f"{H_} = 40.8 m  (3 s.f.)", 40))
    G, TOP, X = 660, 260, 1370
    t0, t1 = S("e3b", "is lifted"), S("e3b", "tower")
    k = clamp((t - t0) / (t1 - t0))
    yb = G - (G - TOP) * k
    s.append(floor(1150, 1820, G))
    # the beam at the top of the tower and the cable
    s.append(f'<line x1="1300" y1="160" x2="1590" y2="160" stroke="{INK}" stroke-width="5"/>')
    s.append("".join(f'<line x1="{x}" y1="160" x2="{x + 16}" y2="136" stroke="{INK}" stroke-width="3"/>' for x in range(1306, 1590, 22)))
    s.append(f'<line x1="{X + 75}" y1="160" x2="{X + 75}" y2="{yb - 90}" stroke="{PUR}" stroke-width="5"/>')
    s.append(crate(X, TOP, 150, 90, ghost=True, op=1 - k))
    s.append(crate(X, yb, 150, 90, "60 kg", fs=32))
    hlab = f"{H_} = 40.8 m" if t >= S("e3s3", "40.8") else f"{H_} m"
    s.append(v_arrow(1610, G, TOP, hlab, fade(t, S("e3c")), both=True))
    bo = fade(t, t0)
    if bo > 0:
        hb = 400 * k
        s.append(f'<g opacity="{bo}"><rect x="1060" y="{G - 400}" width="44" height="400" rx="6" fill="#eef1f7"/>'
                 f'<rect x="1060" y="{G - hb}" width="44" height="{hb}" rx="6" fill="{PUR}"/>'
                 + text(1082, G + 40, "Work done", 26, PUR, "middle", weight="bold")
                 + (text(1082, G - 415, "24 kJ", 30, PUR, "middle", weight="bold") if t >= S("e3c", "24 kilojoules") else "") + '</g>')
    # sense check: a 13 storey building beside the tower
    bo2 = fade(t, S("e3chk", "13 storey"))
    if bo2 > 0:
        bx, bw = 1170, 110
        s.append(f'<g opacity="{bo2}"><rect x="{bx}" y="{TOP}" width="{bw}" height="{G - TOP}" fill="#eef1f7" stroke="{NAVY}" stroke-width="3"/>')
        fh = (G - TOP) / 13
        for i in range(13):
            yy = TOP + i * fh
            s.append(f'<rect x="{bx + 14}" y="{yy + fh * 0.25}" width="30" height="{fh * 0.5}" fill="#9fc4e8"/>'
                     f'<rect x="{bx + 64}" y="{yy + fh * 0.25}" width="30" height="{fh * 0.5}" fill="#9fc4e8"/>')
        s.append('</g>')
    s.append(caption(t, [
        (S("e3a"), S("e3s1"), "The problem", "Work backwards from the work done to the height."),
        (S("e3s1"), S("e3s2"), "Step 1: Convert to joules", "1 kJ = 1000 J"),
        (S("e3s2"), S("e3s3"), "Step 2: Work done against gravity", "W = mgh"),
        (S("e3s3"), S("e3chk"), "Step 3: Solve for h", "Divide 24 000 by 588."),
        (S("e3chk"), S("fr1"), "Check", "40.8 m is about a 13 storey building."),
    ]))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ work done against friction
def scene_friction(t):
    op = scene(t, "fr1", "e4a")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Work done against friction"), divider()]
    s.append(notes(t, [(S("fr1", "rough"), 210, "On a rough floor, friction opposes the motion.", 34, NAVY, "normal"),
                       (S("fr2", "To push"), 270, f"Constant speed:  push = {col('friction', RED, True)}", 34, NAVY, "normal")]))
    s.append(working(t, [(S("fr3", "Friction is"), f"{col('Friction', RED)} = {MU}{R_}", 40),
                         (S("fr3", "so R equals"), f"Horizontal floor:   {R_} = {MG}", 40),
                         (S("fr4", "mu m g"), f"{col('Friction', RED)} = {MU}{MG}", 40)], 380, 75))
    s.append(gold_box(t, S("fr4", "multiplied"), 76, 640, 830, 170, ["Work done against friction", f"=  {MU}{it('m')}{it('g')} × {S_}"], 44))
    G, X0, X1 = 470, 1150, 1600
    t0, t1 = S("fr2", "Friction acts"), S("fr2", 1.0)
    k = clamp((t - t0) / (t1 - t0))
    x = X0 + (X1 - X0) * k
    s.append(floor(1000, 1840, G, rough=fade(t, S("fr1", "rough"))))
    s.append(crate(x, G, 140, 90))
    s.append(push(x, G - 45, "push", fade(t, S("fr2", "pushing"))))
    s.append(friction(x + 120, G + 40, "Friction", fade(t, S("fr2", "Friction acts")), 130))
    if 0 < k < 1: s.append(speed_lines(x - 130, G - 45, 0.5))
    ro = fade(t, S("fr3", "normal reaction"))
    s.append(arrow(x + 70, G - 90, x + 70, G - 200, BLUE, w=6, op=ro) + text(x + 84, G - 170, R_, 36, BLUE, op=ro))
    wo = fade(t, S("fr3", "weight"))
    s.append(arrow(x + 70, G - 45, x + 70, G + 10, PUR, w=6, op=wo) + text(x + 150, G - 20, MG, 32, PUR, op=wo))
    s.append(s_arrow(X0, x, G - 250 if ro > 0 else G - 140, S_, fade(t, t0)))
    bo = fade(t, t0)
    s.append(text(1000, 600, "Work done against friction", 30, RED, op=bo, weight="bold"))
    s.append(bar(1000, 615, 700, [(700 * k, RED)], bo, h=36))
    for i in range(1, 4):
        if k >= i / 4:
            s.append(f'<line x1="{1000 + 175 * i}" y1="609" x2="{1000 + 175 * i}" y2="657" stroke="{GOLD}" stroke-width="5" opacity="{bo}"/>')
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ example 4: the coefficient of friction
def scene_ex4(t):
    op = scene(t, "e4a", "q5a")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Example 4: finding the coefficient of friction")]
    s.append(qblock(t, [(S("e4a"), "A crate of mass 8 kg is pushed a distance of 6 m across"),
                        (S("e4a", "a rough"), "a rough horizontal floor. The crate moves at a constant"),
                        (S("e4a", "The crate moves"), "speed. The work done against friction is 72 J.")],
                    ["Calculate the coefficient of friction between the", "crate and the floor."], S("e4b", "Calculate")))
    s.append(working(t, [(S("e4s1", "72 equals"), f"{it('W')} = {FR_}{S_}:   72 = {FR_} × 6", 38),
                         (S("e4s1", "That makes"), f"{FR_} = 12 N", 38),
                         (S("e4s2", "R equals"), f"{R_} = {MG} = 8 × 9.8 = 78.4 N", 38),
                         (S("e4s3", "12 equals"), f"{FR_} = {MU}{R_}:   12 = {MU} × 78.4", 38)], 460, 64))
    s.append(answer_box(t, S("e4s3", "0.153"), 760, 420, f"{MU} = 0.153  (3 s.f.)", 40))
    G, X0, X1 = 470, 1150, 1600
    k = clamp((t - S("e4a", "is pushed")) / (S("e4a", "The crate moves") - S("e4a", "is pushed")))
    x = X0 + (X1 - X0) * k
    s.append(floor(1000, 1840, G, rough=1))
    s.append(crate(X1, G, 140, 90, ghost=True, op=1 - k))
    s.append(crate(x, G, 140, 90, "8 kg", fs=32))
    s.append(push(x, G - 45, "push", 1))
    flab = col(f'{it("F")} = 12 N', RED) if t >= S("e4s1", "12 newtons") else "Friction"
    s.append(friction(x + 120, G + 40, flab, 1, 130))
    if 0 < k < 1: s.append(speed_lines(x - 130, G - 45, 0.5))
    ro = fade(t, S("e4s2", "R equals"))
    rlab = R_ + (col(" = 78.4 N", BLUE) if t >= S("e4s2", "78.4") else "")
    s.append(arrow(x + 70, G - 90, x + 70, G - 190, BLUE, w=6, op=ro) + label(x + 56, G - 150, rlab, 34, BLUE, "end", ro))
    s.append(s_arrow(X0, x, G - 140 if ro <= 0 else G - 230, f"{S_} = 6 m"))
    s.append(bar(1200, 600, 520, [(520 * k, RED)], 1, lab="against friction", labc=RED,
                 value="72 J" if t >= S("e4b", "72 joules") else None, valc=RED))
    s.append(caption(t, [
        (S("e4a"), S("e4s1"), "The problem", "Work backwards from the work done to μ."),
        (S("e4s1"), S("e4s2"), "Step 1: Find the friction", "Work done = force × distance"),
        (S("e4s2"), S("e4s3"), "Step 2: Normal reaction", "Horizontal floor and push, so R = mg."),
        (S("e4s3"), S("q5a"), "Step 3: Friction = μR", "Divide 12 by 78.4."),
    ]))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ your turn
def scene_q5(t):
    op = scene(t, "q5b", "cta")
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Your turn: work done in 3 seconds")]
    s.append(qblock(t, [(S("q5b"), "A crate of mass 5 kg is pushed across a rough horizontal"),
                        (S("q5b", "floor"), f"floor at a constant speed of 4 {MS}. The coefficient"),
                        (S("q5c"), "of friction between the crate and the floor is 0.4.")],
                    ["Calculate the work done against friction in 3 seconds."], S("q5c", "Calculate")))
    s.append(working(t, [(S("s5a", "4 times 3"), f"{S_} = {it('v')}{it('t')} = 4 × 3 = 12 m", 36),
                         (S("s5b", "R equals"), f"{R_} = {MG},  so  {FR_} = {MU}{MG}", 36),
                         (S("s5b", "0.4 times"), f"{FR_} = 0.4 × 5 × 9.8 = 19.6 N", 36),
                         (S("s5c", "19.6 times"), f"{it('W')} = {FR_}{S_} = 19.6 × 12", 36)], 560, 64))
    s.append(answer_box(t, S("s5c", "235.2 joules"), 870, 360, f"{it('W')} = 235.2 J", 42))
    # 3 seconds at 4 m/s: once while the question is read, again for the distance
    G, X0, X1 = 470, 1150, 1600
    m1 = S("q5b", "constant speed")
    m2 = S("s5a", "At 4")
    if t < m2 - 0.6:
        tt = clamp(t - m1, 0, 3.0)
    else:
        tt = clamp(t - m2, 0, 3.0)
    x = X0 + (X1 - X0) * tt / 3.0
    s.append(floor(1000, 1840, G, rough=1))
    s.append(crate(x, G, 140, 90, "5 kg", fs=32))
    s.append(push(x, G - 45, f"{it('v')} = 4 {MS}", 1, 150, 30))
    flab = col(f'{it("F")} = 19.6 N', RED) if t >= S("s5b", "19.6 newtons") else "Friction"
    s.append(friction(x + 120, G + 40, flab, 1, 130))
    if 0 < tt < 3.0: s.append(speed_lines(x - 150, G - 45, 0.5))
    slab = f"{S_} = 12 m" if t >= S("s5a", "12 metres") else f"{S_} = ?"
    s.append(s_arrow(X0, x, G - 140, slab))
    s.append(clock(1560, 200, tt, fade(t, m1 - 0.5)))
    kw = clamp((t - S("s5c", "The work done")) / max(0.5, S("s5c", "235.2 joules") - S("s5c", "The work done")))
    s.append(bar(1200, 600, 520, [(520 * kw, RED)], fade(t, S("s5c", "The work done")), lab="against friction", labc=RED,
                 value="235.2 J" if t >= S("s5c", "235.2 joules") else None, valc=RED))
    s.append(caption(t, [
        (S("q5b"), S("q5p"), "Your turn", "Constant speed on a rough floor, for 3 seconds"),
        (S("s5a"), S("s5b"), "Step 1: Distance travelled", "distance = speed × time"),
        (S("s5b"), S("s5c"), "Step 2: Friction", "F = μR and R = mg"),
        (S("s5c"), S("s5chk"), "Step 3: Work done", "Friction × distance"),
    ]))
    s.append(mistake(t, S("s5chk", "A common mistake"), S("cta") - 0.4, "Common mistake: multiplying by the time",
                     "19.6 × 3 = 58.8  is not work done", "Work done is force × distance, not force × time.",
                     S("s5chk", "That gives"), S("s5chk", "Work done is always")))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ frame
def frame_svg(t):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         DEFS, f'<rect width="{W}" height="{H}" fill="white"/>']
    for sc in (scene_idea, scene_amount, scene_ex1, scene_lift, scene_ex2, scene_ex3, scene_friction, scene_ex4, scene_q5):
        s.append(sc(t))
    if S("i1") - 0.6 <= t < S("cta"):
        s.append(footer())
    s.append(pause_banner(t, S("q5p"), S("q5r"), S("q5r", 1.0)))
    s.append(section_card(t, S("e1a") - 0.55, S("e1b") - 0.55, [("Worked", "white"), ("examples", "#ffc94d")],
                          "By a force, against gravity and against friction"))
    s.append(section_card(t, S("q5a") - 0.55, S("q5b") - 0.55, [("Your", "white"), ("turn", "#ffc94d")], "Work done against friction"))
    s.append(cta_card(t, S("cta") - 0.55, S("cta", "You'll find"), S("cta", "the link")))
    s.append(title_image(t, IMG64, S("i1") - 0.55))
    s.append('</svg>')
    return "".join(s)

def render(i):
    cairosvg.svg2png(bytestring=frame_svg(i / FPS).encode(), write_to=f"{OUT}/f{i:05d}.png", output_width=W, output_height=H)
    return i

def encode(out=HERE + "/work.mp4"):
    """frames (and work_audio.mp3 if it is there) -> work.mp4"""
    cmd = ["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{OUT}/f%05d.png"]
    audio = HERE + "/work_audio.mp3"
    if os.path.exists(audio):
        cmd += ["-i", audio, "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        for tt in map(float, sys.argv[2:]):
            cairosvg.svg2png(bytestring=frame_svg(tt).encode(), write_to=f"{HERE}/wtest_{tt:06.1f}.png", output_width=W, output_height=H)
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
