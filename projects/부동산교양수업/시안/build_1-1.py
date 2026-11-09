# 도1-1 맥도날드 돈의 흐름 시안 생성: 실제 크기(mm) SVG
# 사용: python3 -I build_1-1.py  → 도1-1_맥도날드흐름도_v1.svg
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 101, 73                         # 판면 폭 101mm
PT = 25.4 / 72                         # pt → mm
FONT = "'Sandoll 스터디윗미','NanumSquareRound',sans-serif"   # 미리보기 대체 서체
NUM = "'DIN 2014','NanumSquareRound',sans-serif"
TEAL, ORANGE, K80, PALE = "#2A8F99", "#F5A21B", "#4D4D4D", "#FFF4C2"

def icon(name, x, y, size=12):
    body = open(os.path.join(HERE, "icons", name + ".svg"), encoding="utf-8").read()
    inner = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", body.strip())
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 100 100">{inner}</svg>'

def text(x, y, s, pt, weight=400, fill=K80, anchor="middle", family=FONT):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{pt*PT:.3f}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>')

def arrow(x1, y1, x2, y2, color, w):
    return f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{color}" stroke-width="{w}" fill="none" marker-end="url(#a{color[1:]})"/>'

def marker(color):
    return (f'<marker id="a{color[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" '
            f'orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="{color}"/></marker>')

def box(x, y, w, h, fill="none", stroke=TEAL, sw=0.5*PT):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1.5" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.3f}"/>'

e = []
e.append(f'<defs>{marker(TEAL)}{marker(ORANGE)}{marker(K80)}</defs>')

# 손님과 갈림길
e += [icon("손님", 2.5, 21), text(8.5, 36.6, "손님", 8.5, 700), text(8.5, 39.8, "햄버거 값 지불", 7)]
e.append(f'<path d="M15 27.5 H19 M19 14.25 V40.75" stroke="{K80}" stroke-width="0.25" fill="none"/>')
e += [arrow(19, 14.25, 25, 14.25, K80, 0.25), arrow(19, 40.75, 25, 40.75, K80, 0.25)]

# 가맹점 (위)
e += [box(25, 2, 30, 24.5), icon("가맹점", 34, 3.3),
      text(40, 18.8, "가맹점", 8.5, 700), text(40, 21.7, "다른 사업자가 운영", 7),
      text(40, 24.5, "판매대금 = 가맹점 매출", 7)]
# 직영 매장 (아래)
e += [box(25, 29, 30, 24.5), icon("직영매장", 34, 30.3),
      text(40, 45.8, "직영 매장", 8.5, 700), text(40, 48.7, "본사가 직접 운영", 7),
      text(40, 51.5, "판매대금 = 본사 매출", 7)]

# 가맹점 → 본사: ① 로열티 ② 임대료
e += [text(67, 5.2, "① 로열티", 8.5, 700, TEAL), text(67, 8.0, "브랜드·운영 방식 사용", 7),
      arrow(55, 10, 78.8, 10, TEAL, 0.35),
      text(67, 15.2, "② 임대료", 8.5, 700, TEAL), text(67, 18.0, "매장 땅·건물 사용", 7),
      arrow(55, 20, 78.8, 20, TEAL, 0.35)]
# 직영 매장 → 본사: ③
e += [text(67, 38.0, "③ 판매 매출", 8.5, 700, ORANGE), arrow(55, 40.75, 78.8, 40.75, ORANGE, 0.35)]

# 맥도날드 본사
e += [box(79, 2, 22, 51.5, PALE, TEAL, 0.75*PT), icon("본사", 84, 7),
      text(90, 24.2, "맥도날드", 8.5, 700), text(90, 27.6, "본사", 8.5, 700),
      text(90, 33.5, "본사가 받는 돈", 7),
      text(90, 37.6, "① 로열티", 7.5, 700, TEAL), text(90, 41.0, "② 임대료", 7.5, 700, TEAL),
      text(90, 44.4, "③ 직영 매출", 7.5, 700, ORANGE)]

# 도해 제목과 주석
e.append(text(50.5, 59.6, "가맹점과 직영 매장, 돈은 어떻게 흐를까?", 10, 700))
e.append(text(0, 64.4, "• 주요 흐름만 간추린 그림. 가맹점의 판매대금은 가맹점의 매출이다.", 7, anchor="start"))
e.append(f'<text x="0" y="67.8" font-family="{FONT}" font-size="{7*PT:.3f}" fill="{K80}">'
         f'• <tspan font-family="{NUM}" font-weight="700">2024</tspan>년 본사 임대료 수입 약 '
         f'<tspan font-family="{NUM}" font-weight="700">100</tspan>억 달러 = 본사 전체 매출(약 '
         f'<tspan font-family="{NUM}" font-weight="700">259</tspan>억 달러)의 약 '
         f'<tspan font-family="{NUM}" font-weight="700">39%</tspan></text>')
e.append(text(0, 71.6, "출처: McDonald’s, 2024 Form 10-K", 7, 300, anchor="start"))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">'
       + "".join(e) + "</svg>")
out = os.path.join(HERE, "도1-1_맥도날드흐름도_v1.svg")
open(out, "w", encoding="utf-8").write(svg)
print(out)
