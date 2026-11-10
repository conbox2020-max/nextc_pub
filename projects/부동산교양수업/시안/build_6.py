# 제6장 도판 시안: 6-1 도시계획 3단계 / 6-2 카페와 집값(인과) / 6-4 맹모 이야기 4컷 / 6-5 브역대신공평초
# 사용: python3 -I build_6.py [6-1 ...]
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *
from build_3 import C, pic, arrow, note, title, IM as IM3

IM = dict(IM3, s6="illust/6장_항목그림_v1.png", s5="illust/5장_항목그림_v1.png", s64="illust/도6-4_맹모4컷_v1.png")
C.update({"계획도": ("s6", (30, 55, 350, 270)), "카페": ("s6", (435, 40, 320, 270)), "지하철": ("s6", (800, 45, 320, 270)),
          "오피스": ("s6", (1170, 30, 320, 300)), "정문": ("s6", (25, 365, 350, 280)), "대단지": ("s6", (425, 440, 325, 180)),
          "신축": ("s6", (815, 360, 285, 290)), "공원": ("s6", (1170, 385, 345, 265)), "평지": ("s6", (25, 735, 355, 230)),
          "학교": ("s6", (420, 740, 330, 230)), "주택가": ("s6", (800, 745, 320, 225)), "학생": ("s6", (1245, 710, 230, 270)),
          "공사": ("s5", (775, 540, 340, 375))})
W = 101

def mini_zoning(x, y, w, h):
    """관리계획: 용도지역 색을 칠한 작은 지도(5-4와 같은 색)"""
    return [rect(x, y, w, h, "#FFE575", "#666666", 0.2),
            f'<path d="M{x} {y} H{x+w*0.45} L{x+w*0.35} {y+h*0.35} L{x} {y+h*0.4} Z" fill="#A4D28C"/>',
            rect(x + w * 0.45, y + h * 0.35, w * 0.3, h * 0.28, "#F5A3B5", "none", 0),
            f'<path d="M{x+w*0.55} {y+h*0.7} H{x+w} V{y+h} H{x+w*0.5} Z" fill="#AB93C9"/>',
            f'<path d="M{x} {y+h*0.5} H{x+w} M{x+w*0.5} {y} V{y+h}" stroke="#fff" stroke-width="0.8"/>']

# ── 6-1 도시계획 세 단계 ─────────────────────────────
def fig_6_1(h):
    e = []
    steps = [("① 도시·군기본계획", ["장기적인 공간 구조와", "발전 방향"], "큰 방향"),
             ("② 도시·군관리계획", ["용도지역·시설 등을", "구체적으로 결정"], "구체적 결정"),
             ("③ 개별 사업", ["예산과 필요한 인허가 등을", "거쳐 공사 진행"], "실행")]
    for i, (nm, ds, kw) in enumerate(steps):
        cx = 16 + i * 34.5
        e.append(rect(cx - 16, 0, 32, 40, "none", TEAL if i < 2 else ORANGE, 0.3, 1.5))
        e.append(t(cx, 4.8, kw, 7.5, 700, TEAL if i < 2 else ORANGE))
        if i == 0:
            el, b = pic(h, "계획도", cx, 7, 18, 13); e.append(el)
        elif i == 1:
            e += mini_zoning(cx - 9, 8, 18, 12); b = 20
        else:
            el, b = pic(h, "공사", cx, 6.5, 16, 14); e.append(el)
        e.append(t(cx, 25.8, nm, 8, 700, K80))
        e += lines(cx, 30.4, ds, 7, 400, anchor="middle", lead=1.3)
        if i < 2: e.append(arrow(cx + 16.3, 20, cx + 18.2, 20, K80, 0.35))
    e.append(title(48, "뉴스 속 도시계획, 지금 어느 단계일까?"))
    e.append(note(52.8, "• 기본계획에 어떤 시설이나 개발 방향이 담겼다고 해서 바로 공사가 시작되거나 개인이 건축할 권리가 생기는 것은 아니다."))
    return e

# ── 6-2 카페가 생기면 집값이 오를까: 세 가설 ─────────────
def fig_6_2(h):
    e = []
    # 가운데 두 현상
    el, b = pic(h, "카페", 22, 22, 18, 15); e.append(el)
    e.append(t(22, b + 3.6, "새 카페 입점", 8.5, 700))
    el, b2 = pic(h, "주택가", 79, 22, 18, 15); e.append(el)
    e.append(arrow(90, 33, 90, 26, RED, 0.45))
    e.append(t(79, b2 + 3.6, "주변 집값 변화", 8.5, 700))
    # 가설 ① 카페 → 집값, ② 집값(변화 중인 동네) → 카페
    e.append(f'<path d="M33 25 Q50.5 19 68 25" stroke="{TEAL}" stroke-width="0.35" fill="none" stroke-dasharray="1 0.7"/>')
    e.append(arrow(66.5, 24.4, 68.2, 25, TEAL, 0.35))
    e += lines(50.5, 17.5, ["① 가게가 동네의", "편의성에 영향을 줌"], 7, 700, TEAL, "middle", 1.25)
    e.append(f'<path d="M68 35 Q50.5 41 33 35" stroke="{ORANGE}" stroke-width="0.35" fill="none" stroke-dasharray="1 0.7"/>')
    e.append(arrow(34.5, 35.6, 32.8, 35, ORANGE, 0.35))
    e += lines(50.5, 42.6, ["② 가게가 변화 중인", "동네를 골라 들어감"], 7, 700, ORANGE, "middle", 1.25)
    # 가설 ③ 교통·일자리 → 둘 모두
    el, _ = pic(h, "지하철", 43, 0, 11, 9); e.append(el)
    el, _ = pic(h, "오피스", 57.5, 0, 11, 9); e.append(el)
    e.append(t(50.5, 11.6, "③ 교통·일자리 변화가 둘 모두에 영향", 7, 700, K80))
    e.append(f'<path d="M38 5 Q24 6 22 20" stroke="{K80}" stroke-width="0.3" fill="none" stroke-dasharray="1 0.7"/>')
    e.append(arrow(22.3, 18.5, 22, 20.5, K80, 0.3))
    e.append(f'<path d="M63 5 Q77 6 79 20" stroke="{K80}" stroke-width="0.3" fill="none" stroke-dasharray="1 0.7"/>')
    e.append(arrow(78.7, 18.5, 79, 20.5, K80, 0.3))
    e.append(title(56, "함께 나타났다고 원인일까?"))
    e.append(note(60.8, "• 두 일이 함께 나타나는 상관관계만으로는 한 일이 다른 일의 원인인 인과관계를 확정할 수 없다."))
    return e

# ── 6-4 맹모삼천지교와 맹모단기지교 4컷 ─────────────────
def fig_6_4(h):
    e = []
    P = {"1": (8, 8, 754, 494), "2": (778, 8, 750, 494), "3": (8, 518, 754, 498), "4": (778, 518, 750, 498)}
    caps = {"1": ["무덤 가까이 살 때", "장례 치르는 모습을 흉내 내며 놀았다"],
            "2": ["시장 가까이 살 때", "물건을 사고파는 모습을 흉내 냈다"],
            "3": ["학교 가까이 살 때", "예절을 따라 하며 놀자 그곳에 머물렀다"],
            "4": ["짜던 베를 끊으며", "배움을 그만두는 것은 이와 같다고 가르쳤다"]}
    pw, gap = 49.5, 2
    pos = {"1": (0, 0), "2": (pw + gap, 0), "3": (0, 44), "4": (pw + gap, 44)}
    for k, (x, y) in pos.items():
        el, ph = crop(h["s64"], P[k], x, y, pw, multiply=False); e.append(el)
        e.append(badge(x + 3.2, y + 3.2, k, TEAL if k != "4" else ORANGE))
        e.append(t(x, y + ph + 3.6, caps[k][0], 7.5, 700, K80, "start"))
        e.append(t(x, y + ph + 7.0, caps[k][1], 7, 400, K80, "start"))
    for x, y, s, c in ((0, 89.8, "①~③ 맹모삼천지교(孟母三遷之敎)", TEAL), (pw + gap, 89.8, "④ 맹모단기지교(孟母斷機之敎)", ORANGE)):
        e.append(t(x, y, s, 7.5, 700, c, "start"))
    e.append(title(97.5, "맹자의 어머니 이야기는 무엇을 가르치려 했을까?"))
    e.append(note(102.3, "• 맹자가 살던 때보다 200여 년 뒤 한나라 때의 『열녀전』 등에 전하는 옛이야기를 재구성한 그림. 실제 이사 기록이 아니다."))
    return e

# ── 6-5 브역대신공평초 ──────────────────────────────
def fig_6_5(h):
    e = []
    items = [("브", "브랜드", "정문"), ("역", "역세권", "지하철"), ("대", "대단지", "대단지"), ("신", "신축", "신축"),
             ("공", "공원", "공원"), ("평", "평지", "평지"), ("초", "초품아", "학교")]
    loc = {"역", "공", "평", "초"}
    cw = 14.43
    for i, (ch, nm, k) in enumerate(items):
        cx = cw / 2 + i * cw
        col = ORANGE if ch in loc else TEAL
        e.append(f'<circle cx="{cx:.2f}" cy="4.2" r="3.6" fill="{col}"/>')
        e.append(t(cx, 6.0, ch, 10, 700, "#fff"))
        el, b = pic(h, k, cx, 9.5, 13, 10); e.append(el)
        e.append(t(cx, 24.5, nm, 7.5, 700, K80))
    # 입지 조건 묶음 표시(역·공·평·초)
    e += [f'<path d="M{cw*1+1:.2f} 27 V28.5 H{cw*2-1:.2f} V27" stroke="{ORANGE}" stroke-width="0.3" fill="none"/>',
          f'<path d="M{cw*4+1:.2f} 27 V28.5 H{cw*7-1:.2f} V27" stroke="{ORANGE}" stroke-width="0.3" fill="none"/>']
    e.append(t(cw * 1.5, 32, "입지 조건", 7, 700, ORANGE))
    e.append(t(cw * 5.5, 32, "입지 조건", 7, 700, ORANGE))
    el, b = pic(h, "학생", 7, 35.5, 10, 10); e.append(el)
    e += lines(14, 39.2, ["“나에게는 어떤 조건이 가장 중요할까?”", "휠체어·유아차 이용자, 청소년, 돌봄이 필요한 가족마다 다를 수 있다."], 7.5, 700, K80, "start", 1.45)
    e.append(title(52, "브역대신공평초, 일곱 글자 풀이"))
    e.append(note(56.8, "• 사람들이 아파트를 고를 때 자주 따지는 조건을 묶은 줄임말. 법으로 정한 기준도, 모든 사람에게 맞는 점수표도 아니다."))
    return e

FIGS = {"6-1": ("도6-1_도시계획3단계_v1", 57, fig_6_1), "6-2": ("도6-2_카페와집값_v1", 64, fig_6_2),
        "6-4": ("도6-4_맹모이야기4컷_v1", 109, fig_6_4), "6-5": ("도6-5_브역대신공평초_v1", 61, fig_6_5)}

if __name__ == "__main__":
    for k in (sys.argv[1:] or FIGS):
        name, H, fn = FIGS[k]
        write(name, W, H, fn, IM); print(name, W, H)
