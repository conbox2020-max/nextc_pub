# 공통 도비라 시안: 도련 포함 156×220mm. 국부론 도비라 틀(IDML 추출)을 그대로 얹는다.
#   반투명 패널: 페이지 기준 가로 38.3~115mm, 위 도련~167mm, r35g31b32 65%, 흰 3pt 테두리
#   장 번호 20pt·장 제목 18pt 흰 글자(격동굴림2 06 Hv) / 장 아이콘 배지(제안)
# 사용: python3 -I build_dobira.py → 도비라_v1_01~07.svg (_embed 포함)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *
from build_3 import C, IM as IM3
C.update({"공사": ("s5", (775, 540, 340, 375)), "주택가": ("s6", (800, 745, 320, 225)), "입주": ("s5", (1165, 545, 340, 395))})
IM = dict(IM3, s5="illust/5장_항목그림_v1.png", s6="illust/6장_항목그림_v1.png", d="illust/도비라_공통_v1.png")
W, H, B = 156, 220, 3                       # 도련 포함 크기, 도련
TITLE = "'Sandoll 격동굴림2','NanumSquareRound',sans-serif"
CH = [("01", ["내가 밟는 땅,", "누구의 것일까?"], "집"),
      ("02", ["집에도 주민등록증이", "있다고요?"], "등기"),
      ("03", ["보증금의", "정체는 무엇?"], "열쇠"),
      ("04", ["종이 한 장이 내 권리를", "지켜준다고요?"], "계약서"),
      ("05", ["부동산 뉴스의", "비밀 코드를 해독하라!"], "공사"),
      ("06", ["집값이 달라지면,", "삶도 달라질까?"], "주택가"),
      ("07", ["나의 첫 번째", "계약서"], "입주")]

def build_for(i):
    num, ttl, icon = CH[i]
    def build(h):
        e = []
        # 그림: 1024×1536(2:3)을 폭 156mm로 맞추면 높이 234mm → 위쪽 하늘 14mm를 잘라 220mm에 맞춤
        cut = 14 * 1024 / 156
        e.append(f'<svg x="0" y="0" width="{W}" height="{H}" viewBox="0 {cut:.1f} 1024 {H*1024/156:.1f}" preserveAspectRatio="xMidYMin slice">'
                 f'<image href="{h["d"]}" x="0" y="0" width="1024" height="1536"/></svg>')
        px0, px1, py1 = B + 38.3, B + 115, B + 167
        e.append(f'<rect x="{px0}" y="0" width="{px1-px0:.1f}" height="{py1}" fill="#231F20" fill-opacity="0.65"/>')
        e.append(rect(px0, -1, px1 - px0, py1 + 1, "none", "#fff", 3 * PT))
        cx = (px0 + px1) / 2
        e.append(t(cx, 80, num, 20, 800, "#fff", family=TITLE))
        e.append(line(cx, 86, cx, 104, "#fff", 3 * PT))
        for k, s in enumerate(ttl):
            e.append(t(cx, 117 + k * 8.6, s, 18 if len(s) <= 11 else 15.5, 800, "#fff", family=TITLE))
        # 장 아이콘 배지(제안): 지름 16mm 흰 원 + 항목 그림 11mm
        e.append(f'<circle cx="{cx:.2f}" cy="148" r="8" fill="#fff"/>')
        sh, box = C[icon]
        w = min(11, 11 * box[2] / box[3]); hh = w * box[3] / box[2]
        e.append(f'<svg x="{cx-w/2:.2f}" y="{148-hh/2:.2f}" width="{w:.2f}" height="{hh:.2f}" viewBox="{box[0]} {box[1]} {box[2]} {box[3]}"><image href="{h[sh]}" x="0" y="0" width="1536" height="1024"/></svg>')
        # 재단선 표시(시안용)
        e.append(rect(B, B, W - 2 * B, H - 2 * B, "none", "#E33", 0.25, 0, 'stroke-dasharray="1.5 1"'))
        return e
    return build

if __name__ == "__main__":
    for i in range(7):
        name = f"도비라_v1_{CH[i][0]}"
        write(name, W, H, build_for(i), IM); print(name, W, H)
