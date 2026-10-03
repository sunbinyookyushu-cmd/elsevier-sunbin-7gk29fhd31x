# 항공권 세금 논문: Stata 패키지 (2026-10-03)

Li, Liu, Purevjav & Yang (2019 JEEM) 구성에 맞춘 전체 추정. **모든 회귀에 국가 ln GDP·ln 인구(연도별, WDI) 통제**, **do 파일은 루프·매크로·local 없이 한 줄씩 인라인**(어느 블록이든 골라서 바로 실행 가능), CRLF, 블록주석 없음.

## 실행
```
do "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_paper\01_main.do"
do "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_paper\02_events_mediation.do"
```
패키지(reghdfe, ftools, estout, sdid, honestdid, ivreghdfe, ivmediate, weakiv)는 없으면 do 파일이 설치합니다. 로그 `01_main_run.log`, `02_events_mediation_run.log`; 표는 rtf로 저장.

## 데이터 (120_export_stata_all.py가 생성)
| 파일 | 단위 | 내용 |
|---|---|---|
| `stack_month.dta` | 공항×월×사건 (889,695행) | 19개 사건(유럽 8 = 발표일 도넛, 역외 11 = 시행일). 사전 [A−36,A−1], 사후 [E,E+23]. ln 좌석·CO2·CO2/좌석km·편수·편당좌석, 세금 €(dose), 규모 3분위, 국경 50–300km, lngdp·lnpop, 지역, FE id |
| `stack_eff.dta` | 공항×월 | 시행일 기준 ±36개월, 유럽 9건(네덜란드 포함): 창 길이 강건성 |
| `stack_loss.dta` | 공항×월 (at-risk) | 운항 중단 더미(12개월 전 운항, 이번 달 0석) |
| `stack_year.dta` | 공항×연도×사건 (73,694행) | E−3..E+1: ln GACI·취항지·고유벡터·매개, ln CO2와 정확 분해(취항지·취항지당 편수·편당 CO2·기체·거리·강도) |
| `sdid_month.dta` | 국가×기간×사건 | 계절조정 ln 좌석·CO2 (도넛 제거, 균형패널), SDID용 |
| `sdid_year.dta` | 국가×연도×사건 | 좌석가중 국가 평균 ln GACI, SDID용 |
| `events.dta` | 사건 20건 (NLD 포함) | |

## 01_main.do 블록 → 표
| 블록 | 표 | 내용 |
|---|---|---|
| Table 2 | 좌석 | 전체 / 좌석가중 / 규모별 / 규모별 가중 / €당 용량반응 / on-off+€ |
| Table 4 | CO2 | 같은 열 + CO2/좌석km |
| Table 5 (월) | 이벤트타임 | 발표 3년 전·2년 전·사후 1년·2년 (좌석·CO2·강도) |
| A2 | 강건성 | 비과세 유럽 대조군 / 전 세계 대조군+지역×월 FE / 아일랜드 2009 제외 / 시행일 창 ±12~36 |
| Table 3 | 네트워크 위치 | GACI·취항지·고유벡터·매개 × 전체/가중/허브(≥100만석)/규모 |
| Table 5 (연) | 이벤트타임 | GACI·취항지 k=−3,−2,0,+1 |
| Table 7A | 분해 | ln CO2 = 취항지 + 취항지당 편수 + 편당 CO2 (+기체·거리·강도), 전체·규모별 |
| Table 8 | Gelbach | CO2에 취항지·GACI 통제 추가; GACI 탄력성 |
| Table 7B | 월별 마진 | 편수·편당좌석·운항중단, 규모별 |
| Table 9 | 세계 | 19건, 지역×월(연)×사건 FE: 전체/유럽/역외, 좌석·CO2·GACI |

## 02_events_mediation.do 블록
| 블록 | 내용 |
|---|---|
| Table 6 | SDID 사건별 (유럽 9건): 국가 좌석·CO2(월), 국가 GACI(연), 위약 200회 |
| HonestDiD | 월별 이벤트타임(좌석·CO2), 상대크기 M=0~2, 평활 M=0~0.05 |
| Appendix D | IV 매개: ivmediate(처치=€×사후, 도구=처치×사후, 매개=취항지/GACI), 2SLS+weakiv AR, Gelbach 3단계 |

## 표본·정의 (확정 사항)
- 메인 표본: 유럽 8건(네덜란드 제외, 2008 도입→2009 폐지는 SDID에만), 처치국 공항 vs 유럽 코딩 20개국 중 창 안 사건 없는 나라의 공항, 국경 50–300km 공항은 별도 그룹, 50km 이내 제외, 이탈리아 제외.
- 시점: 발표일(원문 확인) 기준 사전 36개월, 발표~시행 사이 제거, 사후 첫 12개월(메인), 13–24개월(부록).
- 규모 3분위: 처치국 안에서 발표 전년도 좌석 기준.
- SE: 국가 클러스터. 와일드 부트스트랩은 보고하지 않음(10/02 결정).
- 역외 11건: 발표일 미확인 → 시행일 기준, 도넛 없음. 역외 세금은 대부분 국제선 전용·소액이라 총좌석 효과는 희석(Table 9 해석 시 주의).
- CO2 = 출발편 LTO+순항 (배출 패널). GACI는 연도별 정규화된 상대지표.

## 주의
- `fe_rt`(지역×월×사건)는 역외 사건이 없는 블록에서 유럽 안 지역 차이만 흡수함.
- 네덜란드(stk 0)는 01에서 제외되어 있음(`stk != 0`).
- ivmediate의 매개 1단계 F는 2 정도(처치와 도구가 거의 같은 변수)라 약한 도구; weakiv AR 구간으로 보고.

## 03_leakage.do / 04_regional_benefits.do (10/03 재작성, HANDOFF_aviation_tax.md 기준)
클라우드 세션이 데이터 없이 쓴 초안(루트 폴더의 `03_leakage.do`·`04_regional_benefits.do`, program·local·foreach 사용, 미검증)을 이 폴더 규칙(인라인·CRLF·전 회귀 lngdp lnpop)으로 다시 썼고, 둘 다 끝까지 실행됨(`03_leakage_run.log`, `04_regional_benefits_run.log`). 루트의 초안 두 파일은 손대지 않음.

### 데이터 (122_build_regional.py가 생성; Eurostat 원자료 `data_external/eurostat/`)
| 파일 | 단위 | 내용 |
|---|---|---|
| `reg_expo.dta` | 사건×NUTS2 | 100km 안 공항(가중 exp(−d/50km))의 사전연도 좌석, 소·중·대형 노출(처치국 3분위 컷을 전 공항에 적용), 국경링 포함 여부 |
| `reg_month.dta` | 사건×NUTS2×월 | catchment 좌석·CO2(ln), 달력 플래그, fe_r(지역×월×사건)·fe_ct(국가×월×사건) |
| `nat_month.dta` | 사건×국가×월 | Eurostat 숙박일(tour_occ_nim, 내국·외국·전체), 처치국+대조국, fe_cm·fe_t |
| `reg_year.dta` | 사건×NUTS2×연(E−3..E+1) | 연간 NUTS2 숙박일(tour_occ_nin2), 고용(lfst_r_lfe2en2: TOTAL·**G-I**; I 단독 미공표), 1인당 GDP(nama_10r_2gdp), catchment GACI·취항지 |
| `bc_inputs.dta` | 사건 | 처치공항 첫해 CO2(톤)·좌석, 좌석가중 세액, 세수 베이스 |
⚠️ Eurostat에 **월별 NUTS2 숙박 표는 없음** → 지역 숙박은 연간, 월별은 국가 단위. 지역 자료 결측: IRL(NUTS 개편으로 연간 숙박 0)·DNK 1998(고용·GDP 없음)·GBR(GDP 없음, 고용 16%)·MLT(지역 1개).

### 03_leakage.do 블록 → 표
| 블록 | 표 | 결과(10/03) |
|---|---|---|
| A 인접국 공항 제거 | L_A_controls | CO2 −.094*/−.099*/−.102*, 좌석 −.090*/−.094*/−.096* → 대조군 오염 없음 |
| B 인접국 허브·비허브 파급 | L_B_spillover | 허브 nhp CO2 −.050(ns)·좌석 −.014(ns)·편당좌석 +.031(ns); 이벤트타임 사전 −.059(ns) → 전환 증거 없음 |
| C 블록 DiD·SDID | L_C_bloc_did + 로그 | 블록 DiD CO2 +.020(ns)·좌석 +.005(ns); 사건별 SDID 8건 전부 ns(블록 단위라 SE 0.06~0.31) |
| D 재라우팅 흔적 | L_D_rerouting | 인접국 허브 stage −.004·편당CO2 −.031(ns); 비허브 취항지 +.167**·stage +.054*; 처치공항 stage −.016(ns) |

### 04_regional_benefits.do 블록 → 표
| 블록 | 표 | 결과(10/03) |
|---|---|---|
| N 국가 월별 숙박 | R0_national_nights | 외국인 −.031(ns), 내국인 +.029(ns); ⚠️외국인 사전 −.081*** |
| R1 지역 월별 연결성 | R1_regional_connectivity | catchment 좌석 −.24(ns)·CO2 −.24*; ⚠️이벤트타임 사전 +.17***/−.22*** |
| R2 지역 연간 결과 | R2_regional_annual | GACI +.032*, 외국인숙박 −.042(ns), 내국인 +.054***, G-I 고용 −.046**, 총고용 −.014*, GDP .009 |
| R3 지역 이벤트타임 | R3_regional_eventtime | 고용 k=−2 +.059** → 사전추세 의심 |
| R4 2SLS | R4_regional_iv | KP F 1.1~3.1 → 약한 도구, 해석 불가 |
| R5 예측손실 노출 | R5_regional_predloss | 내국인숙박 +.29***, G-I 고용 −.25** |
| 7 편익/비용 | benefits_by_event.csv | 좌석가중 CO2 −.003(ns) 기준 감축 0.21Mt(상한 1.98Mt), 세수 44억€, 톤당 비용 5,506€(상한 기준 ~570€); 외국인숙박 손실은 ns 계수(−.031)에서 계산 |
결론(10/03): 유출(leakage)은 없음(A·B·C·D 전부 0). 지역 비용 설계는 사전추세·약한 도구 때문에 아직 쓸 수 없음. 편익/비용 표는 좌석가중 CO2 효과가 0에 가까워 상한 구간을 같이 보고해야 함.

### 다음 할 일
`ssc install avar` 후 02의 weakiv 재실행; 02 honestdid 2번째 호출에 `delta(sd)` 추가; 7A 분해·Gelbach 공통표본 결정; 국가 내 GACI HHI·항공사 유형(LCC) 분할(핸드오프 4번).
