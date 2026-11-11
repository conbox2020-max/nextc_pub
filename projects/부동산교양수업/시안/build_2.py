# 제2장 도판 시안: 2-1(가상 등기 서류 펼침면), 2-2(면적 평면도), 2-3(등기 vs 별도 확인), 2-4(화곡동 4컷), 2-5(연표)
# 사용: python3 -I build_2.py [2-1 2-2 ...]   인자가 없으면 전부
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *

SHEET = {"sheet": "illust/2장_항목그림_v1.png"}
S = {  # 2장_항목그림_v1.png 안의 항목 위치(px)
    "등기": (40, 105, 325, 350), "신분증": (425, 170, 300, 205), "도장": (780, 145, 340, 270),
    "빌라": (1160, 90, 345, 360), "세금": (20, 555, 365, 320), "옛장부": (445, 555, 260, 340),
    "법전": (805, 555, 290, 345), "컴퓨터": (1145, 580, 370, 315)}
W = 101

# ── 2-4 화곡동 사건 4컷 ─────────────────────────────
def fig_2_4(h):
    e = []
    P = {"①": (8, 8, 754, 494), "②": (778, 8, 750, 494), "③": (8, 518, 754, 498), "④": (778, 518, 750, 498)}
    caps = {"①": ["전 주인이 집을 담보로 은행에서", "돈을 빌림 → 을구에 근저당권 기록"],
            "②": ["전 주인이 서류를 위조해 근저당권을", "말소 → 빚은 그대로인데 기록만 지워짐"],
            "③": ["부부가 남은 근저당권이 없는 것을", "확인하고 집을 삼"],
            "④": ["위조가 드러나 은행이 소송 → 판결로", "근저당권 기록이 되살아나 부부의 집이", "전 주인의 빚을 담보하게 됨"]}
    pw, gap = 49.5, 2
    pos = {"①": (0, 0), "②": (pw + gap, 0), "③": (0, 46), "④": (pw + gap, 46)}
    for k, (x, y) in pos.items():
        el, ph = crop(h["img"], P[k], x, y, pw, multiply=False)
        e.append(el)
        e.append(badge(x + 3.2, y + 3.2, k.translate(str.maketrans("①②③④", "1234")), RED if k in "②④" else TEAL))
        e += lines(x, y + ph + 3.6, caps[k], 7, 400)
    # ③ 확대 상자: '말소사항 포함'으로 발급하면 지워진 근저당권도 줄이 그어진 채 보인다
    bx, by, bw, bh = 20.5, 46 + 20.2, 28, 11.4
    e.append(rect(bx, by, bw, bh, "#fff", K80, 0.25, 1))
    e.append(t(bx + 1.2, by + 3.0, "말소사항 포함으로 발급", 7, 700, K80, "start"))
    e.append(t(bx + 1.2, by + 6.4, "근저당권설정", 7, 400, K80, "start"))
    e.append(line(bx + 1.0, by + 5.2, bx + 16.2, by + 5.2, RED, 0.3))
    e.append(t(bx + 1.2, by + 9.8, "말소 20○○.○.○", 7, 400, K80, "start"))
    e.append(f'<ellipse cx="{bx+12.9:.2f}" cy="{by+8.9:.2f}" rx="6.6" ry="2.2" fill="none" stroke="{RED}" stroke-width="0.3"/>')
    e.append(t(W / 2, 99.5, "기록이 지워졌다고 빚까지 사라진 것은 아니에요.", 10))
    e.append(t(0, 104.3, "• 실제 서류가 아닌 설명용 재구성. 2017년 매입, 2022년 대법원 확정 사건(본문 참조).", 7, 300, anchor="start"))
    return e

# ── 2-3 등기에서 확인하는 것 vs 따로 확인할 것 ─────────
def fig_2_3(h):
    e = []
    # 왼쪽 카드
    e.append(rect(0, 0, 38, 50, "none", TEAL, 0.25, 1.5))
    e.append(t(19, 6.2, "등기 기록으로 확인", 8.5, fill=TEAL))
    el, _ = crop(h["sheet"], S["등기"], 9, 9, 20); e.append(el)
    e += lines(4, 35.5, ["• 등록된 소유자", "• 등록된 권리"], 7.5, 700)
    e.append(t(6.4, 35.5 + 2 * 7.5 * PT * 1.35, "(근저당권 등)", 7.5, 700, anchor="start"))
    # 오른쪽 카드
    e.append(rect(41, 0, 60, 50, "none", ORANGE, 0.25, 1.5))
    e.append(t(71, 6.2, "따로 확인할 것", 8.5, fill=ORANGE))
    items = [("신분증", ["계약 상대방의", "신분"]), ("도장", ["임대할", "권한"]),
             ("빌라", ["건물의 행정 정보", "(건축물대장)"]), ("세금", ["세금", "(납세증명서 등)"])]
    for i, (k, cap) in enumerate(items):
        cx = 41 + 15 + (i % 2) * 30; cy = 9.5 + (i // 2) * 20.5
        bw, bh = S[k][2], S[k][3]
        w = min(13, 11 * bw / bh)                      # 높이 11mm 넘지 않게
        el, ih = crop(h["sheet"], S[k], cx - w / 2, cy, w); e.append(el)
        e += lines(cx, cy + 14.8, cap, 7, 700, anchor="middle", lead=1.25)
    e.append(t(W / 2, 57.0, "중요한 공식 기록이지만,", 10))
    e.append(t(W / 2, 61.6, "그것만으로 모든 권리가 보장되지는 않아요.", 10))
    return e

# ── 2-5 땅의 기록은 어떻게 바뀌어 왔을까 ──────────────
def fig_2_5(h):
    e = []
    nodes = [("옛장부", "조선시대", ["양안: 토지대장", "문기: 거래 문서"]),
             ("등기", "일제강점기", ["조선부동산등기령", "에 따른 등기"]),
             ("법전", "1960년", ["부동산등기법", "제정"]),
             ("컴퓨터", "1992~2002년", ["등기 전산화", "시작·전국 완료"])]
    e.append(line(3, 21.5, 98, 21.5, K80, 0.3))
    e.append(f'<path d="M98 20.3 L100.5 21.5 L98 22.7 Z" fill="{K80}"/>')
    for i, (k, yr, cap) in enumerate(nodes):
        cx = 12.6 + i * 25.3
        el, ih = crop(h["sheet"], S[k], cx - 7, 1.5, 14 if k != "컴퓨터" else 15.5)
        e.append(el)
        e.append(f'<circle cx="{cx}" cy="21.5" r="1.3" fill="{TEAL}" stroke="#fff" stroke-width="0.3"/>')
        e.append(t(cx, 27.5, yr, 8.5, fill=TEAL))
        e += lines(cx, 31.6, cap, 7, 400, anchor="middle", lead=1.3)
    e.append(t(W / 2, 43.5, "땅의 기록은 어떻게 바뀌어 왔을까?", 10))
    e.append(t(0, 48.2, "• 양안·문기는 오늘날의 등기와 같은 제도는 아니다.", 7, 300, anchor="start"))
    return e

FIGS = {"2-4": ("도2-4_화곡동4컷_v1", 106, fig_2_4, {"img": "illust/도2-4_화곡동4컷_v1.png"}),
        "2-3": ("도2-3_등기와별도확인_v1", 64, fig_2_3, SHEET),
        "2-5": ("도2-5_등기역사연표_v1", 50, fig_2_5, SHEET)}


# ── 2-1 가상 등기사항전부증명서 (펼침면 2쪽) ───────────
K10, K60 = "#E6E6E6", "#666666"
DW = 72                                   # 서류 폭, 오른쪽 27mm는 설명 태그 자리

def table(x, y, widths, head, rows, rh, pt=7):
    """머리글 + 행. rows: [[줄 목록, ...], ...]. 반환: (요소, 칸 좌표 dict[(r,c)] = (x, y, w, h))"""
    e, cells = [], {}
    nl = max(len(h_) if isinstance(h_, list) else 1 for h_ in head)
    hh = 1.7 + nl * pt * PT * 1.25
    xx = x
    for c, (w, h_) in enumerate(zip(widths, head)):
        e.append(rect(xx, y, w, hh, K10, K60, 0.15))
        e += lines(xx + w / 2, y + 3.2, h_ if isinstance(h_, list) else [h_], pt, 700, K80, "middle", 1.25, DOC)
        xx += w
    yy = y + hh
    for r, (row, h_) in enumerate(zip(rows, rh)):
        xx = x
        for c, (w, cell) in enumerate(zip(widths, row)):
            e.append(rect(xx, yy, w, h_, "#fff", K60, 0.15))
            e += lines(xx + w / 2, yy + 3.3, cell, pt, 400, K80, "middle", 1.3, DOC)
            cells[(r, c)] = (xx, yy, w, h_)
            xx += w
        yy += h_
    return e, cells, yy

def section(x, y, title, sub, hint):
    return [t(x, y, f"【 {title} 】 ( {sub} )", 7.5, 700, K80, "start", DOC), t(DW - 1.5, y, hint, 7, 700, TEAL, "end")]

def virtual_tag(x, y):
    s = "설명을 위해 주요 칸만 간추린 가상 서류"
    w = em(s) * 7 * PT + 3
    return [rect(x, y, w, 4.6, K60, "none", 0, 0.8), t(x + w / 2, y + 3.25, s, 7, 700, "#fff")]

def side_tag(y, rows, col, tx, ty):
    el, b = tag(87.5, y, [(r, 7, col if i == 0 else K80) for i, r in enumerate(rows)], col)
    return el + [leader(b[0], y, tx, ty, col)]

def fig_2_1L(h):
    e = virtual_tag(0, 0)
    frame_at = len(e)
    e.append(t(DW / 2, 12.2, "등기사항전부증명서", 9, 700, K80, family=DOC))
    e.append(t(DW / 2, 15.8, "(말소사항 포함) - 집합건물", 7, 400, K80, family=DOC))
    e.append(t(2, 21.2, "[집합건물] 가람시 새봄로 10 새봄빌라 제3층 제301호", 7, 700, K80, "start", DOC))
    e += section(2, 27.0, "표 제 부", "1동의 건물의 표시", "어떤 부동산인가?")
    el, c1, yy = table(2, 28.6, [11, 30, 27], ["표시번호", "소재지번, 건물명칭 및 번호", "건물내역"],
                       [[["1"], ["가람시 새봄로 10", "새봄빌라"], ["철근콘크리트구조", "3층 다세대주택"]]], [9])
    e += el
    e.append(t(2, yy + 4.2, "( 대지권의 목적인 토지의 표시 )", 7, 700, K80, "start", DOC))
    el, c2, yy = table(2, yy + 5.6, [11, 29, 12, 16], ["표시번호", "소재지번", "지 목", "면 적"],
                       [[["1"], ["가람시 새봄로 10"], ["대"], ["○○○㎡"]]], [6])
    e += el
    gap_y = yy + 1.6                                   # 대지권 표와 다음 제목 사이 틈
    e += section(2, yy + 5.0, "표 제 부", "전유부분의 건물의 표시", "")
    el, c3, yy = table(2, yy + 6.6, [11, 22, 35], ["표시번호", "건물번호", "건물내역"],
                       [[["1"], ["제3층 제301호"], ["철근콘크리트구조", "42㎡"]]], [9])
    e += el
    # 강조 표시
    x_, y_, w_, h_ = c2[(0, 2)]
    e.append(f'<circle cx="{x_+w_/2:.2f}" cy="{y_+h_/2-0.6:.2f}" r="2.4" fill="none" stroke="{ORANGE}" stroke-width="0.35"/>')
    x3, y3, w3, h3 = c3[(0, 2)]
    l2 = y3 + 3.3 + 7 * PT * 1.3                      # 두 번째 줄 기준선
    e.append(rect(x3 + w3 / 2 - 5.5, l2 - 2.6, 11, 3.6, "none", TEAL, 0.35, 0.6))
    # 설명 태그
    e += side_tag(21.0, ["① 주소·동·호수가", "직접 본 집과 같은가?"], TEAL, 70.5, 20.4)
    e += side_tag(l2 - 0.8, ["② 전유부분 면적", "= 전용면적 42㎡"], TEAL, x3 + w3 / 2 + 5.5, l2 - 0.8)
    # 지목 확대 상자
    e.insert(frame_at, rect(0, 6.5, DW, yy + 3 - 6.5, "#FAFAFA", K60, 0.25))
    by = yy + 6
    e.append(rect(0, by, 101, 22, "#fff", ORANGE, 0.3, 1.5, 'stroke-dasharray="1.2 0.8"'))
    cxj, cyj = x_ + w_ / 2, y_ + h_ / 2 - 0.6        # 지목 동그라미 → 서류 오른쪽 밖 → 확대 상자 (표를 가로지르지 않게)
    e.append(f'<path d="M{cxj:.2f} {cyj+2.4:.2f} V{gap_y:.2f} H{DW+3:.2f} V{by:.2f}" stroke="{ORANGE}" stroke-width="0.2" fill="none"/>')
    e.append(t(3, by + 5.0, "토지 기록 확대 — 지목", 8.5, 700, ORANGE, "start"))
    e += lines(3, by + 9.6, ["지목: 토지의 주된 쓰임새를 나누어 등록한 종류",
                             "전(밭) · 답(논) · 임야(산림) · 대(주택·상가 등의 부지)",
                             "지목이 '대'라도 원하는 건물을 모두 지을 수 있는 것은 아니다.",
                             "용도지역 등 다른 규정도 함께 확인한다."], 7, 400, lead=1.38)
    return e

def fig_2_1R(h):
    e = virtual_tag(0, 0)
    frame_at = len(e)
    widths = [8, 11, 13, 13, 23]
    head = [["순위", "번호"], ["등기", "목적"], ["접 수"], ["등기원인"], ["권리자 및", "기타사항"]]
    e += section(2, 13.0, "갑 구", "소유권에 관한 사항", "")
    e.append(t(2 + DW - 4, 17.0, "소유자로 누가 적혀 있나?", 7, 700, TEAL, "end"))
    el, ca, yy = table(2, 18.6, widths, head,
                       [[["1"], ["소유권", "이전"], ["20○○년", "○월○일", "제○○호"], ["20○○년", "○월○일", "매매"], ["소유자", "김가람"]]], [12.5])
    e += el
    e += section(2, yy + 7.0, "을 구", "소유권 이외의 권리에 관한 사항", "")
    e.append(t(2 + DW - 4, yy + 11.0, "그 밖에 어떤 권리가 있나?", 7, 700, TEAL, "end"))
    el, cb, yy2 = table(2, yy + 12.6, widths, head,
                        [[["1"], ["근저당권", "설정"], ["20○○년", "○월○일", "제○○호"], ["20○○년", "○월○일", "설정계약"],
                          ["채권최고액", "금24,000,000원", "근저당권자", "새봄은행"]]], [16])
    e += el
    e.append(t(2 + (DW - 4) / 2, yy2 + 6, "-- 이 하 여 백 --", 7, 400, K60, family=DOC))
    e.insert(frame_at, rect(0, 6.5, DW, yy2 + 9 - 6.5, "#FAFAFA", K60, 0.25))
    # 강조
    x, y, w, hh = ca[(0, 4)]; e.append(rect(x + 0.8, y + 4.2, w - 1.6, 4.3, "none", TEAL, 0.35, 0.6))
    xb, yb, wb, hb = cb[(0, 4)]; e.append(rect(xb + 0.4, yb + 0.6, wb - 0.8, 7.0, "none", ORANGE, 0.35, 0.6))
    xc, yc, wc, hc = ca[(0, 2)]; xd = ca[(0, 3)][0]
    e.append(rect(xc + 0.6, yc + 0.6, wc + ca[(0, 3)][2] - 1.2, 6.6, "none", K60, 0.3, 0.6, 'stroke-dasharray="0.8 0.6"'))
    # 설명 태그
    e += side_tag(y + 6.4, ["③ 소유자 이름을", "신분증과 대조"], TEAL, x + w - 0.8, y + 6.4)
    e.append(badge(xc + 0.6, yc + 0.6, "4", K60, r=1.7))          # ④ 표시는 번호로 대응(지시선 없음)
    el, _ = tag(87.5, yc - 7.5, [("④ 원인일자와", 7, K80), ("접수일자는", 7, K80), ("다를 수 있다", 7, K80)], K80); e += el
    e += side_tag(yb + 5.0, ["⑤ 채권최고액 ≠", "남은 빚", "(담보의 최대 범위)"], ORANGE, xb + wb - 0.4, yb + 3.0)
    e.append(t(W / 2, 90.0, "등기사항전부증명서의 세 칸: 표제부·갑구·을구", 10))
    e += lines(0, 95.0, ["• 설명을 위해 주요 칸만 간추린 가상 서류. 주소·인명·은행명은 모두 가상이며,", "  실제 서류의 개인정보는 쓰지 않았다."], 7, 300)
    return e

# ── 2-2 전용·공급·계약면적 ─────────────────────────
A2, A3 = 10, 8             # ②주거공용·③기타공용 가상 수치(㎡). 2026-11-11 편집자 확정(A안: 공급 52㎡, 계약 60㎡). None이면 점선 자리표시

def fig_2_2(h):
    e = ['<defs><pattern id="hatch" width="1.6" height="1.6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         f'<line x1="0" y1="0" x2="0" y2="1.6" stroke="{ORANGE}" stroke-width="0.25"/></pattern>'
         '<pattern id="dots" width="1.6" height="1.6" patternUnits="userSpaceOnUse">'
         f'<circle cx="0.8" cy="0.8" r="0.28" fill="{ORANGE}"/></pattern></defs>']
    # 3층 평면
    e.append(t(0, 3.0, "3층 평면 (위에서 내려다본 그림)", 7, 700, K60, "start"))
    e.append(rect(0, 5, 56, 40, "none", K60, 0.25))
    e.append(rect(0.6, 5.6, 38, 38.8, TEAL_T, "none", 0))                       # ① 전유
    e.append(rect(39.2, 5.6, 16.2, 38.8, YELLOW_T, "none", 0))                  # ② 주거공용
    e.append(rect(39.2, 5.6, 16.2, 38.8, "url(#hatch)", "none", 0))
    for i in range(9):                                                         # 계단
        e.append(line(40.5, 8 + i * 2.2, 54, 8 + i * 2.2, K60, 0.2))
    e.append(rect(40.5, 8, 13.5, 17.6, "none", K60, 0.2))
    W_ = K80
    e += [line(0.6, 5.6, 38.6, 5.6, W_, 0.6), line(38.6, 5.6, 38.6, 36, W_, 0.6), line(38.6, 40.5, 38.6, 44.4, W_, 0.6),
          line(0.6, 5.6, 0.6, 44.4, W_, 0.6), line(0.6, 44.4, 38.6, 44.4, W_, 0.6),
          line(18, 5.6, 18, 22, W_, 0.4), line(0.6, 25, 12, 25, W_, 0.4), line(15, 25, 18, 25, W_, 0.4),
          line(12, 31, 12, 44.4, W_, 0.4), line(0.6, 31, 12, 31, W_, 0.4)]
    e += [t(9.3, 16.5, "방", 7.5, 700), t(27, 22, "거실·부엌", 7.5, 700), t(6.3, 38.6, "화장실", 7), t(46.8, 33.5, "계단·복도", 7, 700)]
    e.append(t(36.4, 39.2, "현관", 7, 400, anchor="end"))
    # 1층 주차장
    e.append(t(0, 50.6, "1층 주차장", 7, 700, K60, "start"))
    e.append(rect(0, 52, 56, 11, ORANGE_T, K60, 0.25))
    e.append(rect(0, 52, 56, 11, "url(#dots)", "none", 0))
    for i in range(1, 6): e.append(line(i * 9.3, 52, i * 9.3, 58, K60, 0.25))
    e += [badge(4, 9.5, "1", TEAL), badge(51.5, 41, "2", YELLOW, fg=K80), badge(4, 59.5, "3", ORANGE)]
    e.append(t(51.5, 42.05, "", 1))
    # 막대
    bx, sc = 61, 0.42                         # ① 42㎡ → 17.6mm (가상 축척)
    L1 = 42 * sc
    rows = [("전용면적", "①", [("①", L1, TEAL, None)]),
            ("공급면적", "①+②", [("①", L1, TEAL, None), ("②", (A2 or 0) * sc, YELLOW, "url(#hatch)")]),
            ("계약면적", "①+②+③", [("①", L1, TEAL, None), ("②", (A2 or 0) * sc, YELLOW, "url(#hatch)"),
                                  ("③", (A3 or 0) * sc, ORANGE_T, "url(#dots)")])]
    for i, (nm, fm, segs) in enumerate(rows):
        y = 8 + i * 15
        e.append(t(bx, y, nm, 8.5, 700, K80, "start"))
        e.append(t(bx + 17, y, fm, 7.5, 700, K60, "start", NUM))
        x = bx
        for k, ln, col, pat in segs:
            if ln == 0:                              # 수치 미정: 점선 자리표시
                ln = 7
                e.append(rect(x, y + 2, ln, 5, "none", RED, 0.25, 0, 'stroke-dasharray="0.8 0.6"'))
                e.append(t(x + ln / 2, y + 5.5, "?", 7.5, 700, RED))
            else:
                e.append(rect(x, y + 2, ln, 5, col, "none", 0))
                if pat: e.append(rect(x, y + 2, ln, 5, pat, "none", 0))
                small = ln < 5                       # 좁은 칸(②·③)은 번호를 작게
                e.append(t(x + ln / 2, y + (5.0 if small else 5.5), k, 5.5 if small else 7.5, 700, "#fff" if col == TEAL else K80))
            x += ln
        if A2 is not None and A3 is not None:      # 막대 끝에 합계
            total = 42 + sum(v for kk, v in (("②", A2), ("③", A3)) if any(sg[0] == kk for sg in segs))
            e.append(t(x + 1.2, y + 5.5, f"{total}㎡", 7.5, 700, K80, "start", NUM))
    e.append(t(bx, 52.0, "① 42㎡ = 등기의 전유부분 면적", 7, 700, TEAL, "start"))
    if A2 is None or A3 is None:
        e.append(t(bx, 56.0, "※ 시안: ②·③ 가상 수치 확정 후", 7, 700, RED, "start"))
        e.append(t(bx, 59.4, "   막대 길이를 비례로 조정", 7, 700, RED, "start"))
    else:
        e.append(t(bx, 56.0, f"② 계단·복도 {A2}㎡", 7, 700, K80, "start"))
        e.append(t(bx, 59.4, f"③ 주차장 등 {A3}㎡", 7, 700, K80, "start"))
    e.append(t(W / 2, 70.0, "같은 집이라도 어디까지 더했는지에 따라", 10))
    e.append(t(W / 2, 74.6, "넓이 숫자가 달라져요.", 10))
    e.append(t(0, 79.4, "• 설명을 위한 가상 평면도. ②·③의 숫자는 설명을 위한 가상 수치다.", 7, 300, anchor="start"))
    return e

FIGS.update({"2-1L": ("도2-1_가상등기서류_왼쪽_v1", 110, fig_2_1L, {}),
             "2-1R": ("도2-1_가상등기서류_오른쪽_v1", 101, fig_2_1R, {}),
             "2-2": ("도2-2_면적평면도_v2", 82, fig_2_2, {})})

if __name__ == "__main__":
    for k in (sys.argv[1:] or FIGS):
        if k in FIGS:
            name, H, fn, imgs = FIGS[k]
            write(name, W, H, fn, imgs); print(name, W, H)
