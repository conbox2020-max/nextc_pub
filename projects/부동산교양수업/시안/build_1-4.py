# 도1-4 가구 평균 자산 구성: 수치로 계산한 벡터 도넛 + 생성 일러스트 항목 그림
# 사용: python3 -I build_1-4.py → 도1-4_자산구성_v1.svg(링크), _embed.svg(미리보기)
# 데이터: 국가데이터처·한국은행·금융감독원, 「2025년 가계금융복지조사 결과」(2025.12.4), 2025년 3월 말 기준
import os, math, base64
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = "illust/도1-4_항목그림_v1.png"          # 1536×1024, 왼쪽 집·차 / 오른쪽 통장·동전
CROP = {"실물": (90, 215, 620, 530), "금융": (870, 250, 600, 520)}   # 원본 px (x, y, w, h)
DATA = [("실물자산", 75.8, "#2A8F99", "부동산, 자동차 등"),   # 도해_청록
        ("금융자산", 24.2, "#FFD43B", None)]                 # 도해_노랑 (칠만, 글자색으로 쓰지 않음)
assert abs(sum(v for _, v, _, _ in DATA) - 100) < 1e-9
W, H = 101, 74
PT = 25.4 / 72
FONT = "'Sandoll 스터디윗미','NanumSquareRound',sans-serif"
NUM = "'DIN 2014','NanumSquareRound',sans-serif"
K80 = "#4D4D4D"

def t(x, y, s, pt, w=700, fill=K80, anchor="middle", family=FONT):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{pt*PT:.3f}" font-weight="{w}" '
            f'fill="{fill}" text-anchor="{anchor}">{s}</text>')

def ring_seg(cx, cy, R, r, a0, a1, fill):
    """12시 방향 0°, 시계 방향 각도(도)로 도넛 조각을 그린다."""
    def pt(rad, a):
        th = math.radians(a - 90)
        return cx + rad * math.cos(th), cy + rad * math.sin(th)
    large = 1 if a1 - a0 > 180 else 0
    (x0, y0), (x1, y1) = pt(R, a0), pt(R, a1)
    (x2, y2), (x3, y3) = pt(r, a1), pt(r, a0)
    return (f'<path d="M{x0:.3f} {y0:.3f} A{R} {R} 0 {large} 1 {x1:.3f} {y1:.3f} '
            f'L{x2:.3f} {y2:.3f} A{r} {r} 0 {large} 0 {x3:.3f} {y3:.3f} Z" fill="{fill}" '
            f'stroke="#fff" stroke-width="0.5"/>')

def vignette(href, key, x, y, w):
    cx, cy, cw, ch = CROP[key]
    h = w * ch / cw
    return (f'<svg x="{x}" y="{y}" width="{w}" height="{h:.3f}" viewBox="{cx} {cy} {cw} {ch}" style="mix-blend-mode:multiply">'  # 배경 미세 회색 제거(인디자인: 효과 > 곱하기)
            f'<image href="{href}" x="0" y="0" width="1536" height="1024"/></svg>')

def build(href):
    e = []
    cx, cy, R, r = 25, 27, 22, 13
    a = 0
    for name, v, col, _ in DATA:                       # 비율 그대로 각도 계산 (100% = 360°)
        e.append(ring_seg(cx, cy, R, r, a, a + v * 3.6, col)); a += v * 3.6
    e += [t(cx, cy - 0.6, "가구 평균", 8.5), t(cx, cy + 3.4, "자산의 구성", 8.5)]
    rows = [(4.5, "실물"), (30.5, "금융")]
    for (y0, key), (name, v, col, sub) in zip(rows, DATA):
        e.append(vignette(href, key, 51.5, y0, 22))
        e.append(f'<rect x="77" y="{y0+4.3}" width="3.2" height="3.2" rx="0.4" fill="{col}" stroke="{K80}" stroke-width="0.15"/>')
        e.append(t(81.6, y0 + 7.1, name, 9, anchor="start"))
        e.append(t(77, y0 + 15.2, f"{v:.1f}%", 18, 700, K80, "start", NUM))
        if sub: e.append(t(77, y0 + 19.6, sub, 7, 400, anchor="start"))
    e.append(t(W / 2, 59.5, "가구 자산의 약 4분의 3은 실물자산", 10))
    e.append(t(0, 64.6, "• 2025년 3월 말 기준. 실물자산에는 부동산 외의 자산도 포함되며, 가구마다 비중은 다르다.", 7, 300, anchor="start"))
    e.append(t(0, 68.4, "출처: 국가데이터처·한국은행·금융감독원, 「2025년 가계금융복지조사 결과」", 7, 300, anchor="start"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">'
            + "".join(e) + "</svg>")

open(os.path.join(HERE, "도1-4_자산구성_v1.svg"), "w", encoding="utf-8").write(build(IMG))
data = base64.b64encode(open(os.path.join(HERE, IMG), "rb").read()).decode()
open(os.path.join(HERE, "도1-4_자산구성_v1_embed.svg"), "w", encoding="utf-8").write(build("data:image/png;base64," + data))
print("ok")
