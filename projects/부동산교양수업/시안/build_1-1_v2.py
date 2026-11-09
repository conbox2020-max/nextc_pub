# 도1-1 v2: 생성 일러스트(101×67.3mm) 위에 국부론 방식 라벨을 얹은 시안
# 사용: python3 -I build_1-1_v2.py
#   → 도1-1_맥도날드흐름도_v2.svg (이미지 링크, 작업용)
#   → 도1-1_맥도날드흐름도_v2_embed.svg (이미지 내장, 미리보기용)
import os, base64
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = "illust/도1-1_일러스트_v2.png"
W, IH = 101, 101 * 1024 / 1536          # 그림 101×67.33mm
H = 84
PT = 25.4 / 72
FONT = "'Sandoll 스터디윗미','NanumSquareRound',sans-serif"
TEAL, ORANGE, K80 = "#2A8F99", "#F5A21B", "#4D4D4D"

def t(x, y, s, pt, w=700, fill=K80, anchor="middle"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{pt*PT:.3f}" font-weight="{w}" '
            f'fill="{fill}" text-anchor="{anchor}">{s}</text>')

def tag(cx, cy, lines, stroke=K80):
    """흰 바탕 라벨. lines = [(글자, pt, 색), ...]"""
    hgt = sum(p * PT * 1.25 for _, p, _ in lines) + 1.6
    em = lambda s: sum(0.35 if c == ' ' else 1.0 for c in s)   # 한글·원문자 1em, 공백 0.35em
    wid = max(em(s) * p * PT for s, p, _ in lines) + 2.4
    x, y = cx - wid / 2, cy - hgt / 2
    out = [f'<rect x="{x:.2f}" y="{y:.2f}" width="{wid:.2f}" height="{hgt:.2f}" rx="1.2" '
           f'fill="#fff" fill-opacity="0.92" stroke="{stroke}" stroke-width="0.18"/>']
    yy = y + 0.8
    for s, p, c in lines:
        yy += p * PT * 1.25
        out.append(t(cx, yy - p * PT * 0.3, s, p, 700, c))
    return out, (x, y, wid, hgt)

def leader(x1, y1, x2, y2, c=K80):
    return f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{c}" stroke-width="0.2" fill="none"/><circle cx="{x2}" cy="{y2}" r="0.5" fill="{c}"/>'

def build(href):
    e = [f'<image href="{href}" x="0" y="0" width="{W}" height="{IH:.3f}"/>']
    # 패널 제목 (왼쪽 위 여백)
    e += [t(3, 6.5, "가맹점", 9.5, anchor="start"), t(3, 10.3, "다른 사업자가 운영", 7.5, 400, anchor="start")]
    e += [t(53.5, 6.5, "직영 매장", 9.5, anchor="start"), t(53.5, 10.3, "본사가 직접 운영", 7.5, 400, anchor="start")]
    # 본사 (두 패널의 빌딩)
    for cx, cy in ((33.5, 15.6), (80.5, 14.2)):            # 빌딩 왼쪽 흰 여백
        p, _ = tag(cx, cy, [("맥도날드 본사", 7.5, K80)]); e += p
    # 손님 → 햄버거 값
    p, _ = tag(19.5, 30.5, [("햄버거 값", 7.5, K80)]); e += p
    e.append(leader(19.5, 32.3, 15.6, 41.8))
    # 가맹점주 → 본사 직원: ① 로열티 ② 임대료
    p, b = tag(42, 28.5, [("① 로열티", 7.5, TEAL), ("② 임대료", 7.5, TEAL)], TEAL); e += p
    e.append(leader(41, b[1] + b[3], 39.2, 42.8, TEAL))
    # 인물 이름
    p, _ = tag(31.3, 57.5, [("가맹점주", 7, K80)]); e += p
    p, _ = tag(44.6, 62.8, [("본사 직원", 7, K80)]); e += p
    # 직영 매장 판매 매출 → 본사
    p, b = tag(74.5, 27.2, [("③ 판매 매출", 7.5, ORANGE)], ORANGE); e += p
    e.append(leader(b[0] + b[2], 27.2, 86.4, 30.0, ORANGE))
    # 도해 제목과 주석
    e.append(t(W / 2, IH + 6.2, "가맹점과 직영 매장, 돈은 어떻게 흐를까?", 10))
    e.append(t(0, IH + 11.2, "• 가맹점의 판매대금은 가맹점 매출, 직영 매장의 판매대금은 본사 매출이다.", 7, 300, anchor="start"))
    e.append(t(0, IH + 14.6, "• 주요 흐름만 간추린 그림이다.", 7, 300, anchor="start"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">'
            + "".join(e) + "</svg>")

open(os.path.join(HERE, "도1-1_맥도날드흐름도_v2.svg"), "w", encoding="utf-8").write(build(IMG))
data = base64.b64encode(open(os.path.join(HERE, IMG), "rb").read()).decode()
open(os.path.join(HERE, "도1-1_맥도날드흐름도_v2_embed.svg"), "w", encoding="utf-8").write(build("data:image/png;base64," + data))
print("ok")
