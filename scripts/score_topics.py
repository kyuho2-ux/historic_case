"""소재 후보(data/candidates.csv)를 점수화해 우선순위 표를 출력한다.

사용법:
    python3 scripts/score_topics.py            # 마크다운 표 출력
    python3 scripts/score_topics.py > out.md   # 파일로 저장

점수 로직은 docs/06-topic-selection.md 참고.
"""

import csv
import sys
from pathlib import Path

# 기본 점수 70점: 한국인 공감도와 스토리 품질
CORE_WEIGHTS = {
    "K": 20,  # 한국인 인지도
    "D": 15,  # 결정의 선명도
    "F": 15,  # 운명의 낙차
    "T": 10,  # 반전·의외성
    "V": 10,  # 검증 가능성
}
# 타깃 가산점 30점: 네 독자층 각 7.5점
TARGET_WEIGHTS = {
    "CEO": 7.5,  # 경영자
    "MGR": 7.5,  # 중간 관리자
    "STU": 7.5,  # 학생
    "INV": 7.5,  # 주식 투자자
}
TARGET_LABELS = {"CEO": "경영자", "MGR": "관리자", "STU": "학생", "INV": "투자자"}


def score(row):
    core = sum(int(row[k]) / 5 * w for k, w in CORE_WEIGHTS.items())
    target = sum(int(row[k]) / 5 * w for k, w in TARGET_WEIGHTS.items())
    return core, target, core + target + int(row["risk"])


def gate(row):
    """통과하지 못하면 점수와 무관하게 보류한다."""
    if int(row["V"]) <= 2:
        return "보류: 검증 자료 부족"
    if int(row["D"]) <= 2:
        return "보류: 결정의 순간이 불분명"
    return ""


def grade(total):
    if total >= 88:
        return "S"
    if total >= 83:
        return "A"
    if total >= 75:
        return "B"
    return "C"


def main():
    path = Path(__file__).resolve().parent.parent / "data" / "candidates.csv"
    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        row["core"], row["target"], row["total"] = score(row)
        row["gate"] = gate(row)
        top = [TARGET_LABELS[k] for k in TARGET_WEIGHTS if int(row[k]) >= 5]
        row["top"] = ", ".join(top) or "-"

    # 동점이면 한국인 인지도 → 한국 소재 → 투자자 가산 순으로 앞선다
    passed = sorted(
        (r for r in rows if not r["gate"]),
        key=lambda r: (-r["total"], -int(r["K"]), r["region"] != "한국", -int(r["INV"])),
    )
    held = [r for r in rows if r["gate"]]

    out = sys.stdout
    out.write("| 순위 | 등급 | ID | 소재 | 기업 | 연도 | 기본(70) | 가산(30) | 리스크 | 총점 | 최고 반응 타깃 |\n")
    out.write("|---|---|---|---|---|---|---|---|---|---|---|\n")
    for i, r in enumerate(passed, 1):
        out.write(
            f"| {i} | {grade(r['total'])} | {r['id']} | {r['title']} | {r['company']} | {r['year']} "
            f"| {r['core']:.0f} | {r['target']:.1f} | {r['risk']} | **{r['total']:.1f}** | {r['top']} |\n"
        )
    if held:
        out.write("\n**보류 소재**\n\n")
        for r in held:
            out.write(f"- {r['id']} {r['title']} ({r['company']}) — {r['gate']}, 참고 점수 {r['total']:.1f}\n")


if __name__ == "__main__":
    main()
