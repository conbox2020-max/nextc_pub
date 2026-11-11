# 조판 데이터(JSON)를 담은 인디자인 조판 스크립트(UXP .idjs / ExtendScript .jsx 겸용)를 만든다.
# 사용: python3 -I make_layout_script.py <조판 폴더>
# 스크립트 본문은 ES3 문법만 쓴다(ExtendScript에서도 돌아야 하므로 let·const·화살표 함수 금지).
import sys, os, json, re
D = sys.argv[1]
order = ["ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07", "back"]

# 괄호 처리(2026-11-11, 편집자 요청: 국부론 수업과 같게)
# 국부론은 본문 계열 문단의 괄호 기호를 지우고, 괄호 속 글자에 문자 스타일 '한글괄호'·'영문괄호'
# (고딕Neo1 Lt 8pt, K80, 기준선 −1pt)를 썼다. 캡션·도판 출처·저서 연도에는 괄호를 남겼다.
# → 출처 목록(참고 자료)과 도판 자리 문단은 괄호를 그대로 둔다.
PAREN_STYLES = {"본문", "본문 삽입", "잠깐 제목", "목록", "번호 목록", "잠깐 본문", "잠깐 본문 첫", "잠깐 본문 이어", "잠깐 본문 끝",
                "절 제목", "소제목", "소소제목", "질문 제목"}
paren_log = []
LONG_PAREN = 15   # 괄호 속 한글 글자가 이보다 길면 '긴 괄호'(영문 이름은 길어도 영문괄호)

def prep(s, t):
    """조판용으로 문단을 다듬는다. 돌려주는 값: (스타일, 글자, [[시작, 길이, 문자 스타일], …]) 또는 None(뺄 문단)"""
    if re.fullmatch(r"\s*#+\s*", t):
        return None                                   # 원고의 마크다운 제목 기호만 남은 줄
    if s == "소제목":                                 # ❶~❾: 스터디윗미에 글리프가 없어 다른 글꼴로 바뀐다 → 다른 소제목과 같은 '1)'
        t = re.sub(r"^([❶-❾])\s*", lambda m: f"{ord(m.group(1)) - 0x2775}) ", t)
    spans = []
    if s in PAREN_STYLES:
        out, pos = "", 0
        for m in re.finditer(r"\(([^()]+)\)", t):
            inner = m.group(1)
            latin = re.search(r"[A-Za-z]", inner) and not re.search(r"[가-힣㐀-鿿]", inner)
            out += t[pos:m.start()]
            if not latin and len(inner) > LONG_PAREN:
                # 긴 괄호(한글 문장·구절, 2026-11-11 편집자 결정): 괄호 기호를 남기고 크기만 10pt('긴괄호')
                spans.append([len(out), len(inner) + 2, "긴괄호"])
                out += "(" + inner + ")"
                paren_log.append(f"{s}: {inner}")
            else:
                spans.append([len(out), len(inner), "영문괄호" if latin else "한글괄호"])
                out += inner
            pos = m.end()
        t = out + t[pos:]
    if any(ord(c) > 0xFFFF for c in t):
        raise SystemExit("BMP 밖 글자가 있어 문자 위치가 어긋날 수 있음: " + t[:40])
    return s, t, spans

def dobira_lines(t, one_line=12):   # 18pt 12자 ≈ 70mm < 글상자 폭 76.7mm
    """도비라 장 제목: 길면 가운데에 가장 가까운 띄어쓰기에서 두 줄로(국부론 '애덤 스미스는 / 누구인가?'처럼)"""
    if len(t) <= one_line or " " not in t: return [t]
    mid = len(t) / 2
    at = min((i for i, c in enumerate(t) if c == " "), key=lambda i: abs(i - mid))
    return [t[:at], t[at + 1:]]

# 장마다 절 제목 색(2026-11-11 편집자 요청). 국부론은 부마다 '대제목' 색을 장 색 견본으로 바꿨다
# (1부 chapter 7, 2부 chapter 8, 3부 chapter 10). 국부론 장 색 견본 8개 중 7개를 쓰고, 이웃 장끼리
# 색이 겹치지 않게 색상환을 돌려 배치했다. 녹색이 둘이라 탁한 'chapter 1, 17'(50/0/88/36)은 뺐다.
# 견본 이름의 숫자는 국부론 장 번호다(이 책의 장 번호가 아님). 뒷부속은 기본 '절 제목'(chapter 2, 16).
CH_COLOR = {"01": "chapter 2, 16",   # 88/44/99/6  짙은 녹색(지금 색)
            "02": "chapter 8",       # 12/62/56/0  적갈색(국부론 2부) — 마젠타 소제목과 덜 겹치게 7장과 맞바꿈
            "03": "chapter 5, 13",   # 80/37/14/0  파랑
            "04": "chapter 10",      # 0/71/83/0   주황(국부론 3부)
            "05": "chapter 11",      # 0/70/5/36   자주
            "06": "Chapter 9",       # 0/57/93/17  황토
            "07": "chapter 7"}       # 4/68/46/0   장미색(국부론 1부)

# 잠깐 코너 제목(2026-11-11 편집자 요청: 모든 잠깐 코너에 제목, 국부론 잠깐 코너와 같게) — 원고에 없어 [제안]으로 따로 둔다
JT = json.load(open(os.path.join(D, "잠깐_제목.json"), encoding="utf-8"))["제목"]
JTITLE = {(x["장"], x["순서"]): x for x in JT}

book = []
for k in order:
    blocks = json.load(open(os.path.join(D, k + ".json"), encoding="utf-8"))
    title = next((b for b in blocks if b["s"] == "장 제목"), None)
    num = title["n"] if title else ""
    paras, jn = [], 0
    for bi, b in enumerate(blocks):
        if b["s"] == "장 제목": continue
        if b["s"] == "잠깐 라벨":
            # '잠깐!' 글자는 국부론 리본에 들어 있으므로 라벨 문단 대신 제목 문단을 둔다
            jn += 1
            jt = JTITLE.get((k, jn))
            body = blocks[bi + 1]["t"] if bi + 1 < len(blocks) else ""
            if not jt or not body.startswith(jt["첫머리"]):
                raise SystemExit(f"잠깐 제목이 맞지 않음: {k} {jn}번째 상자 — 잠깐_제목.json 확인 ('{body[:20]}')")
            r = prep("잠깐 제목", jt["제목"])
            paras.append(["잠깐 제목", r[1], "", r[2]])
            continue
        r = prep(b["s"], b["t"])
        if not r: continue
        s = r[0]
        if s == "절 제목" and num in CH_COLOR: s = "절 제목_" + num    # 장별 절 제목(색만 다름)
        paras.append([s, r[1], b.get("fig") or "", r[2]])
    if jn != sum(1 for x in JT if x["장"] == k):
        raise SystemExit(f"잠깐 상자 수가 다름: {k} 원고 {jn}, 잠깐_제목.json {sum(1 for x in JT if x['장'] == k)}")
    tt = title["t"] if title else ""
    book.append({"key": k, "num": title["n"] if title else "", "title": tt, "dobira": dobira_lines(tt), "p": paras})

# 태그 텍스트도 같은 내용으로 다시 쓴다(괄호 문자 스타일 포함)
def tagged(ch):
    def esc(s): return s.replace("\\", "\\\\").replace("<", "\\<").replace(">", "\\>")
    out = ["<UNICODE-WIN>", "<Version:13>"]
    if ch["num"]:
        out.append(f"<ParaStyle:도비라 번호>{ch['num']}")
        for ln in ch["dobira"]: out.append(f"<ParaStyle:도비라 제목>{esc(ln)}")
    for s, t, fig, spans in ch["p"]:
        line, pos = "", 0
        for a, n, cs in spans:
            line += esc(t[pos:a]) + f"<CharStyle:{cs}>" + esc(t[a:a + n]) + "<CharStyle:>"; pos = a + n
        out.append(f"<ParaStyle:{s}>" + line + esc(t[pos:]))
    return "\r\n".join(out)
for ch in book:
    with open(os.path.join(D, ch["key"] + "_태그텍스트.txt"), "wb") as f:
        f.write(b"\xff\xfe" + tagged(ch).encode("utf-16-le"))
# 도판 크기(mm, 시안 기준). 2-1은 펼침면이라 두 칸.
FIGSIZE = {"1-1": (101, 84), "1-2": (45, 40), "1-3": (101, 84), "1-4": (101, 74), "1-5": (101, 60),
           "2-1": (101, 110), "2-1R": (101, 101), "2-2": (101, 82), "2-3": (101, 64), "2-4": (101, 106), "2-5": (101, 50),
           "3-1": (101, 75), "3-2": (101, 48), "3-3": (101, 78), "3-4": (101, 80), "3-5": (101, 75), "3-6": (101, 81), "3-7": (101, 56),
           "4-1": (101, 156), "4-2": (101, 86), "4-3": (101, 79), "4-4": (101, 82),
           "5-1": (101, 77), "5-2": (101, 62), "5-3": (101, 64), "5-4": (101, 77), "5-5": (101, 98), "5-6": (101, 78), "5-7": (101, 49),
           "6-1": (101, 57), "6-2": (101, 64), "6-4": (101, 109), "6-5": (101, 61),
           "7-1": (101, 48), "7-2": (101, 86), "7-3": (101, 72), "7-4": (101, 98), "7-5": (101, 98), "7-6": (101, 56)}
# 도판은 인디자인에서 직접 짠다(2026-11-11 확정). 자리 상자에 참고할 제작지시 파일 이름을 적는다.
SIAN = os.path.join(D, "..", "시안")
if os.path.isdir(SIAN):
    have = set(os.listdir(SIAN))
else:   # 시안 폴더가 작업 트리에 없으면 git에 올라간 파일 이름으로 대신한다
    import subprocess
    r = subprocess.run(["git", "-C", D, "ls-files", "-z", "--", "../시안"], capture_output=True, text=True)
    have = {os.path.basename(x) for x in r.stdout.split("\0") if x}
GUIDE = {}
for fid in FIGSIZE:
    base = fid.rstrip("R")
    for name in (f"도{base}_인디자인_제작지시.md", f"{base.split('-')[0]}장_인디자인_제작지시.md"):
        if name in have: GUIDE[fid] = "시안/" + name; break
    else:
        GUIDE[fid] = "제작지시 없음 — 시안 이미지 참고"
# 도판 넣기(2026-11-11 편집자 요청): 시안의 실제 크기 PDF(도판마다 가장 높은 버전)를 자리 상자에 넣는다.
# 시안이 없는 도판(1-2, 1-5)은 회색 자리 상자로 둔다. 2-1은 왼쪽·오른쪽 두 쪽
import unicodedata
haveN = {unicodedata.normalize("NFC", x) for x in have}
FIGFILE = {}
for fid in FIGSIZE:
    base = fid.rstrip("R")
    c = [f for f in haveN if f.startswith(f"도{base}_") and f.endswith("_실제크기.pdf")]
    if base == "2-1": c = [f for f in c if ("오른쪽" in f) == (fid == "2-1R")]
    c.sort(key=lambda f: int((re.search(r"_v(\d+)", f) or re.search(r"(\d*)", "0")).group(1) or 0))
    if c: FIGFILE[fid] = c[-1]
DOBIRA_IMG = "illust/도비라_공통_v1.png"
# 앞부속(2026-11-11 확정): 1~3쪽 표제지·판권·속표지 자리, 4쪽부터 머리말 자리(원고 미입수, 자리만)
FRONT = {"reserve": ["표제지", "판권", "속표지"], "preface": "[머리말 자리 — 원고를 받으면 이 문단을 바꿔 넣는다]"}
# 저장 위치(2026-11-11 사용자 지정): conbo > 인디자인 > 10대를 위한 부동산 교양 수업
# 실제 폴더 이름은 '10대를 위한 부동산 교양수업'(띄어쓰기 없음, 2026-11-11 확인) → 두 이름을 모두 찾는다
SAVE = {"folder": ["인디자인", "10대를 위한 부동산 교양수업"], "alt": ["10대를 위한 부동산 교양 수업"], "user": "conbo", "file": "부동산교양수업_본문_v1"}
LONG_N = sum(1 for ch in book for p in ch["p"] for sp in p[3] if sp[2] == "긴괄호")
PAREN_N = sum(len(p[3]) for ch in book for p in ch["p"]) - LONG_N
data = json.dumps({"book": book, "fig": FIGSIZE, "guide": GUIDE, "front": FRONT, "save": SAVE,
                   "parenCount": PAREN_N, "longParen": LONG_N, "chColor": CH_COLOR, "jamkkanN": len(JT),
                   "figFile": FIGFILE, "dobiraImg": DOBIRA_IMG, "sianAbs": os.path.abspath(SIAN)}, ensure_ascii=False)
JS = r'''// 《10대를 위한 부동산 교양 수업》 본문 조판 스크립트 (자동 생성: tools/make_layout_script.py — 이 파일을 직접 고치지 말 것)
// UXP(.idjs)와 ExtendScript(.jsx) 모두에서 돈다.
// 준비: 인디자인에서 《국부론 수업》 새 조판 파일(국부론수업_본문_새조판.indd)을 열어 두고 앞에 둔다. 원본은 읽기만 한다.
// 동작: 새 문서를 만들고 국부론의 스타일·견본·부모 페이지를 가져온 뒤, 원고 1~7장과 뒷부속을 흘려 넣는다.
// 결과: 끝나면 요약 창을 띄우고, 전체 기록을 1쪽 왼쪽 대지에 '조판 기록' 글상자로 남긴다.
var ID = (typeof require !== "undefined") ? require("indesign") : null;   // UXP면 indesign 모듈, ExtendScript면 null
var APP = ID ? ID.app : app;
function E(name) { return ID ? ID[name] : eval(name); }   // 열거형 이름 → 값 (UXP/ExtendScript 공통)
var DATA = __DATA__;
var MM = 72 / 25.4;
var FRAME_H = 214 - 19.5 - 31;      // 판면 높이(mm)
var FIG_MAX_H = FRAME_H - 15;       // 도판 자리 상자 최대 높이(mm): 판면 높이 − (자리 문단 한 줄 + 앞뒤 간격)
var log = [];          // 확인 필요
var report = [];       // 장별 시작 쪽 등
var started = false;
var FIG_GRAY = null;   // 도판 자리 상자 칠(makeStyles에서 정함)
// 잠깐 상자 치수(mm). top/bottom: 음영 위·아래 오프셋, before/after: 상자 앞뒤 간격(리본이 윗글에 닿지 않게)
var JBOX = { top: 10, bottom: 6, before: 13, after: 8, ribbonDX: -4.8, ribbonDY: -4.8 };
var RIBBON = null;     // 국부론에서 복사한 '잠깐 !' 리본(새 문서 1쪽에 원본 하나, 끝나면 지움)
var RIBBON_N = 0;
var RIB_CORR = null;   // 리본 위치 보정값 [가로, 세로](pt) — 첫 리본에서 잰다

function copyRibbon(src, doc) {
    // 국부론 잠깐 코너에서 '잠깐 !' 리본 그룹(노란 띠 + 글상자)을 찾아 새 문서로 복사한다.
    // 리본과 상자의 위치 차이도 국부론에서 다시 잰다(기본값 −4.8mm, −4.8mm)
    try {
        var pages = src.pages;
        for (var i = 0; i < pages.length; i++) {
            var gs = pages.item(i).groups;
            for (var k = 0; k < gs.length; k++) {
                var G = gs.item(k), subs = G.groups;
                for (var s = 0; s < subs.length; s++) {
                    var R = subs.item(s), tfs = R.textFrames;
                    if (!tfs.length || !/^잠깐/.test(String(tfs.item(0).contents))) continue;
                    var gt = G.textFrames;
                    for (var t = 0; t < gt.length; t++) {
                        var f = gt.item(t), cn = "";
                        try { cn = f.fillColor.name; } catch (e) {}
                        if (cn.indexOf("Y=68") >= 0) {
                            var rb = R.geometricBounds, bb = f.geometricBounds;
                            JBOX.ribbonDX = (rb[1] - bb[1]) / MM; JBOX.ribbonDY = (rb[0] - bb[0]) / MM;
                        }
                    }
                    var c = R.duplicate(doc.pages.item(0));
                    report.push("잠깐 리본: 국부론 " + pages.item(i).name + "쪽 리본을 복사(상자 왼쪽 위에서 " +
                        Math.round(-JBOX.ribbonDX * 10) / 10 + "mm, " + Math.round(-JBOX.ribbonDY * 10) / 10 + "mm 바깥)");
                    return c;
                }
            }
        }
    } catch (e) { log.push("잠깐 리본 복사: " + e); return null; }
    log.push("잠깐 리본을 국부론에서 찾지 못함 — 리본 없이 상자만 만듦");
    return null;
}

function placeRibbons(story) {
    if (!RIBBON) return 0;
    var AP = E("AnchorPosition"), n = 0, ps = story.paragraphs;
    for (var i = 0; i < ps.length; i++) {
        var p = ps.item(i);
        if (p.appliedParagraphStyle.name !== "잠깐 제목") continue;
        try {
            var ip = p.insertionPoints.item(0), pg = ip.parentTextFrames[0].parentPage;
            var r = RIBBON.duplicate(pg);
            r.anchoredObjectSettings.insertAnchoredObject(ip, AP.ANCHORED);
            var ao = r.anchoredObjectSettings;
            setp(ao, "anchorPoint", E("AnchorPoint").TOP_LEFT_ANCHOR);
            setp(ao, "horizontalReferencePoint", E("AnchoredRelativeTo").COLUMN_EDGE);
            setp(ao, "verticalReferencePoint", E("VerticallyRelativeTo").LINE_ASCENT);
            try { ao.pinPosition = false; } catch (e) {}                    // 판면 밖(위 여백)으로 나가도 그대로
            try { ao.spineRelative = false; } catch (e) {}
            var cx = RIB_CORR ? RIB_CORR[0] : 0, cy = RIB_CORR ? RIB_CORR[1] : 0;
            setp(ao, "anchorXoffset", JBOX.ribbonDX * MM + cx);
            setp(ao, "anchorYoffset", (JBOX.ribbonDY - JBOX.top) * MM + cy);   // 음영 위 오프셋만큼 + 리본 돌출만큼 위로
            if (!RIB_CORR) {
                // 리본은 회전된 그룹이라 인디자인이 회전 전 테두리로 위치를 잡는다(3차 실행 실측: 오른쪽 9.8mm 어긋남).
                // 첫 리본의 실제 위치를 재서 보정값을 구하고 이후 리본에 그대로 쓴다
                // 회전된 그룹에서는 가로 오프셋의 방향이 뒤집혀 작동하기도 한다(4차 실행 실측) → 보정 뒤 다시 재서
                // 오차가 커졌으면 반대 방향으로 고친다
                try {
                    var fb = ip.parentTextFrames[0].geometricBounds, ln = p.lines.item(0);
                    var want = [fb[1] + JBOX.ribbonDX * MM, ln.baseline - ln.ascent - JBOX.top * MM + JBOX.ribbonDY * MM];   // [왼, 위]
                    function err() { var g = r.geometricBounds; return [want[0] - g[1], want[1] - g[0]]; }
                    var keys = ["anchorXoffset", "anchorYoffset"], base = [ao.anchorXoffset, ao.anchorYoffset], corr = [0, 0];
                    for (var ax = 0; ax < 2; ax++) {
                        var e0 = err()[ax];
                        if (Math.abs(e0) < 0.3) continue;
                        ao[keys[ax]] = base[ax] + e0;
                        if (Math.abs(err()[ax]) > Math.abs(e0)) ao[keys[ax]] = base[ax] - e0;
                        corr[ax] = ao[keys[ax]] - base[ax];
                    }
                    RIB_CORR = corr;
                    var left = err();
                    report.push("잠깐 리본 위치 보정: 가로 " + Math.round(corr[0] / MM * 10) / 10 + "mm, 세로 " + Math.round(corr[1] / MM * 10) / 10 +
                        "mm (남은 오차 " + Math.round(left[0] / MM * 10) / 10 + ", " + Math.round(left[1] / MM * 10) / 10 + "mm)");
                    if (Math.abs(left[0]) > MM || Math.abs(left[1]) > MM) log.push("잠깐 리본 위치가 국부론과 1mm 넘게 다름 — 화면 확인");
                } catch (e) { RIB_CORR = [0, 0]; log.push("잠깐 리본 위치 보정 실패: " + e); }
            }
            n++;
        } catch (e) { log.push("잠깐 리본 넣기(" + p.contents.substr(0, 10) + "): " + e); }
    }
    return n;
}
var RESULT = null;     // { doc, src, summary }

// ── 공통 도우미 ──────────────────────────────────────────
function say(msg) {
    // UXP 스크립트에는 alert가 없을 수 있다 → 인디자인 대화상자로 대신 띄운다
    if (typeof alert === "function") { try { alert(msg); return; } catch (e) {} }
    try { if (typeof console !== "undefined") console.log(msg); } catch (e) {}
    try {
        var d = APP.dialogs.add({ name: "조판 결과" });
        var col = d.dialogColumns.add();
        var lines = String(msg).split("\n");
        for (var i = 0; i < lines.length && i < 30; i++) col.staticTexts.add({ staticLabel: lines[i] || " " });
        d.show(); d.destroy();
    } catch (e) {}
}
function filePath(f) {
    // ExtendScript는 File 객체, UXP는 경로 문자열을 돌려준다
    if (f === null || f === undefined) return "";
    if (typeof f === "string") return f;
    return f.fsName || f.nativePath || String(f);
}
function withSource(srcFile, label, fn) {
    // 원본 파일을 받는 메서드: 받은 값 그대로 시도 → 실패하면 경로 문자열로 다시 시도
    try { fn(srcFile); return; } catch (e1) {
        var p = filePath(srcFile);
        if (p && p !== srcFile) { try { fn(p); return; } catch (e2) { log.push(label + ": " + e2); return; } }
        log.push(label + ": " + e1);
    }
}
function findStyle(doc, coll, name) { var s = doc[coll].itemByName(name); return s.isValid ? s : null; }
function setp(obj, k, v) {
    var who = "";
    try { who = obj.name; } catch (e) {}
    try { obj[k] = v; } catch (e) { log.push(who + "." + k + ": " + e); return; }
    // UXP에서는 잘못된 속성 이름이 오류 없이 무시될 수 있다 → 숫자·참거짓은 다시 읽어 확인
    if (typeof v === "number" || typeof v === "boolean") {
        var r; try { r = obj[k]; } catch (e) { r = undefined; }
        if (typeof v === "number" ? !(typeof r === "number" && Math.abs(r - v) < 0.01) : r !== v)
            log.push(who + "." + k + " 적용 안 됨(값 " + r + ")");
    }
}
function fontName(family, styles) {
    // 설치된 글꼴에서 '가족\t스타일' 이름을 찾는다. 스타일 이름 후보를 차례로 시도
    for (var i = 0; i < styles.length; i++) {
        var n = family + "\t" + styles[i];
        try { if (APP.fonts.itemByName(n).isValid) return n; } catch (e) {}
    }
    log.push("글꼴 없음: " + family + " " + styles.join("/") + " — 국부론 패키지의 Document fonts가 새 문서에는 적용되지 않았을 수 있음");
    return null;
}
function swatchOrMake(doc, names, cmyk) {
    for (var i = 0; i < names.length; i++) { var s = doc.swatches.itemByName(names[i]); if (s.isValid) return s; }
    try {
        var c = doc.colors.add({ name: names[0], model: E("ColorModel").PROCESS, space: E("ColorSpace").CMYK, colorValue: cmyk });
        log.push("견본 새로 만듦: " + names[0] + " (국부론에서 같은 이름을 못 찾음)");
        return c;
    } catch (e) { log.push("견본 만들기 실패: " + names[0] + ": " + e); return doc.swatches.itemByName("Black"); }
}
function isRightPage(page) {
    // 마주 보는 페이지, 1쪽 시작: documentOffset 짝수 = 오른쪽(홀수 쪽). 열거형 비교를 피한다(UXP 차이)
    return page.documentOffset % 2 === 0;
}

// ── 본 작업 ──────────────────────────────────────────────
function main() {
    started = true;
    if (APP.documents.length === 0) { say("《국부론 수업》 파일을 먼저 여세요."); return; }
    var src = APP.activeDocument;
    if (!src.saved) { say("열린 문서를 먼저 저장하세요(스타일을 파일에서 가져옵니다)."); return; }
    var srcFile = src.fullName;
    var srcMasterName = mainMasterName(src);
    var MU = E("MeasurementUnits");
    APP.scriptPreferences.measurementUnit = MU.POINTS;

    // 1) 새 문서: 판형 150×214, 여백 위19.5 아래31 안쪽27 바깥22, 1단, 도련 3 (국부론 IDML 값)
    var doc = APP.documents.add();
    var dp = doc.documentPreferences;
    dp.facingPages = true; dp.pageWidth = 150 * MM; dp.pageHeight = 214 * MM;
    dp.documentBleedTopOffset = 3 * MM; dp.documentBleedBottomOffset = 3 * MM;
    dp.documentBleedInsideOrLeftOffset = 3 * MM; dp.documentBleedOutsideOrRightOffset = 3 * MM;
    setMargins(doc.marginPreferences);
    var ms0 = doc.masterSpreads.item(0);
    for (var mi = 0; mi < ms0.pages.length; mi++) setMargins(ms0.pages.item(mi).marginPreferences);

    // 2) 국부론에서 스타일·견본·부모 페이지 가져오기
    var CR = E("GlobalClashResolutionStrategy").LOAD_ALL_WITH_OVERWRITE, IF = E("ImportFormat");
    withSource(srcFile, "견본", function (f) { doc.loadSwatches(f); });
    withSource(srcFile, "문자·문단 스타일", function (f) { doc.importStyles(IF.TEXT_STYLES_FORMAT, f, CR); });
    withSource(srcFile, "개체 스타일", function (f) { doc.importStyles(IF.OBJECT_STYLES_FORMAT, f, CR); });
    withSource(srcFile, "표 스타일", function (f) { doc.importStyles(IF.TABLE_AND_CELL_STYLES_FORMAT, f, CR); });
    withSource(srcFile, "부모 페이지", function (f) { doc.loadMasters(f, CR); });
    var master = pickMaster(doc, srcMasterName);
    fixRunningHead(doc);
    RIBBON = copyRibbon(src, doc);
    DOBIRA_SRC = findDobiraSource(src);

    // 3) 이 책용 스타일 만들기 — 국부론 스타일을 바탕으로
    makeStyles(doc);

    // 4) 장마다 흘리기
    var LO = E("LocationOptions");
    // 앞부속 자리: 1~3쪽(표제지·판권·속표지)은 부모 페이지 없이 비워 두고 이름표만 둔다
    var rs = DATA.front.reserve;
    for (var r = 0; r < rs.length; r++) {
        var fp = (r === 0) ? doc.pages.item(0) : doc.pages.add(LO.AT_END);
        try { fp.appliedMaster = E("NothingEnum").NOTHING; } catch (e) { log.push(rs[r] + " 쪽 부모 페이지 없음 지정: " + e); }
        label(fp, "[" + rs[r] + " 자리]");
    }
    report.push("앞부속: 1~" + rs.length + "쪽 " + rs.join("·") + " 자리");
    // 머리말 자리: 4쪽부터
    var pp = doc.pages.add(LO.AT_END);
    pp.appliedMaster = master;
    addSection(doc, pp, "머리말");
    var pres = flow(doc, pp, { key: "머리말", p: [["본문", DATA.front.preface, "", []]] }, master);
    report.push("머리말: " + pp.name + "~" + pres.last + "쪽 자리(원고 미입수). 1장 도비라가 짝수 쪽에서 시작하도록 뒤에 빈 쪽이 생길 수 있음");
    var blanks = [];
    for (var c = 0; c < DATA.book.length; c++) {
        var ch = DATA.book[c];
        var page = doc.pages.add(LO.AT_END);
        var line = (ch.num ? ch.num + "장" : ch.key) + ": ";
        if (ch.num) {
            // 도비라 펼침면(짝수 쪽 + 홀수 쪽): 지금 쪽이 홀수(오른쪽)면 그 쪽을 빈 쪽으로 두고 다음 쪽부터.
            // 국부론처럼 빈 쪽과 도비라 펼침면에는 부모 페이지를 걸지 않는다(러닝헤드·쪽번호 없음)
            if (isRightPage(page)) { noMaster(page); blanks.push(page.name); page = doc.pages.add(LO.AT_END); }
            noMaster(page);
            var right = doc.pages.add(LO.AT_END); noMaster(right);
            dobira(doc, right, ch);
            // 국부론처럼 도비라 쪽에서 섹션을 시작하고 장 제목을 섹션 표시자로 → 오른쪽 러닝헤드에 장 제목
            addSection(doc, right, ch.title);
            line += "도비라 " + page.name + "~" + right.name + "쪽, ";
            page = doc.pages.add(LO.AT_END);
        } else {
            addSection(doc, page, "책을 덮으며");
        }
        page.appliedMaster = master;
        line += "본문 " + page.name + "쪽부터";
        var res = flow(doc, page, ch, master);
        line += " " + res.last + "쪽까지" + (res.overset ? " ※넘침 남음" : "");
        report.push(line);
    }
    if (blanks.length) report.push("빈 쪽(부모 페이지 없음): " + blanks.join(", ") + "쪽");
    try { if (RIBBON) RIBBON.remove(); } catch (e) {}
    var figTotal = 0; for (var fk in DATA.figFile) figTotal++;
    report.push("도판: 시안 PDF " + FIG_N + "/" + figTotal + "개 넣음(시안 없는 1-2·1-5는 회색 자리 상자)");
    if (FIG_MISS.length) log.push("시안 파일 없음: " + FIG_MISS.join(", "));
    report.push("잠깐 코너: 제목 " + DATA.jamkkanN + "개, 리본 " + RIBBON_N + "개");
    if (RIBBON && RIBBON_N !== DATA.jamkkanN) log.push("잠깐 리본 수(" + RIBBON_N + ")가 제목 수(" + DATA.jamkkanN + ")와 다름");
    report.push("괄호: " + DATA.parenCount + "곳에서 괄호 기호를 지우고 '한글괄호'·'영문괄호' 문자 스타일 적용, 긴 괄호 " + DATA.longParen + "곳은 괄호를 남기고 10pt('긴괄호'). 출처·도판 자리는 그대로");
    try { APP.scriptPreferences.measurementUnit = E("AutoEnum").AUTO_VALUE; } catch (e) {}   // AUTO_VALUE는 AutoEnum에 있다
    var summary = "조판 완료: 총 " + doc.pages.length + "쪽\n" + report.join("\n") +
        (log.length ? ("\n\n확인 필요 " + log.length + "건 (전체는 1쪽 왼쪽 대지의 '조판 기록')\n" + log.slice(0, 12).join("\n")) : "\n\n확인 필요 없음");
    writeLog(doc, summary + (log.length > 12 ? "\n" + log.slice(12).join("\n") : ""));
    RESULT = { doc: doc, src: filePath(srcFile), summary: summary };
}

function noMaster(page) {
    try { page.appliedMaster = E("NothingEnum").NOTHING; } catch (e) { log.push(page.name + "쪽 부모 페이지 없음 지정: " + e); }
}
function addSection(doc, page, marker) {
    // 국부론: 머리말·부 도비라 쪽에서 섹션 시작, 쪽번호 이어 매김, 섹션 표시자 = 부 제목(오른쪽 러닝헤드에 나옴)
    try {
        var s = doc.sections.add(page);
        setp(s, "continueNumbering", true);
        try { s.includeSectionPrefix = false; } catch (e) {}
        s.marker = marker;
    } catch (e) { log.push("섹션 " + marker + ": " + e); }
}
function fixRunningHead(doc) {
    // 국부론 부모 페이지의 왼쪽 러닝헤드 '10대를 위한 국부론 수업'을 이 책 제목으로 바꾼다(쪽번호 표시자는 그대로)
    var n = 0, FROM = "국부론 수업", TO = "부동산 교양 수업";
    for (var m = 0; m < doc.masterSpreads.length; m++) {
        var tfs = doc.masterSpreads.item(m).textFrames;
        for (var i = 0; i < tfs.length; i++) {
            try {
                var st = tfs.item(i).parentStory, at = String(st.contents).indexOf(FROM);
                if (at < 0) continue;
                st.characters.itemByRange(at, at + FROM.length - 1).contents = TO;
                n++;
            } catch (e) { log.push("러닝헤드 바꾸기: " + e); }
        }
    }
    if (n) report.push("러닝헤드: '10대를 위한 " + TO + "'로 바꿈(" + n + "곳)");
    else log.push("러닝헤드에서 '" + FROM + "'를 찾지 못함 — 부모 페이지를 직접 확인할 것");
}

function label(page, text, top) {
    // 자리 이름표(인쇄 안 됨). top: 쪽 위에서 mm
    try {
        var b = page.bounds, y = (top === undefined ? 90 : top);
        var t = page.textFrames.add({ geometricBounds: [b[0] + y * MM, b[1] + 20 * MM, b[0] + (y + 20) * MM, b[3] - 20 * MM] });
        t.contents = text;
        try { t.nonprinting = true; } catch (e) {}
    } catch (e) { log.push("이름표 " + text + ": " + e); }
}

function setMargins(mp) {
    // 마주 보는 페이지에서 left = 안쪽, right = 바깥
    mp.top = 19.5 * MM; mp.bottom = 31 * MM; mp.left = 27 * MM; mp.right = 22 * MM; mp.columnCount = 1;
}

function mainMasterName(src) {
    // 국부론 페이지에 가장 많이 적용된 부모 페이지 이름 = 본문용
    var count = {}, best = "", n = 0;
    try {
        var pages = src.pages;
        for (var i = 0; i < pages.length; i++) {
            var m = pages.item(i).appliedMaster;
            if (!m || !m.isValid) continue;
            var k = m.name; count[k] = (count[k] || 0) + 1;
            if (count[k] > n) { n = count[k]; best = k; }
        }
    } catch (e) { log.push("국부론 부모 페이지 집계: " + e); }
    return best;
}
function pickMaster(doc, name) {
    if (name) { var m = doc.masterSpreads.itemByName(name); if (m.isValid) { report.push("부모 페이지: " + name + " (국부론 본문에 가장 많이 쓰인 것)"); return m; } }
    var last = doc.masterSpreads.item(doc.masterSpreads.length - 1);
    log.push("본문 부모 페이지를 이름으로 못 찾아 마지막 부모 페이지(" + last.name + ")를 썼음");
    return last;
}

function frameBounds(page) {
    var b = page.bounds, top = 19.5 * MM, bot = 31 * MM, ins = 27 * MM, out = 22 * MM;
    var isRight = isRightPage(page);
    return [b[0] + top, b[1] + (isRight ? ins : out), b[2] - bot, b[3] - (isRight ? out : ins)];
}

// ── 시안 파일 찾기·넣기 ─────────────────────────────────
var SIAN_DIR = null, FIG_N = 0, FIG_MISS = [];
function sianDir() {
    if (SIAN_DIR !== null) return SIAN_DIR;
    var c = [];
    try { if (!ID) c.push(File($.fileName).parent.parent.fsName + "/시안"); } catch (e) {}   // 스크립트 옆(조판/..)
    c.push(DATA.sianAbs);
    for (var i = 0; i < c.length; i++) if (exists(c[i]) === true) { SIAN_DIR = c[i]; return SIAN_DIR; }
    SIAN_DIR = "";
    log.push("시안 폴더를 찾지 못해 도판을 넣지 않음: " + c.join(" / "));
    return SIAN_DIR;
}
function placeInto(frame, name, fill) {
    // frame에 시안 파일을 넣고 맞춘다. fill: true면 틀을 꽉 채움(도비라), 아니면 비율대로 맞춤
    var dir = sianDir(); if (!dir) return false;
    var p = dir + "/" + name;
    if (exists(p) !== true) { FIG_MISS.push(name); return false; }
    var pp = APP.pdfPlacePreferences, oldCrop = null;
    try { oldCrop = pp.pdfCrop; pp.pdfCrop = E("PDFCrop").CROP_MEDIA; } catch (e) {}   // PDF 크기 그대로(실제 크기 시안)
    try { if (!ID) frame.place(new File(p)); else frame.place(p); }
    catch (e) { try { frame.place(p); } catch (e2) { log.push("넣기 실패 " + name + ": " + e2); return false; } }
    finally { try { if (oldCrop !== null) pp.pdfCrop = oldCrop; } catch (e) {} }
    var FO = E("FitOptions");
    try { frame.fit(fill ? FO.FILL_PROPORTIONALLY : FO.PROPORTIONALLY); frame.fit(FO.CENTER_CONTENT); } catch (e) {}
    return true;
}
var DOBIRA_SRC = null;   // 국부론 도비라 쪽의 장식(띠·테두리·선·글상자) — 그림만 빼고
function findDobiraSource(src) {
    // 국부론에서 그림이 있고 반투명 띠가 있는 첫 쪽(19쪽 '애덤 스미스는 누구인가?')
    try {
        for (var i = 0; i < src.pages.length; i++) {
            var pg = src.pages.item(i), its = pg.pageItems, img = false, band = false, keep = [];
            for (var k = 0; k < its.length; k++) {
                var it = its.item(k).getElements()[0], hasImg = false;
                try { hasImg = it.images.length > 0; } catch (e) {}
                if (hasImg) { img = true; continue; }
                try { if (it.transparencySettings.blendingSettings.opacity < 100 && it.constructor.name === "Rectangle") band = true; } catch (e) {}
                keep.push(it);
            }
            if (img && band && keep.length >= 3) { report.push("도비라 장식: 국부론 " + pg.name + "쪽에서 복사"); return { page: pg, items: keep }; }
        }
    } catch (e) { log.push("국부론 도비라 찾기: " + e); }
    log.push("국부론 도비라를 찾지 못함 — 도비라는 회색 바탕으로 둠");
    return null;
}

function dobira(doc, page, ch) {
    var b = page.bounds, bl = 3 * MM;
    var r = page.rectangles.add({ geometricBounds: [b[0] - bl, b[1], b[2] + bl, b[3] + bl] });
    var k80 = doc.swatches.itemByName("C=0 M=0 Y=0 K=80");
    setp(r, "fillColor", k80.isValid ? k80 : doc.swatches.itemByName("Black"));
    // 공통 일러스트(확정 2026-11-09)를 재단선까지 꽉 채우고, 국부론 도비라 장식을 같은 자리에 얹는다
    if (DATA.dobiraImg && placeInto(r, DATA.dobiraImg, true) && DOBIRA_SRC) {
        var sb = DOBIRA_SRC.page.bounds, num = null, ttl = null;
        // 복제 순서만으로는 앞뒤가 국부론과 같게 쌓이지 않는다(5·6차 실행) → 복사 뒤 글이 든 개체를 맨 앞으로, 그림을 맨 뒤로 직접 옮긴다
        var withText = [];
        for (var i = DOBIRA_SRC.items.length - 1; i >= 0; i--) {
            try {
                var s = DOBIRA_SRC.items[i], c = s.duplicate(page), g = s.geometricBounds;
                var hasT = (c.constructor.name === "TextFrame");
                try { var api = c.allPageItems; for (var z = 0; z < api.length && !hasT; z++) if (api[z].constructor.name === "TextFrame") hasT = true; } catch (eW) {}
                if (hasT) withText.push(c);
                c.move([b[1] + (g[1] - sb[1]), b[0] + (g[0] - sb[0])]);
                var tfs = (c.constructor.name === "TextFrame") ? [c] : c.textFrames;
                var all = []; try { all = c.allPageItems; } catch (e) {}
                if (c.constructor.name === "TextFrame") all = [c];
                for (var a = 0; a < all.length; a++) {
                    if (all[a].constructor.name !== "TextFrame") continue;
                    if (/^\s*\d+\s*$/.test(String(all[a].contents))) num = all[a]; else ttl = all[a];
                }
            } catch (e) { log.push("도비라 장식 복사: " + e); }
        }
        try { r.sendToBack(); } catch (e) {}
        for (var w = 0; w < withText.length; w++) { try { withText[w].bringToFront(); } catch (e) {} }
        if (num && ttl) {
            num.parentStory.contents = ch.num;
            ttl.parentStory.contents = ch.dobira.join("\r");
            try { ttl.recompose(); if (ttl.overflows) log.push(ch.num + "장 도비라 제목이 글상자를 넘침"); } catch (e) {}
            return;
        }
        log.push(ch.num + "장 도비라: 국부론 번호·제목 글상자를 못 찾아 기본 배치로 둠");
    }
    var t = page.textFrames.add({ geometricBounds: [b[0] + 95 * MM, b[1] + 38.3 * MM, b[0] + 160 * MM, b[1] + 115 * MM] });
    // 장 번호와 장 제목만 넣는다. 도비라 일러스트 안내는 인쇄 안 되는 이름표로 따로(넘친 글 방지)
    // 국부론 도비라처럼 제목을 어절 사이에서 두 줄로 나눈다(글자 중간 줄바꿈 방지)
    t.contents = ch.num + "\r" + ch.dobira.join("\r");
    var pn = findStyle(doc, "paragraphStyles", "도비라 번호"), pt = findStyle(doc, "paragraphStyles", "도비라 제목");
    var tp = t.parentStory.paragraphs;
    if (pn) tp.item(0).appliedParagraphStyle = pn;
    if (pt) for (var i = 1; i < tp.length; i++) tp.item(i).appliedParagraphStyle = pt;
    try { t.recompose(); if (t.overflows) log.push(ch.num + "장 도비라 제목이 글상자를 넘침"); } catch (e) {}
    label(page, "[도비라 자리 — 공통 일러스트: 시안/illust/도비라_공통_v1.png]", 170);
}

function flow(doc, page, ch, master) {
    var LO = E("LocationOptions");
    var tf = page.textFrames.add({ geometricBounds: frameBounds(page) });
    var texts = [];
    for (var i = 0; i < ch.p.length; i++) texts.push(ch.p[i][1]);
    tf.contents = texts.join("\r");
    var story = tf.parentStory, paras = story.paragraphs;
    if (paras.length !== ch.p.length) log.push(ch.key + ": 문단 수 불일치(데이터 " + ch.p.length + ", 인디자인 " + paras.length + ")");
    var cache = {};
    for (var j = 0; j < ch.p.length && j < paras.length; j++) {
        var nm = ch.p[j][0];
        if (!(nm in cache)) { cache[nm] = findStyle(doc, "paragraphStyles", nm); if (!cache[nm]) log.push("스타일 없음: " + nm); }
        if (cache[nm]) paras.item(j).applyParagraphStyle(cache[nm], true);
        // 괄호를 지운 자리: 괄호 속 글자에 국부론 문자 스타일 '한글괄호'·'영문괄호'
        var spans = ch.p[j][3] || [];
        for (var sp = 0; sp < spans.length; sp++) {
            var csn = spans[sp][2];
            if (!(("c:" + csn) in cache)) { cache["c:" + csn] = findStyle(doc, "characterStyles", csn); if (!cache["c:" + csn]) log.push("문자 스타일 없음: " + csn); }
            if (!cache["c:" + csn]) continue;
            try { paras.item(j).characters.itemByRange(spans[sp][0], spans[sp][0] + spans[sp][1] - 1).appliedCharacterStyle = cache["c:" + csn]; }
            catch (e) { log.push(ch.key + " 괄호 문자 스타일(" + ch.p[j][1].substr(0, 12) + "…): " + e); }
        }
    }
    // 먼저 끝까지 흘린다. 넘친(overset) 텍스트 안에는 개체를 넣을 수 없다
    var th = thread(doc, tf, ch, master);
    // 도판 자리: 시안 크기의 회색 상자를 '줄 위' 고정 개체로 넣는다.
    // (인라인으로 넣으면 고정 행간 26pt 때문에 상자가 윗줄 글자를 덮는다)
    var AP = E("AnchorPosition"), HA = E("HorizontalAlignment");
    // 회색 자리 상자: 국부론에 회색 견본이 없어 Paper(흰색)로 칠해져 보이지 않던 문제 → K15 견본을 만들고 개체 스타일 '도판 자리'로
    var figOS = findStyle(doc, "objectStyles", "도판 자리");
    var figPS = findStyle(doc, "paragraphStyles", "도판 자리");
    for (var k = ch.p.length - 1; k >= 0; k--) {
        var fid = ch.p[k][2];
        if (!fid || k >= paras.length) continue;
        var ids = (fid === "2-1") ? ["2-1R", "2-1"] : [fid];   // 뒤에서부터 넣으므로 결과 순서는 2-1, 2-1R
        // 시안 PDF가 있는 도판은 원고의 도판 설명 글(인쇄용이 아님)을 지우고 그림만 남긴다
        var hasFile = true;
        for (var q0 = 0; q0 < ids.length; q0++) if (!DATA.figFile[ids[q0]]) hasFile = false;
        if (hasFile) {
            try {
                var pk = paras.item(k), nc = pk.characters.length;
                var endAt = (pk.characters.item(nc - 1).contents === "\r") ? nc - 2 : nc - 1;
                if (endAt >= 0) pk.characters.itemByRange(0, endAt).remove();
            } catch (eDel) { log.push("도" + fid + " 설명 글 지우기: " + eDel); }
        }
        for (var q = 0; q < ids.length; q++) {
            var sz = DATA.fig[ids[q]] || [101, 60], h = sz[1], file = DATA.figFile[ids[q]];
            if (h > FIG_MAX_H) { log.push("도" + ids[q] + ": 높이 " + h + "mm가 판면에 안 들어가 상자를 " + FIG_MAX_H + "mm로 줄임" + (file ? "(시안 " + Math.round(FIG_MAX_H / h * 100) + "%로 축소)" : "") + " — 실제 도판은 한 면 전체로 따로 앉힐 것"); h = FIG_MAX_H; }
            try {
                if (q > 0) paras.item(k).insertionPoints.item(0).contents = "\r";   // 2-1 펼침면: 상자마다 문단을 나눈다
                var ip = paras.item(k).insertionPoints.item(0), box;
                try { box = file ? ip.rectangles.add() : ip.textFrames.add(); }
                catch (eAdd) {
                    // 대안: 쪽에 상자를 만든 뒤 그 자리에 고정 개체로 넣는다
                    var pg = ip.parentTextFrames[0].parentPage;
                    box = file ? pg.rectangles.add() : pg.textFrames.add();
                    box.anchoredObjectSettings.insertAnchoredObject(ip, AP.ABOVE_LINE);
                }
                box.geometricBounds = [0, 0, h * MM, sz[0] * MM];
                var ao = box.anchoredObjectSettings;
                setp(ao, "anchoredPosition", AP.ABOVE_LINE);
                setp(ao, "horizontalAlignment", HA.CENTER_ALIGN);
                if (file) {
                    try { box.strokeWeight = 0; box.fillColor = doc.swatches.itemByName("None"); } catch (eF) {}
                    if (placeInto(box, file, false)) { FIG_N++; continue; }
                    // 넣기에 실패하면 회색 자리 상자로 되돌린다
                    try { box.fillColor = FIG_GRAY; } catch (eF2) {}
                    continue;
                }
                box.contents = "[도" + ids[q].replace("R", " 오른쪽") + "] " + sz[0] + "×" + sz[1] + "mm — 인디자인에서 제작: " + (DATA.guide[ids[q]] || "시안 참고");
                if (figOS) { try { box.applyObjectStyle(figOS, true); } catch (eOS) { box.appliedObjectStyle = figOS; } }
                if (figPS) try { box.parentStory.paragraphs.item(0).appliedParagraphStyle = figPS; } catch (ePS) {}
                if (FIG_GRAY) box.fillColor = FIG_GRAY;
            } catch (e) { log.push("도판 자리 " + ids[q] + ": " + e); }
        }
    }
    // 상자 때문에 늘어난 만큼 다시 흘린다
    th = thread(doc, th.last, ch, master);
    // 잠깐 리본: 흘리기가 끝난 뒤 제목 문단마다 붙인다(사용자 지정 고정 개체라 글 흐름을 밀지 않는다)
    var nr = placeRibbons(story);
    if (nr) { RIBBON_N += nr; th = thread(doc, th.last, ch, master); }
    return { last: th.last.parentPage ? th.last.parentPage.name : page.name, overset: th.overset };
}

function thread(doc, start, ch, master) {
    // 넘친 글을 새 쪽으로 이어 흘리기. 새 틀에 글이 한 자도 안 들어가면(안 들어가는 개체) 멈춘다
    var LO = E("LocationOptions");
    var last = start, guard = 0, overset = false;
    try { last.recompose(); } catch (e) {}
    while (last.overflows) {
        if (guard++ >= 400) { overset = true; log.push(ch.key + ": 400쪽을 넘겨 흘리기를 멈춤"); break; }
        var np = doc.pages.add(LO.AT_END);
        np.appliedMaster = master;
        var nf = np.textFrames.add({ geometricBounds: frameBounds(np) });
        last.nextTextFrame = nf;
        try { nf.recompose(); } catch (e) {}
        if (nf.characters.length === 0) {
            overset = true;
            log.push(ch.key + ": " + np.name + "쪽 틀에 글이 들어가지 않아 멈춤(판면보다 큰 개체 확인)");
            nf.remove(); np.remove(); break;
        }
        last = nf;
    }
    return { last: last, overset: overset };
}

function makeStyles(doc) {
    var P = doc.paragraphStyles;
    function mk(name, base, props) {
        var s = P.itemByName(name);
        if (!s.isValid) s = P.add({ name: name });
        var b = P.itemByName(base);
        if (b.isValid) setp(s, "basedOn", b); else log.push("바탕 스타일 없음: " + base + " (" + name + ")");
        for (var i = 0; i < props.length; i++) {
            if (props[i][1] === null) continue;   // 글꼴을 못 찾은 경우
            setp(s, props[i][0], props[i][1]);
        }
        return s;
    }
    // 서체·스타일은 모두 국부론 수업 스타일을 바탕으로 한다(2026-11-11 편집자 요청). 국부론에 없는 요소(셋째 단계 제목·목록·질문·
    // 잠깐 상자·출처 목록)는 국부론의 가장 가까운 스타일을 바탕으로 하고, 서체는 국부론에서 쓴 것만 쓴다.
    var SP = E("StartParagraph"), J = E("Justification");
    var yellow = swatchOrMake(doc, ["C=0 M=6 Y=68 K=0"], [0, 6, 68, 0]);
    var teal = swatchOrMake(doc, ["도해_청록 c80m30y40"], [80, 30, 40, 0]);
    FIG_GRAY = swatchOrMake(doc, ["C=0 M=0 Y=0 K=15"], [0, 0, 0, 15]);
    var gothicLt = fontName("Sandoll 고딕Neo1", ["03 Lt", "Lt"]);
    var gyeokdong = fontName("Sandoll 격동굴림2", ["06 Hv", "Hv"]);
    // 두 줄 제목이 쪽에서 갈라지지 않게. keepAllLinesTogether는 keepLinesTogether가 켜져 있어야 동작한다(3차 실행에서 확인)
    var heads = [["keepLinesTogether", true], ["keepAllLinesTogether", true]];
    // [확정 2026-11-10] 절 제목: 국부론 '대제목'과 같은 서체·크기·색, 새 쪽 시작만 끔
    mk("절 제목", "대제목", [["startParagraph", SP.ANYWHERE], ["spaceBefore", 39], ["spaceAfter", 6.5], ["keepWithNext", 3]].concat(heads));
    // 장마다 절 제목 색: '절 제목_01'~'_07'은 '절 제목'을 바탕으로 색만 국부론 장 색 견본으로
    for (var cn in DATA.chColor) {
        var sw = doc.swatches.itemByName(DATA.chColor[cn]);
        if (!sw.isValid) { log.push("장 색 견본 없음: " + DATA.chColor[cn] + " (" + cn + "장) — 기본 절 제목 색으로 둠"); mk("절 제목_" + cn, "절 제목", []); continue; }
        mk("절 제목_" + cn, "절 제목", [["fillColor", sw]]);
    }
    // [레퍼런스] 소제목 = 국부론 '큰 제목'(스터디윗미 03 Bold 13/26)
    mk("소제목", "큰 제목", [["spaceBefore", 13], ["keepWithNext", 2]].concat(heads));
    // 셋째 단계 제목 = 국부론 '학파 인물'(스터디윗미 03 Bold 10.5/26)에서 왼쪽 들여쓰기만 0
    mk("소소제목", "학파 인물", [["leftIndent", 0], ["firstLineIndent", 0], ["spaceBefore", 6.5], ["keepWithNext", 2]].concat(heads));
    mk("질문 제목", "소소제목", [["fillColor", teal]]);
    // 목록 = 국부론 '본문'에 내어쓰기만
    mk("목록", "본문", [["leftIndent", 4 * MM], ["firstLineIndent", -4 * MM]]);
    mk("번호 목록", "본문", [["leftIndent", 5 * MM], ["firstLineIndent", -5 * MM]]);
    // '잠깐!' 코너 = 국부론 잠깐 코너 실측(49·142쪽, 2026-11-11 편집자 요청). 국부론은 손으로 놓은 그룹이지만,
    // 여기서는 글 흐름을 따라 움직이도록 문단 음영으로 같은 모양을 만든다.
    //  상자: 폭 101mm(판면), 0/6/68/0 불투명도 36% → 농도 36%, 둥근 모서리 5mm
    //  글: 상자 안 왼 10.7 / 오른 10.8mm, 위 10mm, 아래 약 8mm
    //  제목: 스터디윗미 03 Bold 12/24pt, 본문: 스터디윗미 01 Light 10.5/24pt, 모든 문단 첫 줄 3mm, 자간 0
    //  리본('잠깐 !'): 국부론 리본 그룹을 복사해 제목 문단에 고정(상자 왼쪽 위에서 4.8mm 바깥)
    var bold = fontName("Sandoll 스터디윗미", ["03 Bold", "Bold"]), light = fontName("Sandoll 스터디윗미", ["01 Light", "Light"]);
    var RC = E("CornerOptions").ROUNDED_CORNER, R5 = 5 * MM;
    var shade = [["paragraphShadingOn", true], ["paragraphShadingColor", yellow], ["paragraphShadingTint", 36],
                 ["paragraphShadingTopOffset", JBOX.top * MM], ["paragraphShadingBottomOffset", JBOX.bottom * MM],
                 ["paragraphShadingLeftOffset", 0], ["paragraphShadingRightOffset", 0],
                 ["paragraphShadingTopLeftCornerOption", RC], ["paragraphShadingTopRightCornerOption", RC],
                 ["paragraphShadingBottomLeftCornerOption", RC], ["paragraphShadingBottomRightCornerOption", RC],
                 ["paragraphShadingTopLeftCornerRadius", R5], ["paragraphShadingTopRightCornerRadius", R5],
                 ["paragraphShadingBottomLeftCornerRadius", R5], ["paragraphShadingBottomRightCornerRadius", R5],
                 ["mergeConsecutiveParaBorders", true]];   // 이어진 문단을 한 상자로(모서리가 문단마다 둥글어지지 않게)
    try { shade.push(["paragraphShadingTopOrigin", E("ParagraphShadingTopOriginEnum").ASCENT_TOP_ORIGIN]); } catch (e) {}
    try { shade.push(["paragraphShadingBottomOrigin", E("ParagraphShadingBottomOriginEnum").DESCENT_BOTTOM_ORIGIN]); } catch (e) {}
    var boxIn = [["leftIndent", 10.7 * MM], ["rightIndent", 10.8 * MM], ["firstLineIndent", 3 * MM], ["tracking", 0]];
    mk("잠깐 제목", "본문", [["appliedFont", bold], ["pointSize", 12], ["leading", 24], ["justification", J.LEFT_ALIGN],
        ["spaceBefore", JBOX.before * MM], ["spaceAfter", 0], ["keepWithNext", 2]].concat(heads, boxIn, shade));
    mk("잠깐 본문", "본문", [["appliedFont", light], ["pointSize", 10.5], ["leading", 24], ["spaceAfter", JBOX.after * MM]].concat(boxIn, shade));
    // 여러 문단 상자: 국부론처럼 모든 문단 첫 줄 3mm, 문단 사이 간격 없음, 마지막 문단 뒤만 간격
    mk("잠깐 본문 첫", "잠깐 본문", [["spaceAfter", 0]]);
    mk("잠깐 본문 이어", "잠깐 본문 첫", []);
    mk("잠깐 본문 끝", "잠깐 본문 이어", [["spaceAfter", JBOX.after * MM]]);
    // 도판 자리 = 국부론 '캡션'(스터디윗미 03 Bold 10/12.8, 가운데)
    mk("도판 자리", "캡션", [["spaceBefore", 6.5], ["spaceAfter", 13]]);
    // 출처 목록 = 국부론 '표 본문'(고딕Neo1 Lt 8/12, 자간 −50)에 내어쓰기
    mk("참고 자료", "표 본문", [["appliedFont", gothicLt], ["justification", J.LEFT_ALIGN], ["firstLineIndent", -6 * MM], ["leftIndent", 6 * MM]]);
    mk("참고 자료 제목", "소소제목", [["spaceBefore", 13]]);
    // 도비라 = 국부론 19쪽 실측: 장 제목 격동굴림2 06 Hv 18/23.6pt, 자간 0, 흰색, 가운데('만화 대사' 바탕). 장 번호 20pt
    var white = doc.swatches.itemByName("Paper");
    mk("도비라 제목", "만화 대사", [["appliedFont", gyeokdong], ["pointSize", 18], ["leading", 23.6], ["tracking", 0], ["fillColor", white], ["justification", J.CENTER_ALIGN]]);
    mk("도비라 번호", "도비라 제목", [["pointSize", 20], ["leading", 26], ["spaceAfter", 4]]);
    // 긴 괄호(한글 문장·구절): 괄호는 남기고 크기만 10pt. 서체·색은 문단 그대로(2026-11-11 편집자 결정)
    try {
        var lp = doc.characterStyles.itemByName("긴괄호");
        if (!lp.isValid) lp = doc.characterStyles.add({ name: "긴괄호" });
        setp(lp, "pointSize", 10);
    } catch (e) { log.push("문자 스타일 긴괄호: " + e); }
    // 도판 자리 상자 개체 스타일: K15 칠, 선 없음
    try {
        var os = doc.objectStyles.itemByName("도판 자리");
        if (!os.isValid) os = doc.objectStyles.add({ name: "도판 자리" });
        setp(os, "fillColor", FIG_GRAY);
        try { os.strokeColor = doc.swatches.itemByName("None"); } catch (e) {}
    } catch (e) { log.push("개체 스타일 도판 자리: " + e); }
}

function writeLog(doc, text) {
    try {
        var p = doc.pages.item(0), b = p.bounds;
        var t = p.textFrames.add({ geometricBounds: [b[0], b[1] - 130 * MM, b[2], b[1] - 10 * MM] });
        t.contents = text;
        t.name = "조판 기록";
        try { t.nonprinting = true; } catch (e) {}
    } catch (e) { log.push("조판 기록 글상자: " + e); }
}

// ── 저장 ────────────────────────────────────────────────
// 지정 폴더(conbo > 인디자인 > 10대를 위한 부동산 교양 수업)를 찾아 새 문서를 저장한다.
// 폴더를 못 찾거나, 같은 이름 파일이 있는지 확인할 수 없으면 저장하지 않는다(덮어쓰기 방지).
function exists(p) {
    // true / false / null(확인 불가)
    if (!ID) { try { return Folder(p).exists || File(p).exists; } catch (e) { return null; } }
    var fs = null; try { fs = require("fs"); } catch (e) { return null; }
    var missing = false, tries = [p, "file:" + p];
    for (var i = 0; i < tries.length; i++) {
        try { fs.lstatSync(tries[i]); return true; }
        catch (e) { if (/ENOENT|not ?found|no such|exist/i.test(String(e))) missing = true; }
    }
    return missing ? false : null;
}
function homeDirs(srcPath) {
    var out = [], m;
    if ((m = /^(\/Users\/[^\/]+)/.exec(srcPath))) out.push(m[1]);
    if ((m = /^([A-Za-z]:\\Users\\[^\\]+)/.exec(srcPath))) out.push(m[1]);
    if (!ID) { try { out.push(Folder("~").fsName); } catch (e) {} }
    else { try { out.push(require("os").homedir()); } catch (e) {} }
    out.push("/Users/" + DATA.save.user);
    return out;
}
function saveDoc(doc, srcPath) {
    var S = DATA.save, homes = homeDirs(srcPath), cands = [];
    for (var i = 0; i < homes.length; i++) {
        var sep = homes[i].indexOf("\\") >= 0 ? "\\" : "/", h = homes[i];
        var names = [S.folder].concat([]);
        for (var a = 0; a < (S.alt || []).length; a++) names.push([S.folder[0], S.alt[a]]);
        for (var nI = 0; nI < names.length; nI++) {
            var F = names[nI];
            var tails = [F, [S.user].concat(F), ["Documents", S.user].concat(F), ["Desktop", S.user].concat(F)];
            for (var t = 0; t < tails.length; t++) cands.push(h + sep + tails[t].join(sep));
        }
    }
    var folder = null, unknown = false;
    for (var c = 0; c < cands.length && !folder; c++) { var ex = exists(cands[c]); if (ex === true) folder = cands[c]; else if (ex === null) unknown = true; }
    if (!folder) return "저장 안 함: '" + S.user + " > " + S.folder.join(" > ") + "' 폴더를 " + (unknown ? "확인할 수 없음" : "찾지 못함") + ". [파일 > 저장]으로 직접 저장하세요.";
    var sep2 = folder.indexOf("\\") >= 0 ? "\\" : "/", path = null;
    for (var n = 1; n < 50 && !path; n++) {
        var p = folder + sep2 + S.file + (n > 1 ? "_" + n : "") + ".indd";
        var e2 = exists(p);
        if (e2 === null) return "저장 안 함: 같은 이름 파일이 있는지 확인할 수 없음(덮어쓰기 방지). 폴더: " + folder;
        if (e2 === false) path = p;
    }
    if (!path || path === srcPath) return "저장 안 함: 저장할 파일 이름을 정하지 못함";
    try { if (!ID) doc.save(new File(path)); else doc.save(path); }
    catch (e) { try { doc.save(path); } catch (e2b) { return "저장 실패: " + e2b + " (" + path + ")"; } }
    return "저장: " + path;
}

// 실행: 되돌리기 한 번으로 전체를 취소할 수 있게 doScript로 감싼다. 안 되면 그냥 실행
(function () {
    try {
        var lang = ID ? E("ScriptLanguage").UXPSCRIPT : E("ScriptLanguage").JAVASCRIPT;
        APP.doScript(main, lang, [], E("UndoModes").ENTIRE_SCRIPT, "부동산교양수업 조판");
        if (!started) main();   // doScript가 함수를 실행하지 않은 경우
    } catch (e) {
        if (!started) main(); else { say("실행 중 오류: " + e + "\n" + log.join("\n")); return; }
    }
    if (!RESULT) return;
    var saved = "";
    try { saved = saveDoc(RESULT.doc, RESULT.src); } catch (e) { saved = "저장 실패: " + e; }
    say(saved + "\n\n" + RESULT.summary);
})();
'''
JS = JS.replace("__DATA__", data)
for ext in ("idjs", "jsx"):
    with open(os.path.join(D, f"조판_부동산교양수업.{ext}"), "w", encoding="utf-8-sig" if ext == "jsx" else "utf-8") as f:
        f.write(JS)
print("ok", len(JS), "괄호 지움", PAREN_N, "긴 괄호(10pt)", LONG_N)
for x in paren_log: print("  긴 괄호:", x)
