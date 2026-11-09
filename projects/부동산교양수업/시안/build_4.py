# 제4장 도판 시안: 4-1 표준계약서 / 4-2 맨해튼 지도·기록 / 4-3 해약금 / 4-4 협상 저울
# 사용: python3 -I build_4.py [4-1 ...]
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *
from build_3 import C, pic, arrow, note, title, IM as IM3

IM = dict(IM3, s44="illust/도4-4_협상저울_v1.png")
C["지폐"] = ("s1", (1090, 515, 385, 245))           # 도1-4 항목 그림의 원화 지폐
W = 101
K10, K60 = "#E6E6E6", "#666666"
DW = 72

def dl(x, y, rows, pt=7, w=400, anchor="start"):
    return lines(x, y, rows, pt, w, K80, anchor, 1.32, DOC)

def kv(y, rows, lw=15):
    """2열 표(항목 | 내용). rows = [(항목, [줄...]), ...] → (요소, 끝 y, 행 y 목록)"""
    e, ys = [], []
    for k, v in rows:
        h = 1.8 + len(v) * 7 * PT * 1.32 + 0.6
        e.append(rect(2, y, lw, h, K10, K60, 0.15)); e.append(rect(2 + lw, y, DW - 4 - lw, h, "#fff", K60, 0.15))
        e += dl(2 + lw / 2, y + 3.2, [k], 7, 700, "middle")
        e += dl(2 + lw + 1.5, y + 3.2, v)
        ys.append((y, h)); y += h
    return e, y, ys

def side(y, s, col, tx, ty):
    el, b = tag(87.5, y, [(s, 7.5, col)], col)
    return el + [leader(b[0], y, tx, ty, col)]

# ── 4-1 간추린 가상 주택 임대차 계약서 ─────────────────
def fig_4_1(h):
    s = "주택임대차표준계약서 항목 순서를 참고해 간추린 가상 계약서"
    w = em(s) * 7 * PT + 3
    e = [rect(0, 0, w, 4.6, K60, "none", 0, 0.8), t(w / 2, 3.25, s, 7, 700, "#fff")]
    at = len(e)
    e.append(t(DW / 2, 12.0, "주택 임대차 계약서", 9, 700, K80, family=DOC))
    e += dl(3, 17.0, ["임대인(○○○)과 임차인(○○○)은 아래와 같이", "임대차 계약을 체결한다."])
    e.append(t(2, 25.6, "[임차주택의 표시]", 7.5, 700, K80, "start", DOC))
    el, y, ys1 = kv(27, [("소재지", ["가람시 새봄로 ○○, ○○○호"]), ("임차할 부분", ["○○○호 전부 / 면적 ○○㎡"])]); e += el
    e.append(t(2, y + 4.4, "[계약 내용] 보증금과 차임", 7.5, 700, K80, "start", DOC))
    el, y, ys2 = kv(y + 5.8, [("보증금", ["금 ○○○○만 원정"]), ("계약금", ["금 ○○○만 원정은 계약 시 지불"]),
                              ("잔금", ["금 ○○○○만 원정은", "20○○년 ○월 ○일 지불"]),
                              ("차임(월세)", ["금 ○○만 원정은 매월 ○일 지불"]), ("입금 계좌", ["○○은행 ○○○-○○-○○○○"])]); e += el
    e.append(t(2, y + 4.4, "[임대차 기간]", 7.5, 700, K80, "start", DOC))
    yk = y + 8.4
    e += dl(3, yk, ["임대인은 20○○년 ○월 ○일까지 집을 인도하고,", "임대차 기간은 인도일부터 20○○년 ○월 ○일까지로 한다."])
    y = yk + 6.2
    e.append(t(2, y + 4.0, "[계약의 해제]", 7.5, 700, K80, "start", DOC))
    yh = y + 8.0
    e += dl(3, yh, ["중도금(없으면 잔금)을 지급하기 전까지 임대인은 계약금의", "배액을 상환하고, 임차인은 계약금을 포기하고 해제할 수 있다."])
    y = yh + 6.0
    e.append(t(2, y + 4.0, "[특약사항]", 7.5, 700, K80, "start", DOC))
    ys = y + 5.4
    e.append(rect(2, ys, DW - 4, 11, "#fff", K60, 0.15))
    for i in range(3): e.append(line(4, ys + 3.4 + i * 3.2, DW - 4, ys + 3.4 + i * 3.2, "#CCCCCC", 0.15))
    y = ys + 11
    yg = y + 2.5
    e.append(rect(2, yg, DW - 4, 13, "#fff", K60, 0.15))
    for i, who in enumerate(["임대인", "임차인", "개업공인중개사"]):
        yy = yg + 3.8 + i * 3.6
        e.append(t(4, yy, who, 7, 700, K80, "start", DOC))
        e.append(t(30, yy, "○○○", 7, 400, K80, "start", DOC))
        e.append(t(DW - 4, yy, "(서명 또는 날인)", 7, 400, K60, "end", DOC))
    y = yg + 13
    e.insert(at, rect(0, 6.5, DW, y + 2.5 - 6.5, "#FAFAFA", K60, 0.25))
    # 네 가지 질문 태그
    e += side(17.6, "① 누구와 무엇을", TEAL, DW - 1, 17.6)
    e.append(rect(1.2, 26.2, DW - 2.4, ys1[-1][0] + ys1[-1][1] - 26.2 + 0.8, "none", TEAL, 0.3, 1, 'stroke-dasharray="1 0.6"'))
    y2a, y2b = ys2[0][0], ys2[-1][0] + ys2[-1][1]
    e.append(rect(1.2, y2a - 0.8, DW - 2.4, y2b - y2a + 1.6, "none", ORANGE, 0.3, 1, 'stroke-dasharray="1 0.6"'))
    e += side((y2a + y2b) / 2, "② 얼마를 언제", ORANGE, DW - 1, (y2a + y2b) / 2)
    e += side(yk + 1, "③ 언제부터 언제까지", TEAL, DW - 1, yk + 1)
    e += side(yh + 1, "④ 바꾸거나 끝낼 때", K80, DW - 1, yh + 1)
    e.append(leader(85, yh + 4, DW - 1, ys + 5, K80))
    el, b = tag(87.5, yg + 6.5, [("모두 이해한 뒤", 7.5, RED), ("서명", 7.5, RED)], RED)
    e += el + [leader(b[0], yg + 6.5, DW - 1, yg + 6.5, RED)]
    e.append(title(y + 9.5, "종이 한 장에 네 가지 질문의 답이 모두 들어 있는지 확인해요."))
    e.append(note(y + 14.3, "• 설명용 가상 계약서. 이름·주소·계좌·금액은 모두 비워 두었으며, 실제 표준계약서에는 칸과 조항이 더 많다."))
    return e

# ── 4-2 맨해튼과 60길더의 기록 ─────────────────────────
def fig_4_2(h):
    e = []
    # 개략도: 허드슨강·이스트강 사이의 긴 섬 (축척 없음)
    e.append(rect(0, 0, 40, 52, "#EAF3F5", "none", 0, 1.5))
    e.append('<g transform="translate(21 27) rotate(29)">'
             f'<path d="M-3.6 -21 C-2 -23 2 -23 3.2 -20 L4.2 8 C4.4 14 2.8 19 0 21.5 C-2.6 19 -4.2 14 -4.4 8 Z" fill="{YELLOW_T}" stroke="{K80}" stroke-width="0.3"/>'
             '</g>')
    e += [t(21, 28, "맨해튼", 8, 700, K80), t(5, 13, "허드슨강", 7, 400, TEAL, "start"),
          t(34, 46, "이스트강", 7, 400, TEAL, "end"), t(20, 4.5, "미국 뉴욕", 7.5, 700, K80)]
    e.append(arrow(35.5, 9.5, 35.5, 5, K80, 0.3)); e.append(t(35.5, 12.6, "북", 7, 700, K80))
    e.append(t(20, 50.5, "개략도(축척 없음)", 7, 300, K60))
    # 편지 이미지 자리 (실제 사료 — AI로 만들지 않음)
    e.append(rect(43, 0, 58, 52, "#fff", K60, 0.3, 1, 'stroke-dasharray="1.2 0.8"'))
    e += lines(72, 20, ["1626년 피터르 스하헌의 편지", "이미지 자리"], 8, 700, anchor="middle", lead=1.4)
    e += lines(72, 30, ["네덜란드 국가기록원 소장본", "이용 조건 확인 후 배치"], 7, 400, anchor="middle", lead=1.4)
    # 확인되는 것 / 확정하기 어려운 것
    e.append(rect(0, 55, 49.5, 15, "#fff", TEAL, 0.3, 1.2))
    e.append(t(2, 59.6, "기록에서 확인되는 것", 7.5, 700, TEAL, "start"))
    e += lines(2, 63.6, ["60길더 가치의 물건으로", "샀다는 보고"], 7, 400)
    e.append(rect(51.5, 55, 49.5, 15, "#fff", ORANGE, 0.3, 1.2))
    e.append(t(53.5, 59.6, "이 기록만으로 확정하기 어려운 것", 7.5, 700, ORANGE, "start"))
    e += lines(53.5, 63.6, ["구체적인 거래 물품·양쪽의 이해·", "전체 조건"], 7, 400)
    e.append(title(78, "기록은 무엇을 말해 주고, 무엇을 말해 주지 않을까?"))
    e.append(note(82.8, "• ‘24달러’는 뒤 시대에 60길더를 달러로 환산하며 퍼진 숫자다."))
    return e

# ── 4-3 해약금으로 계약을 끝낼 수 있는 때 ───────────────
def fig_4_3(h):
    e = []
    x0, x1, x2 = 12, 52, 90                      # 계약금 / 중도금 / 잔금·입주
    yb = 30
    e.append(rect(x0, yb - 4, x1 - x0, 8, YELLOW_T, "none", 0))
    e += lines((x0 + x1) / 2, yb - 1.2, ["해약금으로 계약을", "끝낼 수 있는 구간"], 7.5, 700, anchor="middle", lead=1.15)
    e.append(line(4, yb + 4, 98, yb + 4, K80, 0.35))
    for x, k, lab in ((x0, "계약서", ["계약서 작성", "계약금 지급"]), (x1, "지폐", ["중도금 지급"]), (x2, "열쇠", ["잔금 지급", "입주"])):
        el, _ = pic(h, k, x, yb + 8, 11, 9); e.append(el)
        e.append(f'<circle cx="{x}" cy="{yb+4}" r="1.4" fill="{TEAL}" stroke="#fff" stroke-width="0.3"/>')
        e += lines(x, yb + 21, lab, 7.5, 700, anchor="middle", lead=1.3)
    e.append(line(x1, yb - 7, x1, yb + 4, RED, 0.35, "0.8 0.5"))
    e += lines(x1 + 1.8, yb - 3.5, ["여기부터는 마음대로", "쓸 수 없음"], 7, 700, RED, "start", 1.25)
    # 위: 낸 사람 / 받은 사람
    for ix, k, a, b in ((8, "세입자", "계약금을 낸 사람", "1천만 원 포기"), (37, "집주인", "계약금을 받은 사람", "2천만 원 반환")):
        el, bot = pic(h, k, ix, 4, 9, 9); e.append(el)
        e.append(t(ix + 5.6, 8.0, a, 7, 400, K80, "start"))
        e.append(t(ix + 5.6, 11.8, b, 8, 700, ORANGE, "start"))
    e.append(title(64, "계약금으로 계약을 끝낼 수 있는 때는 정해져 있어요."))
    e.append(note(68.8, "• 계약금 1천만 원 예시. 해약금으로 끝낼 수 있는 것은 어느 한쪽이 계약 실행에 나서기 전(예: 중도금 지급 전)까지다. 따로 정한 약정이 있거나 계약금 일부만 보낸 경우에는 판단이 달라질 수 있다."))
    return e

# ── 4-4 기울어진 협상 저울 ────────────────────────────
def fig_4_4(h):
    IH = W * 1024 / 1536
    e = [f'<image href="{h["s44"]}" x="0" y="0" width="{W}" height="{IH:.3f}"/>']
    el, b = tag(17, 11, [("시간·정보·돈이", 7.5, K80), ("많은 쪽", 7.5, K80)]); e += el
    e.append(leader(14, b[1] + b[3], 13, 38))
    el, b = tag(89, 5.2, [("급하게 집을 구하는", 7.5, K80), ("세입자", 7.5, K80)]); e += el
    for i, s in enumerate(["주택", "임대차", "보호법", "·", "약관", "규제법"]):
        e.append(t(76.3, 41.2 + i * 3.3, s, 7.5, 700, TEAL))
    e.append(title(IH + 6.2, "기울어진 저울을 법이 받쳐 줘요"))
    e.append(note(IH + 11, "• 법은 주택 임차인과 소비자에게 최소한의 보호를 마련한다. 불공정한 조건에 서명했다고 그 보호를 모두 잃는 것은 아니다."))
    return e

FIGS = {"4-1": ("도4-1_표준계약서_v1", 156, fig_4_1), "4-2": ("도4-2_맨해튼기록_v1", 86, fig_4_2),
        "4-3": ("도4-3_해약금_v1", 79, fig_4_3), "4-4": ("도4-4_협상저울_v1", 82, fig_4_4)}

if __name__ == "__main__":
    for k in (sys.argv[1:] or FIGS):
        name, H, fn = FIGS[k]
        write(name, W, H, fn, IM); print(name, W, H)
