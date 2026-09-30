# manuscript/ — 마스터 원고

꼭지마다 폴더 하나. 기준은 [docs/10-book-quality.md](../docs/10-book-quality.md).

```
manuscript/chNN-이름/
├── design.md    구조 설계도 + 자체 점검표 10문항
├── draft.md     본문 (각주 [^ID], 미확인 표시 ⟦…⟧)
└── sources.md   출처 원장 (주장별 출처·등급·검증 상태)
```

## 규칙

- 본문의 사실 주장에는 각주 `[^ID]`를 붙이고, `sources.md`에 같은 ID의 행을 둔다.
- 확인하지 못한 곳, 이규호 님이 채울 곳은 `⟦…⟧`로 표시한다. **`⟦⟧`가 하나라도 남아 있으면 발행 불가.**
- `sources.md`의 상태 값: `원문확인` / `2차확인`(검색 요약·2차 문헌만 봄) / `미확인` / `충돌`(출처끼리 숫자가 다름).
  **참조된 모든 ID가 `원문확인`이어야 발행 가능.**
- 검사: `python3 scripts/check_manuscript.py manuscript/ch01-hanoi-toshiba`
