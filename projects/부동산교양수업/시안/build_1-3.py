# 도1-3 토지·건물·동산: 생성 일러스트(101×67.3mm) 위에 국부론 방식 라벨을 얹은 시안
# 사용: python3 -I build_1-3.py
#   → 도1-3_토지건물동산_v1.svg (이미지 링크, 작업용)
#   → 도1-3_토지건물동산_v1_embed.svg (이미지 내장, 미리보기용)
import os, base64
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = "illust/도1-3_일러스트_v1.png"
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
    # 묶음 제목: 부동산 (왼쪽 위 여백)
    e += [t(3, 6.5, "부동산", 9.5, fill=TEAL, anchor="start"),
          t(3, 10.3, "움직일 수 없는 재산", 7.5, 400, anchor="start")]
    # 건물: 땅에 붙어 있는 정착물
    p, b = tag(40.5, 8.6, [("건물", 8.5, TEAL), ("땅에 붙어 있는 것", 7, K80)], TEAL); e += p
    e.append(leader(38.0, b[1] + b[3], 35.0, 17.5, TEAL))
    # 토지: 땅 자체 (운동장 위)
    p, _ = tag(30.0, 42.0, [("토지", 8.5, TEAL), ("땅 자체", 7, K80)], TEAL); e += p
    # 동산: 옮길 수 있는 물건 (오른쪽 위 여백)
    p, b = tag(79.0, 22.5, [("동산", 8.5, ORANGE), ("옮길 수 있는 물건", 7, K80)], ORANGE); e += p
    e.append(leader(b[0] + 3.5, b[1] + b[3], 69.8, 42.6, ORANGE))
    e.append(leader(b[0] + b[2] - 3.5, b[1] + b[3], 88.3, 46.4, ORANGE))
    # 도해 제목과 주석
    e.append(t(W / 2, IH + 6.2, "움직일 수 없는 재산과 옮길 수 있는 재산", 10))
    e.append(t(0, IH + 11.2, "• 민법은 토지와 그 정착물을 부동산이라고 한다.", 7, 300, anchor="start"))
    e.append(t(0, IH + 14.6, "• 우리나라는 토지와 건물을 각각 독립된 부동산으로 다룬다.", 7, 300, anchor="start"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">'
            + "".join(e) + "</svg>")

open(os.path.join(HERE, "도1-3_토지건물동산_v1.svg"), "w", encoding="utf-8").write(build(IMG))
data = base64.b64encode(open(os.path.join(HERE, IMG), "rb").read()).decode()
open(os.path.join(HERE, "도1-3_토지건물동산_v1_embed.svg"), "w", encoding="utf-8").write(build("data:image/png;base64," + data))
print("ok")
