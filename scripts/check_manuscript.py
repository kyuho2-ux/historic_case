"""마스터 원고 꼭지의 정합성·출처 게이트를 검사한다.

사용법:
    python3 scripts/check_manuscript.py manuscript/ch01-hanoi-toshiba

기준은 docs/10-book-quality.md 4절. 발행 불가 사유가 하나라도 있으면 종료 코드 1.
"""

import re
import sys
from pathlib import Path

REF = re.compile(r"\[\^([A-Za-z0-9_-]+)\](?!:)")
DEF = re.compile(r"^\[\^([A-Za-z0-9_-]+)\]:", re.M)
MARK = re.compile(r"⟦[^⟧]*⟧")
NUMBER = re.compile(r"\d[\d,\.]*\s*(?:년|월|일|억|만|천|%|퍼센트|마리|명|엔|센트|개|건|배)")
DONE = "원문확인"


def load_ledger(path):
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5 and re.fullmatch(r"[A-Za-z0-9_-]+", cells[0]) and cells[0] != "ID":
            rows[cells[0]] = {"claim": cells[1], "grade": cells[3], "status": cells[4]}
    return rows


def main():
    chapter = Path(sys.argv[1])
    draft = (chapter / "draft.md").read_text(encoding="utf-8")
    ledger = load_ledger(chapter / "sources.md")

    body_only = re.sub(r"^\[\^.*$", "", draft, flags=re.M)
    refs = set(REF.findall(body_only))
    defs = set(DEF.findall(draft))

    blockers, warnings = [], []

    for r in sorted(refs - defs):
        blockers.append(f"각주 [^{r}]가 본문에서 쓰이지만 정의가 없다")
    for d in sorted(defs - refs):
        warnings.append(f"각주 [^{d}]가 정의만 있고 본문에서 쓰이지 않는다")
    for r in sorted(refs):
        if r not in ledger:
            blockers.append(f"[^{r}]가 sources.md 원장에 없다")
        elif ledger[r]["status"] != DONE:
            blockers.append(f"[^{r}] 상태 '{ledger[r]['status']}': {ledger[r]['claim']}")

    marks = MARK.findall(draft)
    for m in marks:
        blockers.append(f"미해결 표시 {m}")

    for i, para in enumerate(re.split(r"\n\s*\n", body_only), 1):
        p = para.strip()
        if not p or p.startswith(("#", ">", "|", "-", "<!--")):
            continue
        if NUMBER.search(MARK.sub("", p)) and not REF.search(p):
            warnings.append(f"문단 {i}: 숫자가 있는데 각주가 없다 → \"{p[:40]}…\"")

    text = re.sub(r"⟦[^⟧]*⟧|\[\^[^\]]*\]", "", body_only)
    chars = len(re.sub(r"\s", "", text))

    print(f"[{chapter.name}] 본문 {chars:,}자 (목표 6,000~8,000자) · 각주 {len(refs)}개 · 미해결 표시 {len(marks)}개")
    counts = {}
    for r in refs:
        s = ledger.get(r, {}).get("status", "원장 없음")
        counts[s] = counts.get(s, 0) + 1
    print("출처 상태: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if warnings:
        print(f"\n경고 {len(warnings)}건")
        for w in warnings:
            print("  - " + w)
    if blockers:
        print(f"\n발행 불가 사유 {len(blockers)}건")
        for b in blockers:
            print("  ✗ " + b)
        sys.exit(1)
    print("\n정합성·출처 게이트 통과")


if __name__ == "__main__":
    main()
