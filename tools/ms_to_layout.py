# 원고(Google Docs → markdown)를 조판용 블록(JSON)과 인디자인 태그 텍스트로 바꾼다.
# 사용: python3 -I ms_to_layout.py <part1-4.md> <part5-7.md> <출력 폴더>
# 블록 = {"s": 문단 스타일, "t": 글자} / 장마다 파일 하나(ch01.json …, back.json)
import sys, re, json, os

FIG = {  # 원고의 '▣ 도판' 순서대로 붙일 도판 번호
    1: ["1-1", "1-2", "1-3", "1-4"], 2: ["2-1", "2-2", "2-3", "2-4"], 3: ["3-1", "3-2", "3-3", "3-4", "3-5", "3-6"],
    4: ["4-1", "4-2", "4-3", "4-4"], 5: ["5-1", "5-4", "5-5", "5-6", "5-7"], 6: ["6-1", "6-2"], 7: ["7-4"]}
EXTRA = {  # 원고에 '▣ 도판'이 없는 제안 도판: (장, 이 소제목/절 제목 뒤 첫 문단 다음, 도판 번호)
    (1, "우리 집값이 오르내리는 이유는?", "1-5"), (2, "역사 속 등기사항전부증명서 이야기", "2-5"),
    (3, "하나의 집, 두 개의 계약서? : 이중계약 사기", "3-7"), (5, "청약이란?", "5-2"),
    (6, "역사 속 부동산 이야기 — 맹모삼천지교를 다시 읽기", "6-4"), (6, "새로운 부동산 용어 : 브역대신공평초를 풀어 보자", "6-5"),
    (7, "[책 속의 책] 프롤로그: 새로운 시작은 늘 설레게 하지", "7-1"), (7, "[책 속의 책] 주하의 집 구하기 프로젝트 Part 1: 내가 살고 싶은 집 조건 정하기", "7-2"),
    (7, "[책 속의 책] 주하의 집 구하기 프로젝트 Part 2: 집 보러 다니기", "7-3"), (7, "다가올 미래, 집의 모양과 생활은 어떻게 달라질까?", "7-5"),
    (7, "[책 속의 책] 에필로그 : 드디어 이사!", "7-6")}
FIGNAME = {}  # 도판 이름(시안 파일)과 크기는 조판 스크립트에서 붙인다

def clean(s):
    s = re.sub(r"\\([!#*\[\]~\-_.()>+`|{}])", r"\1", s)        # 마크다운 이스케이프 해제
    s = s.replace("**", "").strip()
    s = re.sub(r"^\*(.+)\*$", r"\1", s)                          # 줄 전체 기울임
    return re.sub(r"\s{2,}", " ", s).strip()

def split_merged(s):
    """상자 안에서 구분 없이 붙은 문단을 나눈다: 문장 끝 부호 바로 뒤에 공백 없이 한글·여는 따옴표가 오면 새 문단."""
    return [p.strip() for p in re.split(r"(?<=[.!?。])(?=[가-힣“‘])", s) if p.strip()]

def convert(paths):
    lines = []
    for p in paths: lines += open(p, encoding="utf-8").read().split("\n")
    chapters, cur, ch, figi = {}, None, 0, 0
    sub_n, log = 0, []
    in_table_multi = False
    for raw in lines:
        ln = raw.rstrip()
        if not ln.strip() or re.match(r"^\|\s*:?-{3,}", ln): continue
        if ln.startswith("# "):
            t = clean(ln[2:])
            m = re.match(r"제(\d)장 (.+)", t)
            if m:
                ch = int(m.group(1)); figi = 0; cur = chapters.setdefault(f"ch{ch:02d}", [])
                cur.append({"s": "장 제목", "t": m.group(2), "n": f"{ch:02d}"})
            elif t.startswith("책을 덮으며") or t.startswith("자료와 출처"):
                ch = 99; cur = chapters.setdefault("back", [])
                cur.append({"s": "절 제목", "t": t})
            continue                                              # 책 제목 줄은 건너뜀
        if cur is None: continue
        if ln.startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) > 1:                                     # 여러 칸 표(가점제) → 도판 자리 하나
                if not in_table_multi:
                    cur.append({"s": "도판 자리", "t": "[도5-3] 가점제 표 — 표 스타일로 조판(시안: 도5-3_가점제표_v1)", "fig": "5-3"})
                    in_table_multi = True
                continue
            c = clean(cells[0])
            if c.startswith("▣ 도판"):
                fid = FIG.get(ch, [None] * 9)[figi] if figi < len(FIG.get(ch, [])) else None
                figi += 1
                cur.append({"s": "도판 자리", "t": f"[도{fid}] " + re.sub(r"^▣ 도판\s*(\(추가\))?\s*", "", c)[:60] + "…", "fig": fid})
            elif c.startswith("잠깐!"):
                cur.append({"s": "잠깐 라벨", "t": "잠깐!"})
                cur.append({"s": "잠깐 본문", "t": c[len("잠깐!"):].strip()})   # 상자 안 문단 구분은 내보내기에서 확인 불가 → 원문대로 한 문단
            continue
        in_table_multi = False
        if ln.startswith("## ") or ln.strip() == "##":
            t = clean(ln.lstrip("#"))
            if t: cur.append({"s": "절 제목", "t": t}); sub_n = 0
            continue
        m = re.match(r"^\s*(\d+)\)\s*(?:#{1,3}\s*)?(.+)$", ln)
        if m:                                                      # 원고의 번호 소제목 "1) …"
            cur.append({"s": "소제목", "t": f"{m.group(1)}) " + clean(m.group(2))}); continue
        if ln.startswith("### "):
            cur.append({"s": "소소제목", "t": clean(ln[4:])}); continue      # 번호 없는 ### = 셋째 단계
        m = re.match(r"^\s*1\.\s+\*\*(\\#\\#\\#|\\#\\#)?\s*(.+)$", ln)
        if m and ("\\#" in ln or ln.strip().endswith("**")):          # 번호가 붙은 소제목(원본 번호가 모두 '1.'로 내보내짐)
            sub_n += 1; cur.append({"s": "소제목", "t": f"{sub_n}) " + clean(re.sub(r"\\#", "", m.group(2)))}); continue
        if re.match(r"^\s*\*\*.*\*\*\s*$", ln) and len(clean(ln)) < 60:   # 굵은 글씨 한 줄 = 소제목
            t = clean(ln)
            if t.startswith("*** 트럼프") or "트럼프 이야기는" in t:
                log.append("편집 메모 제외: " + t); continue
            cur.append({"s": "소소제목" if t.startswith("■") else "소제목", "t": t}); continue
        if "트럼프 이야기는" in ln:
            log.append("편집 메모 제외: " + clean(ln)); continue
        if re.match(r"^\s*[*-] ", ln):
            cur.append({"s": "목록", "t": "• " + clean(re.sub(r"^\s*[*-] ", "", ln))}); continue
        m = re.match(r"^\s*(\d+)\.\s+(.+)$", ln)
        if m:
            cur.append({"s": "번호 목록", "t": f"{m.group(1)}. " + clean(m.group(2))}); continue
        t = clean(ln)
        if not t or t == "<!-- end list -->": continue
        if t.startswith("□"):
            cur.append({"s": "질문 제목", "t": t}); continue
        if re.match(r"^[❶❷❸❹❺]", t):
            cur.append({"s": "소제목", "t": t}); continue
        if ln.lstrip().startswith("*“"):
            cur.append({"s": "본문 삽입", "t": t}); continue
        if ch == 99 and re.match(r"^\[\d-\d+\]", t):
            cur.append({"s": "참고 자료", "t": t}); continue
        if ch == 99 and re.match(r"^제\d장 출처$", t):
            cur.append({"s": "참고 자료 제목", "t": t}); continue
        cur.append({"s": "본문", "t": t})
    # 제안 도판 자리 끼워 넣기
    for chn, anchor, fid in EXTRA:
        blocks = chapters.get(f"ch{chn:02d}", [])
        for i, b in enumerate(blocks):
            if b["s"] in ("절 제목", "소제목") and anchor in b["t"]:
                j = i + 1
                while j < len(blocks) and blocks[j]["s"] != "본문": j += 1
                blocks.insert(j + 1, {"s": "도판 자리", "t": f"[도{fid}] 제안 도판", "fig": fid}); break
        else:
            log.append(f"제안 도판 {fid} 위치를 찾지 못함: {anchor}")
    return chapters, log

def tagged(blocks):
    def esc(s): return s.replace("\\", "\\\\").replace("<", "\\<").replace(">", "\\>")
    out = ["<UNICODE-WIN>", "<Version:13>"]
    for b in blocks:
        out.append(f"<ParaStyle:{b['s']}>{esc(b['t'])}")
    return "\r\n".join(out)

if __name__ == "__main__":
    p1, p2, outdir = sys.argv[1:4]
    chapters, log = convert([p1, p2])
    os.makedirs(outdir, exist_ok=True)
    stat = {}
    for k, blocks in chapters.items():
        json.dump(blocks, open(os.path.join(outdir, k + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        with open(os.path.join(outdir, k + "_태그텍스트.txt"), "wb") as f:
            f.write(b"\xff\xfe" + tagged(blocks).encode("utf-16-le"))
        stat[k] = {}
        for b in blocks: stat[k][b["s"]] = stat[k].get(b["s"], 0) + 1
    json.dump({"stat": stat, "log": log}, open(os.path.join(outdir, "변환_기록.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k in stat: print(k, sum(stat[k].values()), stat[k])
    print("\n".join(log))
