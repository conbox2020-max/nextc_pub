# 제3장 도판 시안: 3-1 월세·전세 / 3-2 갭투자 / 3-3 경매 배당 / 3-4 신탁 / 3-5 대항력·우선변제권 / 3-6 체크리스트 / 3-7 이중계약
# 사용: python3 -I build_3.py [3-1 ...]   인자가 없으면 전부
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *

IM = {"s3": "illust/3장_항목그림_v1.png", "s2": "illust/2장_항목그림_v1.png", "s1": "illust/도1-4_항목그림_v1.png"}
C = {  # (시트, px 박스)
    "세입자": ("s3", (60, 35, 240, 300)), "집주인": ("s3", (435, 30, 270, 305)), "중개사": ("s3", (815, 30, 285, 305)),
    "신탁직원": ("s3", (1215, 35, 240, 300)), "은행직원": ("s3", (60, 360, 250, 285)), "주민센터": ("s3", (405, 380, 345, 230)),
    "법봉": ("s3", (815, 405, 305, 200)), "시세": ("s3", (1170, 435, 330, 195)), "열쇠": ("s3", (70, 710, 240, 235)),
    "계약서": ("s3", (420, 705, 310, 275)), "달력": ("s3", (805, 720, 300, 240)), "보증서": ("s3", (1210, 700, 250, 270)),
    "등기": ("s2", (40, 105, 325, 350)), "신분증": ("s2", (425, 170, 300, 205)), "빌라": ("s2", (1160, 90, 345, 360)),
    "세금": ("s2", (20, 555, 365, 320)), "집": ("s1", (90, 215, 620, 530)), "도장": ("s2", (780, 145, 340, 270))}
W = 101

def pic(h, k, cx, top, maxw, maxh):
    """항목 그림을 가운데 맞춤으로 최대 폭·높이 안에 앉힌다. 반환: (요소, 아래쪽 y)"""
    sh, box = C[k]
    w = min(maxw, maxh * box[2] / box[3])
    el, hh = crop(h[sh], box, cx - w / 2, top, w)
    return el, top + hh

def arrow(x1, y1, x2, y2, col=K80, sw=0.3):
    import math
    a = math.atan2(y2 - y1, x2 - x1); L = 1.6
    p1 = (x2 - L * math.cos(a - 0.45), y2 - L * math.sin(a - 0.45))
    p2 = (x2 - L * math.cos(a + 0.45), y2 - L * math.sin(a + 0.45))
    return (f'<path d="M{x1:.2f} {y1:.2f} L{x2:.2f} {y2:.2f}" stroke="{col}" stroke-width="{sw}"/>'
            f'<path d="M{x2:.2f} {y2:.2f} L{p1[0]:.2f} {p1[1]:.2f} L{p2[0]:.2f} {p2[1]:.2f} Z" fill="{col}"/>')

def note(y, s, width=99):
    """7pt 주석을 판면 폭에 맞춰 낱말 단위로 줄바꿈한다. 둘째 줄부터 들여쓴다."""
    out, cur = [], ""
    for wd in s.split(" "):
        cand = (cur + " " + wd).strip()
        if em(cand) * 7 * PT > width and cur:
            out.append(cur); cur = "  " + wd
        else:
            cur = cand if not cur.startswith("  ") else cur + " " + wd
    out.append(cur)
    return "".join(t(0, y + i * 3.4, ln, 7, 300, anchor="start", extra='xml:space="preserve"') for i, ln in enumerate(out))
def title(y, s): return t(W / 2, y, s, 10)

# ── 3-1 월세 vs 전세: 2년 계약 동안의 돈 ───────────────
def fig_3_1(h):
    e = []
    el, _ = pic(h, "세입자", 6, 0, 12, 12); e.append(el)
    el, _ = pic(h, "집주인", 95, 0, 12, 12); e.append(el)
    e += [t(6, 15.2, "세입자", 7.5), t(95, 15.2, "집주인", 7.5)]
    e.append(arrow(30, 5, 71, 5, TEAL, 0.4)); e.append(t(50.5, 3.6, "내는 돈", 7.5, 700, TEAL))
    e.append(arrow(71, 10, 30, 10, ORANGE, 0.4)); e.append(t(50.5, 13.4, "돌려받는 돈", 7.5, 700, ORANGE))
    x0, x1 = 20, 94
    for i, (nm, big) in enumerate([("월세", False), ("전세", True)]):
        base = 31 + i * 22
        e.append(t(0, base + 1.2, nm, 10, 700, K80, "start"))
        e.append(line(x0, base, x1, base, K80, 0.3))
        e += [line(x0, base - 1, x0, base + 1, K80, 0.3), line(x1, base - 1, x1, base + 1, K80, 0.3)]
        e += [t(x0, base + 4, "계약·입주", 7, 400), t(x1, base + 4, "2년 뒤 종료", 7, 400)]
        dh = 10 if big else 3.5                                   # 막대 높이: 크기 비교용(비례 아님)
        e.append(rect(x0 + 1, base - dh, 5, dh, TEAL, "none", 0))
        e.append(t(x0 + 1, base - dh - 1.3, "큰 보증금" if big else "보증금", 7, 700, TEAL, "start"))
        e.append(rect(x1 - 6, base - dh, 5, dh, ORANGE, "none", 0))
        e.append(t(x1 - 1, base - dh - 1.3, "정산·반환", 7, 700, ORANGE, "end"))
        if big:
            e.append(t((x0 + x1) / 2, base - 2, "매달 월세 없음", 7.5, 700, K40))
        else:
            for m in range(24):
                xm = x0 + 10 + m * (x1 - x0 - 20) / 23
                e.append(rect(xm - 0.5, base - 2, 1.0, 2, TEAL, "none", 0))
            e.append(t((x0 + x1) / 2, base - 4.8, "매달 월세(24번)", 7.5, 700, TEAL))
    e.append(title(64, "2년 계약 동안 돈은 어떻게 오갈까?"))
    e.append(note(68.8, "• 막대 높이는 크기를 비교하기 위한 그림으로, 실제 금액 비율이 아니다."))
    e.append(note(72.2, "• 월세와 전세 모두 대출 이자·관리비 등 별도 비용이 있을 수 있다."))
    return e

# ── 3-2 갭투자: 집값 2억 원의 구성 ───────────────────
def fig_3_2(h):
    e = []
    el, _ = pic(h, "집", 8, 9, 16, 14); e.append(el)
    e.append(t(8, 26.5, "집값 2억 원", 7.5))
    x0, L = 19, 80                          # 2억 원 = 80mm
    s1, s2 = L * 2000 / 20000, L * 18000 / 20000
    y0 = 14
    e.append(rect(x0, y0, s1, 8, ORANGE, "none", 0))
    e.append(rect(x0 + s1, y0, s2, 8, TEAL, "none", 0))
    e.append(t(x0 + s1 + s2 / 2, y0 + 5.4, "세입자 보증금 1억 8천만 원", 8, 700, "#fff"))
    el, _ = pic(h, "집주인", x0 + s1 / 2, 0, 9, 9); e.append(el)
    e.append(leader(x0 + s1 / 2, 9.4, x0 + s1 / 2, y0 + 1.5, ORANGE))
    e.append(t(x0 + s1 + 1.5, 4.0, "집주인 자기 돈", 7.5, 700, ORANGE, "start"))
    e.append(t(x0 + s1 + 1.5, 7.6, "2천만 원", 7.5, 700, ORANGE, "start", NUM))
    by = y0 + 11
    e.append(f'<path d="M{x0+s1:.2f} {by:.2f} V{by+1.5:.2f} H{x0+L:.2f} V{by:.2f}" stroke="{TEAL}" stroke-width="0.3" fill="none"/>')
    e.append(arrow(x0 + s1 + s2 / 2, by + 1.5, x0 + s1 + s2 / 2, by + 5.5, TEAL))
    e.append(t(x0 + s1 + s2 / 2, by + 9.2, "집주인이 나중에 돌려줘야 할 돈: 1억 8천만 원", 8, 700, TEAL))
    e.append(title(41, "갭투자: 적은 자기 돈으로 샀어도 돌려줄 책임은 그대로"))
    e.append(note(45.8, "• 설명용 가정. 막대 길이는 금액에 비례한다(2억 원 = 전체 막대)."))
    return e

# ── 3-3 경매 배당 가상 사례 ──────────────────────────
def fig_3_3(h):
    e = []
    base, k = 52, 40 / 20000                 # 0원 기준선 y=52, 2억 원 = 40mm
    bars = [("예상 집값", 20000, None, K40), ("경매 매각가", 16000, None, TEAL),
            ("먼저 갚을\n은행 채무", 2000, 16000, RED), ("남은 돈", 14000, None, TEAL), ("돌려줄\n보증금", 15000, None, ORANGE)]
    bw, gap, x = 12, 5, 8
    e.append(line(4, base, 99, base, K80, 0.3))
    e.append(t(3.5, base + 1, "0", 7, 700, K80, "end", NUM))
    pos = []
    for i, (nm, v, top, col) in enumerate(bars):
        if top:                                                   # 공중에 뜬 감소 막대(워터폴)
            y1, y2 = base - top * k, base - (top - v) * k
            e.append(rect(x, y1, bw, y2 - y1, col, "none", 0))
            e.append(t(x + bw / 2, y1 - 1.2, "−2천만 원", 7.5, 700, RED, family=NUM))
        else:
            e.append(rect(x, base - v * k, bw, v * k, col, "none", 0))
            amt = {20000: "2억", 16000: "1억 6천만", 14000: "1억 4천만", 15000: "1억 5천만"}[v] + " 원"
            e.append(t(x + bw / 2, base - v * k - 1.2, amt, 7, 700, K80))
        e += lines(x + bw / 2, base + 3.4, nm.split("\n"), 7, 700, anchor="middle", lead=1.25)
        pos.append(x); x += bw + gap
    # 부족액: 남은 돈(1억4천)과 보증금(1억5천) 사이
    ya, yb = base - 15000 * k, base - 14000 * k
    xb = pos[4]
    e.append(rect(xb, ya, bw, yb - ya, "url(#red)", RED, 0.3))
    e.append(line(pos[3], yb, xb + bw, yb, RED, 0.25, "0.8 0.6"))
    e.append(t(xb + bw + 1, ya + 2.6, "부족", 7.5, 700, RED, "start"))
    e.append(t(xb + bw + 1, ya + 6.0, "1천만 원", 7.5, 700, RED, "start"))
    # 경매·세입자 그림
    el, _ = pic(h, "법봉", pos[1] + bw / 2, 0, 12, 7); e.append(el)
    el, _ = pic(h, "세입자", pos[4] + bw / 2 - 1, 7.5, 9, 9); e.append(el)
    e.insert(0, f'<defs><pattern id="red" width="1.4" height="1.4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             f'<line x1="0" y1="0" x2="0" y2="1.4" stroke="{RED}" stroke-width="0.35"/></pattern></defs>')
    e.append(title(66.5, "집이 팔려도 보증금을 다 돌려받지 못할 수 있어요"))
    e.append(note(71.3, "• 가상 사례. 막대 높이는 금액에 비례한다(0원 기준). 실제 배당에서는 세금·경매 비용과 권리 순위도 따진다."))
    return e

# ── 3-4 신탁된 집 ──────────────────────────────────
def fig_3_4(h):
    e = []
    people = [("집주인", 12, "위탁자", "재산을 맡기는 사람"), ("신탁직원", 50.5, "수탁자", "신탁 내용에 따라 관리"),
              ("은행직원", 89, "수익자", "이익을 받는 사람")]
    for k, cx, nm, sub in people:
        el, b = pic(h, k, cx, 0, 13, 13); e.append(el)
        e.append(t(cx, b + 3.6, nm, 8.5, 700, TEAL))
        e.append(t(cx, b + 7.0, sub, 7, 400))
    e.append(arrow(21, 7, 41.5, 7, TEAL, 0.35)); e.append(t(31.2, 5.4, "소유권 이전", 7, 700, TEAL))
    e.append(t(31.2, 10.7, "(신탁등기)", 7, 400))
    e.append(arrow(59.5, 7, 80, 7, K80, 0.3)); e.append(t(69.7, 5.4, "이익 지급", 7, 700, K80))
    e.append(t(69.7, 10.7, "(예: 우선수익자)", 7, 400))
    # 세입자의 두 질문
    el, b = pic(h, "세입자", 12, 27, 13, 13); e.append(el)
    e.append(t(12, b + 3.4, "세입자", 8.5))
    for i, q in enumerate(["누가 소유자인가?", "누가 어떤 조건으로 임대할 권한이 있는가?"]):
        y = 30 + i * 7.5
        el, bb = tag(0, 0, [(q, 8, K80)])
        wq = bb[2]
        e.append(rect(23, y - 3.3, wq, 5.6, "#fff", K80, 0.2, 2.6))
        e.append(t(23 + wq / 2, y + 0.6, q, 8, 700))
    # 확인할 세 칸
    e.append(t(23, 49.5, "계약 전에 확인할 것", 8, 700, ORANGE, "start"))
    for i, s in enumerate(["신탁원부", "필요한 동의 서류", "보증금 받을 계좌"]):
        x = 23 + i * 26
        e.append(rect(x, 52, 25, 7, "#fff", ORANGE, 0.3, 1.2))
        e.append(rect(x + 1.4, 54, 3, 3, "none", ORANGE, 0.3, 0.4))
        e.append(t(x + 5.2, 56.6, s, 7, 700, K80, "start"))
    e.append(title(68, "신탁된 집, 누구와 어떻게 계약해야 할까?"))
    e.append(note(72.8, "• 임대 권한·동의 조건·보증금 지급처는 신탁 내용에 따라 다르다. 모든 신탁에 같은 조건이 적용되지 않는다."))
    return e

# ── 3-5 대항력과 우선변제권 ─────────────────────────
def fig_3_5(h):
    e = []
    rows = [(["계약서"], "① 계약 체결", ["확정일자"], "입주 전에도 받을 수 있다", "확정일자"),
            (["열쇠", "주민센터"], "② 집 인도 + 주민등록", ["달력"], "두 요건을 모두 갖춘 다음 날 0시", "대항력")]
    for i, (pics, a, pics2, b, out) in enumerate(rows):
        y = 2 + i * 25
        for j, k in enumerate(pics):
            el, _ = pic(h, k, 7 + j * 13, y, 11, 11); e.append(el)
        e.append(t(3 if len(pics) == 1 else 7, y + 15.6, a, 8, 700, TEAL, "start" if len(pics) == 1 else "start"))
        ax = 30 if len(pics) == 2 else 18
        e.append(arrow(ax, y + 6, 46, y + 6, K80, 0.3))
        if pics2 == ["달력"]:
            el, _ = pic(h, "달력", 53, y, 11, 11); e.append(el)
        else:
            el, _ = pic(h, "도장", 53, y + 0.5, 12, 10); e.append(el)
        e.append(t(53, y + 15.6, b, 7, 400))
        e.append(arrow(62, y + 6, 70, y + 6, K80, 0.3))
        e.append(rect(71, y + 1.5, 20, 9, "#fff", TEAL, 0.35, 1.5))
        e.append(t(81, y + 7.4, out, 9, 700, TEAL))
    # 두 줄을 묶는 괄호 → 우선변제권
    e.append(f'<path d="M92.5 8 H95 V33 H92.5" stroke="{ORANGE}" stroke-width="0.35" fill="none"/>')
    e.append(arrow(95, 20.5, 97.5, 20.5, ORANGE, 0.35))
    e.append(rect(64, 47, 37, 10, ORANGE_T, ORANGE, 0.35, 1.5))
    e.append(t(82.5, 51.3, "대항요건 + 확정일자", 7.5, 700, K80))
    e.append(t(82.5, 55.2, "= 우선변제권", 8.5, 700, ORANGE))
    e.append(f'<path d="M98 21 V44 H90 V47" stroke="{ORANGE}" stroke-width="0.3" fill="none"/>')
    e.append(title(64, "대항력과 우선변제권은 언제 생길까?"))
    e.append(note(68.8, "• 우선변제권이 있어도 실제로 돈을 받는 순위·절차·금액은 따로 확인해야 한다. 전액 회수를 보장하지 않는다."))
    return e

# ── 3-6 체크리스트 ─────────────────────────────────
def fig_3_6(h):
    e = []
    cols = [("계약 전", TEAL, [("등기", "등기사항전부증명서"), ("신분증", "상대방 신분·임대 권한"), ("시세", "시세·앞선 권리"),
                               ("빌라", "건축물대장·실제 상태"), ("세금", "세금 자료")]),
            ("계약 후", ORANGE, [("열쇠", "집 인도·전입신고 처리"), ("달력", "확정일자"), ("보증서", "반환보증 신청·발급")])]
    for ci, (hd, col, items) in enumerate(cols):
        x = ci * 52
        e.append(rect(x, 0, 49, 6.5, col, "none", 0, 1.2))
        e.append(t(x + 24.5, 4.6, hd, 9, 700, "#fff"))
        for i, (k, s) in enumerate(items):
            y = 9 + i * 11.2
            el, _ = pic(h, k, x + 6, y, 9.5, 9); e.append(el)
            e.append(rect(x + 13, y + 3, 3.2, 3.2, "none", col, 0.35, 0.4))
            e.append(t(x + 18, y + 5.9, f"{i+1}. {s}", 7.5, 700, K80, "start"))
            e.append(line(x, y + 10.4, x + 49, y + 10.4, K10 if False else "#DDDDDD", 0.2))
    e.append(t(52, 47.5, "※ 확정일자는 계약 후 입주 전에도", 7, 400, K80, "start"))
    e.append(t(52, 50.9, "   미리 받을 수 있다.", 7, 400, K80, "start"))
    e.append(title(73.5, "계약 전 다섯 가지, 계약 후 세 가지"))
    e.append(note(78.3, "• 질문을 시작하는 길잡이. 낯선 내용은 전문가나 공공 상담기관에 확인한다."))
    return e

# ── 3-7 이중계약 ───────────────────────────────────
def fig_3_7(h):
    e = []
    spots = [("집주인", 12, "집주인"), ("중개사", 50.5, "중개사"), ("세입자", 89, "세입자")]
    for k, cx, nm in spots:
        el, b = pic(h, k, cx, 2, 14, 14); e.append(el)
        e.append(t(cx, b + 3.4, nm, 8.5))
    for cx, s in ((12, "월세 계약서"), (89, "전세 계약서")):
        el, b = pic(h, "계약서", cx, 23, 8, 8); e.append(el)
        e.append(t(cx, b + 3.2, s, 7.5, 700, TEAL if s[0] == "전" else ORANGE))
    e.append(arrow(80, 7.5, 60.5, 7.5, TEAL, 0.6)); e.append(t(70.2, 5.6, "전세 보증금", 7.5, 700, TEAL))
    e.append(arrow(41, 11, 21, 11, ORANGE, 0.3)); e.append(t(31, 9.4, "매달 월세", 7.5, 700, ORANGE))
    e.append(rect(36, 26, 29, 8, "#fff", RED, 0.35, 1.2))
    e.append(t(50.5, 29.8, "보증금을 가로채고", 7.5, 700, RED))
    e.append(t(50.5, 33.0, "월세만 보내 속임수를 가림", 7, 400, RED))
    e.append(title(45, "하나의 집, 두 개의 계약서"))
    e.append(note(49.8, "• 수법의 구조를 설명하기 위한 그림. 누구에게 어떤 권한을 받고 무슨 내용으로 계약했는지가 핵심이다."))
    return e

FIGS = {"3-1": ("도3-1_월세전세_v1", 75, fig_3_1), "3-2": ("도3-2_갭투자_v1", 48, fig_3_2),
        "3-3": ("도3-3_경매배당_v1", 78, fig_3_3), "3-4": ("도3-4_신탁구조_v1", 80, fig_3_4),
        "3-5": ("도3-5_대항력우선변제권_v1", 75, fig_3_5), "3-6": ("도3-6_체크리스트_v1", 81, fig_3_6),
        "3-7": ("도3-7_이중계약_v1", 56, fig_3_7)}

if __name__ == "__main__":
    for k in (sys.argv[1:] or FIGS):
        name, H, fn = FIGS[k]
        write(name, W, H, fn, IM); print(name, W, H)
