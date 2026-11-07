"""Tampilan situs: palet, CSS, dan potongan HTML/SVG.

Modul ini sengaja tidak mengimpor Streamlit supaya bagian visualnya bisa diuji
sendiri. Semua fungsi mengembalikan string HTML; ui.html() yang menampilkannya.
"""
import math
import random
import re

FONTS = (
    "https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700"
    "&family=Playfair+Display:wght@600;700&display=swap"
)


def squash(s: str) -> str:
    """Jadikan satu baris. Baris kosong akan memutus blok HTML di parser markdown."""
    return re.sub(r"\s*\n\s*", " ", s).strip()


# --------------------------------------------------------------------------- CSS
CSS = """
@import url('%FONTS%');
:root{--bg:#1b1815;--panel:#251d16;--panel2:#2f241b;--line:rgba(233,184,115,.28);
--gold:#e9b873;--gold-d:#c98a3a;--tan:#ecc994;--tx:#f1e8dc;--mu:#b8a995;--cream:#f3e4cf;--ink:#2a1d12}
.stApp{background:radial-gradient(900px 480px at 88% -6%,rgba(201,138,58,.20),transparent 62%),
radial-gradient(700px 420px at -8% 38%,rgba(201,138,58,.08),transparent 60%),var(--bg)}
html,body,[class*="st-"],.stApp{font-family:'Hanken Grotesk',system-ui,sans-serif}
[data-testid="stHeader"]{background:rgba(27,24,21,.84);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
#MainMenu,footer{visibility:hidden}
.block-container{max-width:1180px;padding-top:2.4rem;padding-bottom:4.5rem}

.gx-kicker{font:600 .78rem/1 'Hanken Grotesk',sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);margin:0 0 1rem}
.gx-h1{font-family:'Playfair Display',Georgia,serif;font-weight:700;font-size:clamp(2.1rem,4.4vw,3.45rem);line-height:1.1;color:var(--tan);margin:0 0 1.1rem}
.gx-h2{font-family:'Playfair Display',Georgia,serif;font-weight:600;font-size:clamp(1.55rem,2.6vw,2.1rem);line-height:1.2;color:var(--tan);margin:0 0 .9rem}
.gx-h2.rule{display:flex;align-items:center;gap:16px}
.gx-h2.rule:after{content:"";flex:0 0 64px;height:1px;background:linear-gradient(90deg,var(--gold),transparent)}
.gx-sec{margin:4.6rem 0 1.5rem}
.gx-lead{color:var(--tx);opacity:.88;max-width:54ch;font-size:1.06rem;line-height:1.7;margin:0 0 1.6rem}
.gx-note{color:var(--mu);font-size:.88rem;line-height:1.55;margin:.9rem 0 0}
.gx-art{width:100%;height:auto;display:block}

.gx-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:20px}
.gx-card{margin:0;display:flex;flex-direction:column;border-radius:22px;overflow:hidden;border:1px solid var(--line);background:var(--panel);box-shadow:0 22px 44px -26px rgba(0,0,0,.9)}
.gx-card svg{display:block;width:100%;height:auto}
.gx-cap{flex:1;background:var(--cream);color:var(--ink);padding:.85rem 1.1rem 1.05rem;display:grid;grid-template-columns:1fr auto;gap:2px 12px;align-items:start}
.gx-cap .t{font-weight:700;font-size:1.02rem}
.gx-cap .d{grid-column:1;font-size:.86rem;line-height:1.45;opacity:.78}
.gx-cap .n{grid-row:1 / span 2;grid-column:2;width:34px;height:34px;border-radius:50%;display:grid;place-items:center;
font:700 .8rem 'Hanken Grotesk',system-ui,sans-serif;color:var(--ink);background:linear-gradient(180deg,#f4cb8b,#d89c4b)}

.gx-sieve{border-radius:26px 150px 150px 26px;overflow:hidden;border:1px solid var(--line);background:#211812}
.gx-sieve svg{display:block;width:100%;height:auto}
.gx-strip{display:flex;flex-wrap:wrap;border:1px solid var(--line);border-radius:30px;padding:1.3rem 0;
background:linear-gradient(180deg,#2b2017,#211812);margin-top:3.4rem}
.gx-strip>div{flex:1 1 190px;padding:.5rem 1.3rem;border-left:1px solid var(--line)}
.gx-strip>div:first-child{border-left:0}
.gx-strip svg{width:34px;height:34px;display:block;margin-bottom:.6rem}
.gx-strip .t{font-weight:700;color:var(--tx);font-size:.98rem}
.gx-strip .d{color:var(--mu);font-size:.85rem;line-height:1.45;margin-top:.2rem}

.gx-two{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}
.gx-panel{border:1px solid var(--line);border-radius:22px;padding:1.5rem 1.6rem;background:linear-gradient(170deg,#2c2118,#211812)}
.gx-panel h3{font:700 1.02rem 'Hanken Grotesk',system-ui,sans-serif;color:var(--tx);margin:0 0 .9rem}
.gx-chips{display:flex;flex-wrap:wrap;gap:8px}
.gx-chips span{border:1px solid var(--line);border-radius:999px;padding:.32rem .8rem;font-size:.86rem;color:var(--tan);background:rgba(233,184,115,.07)}

.gx-steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:20px}
.gx-step{border:1px solid var(--line);border-radius:22px;padding:1.4rem 1.5rem 1.5rem;background:linear-gradient(170deg,#2c2118,#211812)}
.gx-step .n{font-family:'Playfair Display',serif;font-weight:700;font-size:2.4rem;line-height:1;color:transparent;-webkit-text-stroke:1px var(--gold);font-variant-numeric:lining-nums}
.gx-step h3{font:700 1.08rem 'Hanken Grotesk',system-ui,sans-serif;color:var(--tx);margin:.7rem 0 .4rem}
.gx-step p{color:var(--mu);font-size:.93rem;line-height:1.6;margin:0}
.gx-form{font:500 .9rem/1.9 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:var(--tx)}
.gx-form i{font-style:normal;color:var(--gold);display:inline-block;min-width:3.4rem}
.gx-dl{display:grid;grid-template-columns:max-content 1fr;gap:.75rem 1.4rem;margin:0}
.gx-dl dt{color:var(--gold);font-weight:600;font-size:.9rem}
.gx-dl dd{margin:0;color:var(--tx);opacity:.9;font-size:.95rem;line-height:1.55}
.gx-p{color:var(--tx);opacity:.88;line-height:1.75;font-size:1.02rem;margin:0 0 1rem;max-width:62ch}

[class*="st-key-cta-"] a,.st-key-band a,.st-key-split a{border-radius:999px!important;padding:.74rem 1.55rem!important;
font-weight:700!important;border:1px solid var(--gold)!important;transition:filter .15s,transform .15s}
[class*="st-key-cta-"] a:hover,.st-key-band a:hover,.st-key-split a:hover{filter:brightness(1.1);transform:translateY(-1px)}
.st-key-cta-main a,.st-key-band a{background:linear-gradient(180deg,#f4cb8b,#d89c4b)!important;border-color:transparent!important;
box-shadow:0 12px 30px -12px rgba(233,184,115,.7)}
.st-key-cta-main a p,.st-key-band a p{color:#20160c!important}
.st-key-cta-alt a,.st-key-split a{background:transparent!important}
.st-key-cta-alt a p,.st-key-split a p{color:var(--tx)!important}
.st-key-band{border:1px solid var(--line);border-radius:30px;padding:1.6rem 2rem;margin-top:3.4rem;
background:linear-gradient(110deg,#33261b,#221a13)}
.st-key-calc iframe{border:1px solid var(--line);border-radius:20px;background:#1b1815}
@media(max-width:640px){.gx-sieve{border-radius:22px 80px 80px 22px}.st-key-band{padding:1.2rem 1.2rem}}
""".replace("%FONTS%", FONTS)

# ----------------------------------------------------------------- data gradasi
SIEVES = [19, 12.5, 9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.15, 0.075]
MN = [100, 90, 77, 53, 33, 21, 14, 9, 6, 4]          # AC-WC, Spesifikasi Umum 2018
MX = [100, 100, 90, 69, 53, 40, 30, 22, 15, 9]
BLEND = [100, 95.5, 82, 60.5, 44, 31.5, 22.5, 15.5, 10.5, 6.5]
_LO, _HI = math.log10(0.075), math.log10(19)


def _xy(box, d, p):
    x0, y0, x1, y1 = box
    return (x0 + (math.log10(d) - _LO) / (_HI - _LO) * (x1 - x0), y1 - p / 100 * (y1 - y0))


def _path(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def _curves(box):
    hi = [_xy(box, d, p) for d, p in zip(SIEVES, MX)]
    lo = [_xy(box, d, p) for d, p in zip(SIEVES, MN)]
    mid = [_xy(box, d, p) for d, p in zip(SIEVES, BLEND)]
    env = _path(hi) + " L" + " L".join(f"{x:.1f} {y:.1f}" for x, y in reversed(lo)) + "Z"
    return env, _path(hi), _path(lo), _path(mid), mid


# --------------------------------------------------------------------- partikel
SAND = ["#d8bd93", "#c9a877", "#b9915f", "#e0c7a1", "#a98558"]
PEBBLE = ["#8a7762", "#6f6154", "#9b8870", "#7d6c5b", "#5e544b"]
STONE = ["#5d6167", "#70747a", "#4b4f55", "#7a7d82", "#63676d"]


def _pile(rnd, n, rmin, rmax, cols, cx, cy, sx, sy, clip=None, stroke=False):
    out = []
    for _ in range(n):
        r = rnd.uniform(rmin, rmax)
        x, y = rnd.gauss(cx, sx), rnd.gauss(cy, sy)
        if clip and math.hypot(x - clip[0], y - clip[1]) > clip[2] + r * .5:
            continue
        st = ' stroke="rgba(0,0,0,.35)" stroke-width="1"' if stroke else ""
        out.append((y, f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{rnd.choice(cols)}"{st}/>'))
    out.sort(key=lambda t: t[0])
    return "".join(s for _, s in out)


def _ring(cx, cy, r, gid):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#{gid})" stroke-width="2.4"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r + 10}" fill="none" stroke="#e9b873" stroke-opacity=".28" stroke-width="1"/>')


def hero_art() -> str:
    rnd = random.Random(11)
    ax, ay, ar = 232, 266, 196
    bx, by, br = 442, 168, 132
    sand = _pile(rnd, 900, 1.5, 3.6, SAND, ax, ay, ar * .55, ar * .55, clip=(ax, ay, ar))
    peb = _pile(rnd, 190, 4.5, 9.5, PEBBLE, ax + 20, ay + 70, ar * .38, ar * .30, clip=(ax, ay, ar))
    stn = _pile(rnd, 34, 10, 19, STONE, ax + 70, ay + 85, ar * .36, ar * .28, clip=(ax, ay, ar), stroke=True)
    box = (bx - 100, by - 56, bx + 104, by + 62)
    env, hi, lo, mid, pts = _curves(box)
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="#f6ead8"/>' for x, y in pts)
    grid = "".join(f'<line x1="{box[0]}" x2="{box[2]}" y1="{box[3] - p / 100 * (box[3] - box[1]):.1f}" '
                   f'y2="{box[3] - p / 100 * (box[3] - box[1]):.1f}" stroke="#e9b873" stroke-opacity=".14"/>'
                   for p in (0, 25, 50, 75, 100))
    return f"""
<svg class="gx-art" viewBox="0 0 620 480" role="img" aria-label="Ilustrasi tumpukan agregat dan kurva gradasi AC-WC">
<defs>
<clipPath id="gxA"><circle cx="{ax}" cy="{ay}" r="{ar}"/></clipPath>
<clipPath id="gxB"><circle cx="{bx}" cy="{by}" r="{br}"/></clipPath>
<linearGradient id="gxRing" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4cb8b"/><stop offset="1" stop-color="#a8702f"/></linearGradient>
<linearGradient id="gxFade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b1815" stop-opacity=".78"/><stop offset=".65" stop-color="#1b1815" stop-opacity="0"/></linearGradient>
<radialGradient id="gxVig" cx=".5" cy=".5" r=".5"><stop offset=".7" stop-color="#1b1815" stop-opacity="0"/><stop offset="1" stop-color="#1b1815" stop-opacity=".55"/></radialGradient>
</defs>
<path d="M20 130 C 150 20, 360 -10, 600 60" fill="none" stroke="#e9b873" stroke-opacity=".3" stroke-width="1.2"/>
<g clip-path="url(#gxA)"><rect x="{ax - ar}" y="{ay - ar}" width="{2 * ar}" height="{2 * ar}" fill="#6f5638"/>{sand}{peb}{stn}
<rect x="{ax - ar}" y="{ay - ar}" width="{2 * ar}" height="{2 * ar}" fill="url(#gxFade)"/>
<rect x="{ax - ar}" y="{ay - ar}" width="{2 * ar}" height="{2 * ar}" fill="url(#gxVig)"/></g>
{_ring(ax, ay, ar, "gxRing")}
<circle cx="{bx}" cy="{by}" r="{br + 14}" fill="#1b1815"/>
<g clip-path="url(#gxB)"><circle cx="{bx}" cy="{by}" r="{br}" fill="#1d1712"/>{grid}
<path d="{env}" fill="#e9b873" fill-opacity=".2"/>
<path d="{hi}" fill="none" stroke="#e9b873" stroke-width="1.6"/><path d="{lo}" fill="none" stroke="#e9b873" stroke-width="1.6"/>
<path d="{mid}" fill="none" stroke="#f6ead8" stroke-width="3" stroke-linejoin="round"/>{dots}
<text x="{bx - 76}" y="{by - 72}" font-family="Playfair Display,Georgia,serif" font-weight="700" font-size="18" fill="#ecc994">AC-WC</text>
<text x="{box[0]}" y="{box[3] + 20}" font-family="Hanken Grotesk,sans-serif" font-size="10.5" fill="#b8a995">0,075</text>
<text x="{box[2]}" y="{box[3] + 20}" text-anchor="end" font-family="Hanken Grotesk,sans-serif" font-size="10.5" fill="#b8a995">19 mm</text></g>
{_ring(bx, by, br, "gxRing")}
</svg>"""


def sieve_art() -> str:
    rnd = random.Random(5)
    trays = [(24, "19 mm", (8, 12), STONE), (102, "4,75 mm", (4.5, 6.5), PEBBLE),
             (180, "0,6 mm", (2.4, 3.6), SAND), (258, "0,075 mm", (1.4, 2.2), SAND)]
    s = ""
    for y, label, (r0, r1), cols in trays:
        s += (f'<path d="M112 {y} L128 {y + 56} L392 {y + 56} L408 {y} Z" fill="#3a2c20" stroke="#e9b873" stroke-opacity=".55"/>'
              f'<line x1="128" x2="392" y1="{y + 56}" y2="{y + 56}" stroke="#ecc994" stroke-width="2" stroke-dasharray="2 4"/>')
        n = int(260 / (r0 * 1.5))
        s += _pile(rnd, n, r0 * .8, r1, cols, 260, y + 56 - r1 - 4, 70, 5, clip=(260, y + 40, 130), stroke=(r0 > 6))
        s += f'<line x1="408" x2="440" y1="{y + 28}" y2="{y + 28}" stroke="#e9b873" stroke-opacity=".5"/>'
        s += (f'<text x="448" y="{y + 32}" font-family="Hanken Grotesk,sans-serif" font-size="14" font-weight="600" fill="#ecc994">{label}</text>')
    s += ('<path d="M132 336 L392 336 L384 372 L140 372 Z" fill="#3a2c20" stroke="#e9b873" stroke-opacity=".55"/>'
          + _pile(rnd, 190, .8, 1.5, SAND, 262, 366, 70, 2.5, clip=(262, 356, 118))
          + '<text x="448" y="360" font-family="Hanken Grotesk,sans-serif" font-size="14" font-weight="600" fill="#ecc994">Pan</text>'
          + '<line x1="394" x2="440" y1="356" y2="356" stroke="#e9b873" stroke-opacity=".5"/>')
    return f"""<div class="gx-sieve"><svg viewBox="0 0 560 392" role="img" aria-label="Susunan saringan dari kasar ke halus">{s}</svg></div>"""


# ----------------------------------------------------------------- kartu fitur
_BG = ('<defs><linearGradient id="{i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3b2c1f"/>'
       '<stop offset="1" stop-color="#1f1610"/></linearGradient></defs><rect width="240" height="150" fill="url(#{i})"/>')


def _card_gradasi():
    env, hi, lo, mid, pts = _curves((26, 22, 222, 124))
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="#f6ead8"/>' for x, y in pts)
    return (_BG.format(i="c1") + f'<path d="{env}" fill="#e9b873" fill-opacity=".22"/>'
            f'<path d="{hi}" fill="none" stroke="#e9b873" stroke-width="1.4"/><path d="{lo}" fill="none" stroke="#e9b873" stroke-width="1.4"/>'
            f'<path d="{mid}" fill="none" stroke="#f6ead8" stroke-width="2.6" stroke-linejoin="round"/>{dots}')


def _card_jmf():
    ret = [0, 5, 11.5, 22.5, 18, 12.5, 8.5, 6.5, 5, 4, 6.5]
    bars = "".join(f'<rect x="30" y="{14 + i * 11.6:.1f}" width="{v / 22.5 * 140 + 3:.1f}" height="8" rx="2" '
                   f'fill="{"#ecc994" if i == 10 else "#e9b873"}" fill-opacity="{.55 + v / 60:.2f}"/>' for i, v in enumerate(ret))
    cols = "".join(f'<rect x="{194 + i * 11}" y="{128 - (14 + i * 7)}" width="8" height="{14 + i * 7}" rx="1.5" '
                   f'fill="#e9b873" fill-opacity="{.45 + i * .15:.2f}"/>' for i in range(4))
    return (_BG.format(i="c2") + '<line x1="30" x2="30" y1="10" y2="142" stroke="#e9b873" stroke-opacity=".4"/>' + bars + cols
            + '<text x="232" y="142" text-anchor="end" font-family="Hanken Grotesk,sans-serif" font-size="8.5" fill="#b8a995">Kelompok 1–4</text>')


def _card_marshall():
    pts = []
    for k in range(41):
        t = k / 40
        pts.append((34 + t * 176, 126 - (1162 - 620 * (t - .52) ** 2 - 900) / 300 * 92))
    curve = _path(pts)
    dots = "".join(f'<circle cx="{34 + t * 176:.1f}" cy="{126 - (1162 - 620 * (t - .52) ** 2 - 900) / 300 * 92:.1f}" r="3" fill="#f6ead8"/>' for t in (0, 1 / 3, 2 / 3, 1))
    return (_BG.format(i="c3") + '<line x1="34" x2="34" y1="18" y2="126" stroke="#e9b873" stroke-opacity=".4"/><line x1="34" x2="214" y1="126" y2="126" stroke="#e9b873" stroke-opacity=".4"/>'
            '<line x1="34" x2="214" y1="52" y2="52" stroke="#ff8a7a" stroke-width="1.2" stroke-dasharray="5 4"/>'
            '<line x1="34" x2="214" y1="100" y2="100" stroke="#ff8a7a" stroke-width="1.2" stroke-dasharray="5 4"/>'
            f'<path d="{curve}" fill="none" stroke="#e9b873" stroke-width="2.2"/>{dots}'
            '<line x1="122" x2="122" y1="18" y2="126" stroke="#f6ead8" stroke-width="1.6" stroke-dasharray="2 4"/>'
            '<text x="126" y="30" font-family="Hanken Grotesk,sans-serif" font-size="11" font-weight="700" fill="#f6ead8">KAO</text>')


def _card_excel():
    s = _BG.format(i="c4") + '<rect x="24" y="20" width="192" height="96" rx="6" fill="#241a13" stroke="#e9b873" stroke-opacity=".45"/>'
    for r in range(5):
        for c in range(5):
            x, y = 24 + c * 38.4, 20 + r * 19.2
            if r == 0:
                s += f'<rect x="{x:.1f}" y="{y:.1f}" width="38.4" height="19.2" fill="#e9b873" fill-opacity=".8"/>'
            elif c == 0:
                s += f'<rect x="{x:.1f}" y="{y:.1f}" width="38.4" height="19.2" fill="#e9b873" fill-opacity=".16"/>'
            else:
                s += f'<rect x="{x + 7:.1f}" y="{y + 7.5:.1f}" width="{12 + (r * 7 + c * 5) % 16}" height="4" rx="2" fill="#f1e8dc" fill-opacity=".5"/>'
    s += ('<path d="M24 39.2H216M24 58.4H216M24 77.6H216M24 96.8H216M62.4 20V116M100.8 20V116M139.2 20V116M177.6 20V116" stroke="#e9b873" stroke-opacity=".25"/>'
          '<rect x="150" y="84" width="76" height="52" rx="8" fill="#1d1712" stroke="#e9b873" stroke-opacity=".7"/>'
          '<path d="M158 124 C170 122 174 104 186 102 S206 108 218 94" fill="none" stroke="#f6ead8" stroke-width="2.2"/>')
    return s


def cards() -> str:
    items = [
        (_card_gradasi(), "Gradasi gabungan", "Cari proporsi 2–4 fraksi yang paling aman terhadap batas spesifikasi.", "01"),
        (_card_jmf(), "Rancangan campuran (JMF)", "Berat per saringan untuk Kelompok 1–4 sekaligus, lengkap dengan Pb.", "02"),
        (_card_marshall(), "Uji Marshall", "VIM, VMA, VFA, stabilitas, flow, dan kadar aspal optimum.", "03"),
        (_card_excel(), "Ekspor", "Excel dengan rumus hidup dan grafik sebagai gambar untuk laporan.", "04"),
    ]
    out = ""
    for svg, t, d, n in items:
        out += (f'<figure class="gx-card"><svg viewBox="0 0 240 150" role="img" aria-label="{t}">{svg}</svg>'
                f'<figcaption class="gx-cap"><span class="t">{t}</span><span class="n">{n}</span><span class="d">{d}</span></figcaption></figure>')
    return f'<div class="gx-cards">{out}</div>'


# -------------------------------------------------------------------- potongan
def _icon(paths):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="#e9b873" stroke-width="1.6" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{paths}</svg>')


ICONS = {
    "doc": _icon('<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 16h5"/>'),
    "grid": _icon('<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M4 10h16M4 15h16M10 4v16"/>'),
    "chart": _icon('<path d="M4 4v16h16"/><path d="M7 15c3-1 4-6 7-6s3 3 5 2"/>'),
    "device": _icon('<rect x="3" y="5" width="18" height="12" rx="2"/><path d="M8 21h8M12 17v4"/>'),
    "window": _icon('<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18"/>'),
}


def hero_text() -> str:
    return """
<div class="gx-kicker">Alat hitung campuran beraspal</div>
<h1 class="gx-h1">Campuran Aspal yang Kuat Dimulai dari Gradasi yang Tepat</h1>
<p class="gx-lead">Masukkan hasil analisa saringan tiap fraksi, pilih spesifikasi, lalu cari proporsi campuran yang paling jauh dari batas min/maks. Lanjutkan ke rancangan campuran (JMF) dan uji Marshall tanpa pindah alat.</p>"""


def hero_note() -> str:
    return '<p class="gx-note">Tersedia data contoh. Semua hitungan berjalan di browser Anda.</p>'


def section(title: str, rule: bool = False) -> str:
    return f'<div class="gx-sec"><h2 class="gx-h2{" rule" if rule else ""}">{title}</h2></div>'


def split_text() -> str:
    return """
<h2 class="gx-h2">Dari data saringan sampai keputusan campuran</h2>
<p class="gx-lead" style="margin-bottom:1.3rem">Satu perubahan proporsi langsung memperbarui tabel, grafik, dan evaluasi pada setiap ayakan. Hasilnya bisa dibandingkan antar kadar aspal, lalu diekspor ke Excel untuk dilaporkan.</p>"""


def strip() -> str:
    items = [
        ("doc", "Acuan Bina Marga 2018", "Batas gradasi dan syarat Marshall bisa diedit."),
        ("grid", "Rumus hidup", "Excel hasil ekspor tetap menghitung ulang."),
        ("chart", "Grafik siap laporan", "Unduh grafik gradasi dan Marshall sebagai PNG."),
        ("device", "Data di perangkat", "Tersimpan di browser, tidak dikirim ke server."),
        ("window", "Tanpa instalasi", "Cukup dibuka lewat browser."),
    ]
    return '<div class="gx-strip">' + "".join(
        f'<div>{ICONS[k]}<div class="t">{t}</div><div class="d">{d}</div></div>' for k, t, d in items) + "</div>"


def spec_band() -> str:
    chips = lambda xs: '<div class="gx-chips">' + "".join(f"<span>{x}</span>" for x in xs) + "</div>"
    return f"""
<div class="gx-two">
<div class="gx-panel"><h3>Gradasi agregat gabungan</h3>
{chips(["AC-WC", "AC-BC", "AC-Base", "HRS-WC", "HRS-Base", "Latasir Kelas A", "Latasir Kelas B"])}
<p class="gx-note">Batas mengacu pada Spesifikasi Umum Bina Marga 2018 (Divisi 6). Semua angka bisa diubah.</p></div>
<div class="gx-panel"><h3>Syarat Marshall (Laston)</h3>
{chips(["VIM 3–5%", "VMA min 15 / 14 / 13%", "VFA min 65%", "Stabilitas min 800 / 1800 kg", "Flow 2–4 / 3–6 mm", "MQ min 250 (opsional)"])}
<p class="gx-note">Urutan angka: AC-WC / AC-BC / AC-Base. Cocokkan dengan spesifikasi proyek atau dosen.</p></div>
</div>"""


def band_text() -> str:
    return """
<h2 class="gx-h2" style="margin-bottom:.5rem">Mulai dari data contoh</h2>
<p class="gx-p" style="margin:0">Setiap bagian punya tombol Muat contoh. Coba dulu, lalu ganti dengan data saringan dan hasil uji Anda sendiri.</p>"""


def page_head(title: str, lead: str, kicker: str) -> str:
    return f'<div class="gx-kicker">{kicker}</div><h1 class="gx-h1" style="font-size:clamp(1.9rem,3.6vw,2.8rem)">{title}</h1><p class="gx-lead">{lead}</p>'


STEPS = [
    ("Pilih spesifikasi dan fraksi", "Tentukan jenis campuran (AC-WC, AC-BC, HRS, Latasir, atau kustom) dan jumlah fraksi agregat, dua sampai empat."),
    ("Isi % lolos tiap ayakan", "Masukkan hasil analisa saringan untuk setiap fraksi. Batas min dan maks bisa diedit, ayakan baru bisa ditambah."),
    ("Atur pencarian", "Pilih langkah proporsi (1%, 0,5%, atau 0,1%) dan berat total campuran. Untuk empat fraksi, langkah terkecil adalah 0,5%."),
    ("Cari proporsi optimal", "Aplikasi mencari komposisi dengan margin terkecil terhadap batas yang paling besar. Proporsi bisa dibulatkan; tabel dan grafik ikut berubah."),
    ("Lanjut ke JMF dan Marshall", "Hitung berat per saringan untuk Kelompok 1–4, lalu isi data benda uji untuk mendapatkan VIM, VMA, VFA, MQ, dan kadar aspal optimum."),
    ("Unduh hasil", "Ekspor Excel berisi gradasi, JMF, dan data Marshall. Semua grafik yang tersedia bisa diunduh sebagai PNG."),
]


def steps() -> str:
    return '<div class="gx-steps">' + "".join(
        f'<div class="gx-step"><div class="n">{i:02d}</div><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(STEPS, 1)) + "</div>"


def formulas() -> str:
    rows = [
        ("Gmb", "berat kering / (berat SSD − berat dalam air)"),
        ("Gmm", "100 / ((100 − Pb) / Gse + Pb / Gb)"),
        ("VIM", "100 × (Gmm − Gmb) / Gmm"),
        ("VMA", "100 − Gmb × (100 − Pb) / Gsb"),
        ("VFA", "100 × (VMA − VIM) / VMA"),
        ("MQ", "stabilitas / flow"),
        ("Pb", "0,035 CA + 0,045 FA + 0,18 FF + K"),
    ]
    body = "".join(f"<div><i>{a}</i>= {b}</div>" for a, b in rows)
    return f'<div class="gx-panel"><h3>Rumus yang dipakai</h3><div class="gx-form">{body}</div></div>'


def checks() -> str:
    return """
<div class="gx-panel"><h3>Yang perlu diperiksa sendiri</h3>
<p class="gx-p" style="margin-bottom:.7rem">Kalkulator adalah alat bantu, bukan pengganti pengujian. Cocokkan batas spesifikasi dengan dokumen proyek atau dosen, dan pastikan Gsb serta Gse berasal dari uji berat jenis Anda.</p>
<p class="gx-p" style="margin:0">Data contoh bersifat ilustrasi, bukan data laboratorium. Periksa satu hasil dengan hitungan manual sebelum dipakai di laporan.</p></div>"""


def about(pengembang: str = "") -> str:
    dev = f"<dt>Pengembang</dt><dd>{pengembang}</dd>" if pengembang else ""
    return f"""
<div class="gx-two">
<div><p class="gx-p">ProyekAplikom adalah alat bantu komputasi dan pembelajaran interaktif untuk perancangan campuran beraspal. Fokusnya mempercepat pekerjaan yang biasanya dihitung berulang: mencari proporsi fraksi agregat, menyusun rancangan campuran, dan mengolah hasil uji Marshall.</p>
<p class="gx-p">Hasil perhitungan diperlakukan sebagai bahan pertimbangan. Keputusan akhir tetap membutuhkan pemeriksaan manual dan pengujian laboratorium.</p></div>
<div class="gx-panel"><dl class="gx-dl">
<dt>Cakupan</dt><dd>Gradasi gabungan, JMF Kelompok 1–4, uji Marshall, ekspor Excel.</dd>
<dt>Acuan</dt><dd>Spesifikasi Umum Bina Marga 2018 (Divisi 6). Batas dapat diedit.</dd>
<dt>Optimal</dt><dd>Komposisi dengan margin terkecil terhadap batas spesifikasi yang paling besar.</dd>
<dt>Data</dt><dd>Tersimpan di browser pengguna. Perhitungan berjalan di sisi klien.</dd>
<dt>Teknologi</dt><dd>Streamlit untuk kerangka situs; kalkulator berupa HTML dan JavaScript (gradasi.html).</dd>
{dev}</dl></div>
</div>"""


# ------------------------------------------------------- penyesuaian kalkulator
_OVERRIDE = """<style>
@import url('%FONTS%');
:root[data-theme="dark"]{--bg:#1b1815;--cd:#251d16;--tx:#f1e8dc;--mu:#b8a995;--bd:#3a2f25;--ac:#e9b873;--ak:#20160c;
--sf:#2f241b;--er:#ff8a7a;--cr:#f6ead8;--sl:#33271c;--st:#f6ecdd;--hl:#f2c46d;color-scheme:dark}
:root[data-theme="light"]{--bg:#f4efe7;--cd:#fffaf2;--tx:#30251b;--mu:#746659;--bd:#dfd1bd;--ac:#9a6429;--ak:#fffaf2;
--sf:#ece1d1;--er:#a8372b;--cr:#bd531d;--sl:#4a3524;--st:#fffaf2;--hl:#f2c46d;color-scheme:light}
html,body{background:var(--bg)}
body{font-family:'Hanken Grotesk',system-ui,sans-serif}
h1,h2{font-family:'Playfair Display',Georgia,serif;letter-spacing:0}
main>h1,main>.s{display:none}
main{padding-top:6px}
:root[data-theme="dark"] .c{border-radius:16px;background:linear-gradient(180deg,#281f18,#221a14)}
:root[data-theme="light"] .c{border-radius:16px;background:linear-gradient(180deg,#fffaf2,#f3eadc)}
button{border-radius:999px}
.gx-calc-controls{display:flex;justify-content:flex-end;margin:0 0 10px}
.gx-theme-button{padding:7px 14px;border:1px solid var(--bd);background:var(--sf);color:var(--tx)}
</style>""".replace("%FONTS%", FONTS)

_PATCH = """<script>
(function(){
 var root=document.documentElement,button=document.getElementById('gx-theme-toggle');
 try{var saved=localStorage.getItem('grad_theme');root.dataset.theme=saved==='light'?'light':'dark'}catch(err){root.dataset.theme='dark'}
 function updateTheme(){var dark=root.dataset.theme==='dark';button.textContent=dark?'☀️ Tema terang':'🌙 Tema gelap';button.setAttribute('aria-pressed',String(dark))}
 updateTheme();
 button.addEventListener('click',function(){
  root.dataset.theme=root.dataset.theme==='dark'?'light':'dark';
  try{localStorage.setItem('grad_theme',root.dataset.theme)}catch(err){}
  updateTheme();
 });
 try{if(!(window.claude&&window.claude.use)){
  DL={save:async function(o){var b=o.data instanceof Blob?o.data:new Blob([o.data]),url=URL.createObjectURL(b),a=document.createElement('a');
   a.href=url;a.download=o.filename;a.hidden=true;document.body.appendChild(a);a.click();a.remove();
   setTimeout(function(){URL.revokeObjectURL(url)},60000)}};
  var e=document.getElementById('ex2');if(e)e.hidden=false;
 }}catch(err){}
 function fit(){try{var f=window.frameElement;if(f)f.style.height=(document.body.scrollHeight+24)+'px'}catch(err){}}
 try{new ResizeObserver(fit).observe(document.body)}catch(err){}
 window.addEventListener('load',fit);setTimeout(fit,700);
})();
</script>"""


def sesuaikan_kalkulator(src: str) -> str:
    """Selaraskan gradasi.html dengan tema situs tanpa mengubah file aslinya."""
    src = src.replace("</head>", _OVERRIDE + "</head>", 1)
    controls = (
        '<div class="gx-calc-controls"><button id="gx-theme-toggle" '
        'class="gx-theme-button" type="button" aria-pressed="true">'
        "☀️ Tema terang</button></div>"
    )
    src = src.replace("<main>", "<main>" + controls, 1)
    return src.replace("</body>", _PATCH + "</body>", 1)
