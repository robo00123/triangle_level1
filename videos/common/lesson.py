"""Building blocks shared by the Mr Mathematics lesson videos: cue timing, text helpers, captions, working rows,
answer boxes, work bars, the pause banner, section cards and the call to action. Every video draws with the
colours and helpers in make_video.py, so they all look the same."""
import json, math, os, re
from PIL import ImageFont
from make_video import arrow, arrowhead, text, it, col, clamp, fade, ease, card, NAVY, GOLD, W, H

PUR = "#6a2c91"
LOGO = "#2b0f52"
ORANGE = "#ff7a1a"
INK = "#111"

# ------------------------------------------------------------------ timing
def window(t, a, b, f=0.5):
    return fade(t, a, f) * (1 - fade(t, b, f))

class Cues:
    """Times in the narration. Reads the cue file written by sync.py, or estimates from the speaking rate.
    S(key) is the start of a script line, S(key, 0.5) halfway through its words, and S(key, "phrase") the moment
    the narrator starts saying that phrase."""
    def __init__(self, script, path):
        self.words = {}
        if os.path.exists(path):
            c = json.load(open(path))
            self.dur = c.pop("_end")[0]
            self.words = c.pop("_words", {})
            self.c = {k: tuple(v) for k, v in c.items()}
        else:
            self.c, self.dur = script.estimated_cues()
            self.dur += 1.0
        norm = lambda w: re.sub(r"[^\w.']", "", w.lower()).strip(".'")
        self.norm = norm
        self.line_words = {k: [norm(w) for w in line.split()] for k, line in script.SCRIPT}

    def index(self, k, phrase):
        p, ws = [self.norm(w) for w in phrase.split()], self.line_words[k]
        for i in range(len(ws) - len(p) + 1):
            if ws[i:i + len(p)] == p:
                return i
        raise KeyError(f"'{phrase}' is not in script line '{k}'")

    def S(self, k, f=0.0):
        s, d = self.c[k]
        n = len(self.line_words[k])
        if isinstance(f, str):
            f = self.index(k, f) / n
        ws = self.words.get(k)
        if not ws:
            return s + f * d
        pos = clamp(f) * n
        i = min(int(pos), n - 1)
        return ws[i] + (pos - i) * (ws[i + 1] - ws[i])

# ------------------------------------------------------------------ text
NB = lambda x: x.replace('  ', '  ')
_FONTS = {}

def tw(inner, size, bold=False):
    """width of rich text in Liberation Sans, so text with tspans can be centred or right aligned"""
    plain = re.sub(r"<[^>]+>", "", inner).replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    key = (size, bold)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf" % ("Bold" if bold else "Regular"), size)
    return _FONTS[key].getlength(plain)

def label(x, y, inner, size, c, align="start", op=1.0, weight="normal"):
    w = tw(inner, size, weight == "bold")
    x0 = x if align == "start" else x - w / 2 if align == "middle" else x - w
    return text(x0, y, inner, size, c, "start", op, weight)

def flabel(E, d, inner, size, c, op=1.0, gap=14, dx=0, dy=0, align=None):
    """label just beyond the end E of an arrow pointing in direction d"""
    x, y = E[0] + d[0] * gap + dx, E[1] + d[1] * gap + dy
    align = align or ("start" if d[0] > 0.35 else "end" if d[0] < -0.35 else "middle")
    if d[1] > 0.35: y += size * 0.8
    elif d[1] < -0.35: y -= 4
    else: y += size * 0.35
    return label(x, y, inner, size, c, align, op)

# ------------------------------------------------------------------ page furniture
def header(title):
    return (text(80, 80, title, 44, NAVY, weight="bold")
            + f'<line x1="80" y1="105" x2="1840" y2="105" stroke="{NAVY}" stroke-opacity="0.15" stroke-width="3"/>')

def divider(y1=1000):
    return f'<line x1="930" y1="140" x2="930" y2="{y1}" stroke="{NAVY}" stroke-opacity="0.15" stroke-width="3"/>'

def footer():
    return text(1840, 1045, "mr-mathematics.com", 28, LOGO, "end", weight="bold")

def caption(t, steps):
    for a, b, title, line in steps:
        if a <= t < b + 0.4:
            op = fade(t, a, 0.4) * (1 - fade(t, b, 0.4))
            return (f'<g opacity="{op}"><rect x="990" y="720" width="850" height="140" rx="14" fill="#dceaf7"/>'
                    + text(1020, 775, title, 36, NAVY, weight="bold") + text(1020, 830, line, 29, NAVY) + '</g>')
    return ""

def notes(t, items, x=80):
    s = []
    for start, y, inner, size, c, wgt in items:
        o = ease(fade(t, start, 0.5))
        if o > 0:
            s.append(f'<g transform="translate(0,{14 * (1 - o)})">' + text(x, y, NB(inner), size, c, op=o, weight=wgt) + '</g>')
    return "".join(s)

def working(t, rows, y0, step, x=90):
    s = []
    for i, (st, inner, size) in enumerate(rows):
        e = ease(fade(t, st, 0.5))
        if e > 0:
            s.append(f'<g transform="translate(0,{18 * (1 - e)})">' + text(x, y0 + i * step, NB(inner), size, NAVY, op=e) + '</g>')
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

def answer_box(t, start, y, w, inner, size=40, x=76):
    o = fade(t, start, 0.5)
    if o <= 0: return ""
    return (f'<rect x="{x}" y="{y - size - 14}" width="{w}" height="{size + 34}" rx="12" fill="#fff6dd" stroke="{GOLD}" stroke-width="5" opacity="{o}"/>'
            + text(x + 16, y, NB(inner), size, NAVY, op=o))

def pop(t, t0, x, y, txt, dur=2.2, size=46):
    op = window(t, t0, t0 + dur, 0.3)
    if op <= 0: return ""
    sc = 1 + 0.25 * (1 - ease(clamp((t - t0) / 0.35)))
    return (f'<g opacity="{op}" transform="translate({x} {y}) scale({sc}) translate({-x} {-y})">'
            + text(x, y, txt, size, GOLD, "middle", 1, "bold") + '</g>')

def mistake(t, a, b, title, wrong, why, t_wrong, t_why, y=720, h=250):
    op = window(t, a, b, 0.5)
    if op <= 0: return ""
    return (f'<g opacity="{op}"><rect x="990" y="{y}" width="850" height="{h}" rx="14" fill="#fdecea" stroke="#d32f2f" stroke-width="4"/>'
            + text(1020, y + 58, title, 34, "#d32f2f", weight="bold")
            + text(1020, y + 130, NB(wrong), 40, NAVY, op=fade(t, t_wrong))
            + text(1020, y + 200, why, 32, "#d32f2f", op=fade(t, t_why)) + '</g>')

def pause_banner(t, t_pause, t_ready, t_end):
    op = window(t, t_pause, t_end + 0.2, 0.5)
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
    if t >= t_ready:
        ro = fade(t, t_ready, 0.3)
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="#2b0f52" opacity="{ro}"/>')
        s.append(f'<text x="{x + w/2}" y="{y + h/2 + 22}" font-family="Montserrat" font-weight="800" font-size="62" fill="#ffc94d" text-anchor="middle" opacity="{ro}">Let\'s go through it</text>')
    s.append('</g>')
    return "".join(s)

def section_card(t, a, b, lines, subt):
    op = window(t, a, b, 0.4)
    return card(lines, subt, op) if op > 0 else ""

def cta_card(t, start, t_visit, t_pill):
    op = fade(t, start, 0.6)
    if op <= 0: return ""
    s = [f'<g opacity="{op}"><rect width="{W}" height="{H}" fill="url(#bg)"/>']
    for x in range(0, W + 1, 60):
        s.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="white" stroke-opacity="0.05"/>')
    for y in range(0, H + 1, 60):
        s.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="white" stroke-opacity="0.05"/>')
    s.append(f'<text x="{W/2}" y="330" font-family="Montserrat" font-weight="800" font-size="96" fill="white" text-anchor="middle">Full lesson and</text>')
    s.append(f'<text x="{W/2}" y="440" font-family="Montserrat" font-weight="800" font-size="96" fill="#ffc94d" text-anchor="middle">worksheet</text>')
    uo = fade(t, t_visit)
    s.append(f'<text x="{W/2}" y="590" font-family="Montserrat" font-weight="600" font-size="44" fill="white" fill-opacity="0.85" text-anchor="middle" opacity="{uo}">Visit</text>')
    s.append(f'<text x="{W/2}" y="680" font-family="Montserrat" font-weight="800" font-size="72" fill="white" text-anchor="middle" opacity="{uo}">mr-mathematics.com</text>')
    lo = fade(t, t_pill)
    bob = 12 * math.sin(2 * math.pi * 1.2 * t)
    s.append(f'<g opacity="{lo}"><rect x="{W/2 - 460}" y="770" width="920" height="96" rx="48" fill="#ffc94d"/>'
             f'<text x="{W/2}" y="832" font-family="Montserrat" font-weight="700" font-size="42" fill="#2b0f52" text-anchor="middle">Worksheet link in the description below</text>'
             f'<polygon points="{W/2 - 44},{910 + bob} {W/2 + 44},{910 + bob} {W/2},{965 + bob}" fill="#ffc94d"/></g>')
    s.append('</g>')
    return "".join(s)

def title_image(t, img64, end):
    """the lesson's title slide, slowly zooming, until it fades at `end`"""
    op = 1 - fade(t, end, 0.6)
    if op <= 0: return ""
    sc = 1.0 + 0.02 * ease(clamp(t / max(1.0, end)))
    return (f'<g opacity="{op}"><rect width="{W}" height="{H}" fill="white"/>'
            f'<g transform="translate({W/2} {H/2}) scale({sc}) translate({-W/2} {-H/2})">'
            f'<image x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid meet" '
            f'href="data:image/png;base64,{img64}" xlink:href="data:image/png;base64,{img64}"/></g></g>')

# ------------------------------------------------------------------ drawing
def dashed(p0, p1, c, op=1.0, w=4):
    if op <= 0: return ""
    return f'<line x1="{p0[0]}" y1="{p0[1]}" x2="{p1[0]}" y2="{p1[1]}" stroke="{c}" stroke-width="{w}" stroke-dasharray="10,8" opacity="{op}"/>'

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

def moving(t, keys):
    for (t0, s0, _), (t1, s1, _) in zip(keys, keys[1:]):
        if t0 <= t < t1 and abs(s1 - s0) > 1 and t1 - t0 > 0.4:
            return True
    return False

def bar(x, y, wfull, segs, op=1.0, h=30, outline=None, lab=None, labc=NAVY, value=None, valc=NAVY, lab_size=26):
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
        s.append(label(x - 14, y + h * 0.5 + 9, lab, lab_size, labc, "end"))
    if value:
        s.append(text(xx + 12, y + h * 0.5 + 10, value, 28, valc, weight="bold"))
    s.append('</g>')
    return "".join(s)
