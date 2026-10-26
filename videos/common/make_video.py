import math, os, sys, subprocess
import cairosvg
from multiprocessing import Pool

W, H, FPS = 1920, 1080, 30
DUR = 67.0
OUT = os.path.dirname(os.path.abspath(__file__)) + "/frames"
os.makedirs(OUT, exist_ok=True)

NAVY, GREEN, RED, BLUE, GOLD = "#14246b", "#1e8a4c", "#d32f2f", "#2f7fd1", "#e0a400"
BALL, WALLC, PURPLE = "#f6c995", "#c19a6b", "#2b0f52"
F = 'font-family="Liberation Sans"'

# ---------- helpers ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def fade(t, start, dur=0.5): return clamp((t - start) / dur)
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)

def arrowhead(x, y, ang, c, size=26):
    p2 = (x - size * math.cos(ang - 0.42), y - size * math.sin(ang - 0.42))
    p3 = (x - size * math.cos(ang + 0.42), y - size * math.sin(ang + 0.42))
    return f'<polygon points="{x},{y} {p2[0]},{p2[1]} {p3[0]},{p3[1]}" fill="{c}"/>'

def arrow(x0, y0, x1, y1, c, w=6, op=1.0):
    ang = math.atan2(y1 - y0, x1 - x0)
    ex, ey = x1 - 12 * math.cos(ang), y1 - 12 * math.sin(ang)
    return (f'<g opacity="{op}"><line x1="{x0}" y1="{y0}" x2="{ex}" y2="{ey}" stroke="{c}" '
            f'stroke-width="{w}" stroke-linecap="round"/>' + arrowhead(x1, y1, ang, c) + '</g>')

def text(x, y, inner, size=40, colour=NAVY, anchor="start", op=1.0, weight="normal"):
    return (f'<text x="{x}" y="{y}" {F} font-size="{size}" fill="{colour}" font-weight="{weight}" '
            f'text-anchor="{anchor}" opacity="{op}">{inner}</text>')

def it(s): return f'<tspan font-style="italic">{s}</tspan>'
def col(s, c, bold=False): return f'<tspan fill="{c}"{" font-weight=\"bold\"" if bold else ""}>{s}</tspan>'
MS = 'm s<tspan font-size="0.6em" dy="-0.7em">−1</tspan><tspan dy="0.7em"></tspan>'

# ---------- scene geometry ----------
GROUND = 560
WALL_X, WALL_W, WALL_TOP = 1590, 80, 300
R = 52
BY = GROUND - R
XC = WALL_X - R           # ball centre at contact
X0 = 1040                 # start position
V1 = (XC - X0) / 3.0      # px per second for 6 m/s
V2 = V1 * 4 / 6           # px per second for 4 m/s

def ball_state(t):
    """returns (x, squash 0..1, phase) for the ball."""
    for start in (10.0, 50.0):
        hit, leave, stop = start + 3.0, start + 3.4, start + 6.4
        if start <= t < hit:
            return X0 + V1 * (t - start), 0.0, "in"
        if hit <= t < leave:
            return XC, math.sin(math.pi * (t - hit) / 0.4), "hit"
        if leave <= t < stop:
            return XC - V2 * (t - leave), 0.0, "out"
    if t < 10.0:
        return X0, 0.0, "rest"
    if 16.4 <= t < 18.4:
        return XC - V2 * 3.0, 0.0, "hold"
    if 56.4 <= t:
        return XC - V2 * 3.0, 0.0, "hold"
    return XC, 0.0, "static"

def ball_svg(x, squash, op=1.0):
    rx = R * (1 - 0.18 * squash); ry = R * (1 + 0.08 * squash)
    cx = x if squash == 0 else WALL_X - rx
    cy = GROUND - ry
    return (f'<g opacity="{op}"><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{BALL}" stroke="#222" stroke-width="3"/>'
            + text(cx, cy + 12, "0.25", 34, "#111", "middle") + '</g>')

def ground_svg():
    s = [f'<rect x="980" y="{GROUND}" width="{WALL_X + WALL_W - 980}" height="70" fill="white" stroke="#222" stroke-width="2"/>']
    for i, x in enumerate(range(984, WALL_X + WALL_W, 7)):
        w = 2.4 if (i // 6) % 2 == 0 else 1.2
        s.append(f'<line x1="{x}" y1="{GROUND}" x2="{x}" y2="{GROUND + 70}" stroke="#222" stroke-width="{w}"/>')
    s.append(f'<rect x="{WALL_X}" y="{WALL_TOP}" width="{WALL_W}" height="{GROUND - WALL_TOP}" fill="{WALLC}" stroke="#222" stroke-width="2"/>')
    return "".join(s)

def flash_svg(t):
    out = []
    for hit in (13.0, 53.0):
        if hit <= t < hit + 0.9:
            k = (t - hit) / 0.9
            op = 1 - k
            for ang in (150, 180, 210, 125, 235):
                a = math.radians(ang)
                r0, r1 = R + 10 + 30 * k, R + 40 + 30 * k
                out.append(f'<line x1="{WALL_X + r0 * math.cos(a)}" y1="{BY + r0 * math.sin(a)}" '
                           f'x2="{WALL_X + r1 * math.cos(a)}" y2="{BY + r1 * math.sin(a)}" '
                           f'stroke="{GOLD}" stroke-width="6" stroke-linecap="round" opacity="{op}"/>')
    return "".join(out)

def speed_lines(x, direction, op=1.0):
    s = []
    for dy, ln in ((-25, 50), (0, 70), (25, 50)):
        if direction > 0:
            x1 = x - R - 15; x0 = x1 - ln
        else:
            x0 = x + R + 15; x1 = x0 + ln
        s.append(f'<line x1="{x0}" y1="{BY + dy}" x2="{x1}" y2="{BY + dy}" stroke="#999" stroke-width="4" stroke-linecap="round" opacity="{op}"/>')
    return "".join(s)

# ---------- static diagram arrows (working phase) ----------
def u_label(t):
    if t < 21.5:
        return f'{it("u")} = 6 {MS}'
    return f'{it("u")} = <tspan font-weight="bold">−6</tspan> {MS}'

def v_label(t):
    return f'{it("v")} = 4 {MS}' if t >= 46 else f'{it("v")} = ?'

def static_arrows(t, op):
    s = []
    gy = GROUND - 40
    s.append(arrow(XC - R - 300, gy, XC - R - 25, gy, GREEN, op=op))
    hl = fade(t, 21.5, 0.4) * (1 - fade(t, 24.5, 0.6))
    if hl > 0:
        s.append(f'<rect x="{XC - R - 330}" y="{gy - 82}" width="330" height="60" rx="10" fill="{GOLD}" opacity="{0.28 * hl * op}"/>')
    s.append(text(XC - R - 310, gy - 38, u_label(t), 36, GREEN, op=op))
    by = BY - R - 120
    s.append(arrow(XC + 10, by, XC - 270, by, BLUE, op=op))
    s.append(text(XC - 260, by - 22, v_label(t), 36, BLUE, op=op))
    iy = BY - 20
    s.append(arrow(WALL_X + WALL_W + 140, iy, WALL_X + 4, iy, RED, op=op))
    s.append(text(WALL_X + WALL_W + 20, iy + 62, f'|{it("I")}| = 2.5 N s', 34, RED, op=op))
    return "".join(s)

# ---------- left column ----------
QUESTION = [
    "A ball of mass 0.25 kg moving along a horizontal",
    f"surface hits a fixed vertical wall at right angles",
    f"with speed 6 {MS}. It rebounds at right angles.",
    "The magnitude of the impulse exerted on the ball",
    "by the wall is 2.5 N s.",
]

WORK = [  # (time, y, svg-inner, size)
    (21.5, 530, f'Take away from the wall as {col("positive", GOLD, True)}: {it("u")} = {col("−6", GREEN, True)}', 40),
    (26.0, 615, f'{col(it("I"), RED)} = {it("m")}{col(it("v"), BLUE)} − {it("m")}{col(it("u"), GREEN)}', 46),
    (31.0, 700, f'{col("2.5", RED)} = 0.25{col(it("v"), BLUE)} − 0.25({col("−6", GREEN, True)})', 46),
    (37.0, 785, f'{col("2.5", RED)} = 0.25{col(it("v"), BLUE)} + 1.5', 46),
    (41.0, 870, f'0.25{col(it("v"), BLUE)} = 1', 46),
    (45.0, 960, f'{col(it("v"), BLUE)} = 4', 50),
]

CAPTIONS = [  # (start, end, title, line)
    (5.0, 10.0, "The problem", "A ball hits a wall at right angles and bounces back."),
    (10.0, 18.6, "Watch the ball", f"It arrives at 6 {MS}, receives an impulse and rebounds."),
    (18.6, 26.0, "Step 1: Choose a positive direction", "The impulse acts away from the wall, so call that positive."),
    (26.0, 31.0, "Step 2: Impulse = change in momentum", "Write down I = mv − mu."),
    (31.0, 37.0, "Step 3: Substitute the values", "The ball moved towards the wall, so u = −6."),
    (37.0, 41.0, "Step 4: Simplify", "Two negatives make a positive: −0.25(−6) = +1.5"),
    (41.0, 45.0, "Step 5: Rearrange", "Subtract 1.5 from both sides."),
    (45.0, 50.0, "Step 6: Solve", "Divide by 0.25 to find v."),
    (50.0, 57.0, "Check the answer", "4 &lt; 6, so the ball leaves the wall slower than it arrived."),
]

def caption_svg(t):
    for start, end, title, line in CAPTIONS:
        if start <= t < end + 0.4:
            op = fade(t, start, 0.4) * (1 - fade(t, end, 0.4))
            return (f'<g opacity="{op}"><rect x="980" y="700" width="860" height="140" rx="14" fill="#dceaf7"/>'
                    + text(1010, 755, title, 38, NAVY, weight="bold")
                    + text(1010, 810, line, 30, NAVY) + '</g>')
    return ""

def mistake_svg(t):
    op = fade(t, 57.4, 0.5) * (1 - fade(t, 64.0, 0.5))
    if op <= 0: return ""
    l2 = fade(t, 58.6, 0.5); l3 = fade(t, 60.4, 0.5)
    return (f'<g opacity="{op}"><rect x="980" y="700" width="860" height="270" rx="14" fill="#fdecea" stroke="{RED}" stroke-width="4"/>'
            + text(1010, 760, "Common mistake: forgetting the sign of u", 36, RED, weight="bold")
            + text(1010, 835, f'2.5 = 0.25{it("v")} − 0.25(6)   →   {it("v")} = 16', 40, NAVY, op=l2)
            + text(1010, 910, "16 &gt; 6: faster than it arrived. Not possible!", 34, RED, op=l3)
            + '</g>')

def positive_svg(t):
    op = fade(t, 19.2, 0.5)
    if 57.4 <= t: op *= 1 - fade(t, 57.4, 0.5)
    if op <= 0: return ""
    y = 250
    return (arrow(1420, y, 1180, y, GOLD, w=7, op=op)
            + text(1440, y + 14, "+ positive", 40, GOLD, op=op, weight="bold"))

# ---------- title and end cards ----------
def card(title_lines, sub, op):
    s = [f'<g opacity="{op}"><rect width="{W}" height="{H}" fill="url(#bg)"/>']
    for x in range(0, W + 1, 60):
        s.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="white" stroke-opacity="0.05"/>')
    for y in range(0, H + 1, 60):
        s.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="white" stroke-opacity="0.05"/>')
    y = 420
    for i, (ln, c) in enumerate(title_lines):
        s.append(f'<text x="{W/2}" y="{y + i * 110}" font-family="Montserrat" font-weight="800" font-size="96" fill="{c}" text-anchor="middle">{ln}</text>')
    s.append(f'<text x="{W/2}" y="{y + len(title_lines) * 110 + 30}" font-family="Montserrat" font-weight="500" font-size="40" fill="white" fill-opacity="0.85" text-anchor="middle">{sub}</text>')
    s.append(f'<text x="{W/2}" y="{H - 90}" font-family="Montserrat" font-weight="700" font-size="40" fill="#ffc94d" text-anchor="middle">mr-mathematics.com</text>')
    s.append('</g>')
    return "".join(s)

DEFS = '''<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#2b0f52"/><stop offset="1" stop-color="#140a33"/></linearGradient></defs>'''

# ---------- frame ----------
def frame_svg(t):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', DEFS,
         f'<rect width="{W}" height="{H}" fill="white"/>']

    main_op = fade(t, 3.6, 0.6) * (1 - fade(t, 64.2, 0.6))
    if main_op > 0:
        s.append(f'<g opacity="{main_op}">')
        # header
        s.append(text(80, 80, "Impulse: a ball rebounding off a wall", 44, NAVY, weight="bold"))
        s.append(f'<line x1="80" y1="105" x2="1840" y2="105" stroke="{NAVY}" stroke-opacity="0.15" stroke-width="3"/>')
        # question
        for i, ln in enumerate(QUESTION):
            s.append(text(80, 175 + i * 46, ln, 32, NAVY, op=fade(t, 4.4 + i * 0.5, 0.5)))
        fop = fade(t, 7.2, 0.5)
        s.append(f'<rect x="70" y="415" width="840" height="60" rx="8" fill="#dceaf7" opacity="{fop}"/>')
        s.append(text(84, 456, "Find the speed of the ball just after it rebounds.", 32, NAVY, op=fop))
        # working
        for start, y, inner, size in WORK:
            k = ease(fade(t, start, 0.5))
            if k > 0:
                s.append(f'<g transform="translate(0,{20 * (1 - k)})">' + text(90, y, inner, size, NAVY, op=k) + '</g>')
        aop = fade(t, 46.0, 0.5)
        if aop > 0:
            s.append(f'<rect x="76" y="{960 - 62}" width="330" height="88" rx="12" fill="none" stroke="{GOLD}" stroke-width="5" opacity="{aop}"/>')
            s.append(text(430, 960, f'Speed = 4 {MS}', 42, BLUE, op=aop, weight="bold"))

        # diagram
        s.append(ground_svg())
        s.append(positive_svg(t))
        x, sq, phase = ball_state(t)
        # static arrows during the working phase
        sop = fade(t, 18.4, 0.5) * (1 - fade(t, 49.4, 0.5))
        if sop > 0:
            s.append(static_arrows(t, sop))
        # crossfade of the ball back to the wall before the working
        if 17.4 <= t < 18.4:
            k = (t - 17.4) / 1.0
            s.append(ball_svg(XC - V2 * 3.0, 0, 1 - k))
            s.append(ball_svg(XC, 0, k))
        elif 49.4 <= t < 50.0:
            k = (t - 49.4) / 0.6
            s.append(ball_svg(XC, 0, 1 - k))
            s.append(ball_svg(X0, 0, k))
        else:
            s.append(ball_svg(x, sq))
        # moving arrows during the animated phases
        replay = t >= 50
        if phase == "in":
            s.append(speed_lines(x, +1))
            s.append(arrow(x - 120, BY - R - 50, x + 60, BY - R - 50, GREEN))
            s.append(text(x - 120, BY - R - 72, f'{it("u")} = 6 {MS}', 34, GREEN))
        if phase in ("hit",) or (phase in ("out", "hold") and t < 18.4) or (phase in ("out", "hold") and replay):
            iop = 1.0 if phase != "hit" else clamp((t - (13.0 if not replay else 53.0)) / 0.2)
            hold_fade = 1.0
            if not replay and t >= 17.4: hold_fade = 1 - clamp(t - 17.4)
            iy = BY - 20
            s.append(arrow(WALL_X + WALL_W + 140, iy, WALL_X + 4, iy, RED, op=iop * hold_fade))
            s.append(text(WALL_X + WALL_W + 20, iy + 62, f'|{it("I")}| = 2.5 N s', 34, RED, op=iop * hold_fade))
        if phase in ("out", "hold") and (t < 18.4 or replay):
            hold_fade = 1.0
            if not replay and t >= 17.4: hold_fade = 1 - clamp(t - 17.4)
            if phase == "out": s.append(speed_lines(x, -1, hold_fade))
            lab = f'{it("v")} = 4 {MS}' if replay else f'{it("v")} = ?'
            s.append(arrow(x + 50, BY - R - 50, x - 150, BY - R - 50, BLUE, op=hold_fade))
            s.append(text(x - 150, BY - R - 72, lab, 34, BLUE, op=hold_fade))
        s.append(flash_svg(t))

        s.append(caption_svg(t))
        s.append(mistake_svg(t))
        s.append(text(1840, 1045, "mr-mathematics.com", 28, PURPLE, "end", weight="bold"))
        s.append('</g>')

    # title card
    top = 1 - fade(t, 3.2, 0.6)
    if top > 0:
        s.append(card([("Impulse and", "white"), ("Momentum", "#ffc94d")], "Finding the rebound speed of a ball", top))
    eop = fade(t, 64.4, 0.6)
    if eop > 0:
        s.append(card([("Impulse =", "white"), ("change in momentum", "#ffc94d")], "I = mv − mu   ·   choose a positive direction first", eop))
    s.append('</svg>')
    return "".join(s)

def render(i):
    t = i / FPS
    path = f"{OUT}/f{i:05d}.png"
    if not os.path.exists(path):
        cairosvg.svg2png(bytestring=frame_svg(t).encode(), write_to=path, output_width=W, output_height=H)
    return i

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        for tt in map(float, sys.argv[2:]):
            cairosvg.svg2png(bytestring=frame_svg(tt).encode(), write_to=f"{OUT}/../test_{tt:05.1f}.png", output_width=W, output_height=H)
        sys.exit()
    n = int(DUR * FPS)
    with Pool(2) as p:
        for k, _ in enumerate(p.imap_unordered(render, range(n), chunksize=20)):
            if k % 300 == 0: print(k, flush=True)
    print("frames done")
