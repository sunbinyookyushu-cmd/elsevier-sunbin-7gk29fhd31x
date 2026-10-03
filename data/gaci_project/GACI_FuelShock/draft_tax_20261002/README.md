# 항공권 세금 논문: 표 초안 (2026-10-02)

DC_MA `draft_econ_v2` 형식(booktabs·threeparttable·굵은 캡션·주석)으로 표만 모은 확인용 문서입니다. 본문은 아직 없습니다.

## 파일
- `tables_tax.tex`: 표 12개. `GACI_FuelShock/110_tax_tables_tex.py`가 결과 CSV(`_res_tax_*.csv`)에서 만든 것이므로 손으로 고치지 말고 110을 다시 돌릴 것.
- `main_tables.tex`, `main_tables.pdf`: 표만 컴파일한 확인용 문서 (TinyTeX: 오류 0, 미정의 참조 0, 8쪽).

## 리서치 퀘스천
항공권 세금은 항공 수요를 줄이는가, 네트워크 안에서 재분배하는가.
답: 국가 좌석 총량은 약 4% 감소(좌석 가중)지만 손실은 작은 공항에 집중(소형 −24%, 대형 ≈0). 허브는 환승 면제로 보호되고 기체를 키워 좌석을 유지. 작은 공항은 편수·취항지·네트워크 중심성을 잃는다. 국경 너머 이탈은 네덜란드에서만.

## 표 (JEEM Li et al. 2019 순서)
| 표 | 라벨 | 내용 | 결과 파일 |
|---|---|---|---|
| 1 | tab:events | 사건 9건: 발표일(원문 확인)·시행일·세율·환승 면제·처치 공항 수·대조국 수 | 세금 코딩 csv |
| 2 | tab:sumstats | 발표 전년도 공항 요약통계 (처치/국경/대조) | parquet 직접 계산 |
| 3 | tab:prepost | 시행 전후 12개월 평균 (원값·잔차) | `_res_tax_checks.csv` T4 |
| 4 | tab:pretrend | 평행추세: 풀링 + 사건별 (발표일 도넛, 연간 구간, 사전 3년) | `_res_tax_jeem.csv` |
| 5 | tab:main | 메인: 비가중/좌석가중 × 전체/규모 3분위 | `_res_tax_by_size.csv` |
| 6 | tab:robust | 창 ±12~36, 위기연도 제외, 도넛, 추세제거, 용량-반응(€당) | `_res_tax_checks.csv`, `_res_tax_pretrend.csv`, `_res_tax_main.csv`, `_res_tax_jeem.csv` |
| 7 | tab:mechanism | M4: 규모별 좌석·편수·편당좌석·운항중단 | `_res_tax_by_size.csv`, `_res_tax_mechanisms.csv` |
| 8 | tab:connectivity | 규모별 GACI·취항지·고유벡터·매개 + 허브만·좌석가중 | `_res_tax_by_size.csv`, `_res_tax_checks.csv` T9 |
| 9 | tab:sdid | 사건별 SDID (국가 합계), 위약 p, 기부국 가중치 | `_res_tax_sdid.csv` |
| 10 | tab:nld | 네덜란드 도입(2008-07)→폐지(2009-07) | `_res_tax_main.csv` NLD |
| 11 | tab:leakage | 국경 링 0–50/50–150/150–300km, 국경 허브 vs 2차 | `_res_tax_main.csv` |
| 12 | tab:costbenefit | 첫해 승객·CO2·세수·€/tCO2 (탑승률 0.8 가정) | `_res_tax_costbenefit.csv` |

## 기준 (10/02 결정)
- 사건: 환승 면제형 국가 항공권세 도입·인상 9건(표 1). 네덜란드는 1년 뒤 폐지라 따로(표 10). 이탈리아(환승 과세, 날짜 미확정)는 처치·대조 모두에서 제외.
- 사건 시점: 발표일 원문 확인(`announcement_dates_verified.csv`). 발표~시행 사이 월 제거(도넛). 사전 36개월, 사후 첫 12개월(메인), 2년째는 부록.
- 대조군: 코딩된 유럽 21개국 중 창 안에 자기 사건 없는 나라. 국경 공항(50–300km)은 별도 그룹, 50km 이내는 제외.
- 고정효과: 공항×달력월×스택, 월×스택. SE: 국가 클러스터만 보고(10/02 결정 C; 와일드 부트스트랩 결과는 `_res_tax_main.csv`에 보존, 본문 미보고).
- 규모 3분위: 처치국 안에서 발표 전년도 좌석 기준.
- 표 6의 도넛·추세제거 행은 발표일 검증 전 코딩(오스트리아 2011-01, 몰타 2004-12)으로 추정됨(주석에 명시). 메인 행과 표 4·5·7·8은 검증된 날짜.
- 제외: 유가 충격·EU ETS(식별 실패, 97~99), 메커니즘 M1–M3(미확정, `_res_tax_mechanisms.csv`에 보존).

## 남은 것
- HonestDiD 정식 구간: `stata_tax/tax_honestdid.do` (사용자 실행).
- 그림: 이벤트스터디(풀링·사건별), 규모별 효과, SDID 경로.
- 메커니즘 M3(항공사 재배치): Fangyu 운항사 자료 도착 후.
- 본문 작성.

## 다시 만들기
`92` → `93` → `94` → `95` → `100` → `101` → `102` → `103` → `110` (모두 `GACI_FuelShock/`에서 `python -u NN_*.py`).
