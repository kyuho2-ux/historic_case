"""소재 후보(data/candidates.csv)를 점수화해 등급별 우선순위를 출력한다.

사용법:
    python3 scripts/score_topics.py > data/ranking.md

점수 로직(v2)은 docs/06-topic-selection.md 참고.
"""

import csv
import sys
from pathlib import Path

# 합계 100점. 각 항목은 0~5점으로 매기고 (점수 ÷ 5 × 가중치)로 환산한다.
WEIGHTS = {
    "K": 15,  # 한국인 인지도
    "D": 10,  # 결정의 선명도
    "F": 15,  # 운명의 낙차
    "T": 10,  # 반전·의외성
    "N": 15,  # 신선도 (기존 콘텐츠 대비 새로운 각도)
    "P": 10,  # 겹쳐 보기 적합도 (역사 사건과 짝이 되는가)
    "C": 5,   # 현재성 (지금 뉴스·주가와 연결되는가)
    "V": 10,  # 검증 가능성
    "S": 10,  # 화자 적합도 (이규호만의 관점·자료)
}

GRADES = [("S", 82), ("A", 75), ("B", 68), ("C", 0)]


def score(row):
    return sum(int(row[k]) / 5 * w for k, w in WEIGHTS.items()) + int(row["risk"])


def gate(row):
    """통과하지 못하면 점수와 무관하게 보류한다."""
    if int(row["V"]) <= 2:
        return "검증 자료 부족"
    if int(row["D"]) <= 2:
        return "결정의 순간이 불분명"
    return ""


def grade(total):
    return next(g for g, cut in GRADES if total >= cut)


def main():
    path = Path(__file__).resolve().parent.parent / "data" / "candidates.csv"
    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        row["total"] = score(row)
        row["gate"] = gate(row)

    passed = sorted((r for r in rows if not r["gate"]), key=lambda r: -r["total"])
    held = [r for r in rows if r["gate"]]

    out = sys.stdout
    # 점수 차이 몇 점은 의미가 없으므로 순위 대신 등급으로 묶어서 보여준다.
    for g, cut in GRADES:
        group = [r for r in passed if grade(r["total"]) == g]
        if not group:
            continue
        label = f"{cut}점 이상" if cut else "68점 미만"
        out.write(f"\n### {g}등급 ({label})\n\n")
        out.write("| ID | 소재 | 기업 | 역사 짝 | 연도 | 신선도 | 겹쳐 보기 | 화자 | 점수 |\n")
        out.write("|---|---|---|---|---|---|---|---|---|\n")
        for r in group:
            out.write(
                f"| {r['id']} | {r['title']} | {r['corporate']} | {r['history']} | {r['years']} "
                f"| {r['N']} | {r['P']} | {r['S']} | {r['total']:.0f} |\n"
            )
    if held:
        out.write("\n### 보류\n\n")
        for r in held:
            out.write(f"- {r['id']} {r['title']} ({r['corporate']}) — {r['gate']}, 참고 점수 {r['total']:.0f}\n")


if __name__ == "__main__":
    main()
