# '잠깐!' 상자 안 문단 나눔을 원본 Google Docs(텍스트 내보내기)와 대조해 조판 데이터에 반영한다.
# 사용: python3 -I split_boxes.py <파트1~4.txt> <파트5~7.txt> <조판 폴더>
#   txt = Drive에서 text/plain으로 내보낸 원고. 상자(표 칸)는 '잠깐!' 줄에서 시작해 탭 한 칸짜리 줄에서 끝난다.
# 글자는 조판 데이터의 것을 그대로 쓰고, 나누는 위치만 원본에서 가져온다(공백을 뺀 글자 수로 맞춘다).
# 결과 스타일 [제안]: 한 문단 상자 = 잠깐 본문 / 여러 문단 = 잠깐 본문 첫 → 잠깐 본문 이어 … → 잠깐 본문 끝
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ms_to_layout import tagged

ORDER = ["ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07", "back"]
BOX_STYLES = ("잠깐 본문", "잠깐 본문 첫", "잠깐 본문 이어", "잠깐 본문 끝")

def nospace(s): return re.sub(r"\s+", "", s)

def doc_boxes(paths):
    boxes = []
    for p in paths:
        lines = re.split(r"\r\n|\n|\r", open(p, encoding="utf-8-sig").read())
        i = 0
        while i < len(lines):
            if lines[i].strip() == "잠깐!":
                body, i = [], i + 1
                while i < len(lines) and lines[i] != "\t" and lines[i].strip() != "잠깐!":
                    if lines[i].strip(): body.append(lines[i].strip())
                    i += 1
                boxes.append(body)
            else:
                i += 1
    return boxes

def split_like(text, pieces):
    """text를 pieces(원본 문단)의 공백 뺀 글자 수에 맞춰 나눈다. 글자가 다르면 None."""
    if nospace(text) != nospace("".join(pieces)):
        # 원본 상자에 끝 표시(탭 줄)가 없으면 뒤 본문까지 읽힌다 → 글자가 맞는 앞 문단까지만 쓴다
        for n in range(1, len(pieces)):
            if nospace(text) == nospace("".join(pieces[:n])): return split_like(text, pieces[:n])
        return None
    out, pos = [], 0
    for k, pc in enumerate(pieces):
        need, start = len(nospace(pc)), pos
        while need and pos < len(text):
            if not text[pos].isspace(): need -= 1
            pos += 1
        out.append(text[start:pos] if k < len(pieces) - 1 else text[start:])
    return [o.strip() for o in out]

def main(p1, p2, D):
    src = doc_boxes([p1, p2])
    data = {k: json.load(open(os.path.join(D, k + ".json"), encoding="utf-8")) for k in ORDER}
    targets = [(k, i) for k in ORDER for i, b in enumerate(data[k]) if b["s"] in BOX_STYLES and
               (i == 0 or data[k][i - 1]["s"] == "잠깐 라벨")]
    report = {"원본 상자 수": len(src), "조판 데이터 상자 수": len(targets), "상자": []}
    if len(src) != len(targets):
        print("상자 수가 다름:", len(src), len(targets)); report["오류"] = "상자 수 불일치 — 반영하지 않음"
        return report
    # 이미 나눈 상자는 다시 합쳐서 비교한다(여러 번 돌려도 같은 결과)
    for (k, i), pieces in reversed(list(zip(targets, src))):
        blocks, j = data[k], i
        if blocks[i]["s"] == "잠깐 본문 첫":
            while blocks[j]["s"] != "잠깐 본문 끝": j += 1
        cur = " ".join(b["t"] for b in blocks[i:j + 1])
        parts = split_like(cur, pieces)
        item = {"장": k, "첫머리": cur[:30], "원본 문단 수": len(pieces)}
        if parts is not None and len(parts) < len(pieces):
            item["원본 문단 수"] = len(parts); item["참고"] = "원본에 상자 끝 표시가 없어 글자가 맞는 앞 문단까지를 상자로 봄"
        if parts is None:
            item["결과"] = "글자 불일치 — 그대로 둠"; item["원본 첫머리"] = "".join(pieces)[:30]
        else:
            if len(parts) == 1: new = [{"s": "잠깐 본문", "t": parts[0]}]
            else: new = [{"s": "잠깐 본문 첫" if n == 0 else ("잠깐 본문 끝" if n == len(parts) - 1 else "잠깐 본문 이어"), "t": t}
                         for n, t in enumerate(parts)]
            blocks[i:j + 1] = new
            item["결과"] = f"{len(parts)}문단"
        report["상자"].insert(0, item)
    for k in ORDER:
        json.dump(data[k], open(os.path.join(D, k + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        with open(os.path.join(D, k + "_태그텍스트.txt"), "wb") as f:
            f.write(b"\xff\xfe" + tagged(data[k]).encode("utf-16-le"))
    return report

if __name__ == "__main__":
    r = main(*sys.argv[1:4])
    out = os.path.join(sys.argv[3], "잠깐상자_대조.json")
    json.dump(r, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for b in r.get("상자", []): print(b["장"], b["원본 문단 수"], b["결과"], b["첫머리"])
    print(r.get("오류", ""), "원본", r["원본 상자 수"], "데이터", r["조판 데이터 상자 수"])
