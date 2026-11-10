# 제7장 도판 시안: 7-1 프롤로그 / 7-2 주하의 메모 / 7-3 세 집 비교 / 7-4 두 줄 시간표 / 7-5 미래의 집 / 7-6 계약과 이삿날
# 사용: python3 -I build_7.py [7-1 ...]
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *
from build_3 import C, pic, arrow, note, title, IM as IM3

IM = dict(IM3, j="illust/7장_주하장면_v1.png", j3="illust/도7-3_세집비교_v1.png", f="illust/7장_미래의집_v1.png",
          s6="illust/6장_항목그림_v1.png")
J = {"도서관": (8, 8, 754, 494), "메모": (778, 8, 750, 494), "계약": (8, 518, 754, 498), "이사": (778, 518, 750, 498)}
F = {"공유": (20, 95, 450, 375), "코하우징": (540, 65, 460, 410), "모듈러": (1060, 25, 460, 455),
     "3D": (15, 600, 450, 350), "제로": (530, 550, 470, 400), "스마트": (1060, 560, 460, 410)}
C["학생"] = ("s6", (1245, 710, 230, 270))
W = 101

# ── 7-1 프롤로그: 도서관 책을 읽는 주하 ────────────────
def fig_7_1(h):
    e = []
    el, ph = crop(h["j"], J["도서관"], 0, 0, 62, multiply=False); e.append(el)
    x = 66
    e.append(line(x, 6, x, 32, YELLOW, 1.2))
    e += lines(x + 3, 10, ["두려움은", "모르는 데서 오고,", "용기는", "아는 데서 온다."], 9, 700, K80, "start", 1.45)
    e += lines(x + 3, 35, ["책을 다 읽은 밤,", "주하가 떠올린 말"], 7, 400, K60 if False else "#666666", "start", 1.35)
    e.append(t(0, ph + 5.5, "프롤로그 — 새로운 시작은 늘 설레게 하지", 10, 700, K80, "start"))
    return e

# ── 7-2 주하의 메모: 내가 살고 싶은 집 ─────────────────
def fig_7_2(h):
    e = []
    el, ph = crop(h["j"], J["메모"], 0, 6, 40, multiply=False); e.append(el)
    e.append(t(0, ph + 10, "다음 날 아침, 태블릿 메모장", 7, 400, "#666666", "start"))
    x0, w = 43, 58
    e.append(rect(x0, 0, w, 84, "#FFFDF4", "#C9C2A6", 0.25, 1))
    e.append(rect(x0 + w / 2 - 8, -1.5, 16, 4, YELLOW, "none", 0, 0.3))           # 테이프
    for i in range(18): e.append(line(x0 + 2, 12 + i * 4.1, x0 + w - 2, 12 + i * 4.1, "#E7E1C8", 0.15))
    e.append(t(x0 + w / 2, 8.6, "내가 살고 싶은 집", 9.5, 700, K80))
    items = [("1. 위치", ["학교에서 걸어서 10분 안팎"]),
             ("2. 가격", ["보증금 최대 500만 원", "월세 40만 원 이하", "+ 한 달 생활비 전체!"]),
             ("3. 방 종류·옵션", ["원룸. 어떤 가전이 포함?", "잘 작동해? 고장 나면 누가?"]),
             ("4. 안전", ["공동현관·창문 잠금", "가로등, 늦게까지 불 켠 가게", "대피로·소화기"])]
    y = 15.6
    for hd, ds in items:
        e.append(t(x0 + 3, y, hd, 8.5, 700, TEAL, "start"))
        e += lines(x0 + 5, y + 4.1, ds, 7.5, 400, K80, "start", 1.45)
        y += 4.1 + len(ds) * 7.5 * PT * 1.45 + 2.6
    e.append(t(x0 + w - 3, 81, "→ 이건 중개사님께 물어보기", 7, 700, ORANGE, "end"))
    return e

# ── 7-3 세 집 비교 ─────────────────────────────────
def fig_7_3(h):
    e = []
    P = [(12, 122, 494, 738), (522, 122, 497, 738), (1034, 122, 494, 738)]
    caps = [("첫 번째 집", ["사진보다 작고 어둡고", "벽지에 습기 얼룩"], RED),
            ("두 번째 집", ["넓고 깔끔하지만", "창 앞이 옆 건물 벽"], ORANGE),
            ("세 번째 집", ["남향 창, 푸른 나무와", "조용한 골목"], TEAL)]
    pw = 32.3
    for i, (box, (nm, ds, col)) in enumerate(zip(P, caps)):
        x = i * (pw + 2.05)
        el, ph = crop(h["j3"], box, x, 0, pw, multiply=False); e.append(el)
        e.append(t(x, ph + 4.2, nm, 8.5, 700, col, "start"))
        e += lines(x, ph + 8.2, ds, 7, 400, K80, "start", 1.35)
    e.append(title(ph + 18.5, "“역시 사진만 믿으면 안 되겠어.”"))
    return e

# ── 7-4 두 줄 시간표 ───────────────────────────────
def fig_7_4(h):
    e = []
    steps = [("학생", ["조건", "정하기"]), ("등기", ["집 보기", "서류 확인", "사전 상담"]), ("계약서", ["계약", "계약금", "1,000만 원"]),
             ("달력", ["확정일자", "대출 최종", "승인"]), ("열쇠", ["잔금", "4,000만 원", "인도·", "전입신고"]), ("보증서", ["반환보증", "신청·심사", "승인"])]
    cw = 101 / 6
    e.append(t(0, 3.4, "주하의 여정", 8, 700, TEAL, "start"))
    e.append(line(2, 16.5, 99, 16.5, TEAL, 0.35))
    for i, (k, lab) in enumerate(steps):
        cx = cw / 2 + i * cw
        el, _ = pic(h, k, cx, 5, 10, 9.5); e.append(el)
        e.append(f'<circle cx="{cx:.2f}" cy="16.5" r="1.3" fill="{TEAL}" stroke="#fff" stroke-width="0.3"/>')
        e += lines(cx, 21.5, lab, 7, 700 if i in (2, 4) else 400, K80, "middle", 1.28)
    # 아래 줄: 권리
    y = 36
    e.append(t(0, y, "보증금을 지키는 권리", 8, 700, ORANGE, "start"))
    c4, c5, c6 = cw * 3.5, cw * 4.5, cw * 5.5
    e.append(rect(c4 - 7.5, y + 2, 15, 6.5, "#fff", ORANGE, 0.3, 1.2)); e.append(t(c4, y + 6.4, "확정일자", 7.5, 700, ORANGE))
    e.append(rect(c5 - 8, y + 2, 16, 14.5, "#fff", ORANGE, 0.3, 1.2))
    e += lines(c5, y + 5.4, ["인도+", "주민등록 →", "다음 날", "대항력"], 7, 700, ORANGE, "middle", 1.25)
    e.append(rect(c4 - 7.5, y + 18.5, (c5 + 8) - (c4 - 7.5), 6.5, ORANGE_T, ORANGE, 0.3, 1.2))
    e.append(t((c4 - 7.5 + c5 + 8) / 2, y + 22.9, "둘을 갖추면 우선변제권", 7.5, 700, K80))
    e.append(rect(c6 - 7.8, y + 2, 15.6, 14.5, "#fff", K80, 0.25, 1.2, 'stroke-dasharray="0.8 0.6"'))
    e += lines(c6, y + 5.4, ["별도 심사", "결과이며", "자동 승인", "아님"], 7, 400, K80, "middle", 1.25)
    # 돈의 흐름: 보증금 5,000만 원
    y = 68
    e.append(t(0, y, "보증금 5,000만 원의 흐름", 8, 700, K80, "start"))
    x0, L = 2, 97
    a = L * 1000 / 5000
    e.append(rect(x0, y + 2.5, a, 7, YELLOW, "none", 0))
    e.append(rect(x0 + a, y + 2.5, L - a, 7, TEAL, "none", 0))
    e.append(t(x0 + a / 2, y + 7.2, "③ 계약 때", 7, 700, K80))
    e.append(t(x0 + a + (L - a) / 2, y + 7.2, "⑤ 잔금 때: 전세자금대출 4,000만 원 → 집주인 계좌", 7.5, 700, "#fff"))
    e.append(t(x0, y + 13.4, "계약금 1,000만 원 = 주하가 준비한 500만 원 + 부모님이 보탠 500만 원", 7, 400, K80, "start"))
    e.append(title(y + 21, "주하의 계약, 순서대로 보기"))
    e.append(note(y + 25.8, "• 가상 이야기의 설정. 대출·반환보증의 심사 결과는 실제 상품의 자격이나 한도를 뜻하지 않는다. 막대 길이는 금액에 비례한다."))
    return e

# ── 7-5 다가올 미래의 집 ────────────────────────────
def fig_7_5(h):
    e = []
    groups = [("함께 사는 방식", [("공유", "공유 주택", ["방은 따로,", "주방·거실은 함께"]), ("코하우징", "코하우징", ["독립된 집 +", "공동 식당·텃밭"])]),
              ("짓는 방식", [("모듈러", "모듈러 주택", ["공장에서 만든 부분을", "현장에서 조립"]), ("3D", "3D 프린팅 주택", ["장비가 재료를", "층층이 쌓아 벽을 만듦"])]),
              ("에너지와 생활", [("제로", "제로에너지 주택", ["단열 + 태양광 등", "재생에너지"]), ("스마트", "스마트홈", ["센서·통신으로", "조명·냉난방 관리"])])]
    cw = 33.2
    for gi, (gname, its) in enumerate(groups):
        x = gi * (cw + 0.7)
        e.append(rect(x, 0, cw, 6, TEAL if gi != 1 else ORANGE, "none", 0, 1))
        e.append(t(x + cw / 2, 4.3, gname, 8, 700, "#fff"))
        for r, (k, nm, ds) in enumerate(its):
            y = 8 + r * 37
            bw, bh = F[k][2], F[k][3]
            wd = min(cw - 4, 24 * bw / bh)                     # 그림 높이 24mm 이하
            el, ih = crop(h["f"], F[k], x + (cw - wd) / 2, y, wd); e.append(el)
            e.append(t(x + cw / 2, y + ih + 3.6, nm, 8, 700, K80))
            e += lines(x + cw / 2, y + ih + 7.2, ds, 7, 400, K80, "middle", 1.25)
    e.append(title(87, "다가올 미래, 집은 어떻게 달라질까?"))
    e.append(note(91.8, "• 서로 경쟁하는 집 종류가 아니라 생각해 볼 질문의 묶음. 3D 프린터가 집 전체를 한 번에 완성하거나, 제로에너지 주택의 전기요금이 늘 0원인 것은 아니다."))
    return e

# ── 7-6 계약하는 날과 이삿날 ─────────────────────────
def fig_7_6(h):
    e = []
    pw = 49.5
    for i, (k, nm, ds) in enumerate([("계약", "계약하는 날", "서명하기 전에 서류와 특약을 하나씩 확인했다"),
                                     ("이사", "이삿날", "짜장면과 탕수육, 그리고 첫 번째 집")]):
        x = i * (pw + 2)
        el, ph = crop(h["j"], J[k], x, 0, pw, multiply=False); e.append(el)
        e.append(t(x, ph + 4.2, nm, 8.5, 700, TEAL, "start"))
        e.append(t(x, ph + 7.8, ds, 7, 400, K80, "start"))
    e.append(title(ph + 16, "주하의 첫 번째 계약서"))
    e.append(note(ph + 20.8, "• 「책 속의 책」의 인물·집·금액은 학습을 위해 만든 가상 설정이다."))
    return e

FIGS = {"7-1": ("도7-1_프롤로그_v1", 48, fig_7_1), "7-2": ("도7-2_주하의메모_v1", 86, fig_7_2),
        "7-3": ("도7-3_세집비교_v1", 72, fig_7_3), "7-4": ("도7-4_두줄시간표_v1", 98, fig_7_4),
        "7-5": ("도7-5_미래의집_v1", 98, fig_7_5), "7-6": ("도7-6_계약과이사_v1", 56, fig_7_6)}

if __name__ == "__main__":
    for k in (sys.argv[1:] or FIGS):
        name, H, fn = FIGS[k]
        write(name, W, H, fn, IM); print(name, W, H)
