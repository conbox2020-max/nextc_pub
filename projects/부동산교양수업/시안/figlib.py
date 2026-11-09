# 시안 공통 함수: mm 단위 SVG 조립 (국부론 도해 스타일)
import os, base64
HERE = os.path.dirname(os.path.abspath(__file__))
PT = 25.4 / 72
FONT = "'Sandoll 스터디윗미','NanumSquareRound',sans-serif"
NUM = "'DIN 2014','NanumSquareRound',sans-serif"
DOC = "'Sandoll 고딕Neo1','NanumGothic',sans-serif"      # 가상 서류 재현용 고딕
TEAL, ORANGE, YELLOW, RED, K80, K40 = "#2A8F99", "#F5A21B", "#FFD43B", "#D0312D", "#4D4D4D", "#999999"
TEAL_T, YELLOW_T, ORANGE_T = "#CFE8EA", "#FFF1B8", "#FCDDB0"     # 칠용 옅은 농도

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def t(x, y, s, pt, w=700, fill=K80, anchor="middle", family=FONT, extra=""):
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}" font-size="{pt*PT:.3f}" font-weight="{w}" '
            f'fill="{fill}" text-anchor="{anchor}" {extra}>{esc(s)}</text>')

def lines(x, y, rows, pt, w=400, fill=K80, anchor="start", lead=1.35, family=FONT):
    return [t(x, y + i * pt * PT * lead, s, pt, w, fill, anchor, family) for i, s in enumerate(rows)]

def em(s): return sum(0.35 if c == " " else (0.55 if c.isascii() else 1.0) for c in s)

def tag(cx, cy, rows, stroke=K80, fill="#fff"):
    """rows = [(글자, pt, 색), ...] → (요소들, (x, y, w, h))"""
    hgt = sum(p * PT * 1.25 for _, p, _ in rows) + 1.6
    wid = max(em(s) * p * PT for s, p, _ in rows) + 2.4
    x, y = cx - wid / 2, cy - hgt / 2
    out = [f'<rect x="{x:.2f}" y="{y:.2f}" width="{wid:.2f}" height="{hgt:.2f}" rx="1.2" fill="{fill}" '
           f'fill-opacity="0.94" stroke="{stroke}" stroke-width="0.18"/>']
    yy = y + 0.8
    for s, p, c in rows:
        yy += p * PT * 1.25
        out.append(t(cx, yy - p * PT * 0.3, s, p, 700, c))
    return out, (x, y, wid, hgt)

def leader(x1, y1, x2, y2, c=K80, dot=True):
    s = f'<path d="M{x1:.2f} {y1:.2f} L{x2:.2f} {y2:.2f}" stroke="{c}" stroke-width="0.2" fill="none"/>'
    return s + (f'<circle cx="{x2:.2f}" cy="{y2:.2f}" r="0.5" fill="{c}"/>' if dot else "")

def badge(cx, cy, s, col=TEAL, r=2.1, fg="#fff"):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}"/>' + t(cx, cy + 1.05, s, 8, 700, fg, family=NUM))

def rect(x, y, w, h, fill="none", stroke=K80, sw=0.18, rx=0, extra=""):
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

def line(x1, y1, x2, y2, c=K80, sw=0.18, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M{x1:.2f} {y1:.2f} L{x2:.2f} {y2:.2f}" stroke="{c}" stroke-width="{sw}"{d}/>'

def crop(href, box, x, y, w, multiply=True, iw=1536, ih=1024):
    """원본 px 박스(bx, by, bw, bh)를 폭 w mm로 잘라 앉힌다. 반환: (요소, 높이)"""
    bx, by, bw, bh = box
    h = w * bh / bw
    st = ' style="mix-blend-mode:multiply"' if multiply else ""   # 인디자인: 효과 > 곱하기
    return (f'<svg x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" viewBox="{bx} {by} {bw} {bh}"{st}>'
            f'<image href="{href}" x="0" y="0" width="{iw}" height="{ih}"/></svg>'), h

def write(name, W, H, build, imgs):
    """imgs: {키: 상대경로}. 링크판(작업용)과 내장판(미리보기용) SVG를 쓴다."""
    def doc(hrefs):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">'
                + "".join(build(hrefs)) + "</svg>")
    open(os.path.join(HERE, f"{name}.svg"), "w", encoding="utf-8").write(doc(imgs))
    emb = {k: "data:image/png;base64," + base64.b64encode(open(os.path.join(HERE, v), "rb").read()).decode()
           for k, v in imgs.items()}
    open(os.path.join(HERE, f"{name}_embed.svg"), "w", encoding="utf-8").write(doc(emb))
