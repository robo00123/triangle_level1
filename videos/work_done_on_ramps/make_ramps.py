import math, os, re, sys, json, base64, subprocess
import cairosvg
from multiprocessing import Pool
from PIL import ImageFont
from make_video import (arrow, arrowhead, text, it, col, clamp, fade, ease, card, DEFS,
                        NAVY, GREEN, RED, BLUE, GOLD, W, H, FPS)
from ramps_script import SCRIPT, estimated_cues

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE + "/frames_ramps"
os.makedirs(OUT, exist_ok=True)
IMG64 = base64.b64encode(open(HERE + "/ramps_title.png", "rb").read()).decode()

WORDS = {}
if os.path.exists(HERE + "/ramps_cues.json"):
    C = json.load(open(HERE + "/ramps_cues.json"))
    DUR = C.pop("_end")[0]
    WORDS = C.pop("_words", {})
    C = {k: tuple(v) for k, v in C.items()}
else:
    C, DUR = estimated_cues()
    DUR += 1.0

_norm = lambda w: re.sub(r"[^\w.']", "", w.lower()).strip(".'")
LINE_WORDS = {k: [_norm(w) for w in line.split()] for k, line in SCRIPT}

def word_index(k, phrase):
    p, ws = [_norm(w) for w in phrase.split()], LINE_WORDS[k]
    for i in range(len(ws) - len(p) + 1):
        if ws[i:i + len(p)] == p:
            return i
    raise KeyError(f"'{phrase}' is not in script line '{k}'")

def S(k, f=0.0):
    """time of a point in script line k: f is a fraction of the way through its words,
    or a word or phrase from the line, giving the moment the narrator starts saying it"""
    s, d = C[k]
    n = len(LINE_WORDS[k])
    if isinstance(f, str):
        f = word_index(k, f) / n
    ws = WORDS.get(k)
    if not ws:
        return s + f * d
    pos = clamp(f) * n
    i = min(int(pos), n - 1)
    return ws[i] + (pos - i) * (ws[i + 1] - ws[i])

def window(t, a, b, f=0.5):
    return fade(t, a, f) * (1 - fade(t, b, f))

PUR = "#6a2c91"
LOGO = "#2b0f52"
ORANGE = "#ff7a1a"
RAMP = "#b7e1f1"      # the ramp colour from the lesson slides
INK = "#111"

# colour code, the same as the lesson slides: T green, R blue, friction red, weight purple, height orange
T_, R_, FR = col(it("T"), GREEN), col(it("R"), BLUE), col(f'{it("F")}r', RED)
MG = col(f'{it("m")}{it("g")}', PUR)
MU = it("μ")
A_ = it("α")
D_, H_ = it("d"), col(it("h"), ORANGE)
SIN, COS = f"sin {A_}", f"cos {A_}"

# ------------------------------------------------------------------ helpers shared with the other videos
def header(title):
    return (text(80, 80, title, 44, NAVY, weight="bold")
            + f'<line x1="80" y1="105" x2="1840" y2="105" stroke="{NAVY}" stroke-opacity="0.15" stroke-width="3"/>')

def divider():
    return f'<line x1="930" y1="140" x2="930" y2="1000" stroke="{NAVY}" stroke-opacity="0.15" stroke-width="3"/>'

def caption(t, steps):
    for a, b, title, line in steps:
        if a <= t < b + 0.4:
            op = fade(t, a, 0.4) * (1 - fade(t, b, 0.4))
            return (f'<g opacity="{op}"><rect x="990" y="720" width="850" height="140" rx="14" fill="#dceaf7"/>'
                    + text(1020, 775, title, 36, NAVY, weight="bold") + text(1020, 830, line, 29, NAVY) + '</g>')
    return ""

NB = lambda x: x.replace('  ', '  ')

def notes(t, items, x=80):
    s = []
    for start, y, inner, size, c, wgt in items:
        o = ease(fade(t, start, 0.5))
        if o > 0:
            s.append(f'<g transform="translate(0,{14 * (1 - o)})">' + text(x, y, NB(inner), size, c, op=o, weight=wgt) + '</g>')
    return "".join(s)

def working(t, rows, y0, step):
    s = []
    for i, (st, inner, size) in enumerate(rows):
        e = ease(fade(t, st, 0.5))
        if e > 0:
            s.append(f'<g transform="translate(0,{18 * (1 - e)})">' + text(90, y0 + i * step, NB(inner), size, NAVY, op=e) + '</g>')
    return "".join(s)

def qblock(t, lines, finds, find_t, y0=160, step=42, size=30):
    s = []
    for i, (st, ln) in enumerate(lines):
        s.append(text(80, y0 + i * step, ln, size, NAVY, op=fade(t, st, 0.5)))
    fo = fade(t, find_t, 0.5)
    fy = y0 + len(lines) * step - 12
    s.append(f'<rect x="70" y="{fy}" width="840" height="{30 + 44 * len(finds)}" rx="10" fill="#dceaf7" opacity="{fo}"/>')
    for i, ln in enumerate(finds):
        s.append(text(86, fy + 46 + i * 44, NB(ln), 29, NAVY, op=fo))
    return "".join(s)

def gold_box(t, start, x, y, w, h, lines, size=46):
    o = fade(t, start, 0.5)
    if o <= 0: return ""
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#fff6dd" stroke="{GOLD}" stroke-width="5" opacity="{o}"/>']
    step = h / (len(lines) + 1)
    for i, ln in enumerate(lines):
        s.append(text(x + 30, y + step * (i + 1) + size * 0.36, NB(ln), size, NAVY, op=o, weight="bold"))
    return "".join(s)

def answer_box(t, start, y, w, inner, size=40):
    o = fade(t, start, 0.5)
    if o <= 0: return ""
    return (f'<rect x="76" y="{y - size - 14}" width="{w}" height="{size + 34}" rx="12" fill="#fff6dd" stroke="{GOLD}" stroke-width="5" opacity="{o}"/>'
            + text(92, y, NB(inner), size, NAVY, op=o))

def pop(t, t0, x, y, txt, dur=2.2, size=46):
    op = window(t, t0, t0 + dur, 0.3)
    if op <= 0: return ""
    sc = 1 + 0.25 * (1 - ease(clamp((t - t0) / 0.35)))
    return (f'<g opacity="{op}" transform="translate({x} {y}) scale({sc}) translate({-x} {-y})">'
            + text(x, y, txt, size, GOLD, "middle", 1, "bold") + '</g>')

def pause_banner(t, pk, rk):
    op = window(t, S(pk), S(rk, 1.0) + 0.2, 0.5)
    if op <= 0: return ""
    x, y, w, h = 60, 520, 850, 330
    cx, cy = x + 120, y + 130
    s = [f'<g opacity="{op}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="#2b0f52"/>',
         f'<circle cx="{cx}" cy="{cy}" r="70" fill="none" stroke="#ffc94d" stroke-width="8"/>',
         f'<rect x="{cx - 28}" y="{cy - 36}" width="20" height="72" rx="5" fill="#ffc94d"/>',
         f'<rect x="{cx + 8}" y="{cy - 36}" width="20" height="72" rx="5" fill="#ffc94d"/>',
         f'<text x="{x + 230}" y="{cy - 10}" font-family="Montserrat" font-weight="800" font-size="60" fill="white">Pause the video</text>',
         f'<text x="{x + 230}" y="{cy + 45}" font-family="Montserrat" font-weight="600" font-size="30" fill="white" fill-opacity="0.9">and try the question yourself</text>',
         f'<text x="{x + 40}" y="{y + 280}" font-family="Montserrat" font-weight="600" font-size="30" fill="white" fill-opacity="0.9">Then press play to check your working</text>']
    if t >= S(rk):
        ro = fade(t, S(rk), 0.3)
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="#2b0f52" opacity="{ro}"/>')
        s.append(f'<text x="{x + w/2}" y="{y + h/2 + 22}" font-family="Montserrat" font-weight="800" font-size="62" fill="#ffc94d" text-anchor="middle" opacity="{ro}">Let\'s go through it</text>')
    s.append('</g>')
    return "".join(s)

def section_card(t, key, nxt, lines, subt):
    op = window(t, S(key) - 0.4, S(nxt) - 0.3, 0.4)
    return card(lines, subt, op) if op > 0 else ""

def cta_card(t):
    op = fade(t, S("cta") - 0.4, 0.6)
    if op <= 0: return ""
    s = [f'<g opacity="{op}"><rect width="{W}" height="{H}" fill="url(#bg)"/>']
    for x in range(0, W + 1, 60):
        s.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="white" stroke-opacity="0.05"/>')
    for y in range(0, H + 1, 60):
        s.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="white" stroke-opacity="0.05"/>')
    s.append(f'<text x="{W/2}" y="330" font-family="Montserrat" font-weight="800" font-size="96" fill="white" text-anchor="middle">Full lesson and</text>')
    s.append(f'<text x="{W/2}" y="440" font-family="Montserrat" font-weight="800" font-size="96" fill="#ffc94d" text-anchor="middle">worksheet</text>')
    uo = fade(t, S("cta", "You'll find"))
    s.append(f'<text x="{W/2}" y="590" font-family="Montserrat" font-weight="600" font-size="44" fill="white" fill-opacity="0.85" text-anchor="middle" opacity="{uo}">Visit</text>')
    s.append(f'<text x="{W/2}" y="680" font-family="Montserrat" font-weight="800" font-size="72" fill="white" text-anchor="middle" opacity="{uo}">mr-mathematics.com</text>')
    lo = fade(t, S("cta", "the link"))
    bob = 12 * math.sin(2 * math.pi * 1.2 * t)
    s.append(f'<g opacity="{lo}"><rect x="{W/2 - 460}" y="770" width="920" height="96" rx="48" fill="#ffc94d"/>'
             f'<text x="{W/2}" y="832" font-family="Montserrat" font-weight="700" font-size="42" fill="#2b0f52" text-anchor="middle">Worksheet link in the description below</text>'
             f'<polygon points="{W/2 - 44},{910 + bob} {W/2 + 44},{910 + bob} {W/2},{965 + bob}" fill="#ffc94d"/></g>')
    s.append('</g>')
    return "".join(s)

def dashed(p0, p1, c, op=1.0, w=4):
    if op <= 0: return ""
    return f'<line x1="{p0[0]}" y1="{p0[1]}" x2="{p1[0]}" y2="{p1[1]}" stroke="{c}" stroke-width="{w}" stroke-dasharray="10,8" opacity="{op}"/>'

# ------------------------------------------------------------------ text measuring (rich text must use anchor start)
_FONTS = {}
def tw(inner, size, bold=False):
    plain = re.sub(r"<[^>]+>", "", inner).replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    key = (size, bold)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf" % ("Bold" if bold else "Regular"), size)
    return _FONTS[key].getlength(plain)

def label(x, y, inner, size, c, align="start", op=1.0, weight="normal"):
    w = tw(inner, size, weight == "bold")
    x0 = x if align == "start" else x - w / 2 if align == "middle" else x - w
    return text(x0, y, inner, size, c, "start", op, weight)

def unit(dx, dy):
    d = math.hypot(dx, dy); return dx / d, dy / d

def flabel(E, d, inner, size, c, op=1.0, gap=14, dx=0, dy=0, align=None):
    """label just beyond the end E of an arrow pointing in direction d"""
    x, y = E[0] + d[0] * gap + dx, E[1] + d[1] * gap + dy
    align = align or ("start" if d[0] > 0.35 else "end" if d[0] < -0.35 else "middle")
    if d[1] > 0.35: y += size * 0.8
    elif d[1] < -0.35: y -= 4
    else: y += size * 0.35
    return label(x, y, inner, size, c, align, op)

def darrow(p0, p1, c, w=5, op=1.0):
    if op <= 0: return ""
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    ex, ey = p1[0] - 12 * math.cos(ang), p1[1] - 12 * math.sin(ang)
    return (f'<g opacity="{op}"><line x1="{p0[0]}" y1="{p0[1]}" x2="{ex}" y2="{ey}" stroke="{c}" stroke-width="{w}" '
            f'stroke-dasharray="12,9"/>' + arrowhead(p1[0], p1[1], ang, c, 22) + '</g>')

def track(t, keys):
    """piecewise-linear (position, opacity) through keyframes [(time, position, opacity)]"""
    if t <= keys[0][0]: return keys[0][1], keys[0][2]
    for (t0, s0, o0), (t1, s1, o1) in zip(keys, keys[1:]):
        if t < t1:
            k = (t - t0) / max(t1 - t0, 1e-6)
            return s0 + (s1 - s0) * k, o0 + (o1 - o0) * k
    return keys[-1][1], keys[-1][2]

def bar(x, y, wfull, segs, op=1.0, h=30, outline=None, lab=None, labc=NAVY, value=None, valc=NAVY):
    """a horizontal work bar. segs = [(width, colour)] drawn end to end."""
    if op <= 0: return ""
    s = [f'<g opacity="{op}"><rect x="{x}" y="{y}" width="{wfull}" height="{h}" rx="6" fill="#eef1f7"/>']
    xx = x
    for w, c in segs:
        if w > 0.5:
            s.append(f'<rect x="{xx}" y="{y}" width="{w}" height="{h}" rx="6" fill="{c}"/>')
        xx += w
    if outline:
        s.append(f'<rect x="{x}" y="{y}" width="{max(xx - x, 1)}" height="{h}" rx="6" fill="none" stroke="{outline}" stroke-width="4"/>')
    if lab:
        s.append(label(x - 14, y + h * 0.5 + 9, lab, 26, labc, "end"))
    if value:
        s.append(text(xx + 12, y + h * 0.5 + 10, value, 28, valc, weight="bold"))
    s.append('</g>')
    return "".join(s)

def tri_icon(x0, y0, adj, opp, hyp, unit_px, op=1.0, size=28, c=NAVY):
    """right-angled triangle with the angle alpha at the bottom left, labelled with its sides"""
    if op <= 0: return ""
    wv, hv = adj * unit_px, opp * unit_px
    A, B, Cc = (x0, y0), (x0 + wv, y0), (x0 + wv, y0 - hv)
    ang = math.degrees(math.atan2(hv, wv))
    s = [f'<g opacity="{op}"><polygon points="{A[0]},{A[1]} {B[0]},{B[1]} {Cc[0]},{Cc[1]}" fill="#fff6dd" stroke="{c}" stroke-width="4" stroke-linejoin="round"/>',
         f'<polyline points="{B[0] - 18},{B[1]} {B[0] - 18},{B[1] - 18} {B[0]},{B[1] - 18}" fill="none" stroke="{c}" stroke-width="2.5"/>',
         label((A[0] + B[0]) / 2, y0 + size + 6, str(adj), size, c, "middle", weight="bold"),
         text(B[0] + 12, y0 - hv / 2 + size * 0.36, str(opp), size, c, weight="bold"),
         f'<text x="{(A[0] + Cc[0]) / 2 - 10}" y="{(A[1] + Cc[1]) / 2 - 12}" font-family="Liberation Sans" font-size="{size}" '
         f'font-weight="bold" fill="{c}" text-anchor="middle" transform="rotate({-ang} {(A[0] + Cc[0]) / 2 - 10} {(A[1] + Cc[1]) / 2 - 12})">{hyp}</text>',
         text(A[0] + 0.3 * wv, y0 - 8, A_, size - 4, c), '</g>']
    return "".join(s)

# ------------------------------------------------------------------ the ramp
class Ramp:
    """A right-angled ramp: bottom-left corner (ax, ay), horizontal base L, angle deg.
    Positions on the slope are s (distance up the slope) and k (distance out from the surface)."""
    def __init__(self, ax, ay, L, deg, bw=120, bh=70):
        self.ax, self.ay, self.L, self.deg = ax, ay, L, deg
        a = math.radians(deg)
        self.c, self.s = math.cos(a), math.sin(a)
        self.Hh = L * math.tan(a)
        self.Sl = L / self.c
        self.bw, self.bh = bw, bh
        self.up, self.down = (self.c, -self.s), (-self.c, self.s)
        self.out, self.into = (-self.s, -self.c), (self.s, self.c)

    def P(self, s, k=0.0):
        return (self.ax + s * self.c - k * self.s, self.ay - s * self.s - k * self.c)

    def svg(self, rough=0.0, op=1.0, alpha=None):
        ax, ay, L, Hh = self.ax, self.ay, self.L, self.Hh
        s = [f'<g opacity="{op}"><polygon points="{ax},{ay} {ax + L},{ay} {ax + L},{ay - Hh}" fill="{RAMP}" '
             f'stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>',
             f'<polyline points="{ax + L - 30},{ay} {ax + L - 30},{ay - 30} {ax + L},{ay - 30}" fill="none" stroke="{INK}" stroke-width="3"/>']
        r = 80
        s.append(f'<path d="M {ax + r} {ay} A {r} {r} 0 0 0 {ax + r * self.c} {ay - r * self.s}" fill="none" stroke="{INK}" stroke-width="3"/>')
        am = math.radians(self.deg / 2)
        s.append(text(ax + (r + 12) * math.cos(am), ay - (r + 12) * math.sin(am) + 14, alpha or A_, 40, INK))
        if rough > 0:
            g = [f'<g opacity="{rough}">']
            k = 30.0
            while k < self.Sl - 20:
                p0, p1 = self.P(k, 0), self.P(k - 12, -16)
                g.append(f'<line x1="{p0[0]}" y1="{p0[1]}" x2="{p1[0]}" y2="{p1[1]}" stroke="#555" stroke-width="3"/>')
                k += 24
            g.append('</g>')
            s.append("".join(g))
        s.append('</g>')
        return "".join(s)

    def box(self, s, lab="", op=1.0, fs=26):
        if op <= 0: return ""
        x, y = self.P(s, 0)
        bw, bh = self.bw, self.bh
        return (f'<g opacity="{op}" transform="translate({x} {y}) rotate({-self.deg})">'
                f'<rect x="{-bw / 2}" y="{-bh}" width="{bw}" height="{bh}" rx="16" fill="white" stroke="{PUR}" stroke-width="5"/>'
                + (text(0, -bh / 2 + fs * 0.36, lab, fs, PUR, "middle") if lab else "") + '</g>')

    def at(self, s):
        bw, bh = self.bw, self.bh
        return dict(front=self.P(s + bw / 2, bh / 2), rear=self.P(s - bw / 2, bh / 2), top=self.P(s, bh),
                    centre=self.P(s, bh / 2), base=self.P(s, 0))

    def force(self, s, kind, op=1.0, lab=None, length=None, size=34, lab_dx=0, lab_dy=0, mid=False, align=None):
        """T up the slope, Fr down the slope, R out of the slope, W straight down."""
        if op <= 0: return ""
        a = self.at(s)
        spec = {"T": (a["front"], self.up, 130, GREEN, T_),
                "Fr": (a["rear"], self.down, 120, RED, "Friction"),
                "R": (a["top"], self.out, 110, BLUE, R_),
                "W": (a["centre"], (0, 1), 130, PUR, MG)}[kind]
        p0, d, ln, c, default = spec
        ln = length or ln
        E = (p0[0] + d[0] * ln, p0[1] + d[1] * ln)
        if mid:
            m = (p0[0] + d[0] * ln / 2 + self.out[0] * 30, p0[1] + d[1] * ln / 2 + self.out[1] * 30)
            return arrow(p0[0], p0[1], E[0], E[1], c, w=6, op=op) + label(m[0], m[1], lab or default, size, c, "middle", op)
        return arrow(p0[0], p0[1], E[0], E[1], c, w=6, op=op) + flabel(E, d, lab or default, size, c, op, dx=lab_dx, dy=lab_dy, align=align)

    def components(self, s, op_cos=1.0, op_sin=1.0, size=30):
        a = self.at(s)["centre"]
        out = ""
        if op_cos > 0:
            E = (a[0] + self.into[0] * 115, a[1] + self.into[1] * 115)
            out += darrow(a, E, PUR, op=op_cos) + flabel(E, self.into, f'{it("m")}{it("g")} {COS}', size, PUR, op_cos)
        if op_sin > 0:
            E = (a[0] + self.down[0] * 125, a[1] + self.down[1] * 125)
            out += darrow(a, E, PUR, op=op_sin) + flabel(E, self.down, f'{it("m")}{it("g")} {SIN}', size, PUR, op_sin, dy=-46)
        return out

    def d_arrow(self, s0, s1, op=1.0, lab=None, k=None, ticks=0):
        """distance moved, drawn above the path from the rear of the box at s0 to the rear at s1"""
        if op <= 0 or s1 - s0 < 2: return ""
        k = self.bh + 45 if k is None else k
        p0, p1 = self.P(s0 - self.bw / 2, k), self.P(s1 - self.bw / 2, k)
        t0, t1 = self.P(s0 - self.bw / 2, k - 14), self.P(s0 - self.bw / 2, k + 14)
        out = [f'<g opacity="{op}"><line x1="{t0[0]}" y1="{t0[1]}" x2="{t1[0]}" y2="{t1[1]}" stroke="{INK}" stroke-width="4"/>']
        if s1 - s0 > 26:
            out.append(arrow(p0[0], p0[1], p1[0], p1[1], INK, w=5))
        for i in range(1, ticks):
            q0, q1 = self.P(s0 - self.bw / 2 + i * (s1 - s0) / ticks, k - 10), self.P(s0 - self.bw / 2 + i * (s1 - s0) / ticks, k + 10)
            out.append(f'<line x1="{q0[0]}" y1="{q0[1]}" x2="{q1[0]}" y2="{q1[1]}" stroke="{GOLD}" stroke-width="5"/>')
        m = self.P((s0 + s1) / 2 - self.bw / 2, k + 30)
        lo = clamp((s1 - s0 - 90) / 60)          # the label waits until the arrow is long enough to hold it
        if lo > 0:
            out.append(label(m[0], m[1] + 12, lab or D_, 38, INK, "middle", lo))
        out.append('</g>')
        return "".join(out)

    def h_marker(self, s0, s1, op=1.0, lab=None, size=38, inside=False):
        """vertical height gained between the rear of the box at s0 and at s1"""
        if op <= 0 or s1 - s0 < 2: return ""
        p0, p1 = self.P(s0 - self.bw / 2, 0), self.P(s1 - self.bw / 2, 0)
        q = (p1[0], p0[1])
        lab = label(q[0] + 16, q[1] - 24, lab or H_, size, ORANGE, "start") if inside else \
            label(q[0] - 14, (q[1] + p1[1]) / 2 + 14, lab or H_, size, ORANGE, "end")
        return f'<g opacity="{op}">' + dashed(p0, q, ORANGE, 1, 5) + dashed(q, p1, ORANGE, 1, 5) + lab + '</g>'


    def h_triangle(self, s0, s1, op=1.0):
        if op <= 0: return ""
        p0, p1 = self.P(s0 - self.bw / 2, 0), self.P(s1 - self.bw / 2, 0)
        q = (p1[0], p0[1])
        m = self.P((s0 + s1) / 2 - self.bw / 2, 34)
        return (f'<polygon points="{p0[0]},{p0[1]} {q[0]},{q[1]} {p1[0]},{p1[1]}" fill="{GOLD}" fill-opacity="0.3" opacity="{op}"/>'
                f'<line x1="{p0[0]}" y1="{p0[1]}" x2="{p1[0]}" y2="{p1[1]}" stroke="{GOLD}" stroke-width="8" opacity="{op}"/>'
                + label(m[0], m[1] + 12, D_, 40, INK, "middle", op))

    def speed_lines(self, s, op=1.0):
        if op <= 0: return ""
        out = []
        for k, ln in ((self.bh * 0.25, 46), (self.bh * 0.5, 66), (self.bh * 0.75, 46)):
            p0 = self.P(s - self.bw / 2 - 16, k)
            p1 = self.P(s - self.bw / 2 - 16 - ln, k)
            out.append(f'<line x1="{p0[0]}" y1="{p0[1]}" x2="{p1[0]}" y2="{p1[1]}" stroke="#999" stroke-width="4" stroke-linecap="round" opacity="{op}"/>')
        return "".join(out)

def moving(t, keys):
    """is the box moving at time t (used for speed lines)"""
    for (t0, s0, _), (t1, s1, _) in zip(keys, keys[1:]):
        if t0 <= t < t1 and abs(s1 - s0) > 1 and t1 - t0 > 0.4:
            return True
    return False

# ------------------------------------------------------------------ opening
def scene_open(t):
    op = 1 - fade(t, S("wd1") - 0.7, 0.6)
    if op <= 0: return ""
    sc = 1.0 + 0.02 * ease(clamp(t / max(1.0, S("wd1"))))
    return (f'<g opacity="{op}"><rect width="{W}" height="{H}" fill="white"/>'
            f'<g transform="translate({W/2} {H/2}) scale({sc}) translate({-W/2} {-H/2})">'
            f'<image x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid meet" '
            f'href="data:image/png;base64,{IMG64}" xlink:href="data:image/png;base64,{IMG64}"/></g></g>')

# ------------------------------------------------------------------ work done: a reminder
def scene_work(t):
    a, b = S("wd1") - 0.7, S("g1") - 0.3
    op = window(t, a, b)
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Work done: a quick reminder"), divider()]
    s.append(notes(t, [(S("wd1", "When"), 220, "When a force moves an object, it does work.", 34, NAVY, "normal"),
                       (S("wd2", "measured"), 470, "Work done is measured in joules (J).", 34, NAVY, "normal"),
                       (S("wd2", "Twice"), 545, col("Twice the distance  →  twice the work", GOLD, True), 36, NAVY, "normal")]))
    s.append(gold_box(t, S("wd1", "The work done"), 76, 270, 820, 120, ["Work done = force × distance"], 46))
    G, BW, BH = 520, 140, 84
    x0, x1 = 1020, 1560
    k = clamp((t - S("wd1", "moves")) / (S("wd2", "twice the work") - S("wd1", "moves")))
    x = x0 + (x1 - x0) * k
    s.append(f'<line x1="990" y1="{G}" x2="1840" y2="{G}" stroke="{INK}" stroke-width="4"/>')
    s.append(f'<rect x="{x}" y="{G - BH}" width="{BW}" height="{BH}" rx="16" fill="white" stroke="{PUR}" stroke-width="5"/>')
    s.append(arrow(x + BW, G - BH / 2, x + BW + 130, G - BH / 2, GREEN, w=6))
    s.append(text(x + BW + 145, G - BH / 2 + 14, it("F"), 40, GREEN))
    if 0 < k < 1:
        for dy, ln in ((-20, 46), (0, 66), (20, 46)):
            s.append(f'<line x1="{x - 16}" y1="{G - BH / 2 + dy}" x2="{x - 16 - ln}" y2="{G - BH / 2 + dy}" stroke="#999" stroke-width="4" stroke-linecap="round"/>')
    # distance and work bar, each in two equal halves
    yd, yb, wfull = 380, 640, 700
    xm = x0 + (x1 - x0) / 2
    if x - x0 > 26:
        s.append(f'<line x1="{x0}" y1="{yd - 14}" x2="{x0}" y2="{yd + 14}" stroke="{INK}" stroke-width="4"/>')
        s.append(arrow(x0, yd, x, yd, INK, w=5))
    s.append(text(1020, yb - 18, "Work done", 32, NAVY, weight="bold"))
    s.append(bar(1020, yb, wfull, [(wfull * k, GREEN)], h=40))
    for frac, ko in ((0.5, k >= 0.5), (1.0, k >= 0.999)):
        if ko:
            xx = x0 + (x1 - x0) * frac
            s.append(f'<line x1="{xx}" y1="{yd - 14}" x2="{xx}" y2="{yd + 14}" stroke="{GOLD}" stroke-width="5"/>')
            s.append(label(xx - (x1 - x0) / 4, yd - 22, D_, 38, INK, "middle"))
            xb = 1020 + wfull * frac
            s.append(f'<line x1="{xb}" y1="{yb - 8}" x2="{xb}" y2="{yb + 48}" stroke="{GOLD}" stroke-width="5"/>')
            s.append(label(xb - wfull / 4, yb + 90, it("W"), 38, GREEN, "middle"))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ work done against gravity
RG = Ramp(1000, 660, 800, 30)
G_S0, G_S1 = 170, 600

def scene_gravity(t):
    a, b = S("g1") - 0.3, S("g8") - 0.3
    op = window(t, a, b)
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Work done against gravity"), divider()]
    mg = f'{it("m")}{it("g")}'
    s.append(notes(t, [
        (S("g1", "pulled"), 200, f"Pull the box a distance {D_} up the slope.", 34, NAVY, "normal"),
        (S("g2", "vertical"), 255, f"It rises a vertical height {H_}.", 34, NAVY, "normal"),
        (S("g3", "weight"), 330, f"Weight:  {col(mg, PUR)}  straight down", 34, NAVY, "normal"),
        (S("g4", "m g sine"), 385, f"Component down the slope:  {col(mg + ' ' + SIN, PUR, True)}", 34, NAVY, "normal"),
    ]))
    s.append(working(t, [
        (S("g5", "m g sine"), f"Work done  =  {col(mg + ' ' + SIN, PUR)} × {D_}", 40),
        (S("g6", "Sine alpha"), f"{SIN} = {H_}/{D_}    so    {D_} {SIN} = {H_}", 40),
    ], 485, 75))
    s.append(gold_box(t, S("g7", "m g h"), 76, 610, 830, 120, [f"Work done against gravity  =  {it('m')}{it('g')}{H_}"], 44))
    s.append(notes(t, [(S("g7", "weight"), 800, col("weight × vertical height", GOLD, True), 36, NAVY, "normal")]))
    # motion
    keys = [(S("g1", "pulled"), G_S0, 1), (S("g2", "The vertical"), G_S1, 1)]
    sb, _ = track(t, keys)
    s.append(RG.svg())
    s.append(RG.h_triangle(G_S0, G_S1, window(t, S("g6", "triangle"), S("g7", "vertical"), 0.5)))
    s.append(RG.h_marker(G_S0, sb, fade(t, S("g2", "rises"), 0.4)))
    s.append(RG.d_arrow(G_S0, sb, fade(t, S("g1", "distance"), 0.4) * (1 - fade(t, S("g3", "The box is moving"), 0.5))))
    if moving(t, keys): s.append(RG.speed_lines(sb))
    s.append(RG.box(sb))
    calm = 1 - 0.85 * window(t, S("g6", "triangle"), S("g7", "height gained"), 0.5)
    s.append(RG.force(sb, "W", fade(t, S("g3", "weight")) * calm))
    s.append(RG.components(sb, (fade(t, S("g4", "One component")) * 0.55 + fade(t, S("g4", "m g cos")) * 0.45 * (1 - fade(t, S("g4", "The other")))) * calm,
                           fade(t, S("g4", "The other"))))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ only the height matters
RH = Ramp(990, 800, 760, 25, bw=110, bh=66)
H_S0, H_S1 = 70, 640

def scene_height(t):
    a, b = S("g8") - 0.3, S("f1") - 0.3
    op = window(t, a, b)
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Only the vertical height matters"),
         f'<line x1="930" y1="140" x2="930" y2="830" stroke="{NAVY}" stroke-opacity="0.15" stroke-width="3"/>']
    mg = f'{it("m")}{it("g")}'
    s.append(notes(t, [(S("g8", "On the left"), 175, "Lift straight up", 40, NAVY, "bold")]))
    s.append(notes(t, [(S("g8", "On the right"), 175, "Pull up the slope", 40, NAVY, "bold")], x=990))
    s.append(notes(t, [(S("g9", "Lifting"), 232, f"Big force {col(mg, GREEN)}, short distance {H_}", 32, NAVY, "normal")]))
    s.append(notes(t, [(S("g9", "Pulling"), 232, f"Small force {col(mg + ' ' + SIN, GREEN)}, long distance {D_}", 32, NAVY, "normal")], x=990))
    y0 = RH.P(H_S0, 0)[1]
    y1 = RH.P(H_S1, 0)[1]
    t0, t1 = S("g9", "Lifting"), S("g10", "same level")
    k = clamp((t - t0) / (t1 - t0))
    lo = fade(t, S("g8", "On the left"))
    # start and finish levels, across both panels
    s.append(dashed((100, y0), (1840, y0), "#9aa3b5", lo, 3))
    s.append(dashed((100, y1), (1840, y1), "#9aa3b5", fade(t, S("g8", "same height")), 3))
    # left: lift straight up
    bx, bw, bh = 560, 110, 66
    by = y0 + (y1 - y0) * k
    s.append(f'<line x1="140" y1="{y0}" x2="860" y2="{y0}" stroke="{INK}" stroke-width="4" opacity="{lo}"/>')
    if k > 0.01:
        s.append(dashed((bx - bw / 2 - 40, y0), (bx - bw / 2 - 40, by), ORANGE, 1, 5))
        s.append(label(bx - bw / 2 - 54, (y0 + by) / 2 + 14, H_, 38, ORANGE, "end"))
    s.append(f'<rect x="{bx - bw / 2}" y="{by - bh}" width="{bw}" height="{bh}" rx="16" fill="white" stroke="{PUR}" stroke-width="5" opacity="{lo}"/>')
    fo = fade(t, S("g9", "Lifting"))
    s.append(arrow(bx, by - bh, bx, by - bh - 170, GREEN, w=6, op=fo))
    s.append(text(bx + 16, by - bh - 120, col(mg, GREEN), 36, GREEN, op=fo))
    # right: pull up the slope
    sb = H_S0 + (H_S1 - H_S0) * k
    s.append(RH.svg(op=fade(t, S("g8", "On the right"))))
    if k > 0.01:
        s.append(RH.h_marker(H_S0, sb))
    s.append(RH.box(sb, op=fade(t, S("g8", "On the right"))))
    s.append(RH.force(sb, "T", fade(t, S("g9", "Pulling")), lab=col(mg + " " + SIN, GREEN), length=170 * RH.s, size=32, mid=True))
    if 0 < k < 1: s.append(RH.speed_lines(sb))
    # work bars fill as the height is gained
    yb = 900
    s.append(bar(240, yb, 560, [(560 * k, PUR)], fade(t, S("g9", "Lifting")), lab="Work done"))
    s.append(bar(1130, yb, 560, [(560 * k, PUR)], fade(t, S("g9", "Lifting")), lab="Work done"))
    vo = fade(t, S("g10", "same level"))
    s.append(text(240 + 572, yb + 25, f'{it("m")}{it("g")}{H_}', 32, PUR, op=vo, weight="bold"))
    s.append(text(1130 + 572, yb + 25, f'{it("m")}{it("g")}{H_}', 32, PUR, op=vo, weight="bold"))
    s.append(notes(t, [(S("g10", "Only"), 990, f"{col(mg, GREEN)} × {H_}  =  {col(mg + ' ' + SIN, GREEN)} × {D_}  =  {it('m')}{it('g')}{H_}", 36, NAVY, "bold")], x=500))
    s.append(pop(t, S("g10", "same level"), 930, 850, "same work!"))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ work done against friction
RF = Ramp(1000, 620, 800, 27)
F_S0, F_S1 = 170, 650

def scene_friction(t):
    a, b = S("f1") - 0.3, S("c1") - 0.3
    op = window(t, a, b)
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Work done against friction"), divider()]
    s.append(notes(t, [
        (S("f1", "friction"), 200, "On a rough slope, friction opposes the motion.", 34, NAVY, "normal"),
        (S("f2", "Friction stays"), 255, "Friction is constant, so the work done grows", 34, NAVY, "normal"),
        (S("f2", "grows steadily"), 300, "steadily with the distance moved.", 34, NAVY, "normal"),
    ]))
    mg = f'{it("m")}{it("g")}'
    s.append(working(t, [
        (S("f3", "R balances"), f"Resolve perpendicular:   {R_} = {col(mg, PUR)} {COS}", 38),
        (S("f4", "Friction equals"), f"Friction is limiting:   {FR} = {MU}{R_}", 38),
        (S("f4", "which is mu"), f"{FR} = {MU}{col(mg, PUR)} {COS}", 38),
    ], 395, 68))
    s.append(gold_box(t, S("f5", "The work done"), 76, 590, 830, 170,
                      ["Work done against friction", f"=  {MU}{R_} × {D_}  =  {MU}{it('m')}{it('g')} {COS} × {D_}"], 40))
    s.append(notes(t, [(S("f6", "For gravity"), 830, f"Gravity:   use the vertical height {H_}", 34, NAVY, "normal"),
                       (S("f6", "For friction"), 885, f"Friction:   use the full distance {col(D_, RED)}", 34, NAVY, "normal")]))
    keys = [(S("f2", "As the box"), F_S0, 1), (S("f2", "every metre"), F_S1, 1)]
    sb, _ = track(t, keys)
    s.append(RF.svg(rough=fade(t, S("f1", "rough"), 0.6)))
    s.append(RF.d_arrow(F_S0, sb, fade(t, S("f2", "As the box"), 0.3), ticks=4 if sb > F_S1 - 1 else 0))
    if moving(t, keys): s.append(RF.speed_lines(sb))
    s.append(RF.box(sb))
    s.append(RF.force(sb, "Fr", fade(t, S("f2", "As the box"))))
    s.append(RF.force(sb, "R", fade(t, S("f3", "normal reaction"))))
    s.append(RF.force(sb, "W", fade(t, S("f3", "Resolve"))))
    s.append(RF.components(sb, op_cos=fade(t, S("f3", "m g cos")), op_sin=0))
    # the friction work bar grows in equal steps with equal distances
    k = (sb - F_S0) / (F_S1 - F_S0)
    yb = 680
    bo = fade(t, S("f2", "As the box"))
    s.append(text(1000, yb - 16, "Work done against friction", 30, RED, op=bo, weight="bold"))
    s.append(bar(1000, yb, 700, [(700 * k, RED)], bo, h=36))
    for i in range(1, 4):
        if k >= i / 4:
            s.append(f'<line x1="{1000 + 700 * i / 4}" y1="{yb - 6}" x2="{1000 + 700 * i / 4}" y2="{yb + 42}" stroke="{GOLD}" stroke-width="5" opacity="{bo}"/>')
    s.append(pop(t, S("f6", "the whole way"), 1400, 820, "the whole distance!", size=40))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ both together
RC = Ramp(1000, 590, 800, 27)
C_S0, C_S1, C_S2 = 180, 330, 640
WG_FULL, WF_FULL = 360, 280       # 6g sin 27 : 0.4 x 6g cos 27, roughly

def scene_combined(t):
    a, b = S("c1") - 0.3, S("tips") - 0.3
    op = window(t, a, b)
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Pulling at a constant speed"), divider()]
    mg = f'{it("m")}{it("g")}'
    s.append(notes(t, [(S("c2", "Constant speed"), 200, "Constant speed: no acceleration,", 34, NAVY, "normal"),
                       (S("c2", "the forces along"), 250, "so the forces along the slope balance.", 34, NAVY, "normal")]))
    s.append(working(t, [
        (S("c2", "T equals"), f"{T_} = {FR} + {col(mg, PUR)} {SIN}", 42),
        (S("c3", "T multiplied"), f"{T_} × {D_} = {FR} × {D_} + {col(mg, PUR)} {SIN} × {D_}", 38),
        (S("c3", "mu m g d"), f"         = {col(MU + mg + 'd ' + COS, RED)} + {col(mg + 'd ' + SIN, PUR)}", 38),
        (S("c3", 0.97), f"         = {mg}{D_}({SIN} + {MU} {COS})", 38),
    ], 340, 78))
    s.append(notes(t, [(S("c4", "against friction"), 640, f"{col('against friction', RED, True)}  +  {col('against gravity', PUR, True)}", 34, NAVY, "normal")]))
    o5 = fade(t, S("c5", "T times d"), 0.5)
    if o5 > 0:
        s.append(f'<rect x="76" y="720" width="830" height="150" rx="16" fill="#fff6dd" stroke="{GOLD}" stroke-width="5" opacity="{o5}"/>')
        s.append(label(491, 815, f"{T_} × {D_}  =  {col(MU + it('R'), RED)} × {D_}  +  {col(it('m'), PUR)}{it('g')}{H_}", 52, NAVY, "middle", o5, "bold"))
    keys = [(S("c1", "pulls"), C_S0, 1), (S("c1", 1.0), C_S1, 1), (S("c4", "Watch the bars"), C_S1, 1), (S("c4", "added together"), C_S2, 1)]
    sb, _ = track(t, keys)
    s.append(RC.svg(rough=1))
    k = clamp((sb - C_S1) / (C_S2 - C_S1))
    s.append(RC.d_arrow(C_S1, sb, fade(t, S("c4", "Watch the bars"), 0.3)))
    if moving(t, keys): s.append(RC.speed_lines(sb))
    s.append(RC.box(sb))
    for kind, st in (("T", S("c1", "A force T")), ("Fr", S("c1", 0.4)), ("R", S("c1", 0.5)), ("W", S("c1", 0.6))):
        s.append(RC.force(sb, kind, fade(t, st)))
    bo = fade(t, S("c4", "against friction"))
    s.append(bar(1230, 650, 660, [(WG_FULL * k, PUR)], bo, lab="against gravity", labc=PUR))
    s.append(bar(1230, 695, 660, [(WF_FULL * k, RED)], bo, lab="against friction", labc=RED))
    s.append(bar(1230, 740, 660, [(WG_FULL * k, PUR), (WF_FULL * k, RED)], bo, outline=GREEN, lab=f"by {T_}", labc=GREEN))
    s.append(pop(t, S("c4", "added together"), 1560, 830, "the two added together!", size=40))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ the four steps
def scene_tips(t):
    a, b = S("tips") - 0.3, S("w0") - 0.4
    op = window(t, a, b)
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Solving problems on a ramp")]
    rows = [("Draw", "Draw a force diagram", f"Show {T_}, friction, {R_} and the weight {MG}."),
            ("Find sine", f"Find sin {A_} and cos {A_}", "Use a right-angled triangle and Pythagoras."),
            ("Resolve", f"Resolve perpendicular to find {R_}", f"{R_} = {col(it('m') + it('g'), PUR)} {COS}, then {FR} = {MU}{R_}"),
            ("Then use", "Gravity: height.   Friction: distance.", f"{it('m')}{it('g')}{H_}   and   {MU}{R_} × {D_}")]
    for i, (f, title, line) in enumerate(rows):
        o = ease(fade(t, S("tips", f), 0.5))
        if o <= 0: continue
        y = 150 + i * 215
        s.append(f'<g opacity="{o}" transform="translate({30 * (1 - o)} 0)"><rect x="80" y="{y}" width="1760" height="185" rx="20" fill="#dceaf7"/>'
                 f'<circle cx="170" cy="{y + 92}" r="52" fill="{GOLD}"/>'
                 + text(170, y + 112, str(i + 1), 56, "white", "middle", weight="bold")
                 + text(260, y + 80, NB(title), 46, NAVY, weight="bold")
                 + text(260, y + 140, NB(line), 34, NAVY) + '</g>')
        # small picture on the right of each step
        if i == 0:
            r = Ramp(1460, y + 165, 330, 26, bw=70, bh=42)
            pic = r.svg(rough=1) + r.box(170) + "".join(arrow(*a, *b, c, w=5) for a, b, c in (
                (r.at(170)["front"], r.P(170 + 35 + 70, 21), GREEN), (r.at(170)["rear"], r.P(170 - 35 - 60, 21), RED),
                (r.at(170)["top"], (r.at(170)["top"][0] + r.out[0] * 60, r.at(170)["top"][1] + r.out[1] * 60), BLUE),
                (r.at(170)["centre"], (r.at(170)["centre"][0], r.at(170)["centre"][1] + 70), PUR)))
            s.append(f'<g opacity="{o}">' + pic.replace('font-size="40"', 'font-size="24"') + '</g>')
        elif i == 1:
            s.append(tri_icon(1560, y + 150, 4, 3, 5, 36, o, 30))
        elif i == 2:
            r = Ramp(1480, y + 165, 300, 26, bw=70, bh=42)
            p = r.at(150)
            pic = (r.svg() + r.box(150) + arrow(*p["top"], p["top"][0] + r.out[0] * 70, p["top"][1] + r.out[1] * 70, BLUE, w=5)
                   + darrow(p["centre"], (p["centre"][0] + r.into[0] * 70, p["centre"][1] + r.into[1] * 70), PUR, 4))
            s.append(f'<g opacity="{o}">' + pic.replace('font-size="40"', 'font-size="24"') + '</g>')
        else:
            r = Ramp(1460, y + 165, 330, 26, bw=60, bh=38)
            pic = r.svg(rough=1) + r.box(75) + r.box(260) + r.h_marker(75, 260, lab=H_, size=30) + r.d_arrow(75, 260, k=60, lab=D_)
            s.append(f'<g opacity="{o}">' + pic.replace('font-size="40"', 'font-size="24"') + '</g>')
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ worked example
R1 = Ramp(1060, 548, 730, math.degrees(math.atan(8 / 15)))
E1_S0, E1_S1 = 300, 565
E1_FR, E1_WF, E1_WG = 20.75, 415.06, 553.41
E1_SCALE = 0.58              # px per joule

def scene_q1(t):
    a, b = S("w1") - 0.3, S("q2a") - 0.4
    op = window(t, a, b)
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Worked example: friction and gravity on a slope")]
    s.append(qblock(t, [
        (S("w1"), f"A rough plane is inclined at an angle {A_} to the"),
        (S("w1", "horizontal"), f"horizontal, where tan {A_} = 8/15. A box of mass 6 kg"),
        (S("w2", "is pulled"), "is pulled at a constant speed up a line of greatest"),
        (S("w2", "The coefficient"), "slope of the plane. The coefficient of friction"),
        (S("w2", "between"), "between the box and the plane is 0.4.")],
        ["a) Find the magnitude of the frictional force.",
         "The box moves 20 m up the plane. Find the work done",
         "b) against friction        c) against gravity."], S("w3")))
    mg = col(f'{it("m")}{it("g")}', PUR)
    s.append(working(t, [
        (S("wtri", "So sine alpha"), f"sin {A_} = 8/17,    cos {A_} = 15/17", 36),
        (S("wR", "R equals"), f"{R_} = 6{it('g')} {COS} = 6 × 9.8 × 15/17 = 51.88… N", 36),
        (S("wF", "Friction is 0.4"), f"a)  {FR} = {MU}{R_} = 0.4 × 51.88… = {col('20.8 N', BLUE, True)}", 36),
        (S("wwf", "so the work"), f"b)  {FR} × {D_} = 20.75… × 20 = {col('415 J', BLUE, True)}", 36),
        (S("wh", "The box rises"), f"{H_} = 20 {SIN} = 20 × 8/17 = 9.411… m", 36),
        (S("wwg", "m g h"), f"c)  {mg}{H_} = 6 × 9.8 × 9.411… = {col('553 J', BLUE, True)}", 36),
        (S("wtot", "415 plus"), f"Work done by {T_} = 415 + 553 = 968 J", 34),
    ], 590, 62))
    # motion: model the problem while it is read, then again for the work done
    rs = S("w3", 0.85)
    keys = [(S("w2", "is pulled"), E1_S0, 1), (S("w3", "Then the box"), E1_S1, 1), (rs, E1_S1, 1), (rs + 0.3, E1_S1, 0), (rs + 0.31, E1_S0, 0),
            (rs + 0.6, E1_S0, 1), (S("wmove", "watch"), E1_S0, 1), (S("wwf", "so the work"), E1_S1, 1)]
    sb, bo = track(t, keys)
    s.append(R1.svg(rough=1))
    s.append(tri_icon(1010, 232, 15, 8, 17, 12, window(t, S("wtri", "draw"), S("wmove"), 0.5), 26))
    second = t >= rs + 0.31
    if second:
        s.append(R1.h_marker(E1_S0, E1_S1, fade(t, S("wh", "height gained")), lab=H_ + col(" = 9.41 m", ORANGE) if t >= S("wh", "9.41") else H_,
                             size=34, inside=True))
        s.append(R1.d_arrow(E1_S0, sb, window(t, S("wmove", "watch"), S("wh", "For gravity"), 0.3) * bo, lab="20 m"))
    else:
        s.append(R1.d_arrow(E1_S0, sb, bo * (1 - fade(t, rs, 0.3))))
    if moving(t, keys): s.append(R1.speed_lines(sb, bo))
    s.append(R1.box(sb, "6 kg", bo))
    s.append(R1.force(sb, "T", bo))
    fr_lab = col(f'{it("F")}r = 20.8 N', RED) if t >= S("wF", "20.8") else "Friction"
    s.append(R1.force(sb, "Fr", bo, lab=fr_lab, size=32, length=100))
    r_lab = R_ + col(" = 51.88 N", BLUE) if t >= S("wR", "51.88") else R_
    s.append(R1.force(sb, "R", bo, lab=r_lab, size=32, length=85, align="end", lab_dx=-6, lab_dy=44))
    s.append(R1.force(sb, "W", bo, lab=col("6" + it("g"), PUR), length=85, align="start", lab_dx=12, lab_dy=-50))
    s.append(R1.components(sb, op_cos=bo * window(t, S("wR", "R equals"), S("wF"), 0.4), op_sin=bo * fade(t, S("wchk", "The component")), size=28))
    # work bars
    kf = clamp((sb - E1_S0) / (E1_S1 - E1_S0)) if second else 0
    kg = ease(clamp((t - S("wwg", "m g h")) / (S("wwg", "553") - S("wwg", "m g h"))))
    bo1 = fade(t, S("wmove", "watch"))
    s.append(bar(1150, 600, 600, [(E1_WF * E1_SCALE * kf, RED)], bo1, lab="against friction", labc=RED,
                 value="415 J" if t >= S("wwf", "415") else None, valc=RED))
    s.append(bar(1150, 640, 600, [(E1_WG * E1_SCALE * kg, PUR)], fade(t, S("wwg", "m g h")), lab="against gravity", labc=PUR,
                 value="553 J" if t >= S("wwg", "553") else None, valc=PUR))
    s.append(bar(1150, 680, 600, [(E1_WF * E1_SCALE, RED), (E1_WG * E1_SCALE, PUR)], fade(t, S("wtot", "both jobs")), outline=GREEN,
                 lab=f"by {T_}", labc=GREEN, value="968 J" if t >= S("wtot", "968") else None, valc=GREEN))
    s.append(caption(t, [
        (S("w1"), S("wtri"), "The problem", "A box is pulled up a rough slope at a constant speed."),
        (S("wtri"), S("wR"), "Step 1: Exact trig values", "tan α = 8/15, so use an 8, 15, 17 triangle."),
        (S("wR"), S("wF"), "Step 2: Resolve perpendicular", "R balances the component 6g cos α."),
        (S("wF"), S("wmove"), "Step 3: Friction is limiting", "The box is moving, so Fr = μR."),
        (S("wmove"), S("wh"), "Step 4: Work done against friction", "Friction × the full distance along the slope"),
        (S("wh"), S("wtot"), "Step 5: Work done against gravity", "Weight × the vertical height gained"),
        (S("wtot"), S("wchk"), "Total work done by T", "Work against friction + work against gravity"),
        (S("wchk"), S("q2a"), "Check", "6g sin α ≈ 27.7 N is bigger than Fr = 20.8 N."),
    ]))
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ your turn
R2 = Ramp(1060, 578, 560, math.degrees(math.atan(3 / 4)))
E2_S0, E2_S1 = 190, 520
E2_SCALE = 11.6              # px per joule

def scene_q2(t):
    a, b = S("q2b") - 0.3, S("cta") - 0.4
    op = window(t, a, b)
    if op <= 0: return ""
    s = [f'<g opacity="{op}">', header("Your turn: finding the coefficient of friction")]
    s.append(qblock(t, [
        (S("q2b"), "A rough surface is inclined at an angle arctan 3/4 to"),
        (S("q2b", "the horizontal"), "the horizontal. A parcel of mass 1.5 kg is pulled 4 m"),
        (S("q2b", "at a constant"), "at a constant speed up the surface by a force acting"),
        (S("q2b", "along a line"), "along a line of greatest slope. The only resistances"),
        (S("q2c"), "to the motion are friction and gravity. The work done"),
        (S("q2c", "by the force"), "by the force is 50 J.")],
        ["Find the coefficient of friction between the parcel",
         "and the surface."], S("q2d")))
    mg = col(f'{it("m")}{it("g")}', PUR)
    s.append(working(t, [
        (S("s2a", "Sine alpha"), f"sin {A_} = 3/5,    cos {A_} = 4/5", 34),
        (S("s2b", "it rises"), f"{H_} = 4 × 3/5 = 2.4 m", 34),
        (S("s2c", "m g h"), f"Against gravity:   {mg}{H_} = 1.5 × 9.8 × 2.4 = 35.28 J", 34),
        (S("s2d", "so the other"), f"Against friction:   50 − 35.28 = {col('14.72 J', RED, True)}", 34),
        (S("s2e", "R is"), f"{R_} = 1.5{it('g')} {COS} = 1.5 × 9.8 × 4/5 = 11.76 N", 34),
        (S("s2f", "So 14.72"), f"{MU}{R_} × {D_}:   14.72 = {MU} × 11.76 × 4 = 47.04{MU}", 34),
    ], 580, 58))
    s.append(answer_box(t, S("s2g", "mu is"), 965, 420, f"{MU} = 0.313  (3 s.f.)", 40))
    # motion while the question is read: the force does 50 J of work
    keys = [(S("q2b", "is pulled"), E2_S0, 1), (S("q2c", "50 joules"), E2_S1, 1)]
    sb, _ = track(t, keys)
    s.append(R2.svg(rough=1))
    s.append(tri_icon(1010, 262, 4, 3, 5, 40, fade(t, S("s2a", "so this is")), 28))
    s.append(R2.h_marker(E2_S0, E2_S1, fade(t, S("s2b", "it rises")), lab=H_ + col(" = 2.4 m", ORANGE) if t >= S("s2b", "2.4") else H_,
                         size=34, inside=True))
    s.append(R2.d_arrow(E2_S0, sb, window(t, S("q2b", "is pulled"), S("s2a", "so this is"), 0.3), lab="4 m"))
    if moving(t, keys): s.append(R2.speed_lines(sb))
    s.append(R2.box(sb, "1.5 kg"))
    s.append(R2.force(sb, "T", 1, length=100))
    fr_lab = col(f'{it("F")}r = {MU}{it("R")}', RED) if t >= S("s2f", "mu R") else "Friction"
    s.append(R2.force(sb, "Fr", 1, lab=fr_lab, size=32))
    s.append(R2.force(sb, "R", 1, lab=R_ + col(" = 11.76 N", BLUE) if t >= S("s2e", "11.76") else R_, size=32, length=85,
                      align="end", lab_dx=-6, lab_dy=26))
    s.append(R2.force(sb, "W", 1, lab=col("1.5" + it("g"), PUR), length=85, align="start", lab_dx=12, lab_dy=-50))
    # the 50 J bar fills during the motion, then is shared between gravity and friction
    k = clamp((sb - E2_S0) / (E2_S1 - E2_S0))
    split = ease(clamp((t - S("s2d", "Gravity takes")) / 1.0))
    wg, wf = 35.28 * E2_SCALE, 14.72 * E2_SCALE
    if split <= 0:
        s.append(bar(1180, 620, 580, [(580 * k, GREEN)], fade(t, S("q2b", "is pulled")), lab="by the force", labc=GREEN,
                     value="50 J" if k >= 1 else None, valc=GREEN))
    else:
        s.append(bar(1180, 620, 580, [(wg, PUR), (wf, RED)], 1, outline=GREEN, lab="by the force", labc=GREEN))
        s.append(text(1180, 685, "35.28 J gravity", 28, PUR, op=split, weight="bold"))
        s.append(label(1180 + 580, 685, "14.72 J friction", 28, RED, "end", split, "bold"))
    if t >= S("s2c", "m g h") and split <= 0:
        s.append(f'<rect x="1180" y="620" width="{wg}" height="30" rx="6" fill="{PUR}" opacity="{0.85 * fade(t, S("s2c", "m g h"))}"/>')
    s.append(pop(t, S("s2d", "14.72"), 1730, 470, "shared out!", size=36))
    s.append(caption(t, [
        (S("q2b"), S("q2p"), "Your turn", "Find μ from the work done by the force."),
        (S("s2a"), S("s2b"), "Step 1: Exact trig values", "tan α = 3/4, so use a 3, 4, 5 triangle."),
        (S("s2b"), S("s2c"), "Step 2: Height gained", "h = d sin α"),
        (S("s2c"), S("s2d"), "Step 3: Work done against gravity", "Weight × the vertical height"),
        (S("s2d"), S("s2e"), "Step 4: Share out the 50 J", "Whatever gravity doesn't take goes to friction."),
        (S("s2e"), S("s2f"), "Step 5: Resolve perpendicular", "R = 1.5g cos α"),
        (S("s2f"), S("s2chk"), "Step 6: Work done against friction", "μR × d = 14.72, then solve for μ."),
    ]))
    mo = window(t, S("s2chk", "A common mistake"), S("cta") - 0.4, 0.5)
    if mo > 0:
        s.append(f'<g opacity="{mo}"><rect x="990" y="720" width="850" height="250" rx="14" fill="#fdecea" stroke="{RED}" stroke-width="4"/>'
                 + text(1020, 778, "Common mistake: using all 50 J for friction", 34, RED, weight="bold")
                 + text(1020, 850, NB(f"50 = {MU} × 11.76 × 4   →   {MU} = 1.06"), 40, NAVY, op=fade(t, S("s2chk", "That gives")))
                 + text(1020, 920, "Bigger than 1: take away the gravity part first!", 32, RED, op=fade(t, S("s2chk", "bigger than 1"))) + '</g>')
    s.append('</g>')
    return "".join(s)

# ------------------------------------------------------------------ frame
def frame_svg(t):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         DEFS, f'<rect width="{W}" height="{H}" fill="white"/>']
    for sc in (scene_work, scene_gravity, scene_height, scene_friction, scene_combined, scene_tips, scene_q1, scene_q2):
        s.append(sc(t))
    if S("wd1") - 0.7 <= t < S("cta"):
        s.append(text(1840, 1045, "mr-mathematics.com", 28, LOGO, "end", weight="bold"))
    s.append(pause_banner(t, "q2p", "q2r"))
    s.append(section_card(t, "w0", "w1", [("Worked", "white"), ("example", "#ffc94d")], "Pulling a box up a rough slope"))
    s.append(section_card(t, "q2a", "q2b", [("Your", "white"), ("turn", "#ffc94d")], "Finding the coefficient of friction"))
    s.append(cta_card(t))
    s.append(scene_open(t))
    s.append('</svg>')
    return "".join(s)

def render(i):
    cairosvg.svg2png(bytestring=frame_svg(i / FPS).encode(), write_to=f"{OUT}/f{i:05d}.png", output_width=W, output_height=H)
    return i

def encode():
    """frames (and ramps_audio.mp3 if it is there) -> ramps.mp4"""
    cmd = ["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{OUT}/f%05d.png"]
    audio = HERE + "/ramps_audio.mp3"
    if os.path.exists(audio):
        cmd += ["-i", audio, "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", HERE + "/ramps.mp4"]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        for tt in map(float, sys.argv[2:]):
            cairosvg.svg2png(bytestring=frame_svg(tt).encode(), write_to=f"{HERE}/rtest_{tt:06.1f}.png", output_width=W, output_height=H)
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == "cues":
        for k, v in C.items(): print(f"{v[0]:7.2f} {v[1]:5.2f} {k}")
        print("DUR", DUR); sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == "encode":
        encode(); sys.exit()
    for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
    n = int(DUR * FPS)
    with Pool(os.cpu_count() or 2) as p:
        for _ in p.imap_unordered(render, range(n), chunksize=20): pass
    print("frames done", n)
