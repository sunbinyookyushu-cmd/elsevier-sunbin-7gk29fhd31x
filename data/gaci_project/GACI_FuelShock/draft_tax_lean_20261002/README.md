# 항공권 세금 논문: 표 세트 (간결판, 2026-10-02)

이전 12표 초안(`../draft_tax_20261002/`)에서 네덜란드 에피소드·전후 평균·용량-반응·국제선 이질성·요약통계를 빼고, CO2·GACI 결과를 넣은 본문 7표 + 부록 2표입니다. 형식은 DC_MA `draft_econ_v2`와 같습니다.

## 파일
- `tables_tax.tex`: `GACI_FuelShock/111_tax_tables_lean.py`가 결과 CSV에서 생성. 손으로 고치지 말고 111을 다시 돌릴 것.
- `main_tables.tex`, `main_tables.pdf`: 확인용 컴파일 (TinyTeX, 오류 0, 6쪽).

## 리서치 퀘스천과 답
항공권 세금은 항공 수요를 줄이는가, 네트워크 안에서 재분배하는가.
국가 좌석 −4%(경계), CO2 −2%(ns), 네트워크 위치 −2%. 손실은 소·중형 공항에 집중(좌석 −24%, 취항지 −13%, GACI −2%); 허브는 환승 면제로 보호되고 기체를 키움. CO2 감소는 전부 노선 퇴출분이고, 연결성 상실로 남은 운항의 km당 배출은 조금 오른다. 국경 이탈은 없다(네덜란드 제외).

## 표
| 표 | 라벨 | 내용 | 결과 파일 |
|---|---|---|---|
| 1 | tab:events | 사건 9건 | 세금 코딩 csv, 발표일 검증 csv |
| 2 | tab:seats | 좌석: 전체 / 좌석가중 / 소·중·대형 + 국경 + 사전추세 행 | `_res_tax_by_size.csv`, `_res_tax_jeem.csv` |
| 3 | tab:network | 네트워크 위치(핵심 기여): GACI·취항지·고유벡터·매개 × 전체 / 좌석가중 / 허브만 / 규모 | `_res_tax_by_size.csv`, `_res_tax_checks.csv`, `_res_tax_gaci_pretrend.csv` |
| 4 | tab:emissions | CO2·CO2/좌석·CO2/좌석km × 같은 열 | `_res_tax_co2.csv` |
| 5 | tab:mechanism | CO2 정확 분해(취항지·편수·편당) + 편수·기체·운항중단 | `_res_tax_co2_channel.csv`, `_res_tax_mechanisms.csv` |
| 6 | tab:gaci_co2 | GACI→CO2 탄력성(총량 +, 강도 −) + Gelbach 분해 | `_res_gaci_intensity.csv` |
| 7 | tab:sdid | 사건별 SDID: 국가 좌석, 국가 평균 GACI | `_res_tax_sdid.csv`, `_res_tax_gaci_sdid.csv` |
| 8 | tab:abatement | 규모별 감축·세수·€/t·GACI·취항지 손실 | `_res_tax_co2_abatement.csv` |
| A1 | tab:eventtime | 이벤트스터디 전체 계수: 좌석(발표 전 3년), GACI(연간, 규모별) | `_res_tax_jeem.csv`, `_res_tax_gaci_pretrend.csv` |
| A2 | tab:robust | 창·위기연도 제외·도넛·추세제거 | `_res_tax_checks.csv`, `_res_tax_pretrend.csv`, `_res_tax_main.csv` |
| A3 | tab:leakage | 국경 거리 링, 국경 허브 vs 2차 | `_res_tax_main.csv` |

(10/03) 결과변수마다 표를 분리: 세 결과를 한 표에 넣으면 기여가 작아 보인다는 지적에 따라 좌석·네트워크·배출을 각각 독립된 표로, 이벤트스터디 전체는 부록으로.

## 기준
- 식별: 공항 단위 스택 DiD(처치국 공항 vs 사건 없는 유럽국 공항, 국경 50–300km 별도 그룹, 50km 이내 제외). 발표일 도넛, 사전 36개월, 사후 12개월. FE 공항×달력월×사건 + 월×사건(월별), 공항×사건 + 연도×사건(연간). SE 국가 클러스터(10/02 결정 C: 와일드 부트스트랩 미보고).
- 보조: 국가 단위 SDID(사건별), Gelbach 분해(기술적; IV 매개 아님).
- 제외: 유가 충격·EU ETS(식별 실패), 메커니즘 M1~M3, 네덜란드 에피소드(A2 주석에 한 줄).
- 표 A1의 도넛·추세제거 행은 발표일 검증 전 코딩(오스트리아·몰타) 추정치(주석 명시).

## 남은 것
그림(이벤트스터디 좌석·GACI, 규모별), HonestDiD(`stata_tax/tax_honestdid.do`, 사용자 실행), 본문.

## 다시 만들기
`92 → 93 → 94 → 95 → 100 → 101 → 102 → 103 → 104 → 105 → 106 → 107 → 111`
