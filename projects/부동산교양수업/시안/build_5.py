# 제5장 도판 시안: 5-1 중개사 / 5-2 청약 흐름 / 5-3 가점제 표 / 5-4 용도지역 / 5-5 재건축·재개발 / 5-6 블록도 / 5-7 세계의 집(사진 자리)
# 사용: python3 -I build_5.py [5-1 ...]
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *
from build_3 import C, pic, arrow, note, title, IM as IM3

IM = dict(IM3, s5="illust/5장_항목그림_v1.png", s55="illust/도5-5_재건축재개발_v1.png")
C.update({"개업": ("s5", (45, 80, 285, 385)), "소속": ("s5", (405, 75, 315, 390)), "보조원": ("s5", (785, 65, 385, 395)),
          "자격증": ("s5", (1195, 85, 290, 315)), "폰": ("s5", (85, 560, 195, 345)), "추첨": ("s5", (415, 600, 285, 295)),
          "공사": ("s5", (775, 540, 340, 375)), "입주": ("s5", (1165, 545, 340, 395))})
W = 101
K60 = "#666666"

# ── 5-1 공인중개사와 중개보조원 ──────────────────────
def fig_5_1(h):
    e = []
    el, _ = pic(h, "자격증", 7, 0, 10, 10); e.append(el)
    e.append(t(14, 4.4, "사무소에서 확인할 것", 8, 700, K80, "start"))
    e.append(t(14, 8.4, "등록증 · 자격증 · 명함의 직함", 7.5, 400, K80, "start"))
    cols = [("개업", "개업공인중개사", TEAL, ["사무소를 등록한 공인중개사", "중개 업무와", "확인·설명에 책임"]),
            ("소속", "소속공인중개사", TEAL, ["자격을 갖추고", "중개 업무 수행"]),
            ("보조원", "중개보조원", ORANGE, ["현장 안내 등 단순 보조", "보조원 신분을 미리 알림", "확인·설명은 대신 못 함"])]
    for i, (k, nm, col, ds) in enumerate(cols):
        cx = 16.8 + i * 33.7
        e.append(rect(cx - 16, 14, 32, 48, "none", col, 0.3, 1.5))
        el, b = pic(h, k, cx, 16.5, 16, 16); e.append(el)
        e.append(t(cx, b + 4, nm, 8.5, 700, col))
        e += lines(cx, b + 8.4, ds, 7, 400, anchor="middle", lead=1.35)
    e.append(title(69, "누가 어떤 일을 할 수 있을까?"))
    e.append(note(73.8, "• 사무소에 있다는 사실만으로 그 사람의 자격과 맡은 일을 알 수는 없다."))
    return e

# ── 5-2 청약에서 입주까지 ──────────────────────────
def fig_5_2(h):
    e = []
    steps = [("폰", ["청약", "신청"]), ("추첨", ["당첨자 선정", "자격 확인"]), ("계약서", ["분양계약", "대금 납부"]),
             ("공사", ["공사", "완료"]), ("입주", ["입주"])]
    for i, (k, lab) in enumerate(steps):
        cx = 10 + i * 20.25
        el, b = pic(h, k, cx, 0, 13, 13); e.append(el)
        e.append(badge(cx, 16.5, str(i + 1), TEAL, r=2))
        e += lines(cx, 22.8, lab, 7.5, 700, anchor="middle", lead=1.25)
        if i < 4: e.append(arrow(cx + 6.2, 16.5, cx + 14, 16.5, K80, 0.3))
    e.append(rect(0, 31, 101, 15, YELLOW_T, "none", 0, 1.5))
    e.append(t(3, 36, "“청약 경쟁률 100 대 1”이란?", 8, 700, K80, "start"))
    e.append(t(3, 41.2, "10집 모집에 1,000건 신청 = 모집한 집 수에 비해 신청 건수가 100배", 7.5, 400, K80, "start"))
    e.append(title(54, "신청과 당첨, 계약은 서로 달라요"))
    e.append(note(58.8, "• 흔한 선분양 아파트의 흐름. 신청 자격과 당첨자를 정하는 방식은 주택과 공급 유형에 따라 다르다."))
    return e

# ── 5-3 가점제 표 (국부론 표 스타일) ───────────────────
def fig_5_3(h):
    e = []
    HEAD, SEP = "#9D9257", "#AA805B"                    # 표_머리 c44m40y76, 표_구분 c38m54y69 (RGB 근사)
    e.append(t(0, 4, "민영주택 일반공급 가점제의 세 가지 기준 (84점 만점)", 8.5, 700, K80, "start", DOC))
    widths = [24, 59, 18]
    xs = [0, 24, 83]
    y = 7
    e.append(rect(0, y, 101, 6, HEAD, "none", 0))
    for x, w, s in zip(xs, widths, ["항목", "기준 내용", "최대 점수"]):
        e.append(t(x + w / 2, y + 4.2, s, 8, 700, "#fff", family=DOC))
    y += 6
    rows = [("무주택 기간", ["주택 소유 이력 등에 따라 계산.", "보통 만 30세부터, 그 전에 혼인했다면", "혼인신고일부터 계산하며", "15년 이상일 때 최고점"], "32점"),
            ("부양가족 수", ["법에서 정한 부양가족에 해당하는", "사람의 수. 함께 산다고 모두", "포함되는 것은 아님"], "35점"),
            ("청약통장 가입 기간", ["규정에 따라 인정되는 가입 기간.", "15년 이상일 때 최고점"], "17점")]
    lh = 8 * PT * 1.45
    for nm, ds, sc in rows:
        rh = 2.6 + len(ds) * lh
        e += lines(xs[0] + widths[0] / 2, y + 4.6, [nm] if len(nm) < 8 else ["청약통장", "가입 기간"], 8, 700, anchor="middle", lead=1.45, family=DOC)
        e += lines(xs[1] + 2.5, y + 4.6, ds, 8, 300, anchor="start", lead=1.45, family=DOC)
        e.append(t(xs[2] + widths[2] / 2, y + 4.6, sc, 8, 700, K80, family=NUM))
        y += rh
        e.append(line(0, y, 101, y, "#BBBBBB", 0.2))
    e.append(line(0, y, 101, y, SEP, 0.5))
    e.append(t(xs[0] + widths[0] / 2, y + 4.6, "총점", 8, 700, K80, family=DOC))
    e.append(t(xs[2] + widths[2] / 2, y + 4.6, "84점", 8, 700, K80, family=NUM))
    y += 6.5
    e.append(line(0, y, 101, y, SEP, 0.5))
    return e

# ── 5-4 용도지역 가상 지도 ─────────────────────────
def fig_5_4(h):
    RES, COM, IND, GRN = "#FFE575", "#F5A3B5", "#AB93C9", "#A4D28C"   # 시안 CMYK의 RGB 근사
    e = ['<defs><pattern id="ind" width="1.6" height="1.6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         f'<line x1="0" y1="0" x2="0" y2="1.6" stroke="#6E5A92" stroke-width="0.3"/></pattern>'
         '<pattern id="grn" width="2.4" height="2.4" patternUnits="userSpaceOnUse">'
         '<circle cx="1.2" cy="1.2" r="0.45" fill="#5E8F49"/></pattern></defs>']
    M = 68
    e.append(rect(0, 0, M, 58, RES, K60, 0.25))
    e.append(f'<path d="M0 0 H30 L25 13 L12 20 L0 21 Z" fill="{GRN}"/><path d="M0 0 H30 L25 13 L12 20 L0 21 Z" fill="url(#grn)"/>')
    e.append(rect(31, 20, 22, 16, COM, "none", 0))
    e.append(f'<path d="M42 38 H{M} V58 H34 V46 Z" fill="{IND}"/><path d="M42 38 H{M} V58 H34 V46 Z" fill="url(#ind)"/>')
    e.append(f'<path d="M46 40 H62 V52 H46 Z" fill="none" stroke="{RED}" stroke-width="0.45" stroke-dasharray="1.2 0.8"/>')
    for d in (f"M0 28 H{M}", "M38 0 V58", "M0 44 H34", f"M53 10 H{M}"):
        e.append(f'<path d="{d}" stroke="#fff" stroke-width="1.8"/>')
    e += [t(9, 11, "녹지지역", 7.5, 700), t(42, 26.5, "상업지역", 7.5, 700), t(18, 36, "주거지역", 7.5, 700),
          t(60, 25, "주거지역", 7.5, 700), t(56, 56.2, "공업지역", 7.5, 700)]
    el, b = tag(54, 47.3, [("주거지역으로 변경", 7, RED), ("추진 중(확정 전)", 7, RED)], RED); e += el
    e.append(t(M, 61.5, "설명을 위한 가상 지도", 7, 300, K60, "end"))
    lg = [(GRN, "url(#grn)", "녹지지역", "산·공원·농지 등 보전"), (RES, None, "주거지역", "아파트·주택"),
          (COM, None, "상업지역", "가게·음식점·사무실"), (IND, "url(#ind)", "공업지역", "공장 등 산업 시설")]
    for i, (c, p, nm, ds) in enumerate(lg):
        y = 2 + i * 11
        e.append(rect(72, y, 5, 5, c, K60, 0.2, 0.6))
        if p: e.append(rect(72, y, 5, 5, p, "none", 0, 0.6))
        e.append(t(79, y + 3.0, nm, 8, 700, K80, "start"))
        e.append(t(79, y + 6.6, ds, 7, 400, K80, "start"))
    e.append(t(72, 49, "→ 미션! 문제 3", 7, 700, RED, "start"))
    e.append(title(69, "지도 위의 색은 그 땅을 어떻게 쓸 수 있는지 정한 규칙이에요."))
    e.append(note(73.8, "• 실제 용도지역은 더 잘게 나뉘며, 지역마다 지을 수 있는 건물의 종류와 규모가 다르다."))
    return e

# ── 5-5 재건축과 재개발 ────────────────────────────
def fig_5_5(h):
    e = []
    P = {"재건축_전": (8, 8, 754, 494), "재개발_전": (778, 8, 750, 494), "재건축_후": (8, 518, 754, 498), "재개발_후": (778, 518, 750, 498)}
    pw = 41
    for side, x in (("재건축", 0), ("재개발", 60)):
        e.append(t(x + pw / 2, 4.6, side, 9.5, 700, TEAL if side == "재건축" else ORANGE))
        el, ph = crop(h["s55"], P[side + "_전"], x, 7, pw, multiply=False); e.append(el)
        e.append(badge(x + 3, 10, "전", K60, r=2.2))
        e.append(arrow(x + pw / 2, 7 + ph + 0.8, x + pw / 2, 7 + ph + 4.6, K80, 0.35))
        el, ph2 = crop(h["s55"], P[side + "_후"], x, 7 + ph + 5.4, pw, multiply=False); e.append(el)
        e.append(badge(x + 3, 7 + ph + 8.4, "후", TEAL if side == "재건축" else ORANGE, r=2.2))
    yb = 7 + ph + 5.4 + ph2
    # 가운데 '기반시설' 칸
    e.append(rect(42.5, 7, 16, yb - 7, "#F4F4F4", "none", 0, 1.2))
    e.append(t(50.5, 13, "기반시설", 8, 700, K80))
    e += lines(50.5, 17.2, ["도로·상하수도", "공원·주차장"], 7, 400, anchor="middle", lead=1.3)
    e.append(arrow(50.5, 24, 44, 24, TEAL, 0.3)); e += lines(50.5, 28.5, ["갖춰져", "있음"], 7, 700, TEAL, "middle", 1.3)
    e.append(arrow(50.5, 39, 57, 39, ORANGE, 0.3)); e += lines(50.5, 43.5, ["부족함", "→ 함께", "정비"], 7, 700, ORANGE, "middle", 1.3)
    # 공통 띠
    y = yb + 2.5
    e.append(rect(0, y, 101, 16, YELLOW_T, "none", 0, 1.2))
    e.append(t(3, y + 4.4, "공사하는 동안 살던 사람들은 이사해야 해요", 8, 700, K80, "start"))
    e += lines(3, y + 8.6, ["집주인(조합원)은 새 집으로 돌아올 수 있지만", "세입자와 가게는 돌아오기 어려울 수 있음"], 7, 400, lead=1.3)
    e += lines(60, y + 8.6, ["재개발: 정해진 날짜 전부터 살거나", "장사한 세입자에게 이사 비용·", "임대주택 기회·영업 보상"], 7, 700, ORANGE, "start", 1.3)
    y += 16
    e.append(title(y + 6, "새 건물만큼, 그곳에 살던 사람의 생활이"))
    e.append(title(y + 10.6, "어떻게 이어지는지도 함께 보아요."))
    return e

# ── 5-6 건폐율·용적률 블록 ──────────────────────────
def fig_5_6(h):
    e = []
    s, c30, s30 = 1.55, math.cos(math.radians(30)), 0.5
    def P(ox, oy, x, y, z): return (ox + (x - y) * c30 * s, oy + (x + y) * s30 * s - z * s)
    def poly(pts, fill, stroke=K80, sw=0.2):
        d = "M" + " L".join(f"{a:.2f} {b:.2f}" for a, b in pts) + " Z"
        return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    def building(ox, oy, fx, fy, floors, cols):
        out = [poly([P(ox, oy, 0, 0, 0), P(ox, oy, 10, 0, 0), P(ox, oy, 10, 10, 0), P(ox, oy, 0, 10, 0)], "#E8E8E8", K60, 0.25)]
        x0, y0 = (10 - fx) / 2, (10 - fy) / 2
        x1, y1 = x0 + fx, y0 + fy
        for k in range(floors):
            z0, z1 = k * 3, (k + 1) * 3
            out.append(poly([P(ox, oy, x1, y0, z0), P(ox, oy, x1, y1, z0), P(ox, oy, x1, y1, z1), P(ox, oy, x1, y0, z1)], cols[0]))   # 오른쪽 면
            out.append(poly([P(ox, oy, x0, y1, z0), P(ox, oy, x1, y1, z0), P(ox, oy, x1, y1, z1), P(ox, oy, x0, y1, z1)], cols[1]))   # 왼쪽 앞면
        zt = floors * 3
        out.append(poly([P(ox, oy, x0, y0, zt), P(ox, oy, x1, y0, zt), P(ox, oy, x1, y1, zt), P(ox, oy, x0, y1, zt)], cols[2]))
        return out
    oy = 30
    e += building(25, oy, 10, 5, 4, ("#7FBFC4", "#2A8F99", "#CFE8EA"))
    e += building(76, oy, 8, 5, 5, ("#F9C979", "#F5A21B", "#FCDDB0"))
    for cx, nm, a, b, col in ((25, "A", "층마다 50㎡ × 4층 = 200㎡", "건폐율 50% · 용적률 200%", TEAL),
                              (76, "B", "층마다 40㎡ × 5층 = 200㎡", "건폐율 40% · 용적률 200%", ORANGE)):
        e.append(t(cx, oy + 20.5, f"{nm}  대지 100㎡", 8.5, 700, col))
        e.append(t(cx, oy + 24.6, a, 7.5, 400))
        e.append(t(cx, oy + 28.6, b, 8, 700, col))
    e.append(title(oy + 37, "용적률이 같아도 건물 모양은 다를 수 있어요"))
    e.append(note(oy + 41.8, "• 각 층이 같은 넓이이고 모든 층이 용적률 계산에 포함된다고 가정. 블록은 대지·바닥 넓이와 층수에 비례하게 그렸다(층 높이는 같게 둠)."))
    return e

# ── 5-7 세계의 재밌는 집 (사진 자리) ───────────────────
def fig_5_7(h):
    e = []
    items = [("안틸리아", "인도 뭄바이", "27층 규모의 개인 주택"), ("케레트 하우스", "폴란드 바르샤바", "내부 폭 72~122cm"),
             ("클라인 보틀 하우스", "호주", "접힌 벽·지붕과 안뜰")]
    for i, (nm, where, ds) in enumerate(items):
        x = i * 34
        e.append(rect(x, 0, 33, 25, "#fff", K60, 0.3, 1, 'stroke-dasharray="1.2 0.8"'))
        e.append(t(x + 16.5, 13.5, "사진 자리", 7.5, 700, K60))
        e.append(t(x + 16.5, 30, nm, 8.5, 700, K80))
        e.append(t(x + 16.5, 34, where, 7, 400))
        e.append(t(x + 16.5, 37.6, ds, 7, 400))
    e.append(title(46, "크고 독특한 집이 모두에게 편한 집일까?"))
    return e

FIGS = {"5-1": ("도5-1_중개사역할_v1", 77, fig_5_1), "5-2": ("도5-2_청약흐름_v1", 62, fig_5_2),
        "5-3": ("도5-3_가점제표_v1", 64, fig_5_3), "5-4": ("도5-4_용도지역_v1", 77, fig_5_4),
        "5-5": ("도5-5_재건축재개발_v1", 98, fig_5_5), "5-6": ("도5-6_건폐율용적률_v1", 78, fig_5_6),
        "5-7": ("도5-7_세계의집_v1", 49, fig_5_7)}

if __name__ == "__main__":
    for k in (sys.argv[1:] or FIGS):
        name, H, fn = FIGS[k]
        write(name, W, H, fn, IM); print(name, W, H)
