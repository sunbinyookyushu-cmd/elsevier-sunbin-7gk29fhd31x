# GACI_CO2 폴더 구성 (2026-09-26 정리)

## 최종본
- `FINAL_20260926/` — **Overleaf에 올릴 완성본.** `overleaf_20260926/`(tex, bib, 그림 7장), 업로드 zip, Overleaf 원본 대비 diff, README(검수 메모), 적용 스크립트, `push_overleaf.sh`(git 브리지용, 선택).
- `FINAL_20260923_figLZ/` — Longfei 통합 그림 원본과 9/23 병합 기록. `FINAL_20260908/`, `FINAL_20260906/` — 이전 후보본(이력).
- `Junya_comments_20260925/` — Junya Estimation 코멘트 대응(붙여넣기 블록, 일본어 답변 docx, 재추정 do-file 결과). `overleaf_20260926/`는 FINAL_20260926과 같은 내용.

## 작업 파일 (스크립트가 이 폴더를 작업 디렉터리로 쓰므로 위치 유지)
- `01_…39_*.py`, `build_*.py`, `_make_*.py`, `_check_*.py` 등 — 파이썬 파이프라인(패널 구축, 표·그림 생성, 문서 생성).
- `co2_*.do` + 같은 이름의 `.log` — Stata 추정과 실행 로그. 9/25 재추정은 `co2_exclusion_suite_cl_20260925.do`, `co2_asn_cl_20260925.do`.
- `*.csv` — 패널(`gaci_co2_panel.csv`, `co2_country_year.csv`, `airport_*_panel.csv` 등)과 결과(`_*.csv`).
- `data_external/`, `data_from_fangyu/`, `_presentation_scripts/`.

## 문서·결과 정리
- `docs_and_results/` — 제안서, 초록 제출본, 공저자 코멘트 대응 메모(LZ·Yifu, 9/02–9/03), 결과 요약 엑셀(`_20260826_final`, `_20260903_LZ`), 시각화 데이터, SAF 패키지 zip.

## 보관(삭제해도 되는 것)
- `_archive_20260926/`
  - `bak/` — `_bak_*` 백업 파일과 `_bak_results_pre0908/`.
  - `overleaf_old/` — 8/26·9/03·9/06 Overleaf 번들과 zip, 옛 템플릿 tex, `co2_tables_20260826.tex`, `draft_co2_skeleton.tex`.
  - `drafts_old/` — 8/22–8/23 Word 초고 v1–v5, 결과 요약 엑셀 초기판(v1–v4).
  - `figures_old/` — 파이썬 스크립트가 만든 개별 PNG(Longfei 통합 그림으로 대체됨; 스크립트로 재생성 가능).
  - `logs_20260908/` — 9/08 재실행 로그.
  - `tex_fragments/` — `_tex_*.tex` 표 조각(13·27·34·38번 스크립트가 재생성).
- `__pycache__/`는 삭제함.

Dropbox 이동이라 되돌릴 수 있음. `_archive_20260926/`를 통째로 지워도 최종본·코드·데이터에는 영향 없음.
