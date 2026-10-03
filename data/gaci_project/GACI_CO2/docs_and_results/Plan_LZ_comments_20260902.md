# LZ 코멘트 반영 계획 (GACI x Aviation CO2, Nature-series 타깃)

작성 2026-09-02, 09-03 리뷰 반영 6건(공항수 6,356 vs 5,354 설명·이웃 stage −2.03* 추가·docx 라벨 중복 제거·stage 명명·3A 옵션2 본명 승격·코멘트4 패널 정합). 코멘트 원본: `Downloads\Comments_GAC&CO2_LZ.docx` (4개 방향 + 5-layer 구조 제안).
현행 canonical: `co2_overleaf_20260826\main_co2_nature_20260826.tex`, 결과 xlsx `CO2_results_summary_20260826_final.xlsx`.

핵심 판단: 4개 코멘트 중 1(분해)과 3(스필오버)은 기존 산출물이 60~80% 커버하므로 "재배치+확장",
2(공항)와 4(배제제약)는 신규 추정이 필요. 전체 신규 스크립트 예상 8~10개, 신규 디스플레이 표 4 + 그림 3.

---

## 0. 코멘트 vs 기존 자산 매핑

| 코멘트 | 이미 있는 것 | 부족한 것 |
|---|---|---|
| 1 분해 | `_feyrer_mechanism.csv`: 항등식 정확 가산분해 flights 6.98 / gauge −0.30ns / stage −0.60*** / intensity −0.40*** = 5.67 (검증 일치). M4 매개분석(skm 86%, flights 84%) | 원고에 항등식 표가 없음(유저가 M3 시트 삭제, 매개분석이 대신). LZ 식(1)(2) 표기, scale/efficiency 합산 수치, 워터폴 그림, 소득별 분해, 로드팩터 부재 명시 |
| 2 공항 | `airport_co2_panel.csv` 5,354공항×1996-2023(97,165; Fangyu 원자료 6,356공항 중 GACI 노드만 유지, 탈락 1,002공항=출발CO2 0.1%·2023년 0.05% → Methods 한 줄 명시), FE 회귀(ln_co2 +3.72/intensity −0.49/intl +0.33, 공항FE+국가×연FE), 효율곡선, 허브 mismatch 표; 유산 IV 실패(F 59.5→2.3) 공개 | 공항 이질성(허브/소형·연결·국내/국제·기초규모·지역/소득), 상위 1/5/10% 기여 집중도, 공항레벨 인과(대안 IV 파일럿) |
| 3 스필오버 | 역거리 가중 nbr_lngaci + nbr_feyrer IV(F=134): 총 +7.45***/intl +10.24***/집약도 +1.31**; 메커니즘 거울상(gauge +5.44***/intl +1.05***/stage −2.03*(p=.045)/flights +2.73 ns = 피더 시그니처); 2-내생 붕괴(F≈5) | (a) own GACI 통제 하 1차 이웃효과, (b) 거리감쇠 밴드/연속, (c) 지역 내 vs 지역 외 + 지역×연 FE, 인접국 W, 플라시보 W |
| 4 배제제약 | 사이즈×사이클 스트레스(F 120→105.8), Conley 플로저블 바운드(85%/42%), RF quintile, 대안 IV 실패 공개, 컷오프 스윕, exCOVID | 비항공 플라시보 아웃컴, 세계GDP×MA 호스레이스, sea-MA 플라시보 도구, zero-first-stage 검정, 개발경로 통제, 대안 a_t, 공간 HAC SE |
| Layer 5 | SAF 시나리오(Mt), SCC $18.2-67.7bn, 귀속지도 356Mt | 허브 집중 기반 정책 반사실(코멘트 2와 연결) 정도만 추가 |

---

## 1. CO2 탄력성 분해 (코멘트 1)

목표: "5.67은 어디서 오나"를 항등식으로 한 표 + 한 그림에 답한다.

항등식(Fangyu 데이터 정의와 정합, 로드팩터 없음):
CO2 = Flights × (Seats/Flight) × (Km/Flight, 평균 stage length = LZ의 Distance) × (CO2/Seat-km)
→ β_CO2 = β_flights + β_gauge + β_stage + β_intensity = 6.98 − 0.30 − 0.60 − 0.40 = 5.67

작업:
1. **표 신설 "Decomposition of the CO2 elasticity"** (`_feyrer_mechanism.csv` 재사용, 추정 재실행 불필요)
   - 열: component / β (se) / share of total(%) / 누적. Scale 블록(flights+gauge+stage = seat-km 6.07 = 107%)과 Efficiency 블록(intensity −0.40 = −7%) 소계 명시 → "scale beats efficiency" 수치화.
   - 합산 검증행: Σβ = 5.669 = Table 1 총CO2 (동일표본 N=4,634).
   - 부가행: LTO share +0.014ns, intl skm share +0.096** (조성마진).
2. **워터폴 그림** (matplotlib): 0 → +6.98 → −0.30 → −0.60 → −0.40 → 5.67. 메인 디스플레이 후보.
3. **분해의 이질성** (신규 do: `co2_decomp_hetero.do`): 소득 tercile × 4성분 (기존 hetero D패널은 intensity만). 저소득 11.4의 분해 vs 고소득 0.35의 분해 → "신규진입국은 편수, 성숙국은 무반응".
4. **국내/국제 분리 분해**: dom, intl 각각 항등식 (데이터에 dom_intl 컬럼 존재) → 국제선 stage 단축 여부 확인.
5. **집약도(technique) 하위분해**: intensity = CO2/skm. gauge ns이므로 대형화가 아닌 기단연비 마진. 가능하면 Fangyu에게 "aircraft-type별 seat-km 가중 평균 연비(CO2/skm at fixed distance)" 집계 요청 → 기단교체(within-type 효율 vs type mix) 분리. 없으면 텍스트로 한계 명시.
6. **로드팩터**: 데이터가 scheduled-capacity 기반이라 LF 항이 항등식에서 상수로 소거됨을 Methods에 명시. 보조로 ICAO/IATA 지역 LF 평균을 곱한 감도(부록 1문단)만.
7. **매개분석(M4)은 부록/ED로 강등**, 항등식 분해가 본문 메커니즘 표를 맡음 (LZ 요구 형식과 일치).
8. Methods에 LZ 식(1)(2)를 우리 표기로 기술 + "OLS 3.59 vs IV 5.67, LATE=지리 컴플라이어(신규진입국)" 문단으로 "왜 큰가" 직접 답변.

산출: Table(분해) 1 + Fig(워터폴) 1 + ED 표(소득별·국내국제) 1. 스크립트: `18_decomp_table_fig.py`, `co2_decomp_hetero.do`.

---

## 2. 공항 레벨 분석 (코멘트 2)

목표: 국가 결과가 집계 아티팩트가 아님 + 효과의 허브 집중 여부.

### 2A. 이질성 (기술적, 공항FE + 국가×연FE, 공항 클러스터) — 확실히 됨
`co2_airport_hetero.do` (airport_co2_panel.csv 그대로):
- 기초(1996) 규모 tercile/분위(dep_seat_km), 기초 GACI tercile, 국제셰어(0 / 0-50 / 50+), 허브 더미(1996 capacity 상위 5%·1% 또는 각국 최대공항), 지역(Region 컬럼), 소득그룹(국가 lnpc 머지).
- 아웃컴 4종(ln_co2, ln_skm, ln_intensity, intl_share). 상호작용 + 분할표본 둘 다.
- 캐비앗 유지: 공항 GACI에 capacity 성분 내장 → **토폴로지 전용 성분(eigenvector/betweenness/closeness)을 대안 회귀자로 추가**해 기계적 상관 완화 (GACI 구축 폴더에서 공항별 성분 추출 필요, 없으면 `deg/eig/close/betw` 재계산).

### 2B. 기여 집중도 (핵심 신규)
`19_airport_concentration.py`:
- 공항별 연결성 귀속배출 = CO2_a,2023 × (1 − exp(−β × Δln GACI_a,1996-2023)). β는 (i) 국가 IV 5.67(기본), (ii) 공항 기술 β 3.72, (iii) 2A 그룹별 β 3가지 감도.
- 랭킹 후 상위 1/5/10/25% 공항의 귀속배출 셰어 + Lorenz 곡선/지니. **벤치마크 = 물리 배출 자체의 집중도**(2023 CO2 상위 1% 셰어)와 비교 → "연결성 유발 배출이 배출 자체보다 더/덜 집중"이 실제 발견.
- 국가 귀속 356Mt와 공항 합의 정합성 체크(국가 합 vs 공항 합).
- 그림: 집중도 곡선 + 상위 20공항 바차트(기존 CO2_attribution_bars 스타일).

### 2C. 공항 레벨 인과 파일럿 (실패 가능, 2일 한도)
유산 IV는 이미 사망. 후보 2개만 시험, 둘 다 사이즈×사이클 검정(a_t × ln cap96_a, a_t × 관문더미) 통과 못 하면 기술분석으로 확정하고 원고에 그대로 공개:
1. **공항 Feyrer 쉬프터**: z_a,t = a_t × ln airMA_a,1996 (공항 좌표 → 국가 인구 중심 거리 가중; 국가×연 FE 하에서 within-country 지리 변동만 사용). `20_airport_feyrer_iv.py` + `co2_airport_feyrer.do`.
2. **네트워크 노출 IV**: 공항 a의 1996 외국 파트너 공항들의 GACI 성장(leave-own-country-out) × 1996 연결 셰어 = 시프트셰어. 코멘트 3의 공항판이기도 함.
3. Yifu 사고 IV는 국가레벨 F 2-4로 실패했으므로 여기선 대기.

### 2D. 원고 배치
Layer 1에 "Airport-level evidence" 소절: 2A 표 1 + 2B 그림 1(집중도) + 2C는 성공 시 표, 실패 시 Methods 한 문단.

---

## 3. 스필오버 정식화 (코멘트 3)

목표: 이웃효과를 "거리감쇠·지역·메커니즘"까지 갖춘 제2 메인결과로.

### 3A. own GACI 통제 하 1차 이웃효과
현재 own은 쉬프터 RF로만 통제(2-내생 F≈5). **본명 스펙 = 옵션 2(동시 도구화)**; 옵션 1은 own이 내생이라 nbr 계수도 오염되므로 참고열로만:
1. own ln GACI를 외생 통제로 두고 nbr만 IV (참고열, 투명 라벨).
2. **W 재정의로 공선성 완화 (본명)**: 역거리(현행)는 a_t×smooth(geography)라 own 쉬프터와 근사 공선. 인접국(contiguity), k-최근접(k=5), 500km 밴드 W로 nbr_feyrer 재구성 → own·nbr 동시 도구화 시 Sanderson-Windmeijer 조건부 F 보고.
3. own 통제를 lnpop·ln_sea_ma에 더해 own 항공 MA96×a_t 직접 포함(현행 hybrid와 동일)은 참고열.

### 3B. 거리감쇠
`21_build_spillover_bands.py` (기존 12 확장): 밴드별 leave-out 평균 = 인접국 / <500km / 500-1,000 / 1,000-2,000 / 2,000-5,000 / >5,000 (활동중심점 거리; 인접국은 Natural Earth admin-0 `touches`). 각 밴드에 동일 밴드 feyrer IV.
- 회귀 1: 밴드 6개 동시 투입(각 IV) → 계수 감쇠 프로파일 그림(coefplot).
- 회귀 2: 연속 감쇠 W = exp(−d/λ), λ ∈ {250, 500, 1000, 2000, 5000km} 그리드 → 1단계 F·계수·AIC 표.
- 플라시보: (i) W 행 무작위 치환 500회 → 계수 분포 vs 실측, (ii) 가장 먼 밴드(>5,000km)만 → 0에 가까워야 "공통 글로벌 트렌드"가 아님.

### 3C. 지역 스필오버
- 지역 정의 2종: UN M49 서브리전(Region 컬럼 활용) + 항공시장 블록(EU 단일항공시장·ASEAN·GCC·MERCOSUR·NAFTA·ECOWAS 등 open-skies 협정 기반).
- within-region leave-out 평균 vs out-of-region 평균 동시 투입.
- **지역×연 FE 추가 스펙**(LZ의 "broader regional trends" 우려 직접 대응): 이 FE 하에서도 거리 밴드 효과가 남는지가 핵심 검정.
- 이질성: 지역별(유럽·아태·아프리카·라탐) 스필오버 계수, 국제셰어 tercile별(국제화된 국가가 더 흡수하는지).

### 3D. 메커니즘 연결 (기존 자산 재배치)
- own 분해(코멘트 1 표)와 nbr 분해(`_spillover_mech.csv`: gauge +5.44/intl +1.05/stage −2.03*/flights ns)를 **한 표 2열 "own vs neighbour"**로 → "자국은 편수, 이웃은 기재 대형화+국제화+단거리화 = 허브 피딩" 개념적 기여.
- 아웃컴 추가: 국내선 CO2(구성 가능, dom 컬럼) → 스필오버는 국제선에 집중되어야 함(현행 intl 10.24 > 총 7.45와 정합).

### 3E. 추론
- 공간 HAC(Conley, `acreg` 또는 python) SE 500/1,000/2,000km 컷오프, 지역 클러스터 병행.

산출: Table(스필오버 확장: A own통제 / B 밴드 / C 지역·지역×연FE) 1 + Fig(감쇠 프로파일+플라시보) 1 + Table(own vs nbr 분해) 1. 스크립트 `21_`, `co2_spill_bands.do`, `co2_spill_region.do`.

---

## 4. 배제제약 강화 (코멘트 4)

목표: "도구는 항공연결성을 통해서만 항공CO2에 영향" 지지 검정 묶음. 기존 3종(사이즈사이클·Conley·대안IV공개)은 유지하고 다음 추가. 우선순위 순.

1. **비항공 플라시보 아웃컴 (최우선)**: 동일 스펙 RF/2SLS로 (a) 국가 총CO2 ex-aviation(`_owid_aviation.csv` 이미 보유 → 즉시 착수 가능), (b) 도로교통 CO2(EDGAR v8 섹터별 또는 IEA), (c) 전력 CO2, (d) 해운 벙커(가능 시), (e) 실질GDP·인구(이미 통제). 항공CO2 RF 0.73 대비 이들 RF가 작거나 0이면 개발일반 경로 기각. 결과를 "RF 계수 비교 바차트"로.
   - 데이터: OWID co2-data.csv(총·석탄·석유·시멘트), EDGAR v8 GHG by sector(transport/road). `22_build_placebo_outcomes.py`.
2. **세계GDP×MA 호스레이스**: 도구 a_t × MA96 옆에 (세계 실질GDP_t × MA96), (유가_t × MA96), (세계 무역량_t × MA96) 추가 → 항공기술 성분이 살아남는지(1단계 F·2SLS β). 사이즈사이클 검정의 "사이클 내용" 버전.
3. **sea-MA 플라시보 도구**: a_t × ln seaMA96을 도구로 쓰면 GACI 1단계가 약하고 RF≈0이어야 함(항공기술이 해운지리로 작동하지 않음). 반대로 shipping technology_t × airMA96도 동일 논리.
4. **Zero-first-stage 검정 (van Kippersluis & Rietveld 2018)**: 기초연결성 상위 tercile은 1단계 F=1.8(쉬프터가 GACI를 못 움직임). 이 서브그룹에서 RF(feyrer_int → CO2)가 0이면 직접효과 부재의 증거. 기존 hetero 결과 재활용, 신규 추정 1개.
5. **개발경로 직접 통제 (bad-control 인지하고 바운드로)**: lnGDP, 무역개방도, 도시화, 관광객 수, FDI를 순차 추가 → β 안정성 표(계수 궤적 그림).
6. **대안 a_t 정의**: 세계 편수·세계 seat-km·세계 GACI 합·제트연료 효율지수·세계 기단 수. MA 감쇠 θ 0.5/1/1.5. 결과 계수 밴드가 좁으면 특정 함수형 의존 아님.
7. **리드 검정**: feyrer_int(t+3), (t+5) 리드를 현재값과 동시 투입 → 리드 유의하면 예상/공통트렌드 의심. a_t 구조상 해석 제한적임을 명시.
8. **과식별 정식화**: Feyrer + 관광 IV 동시 → Hansen J (메모리상 미완). 관광 IV가 사이즈사이클에 취약하므로 참고용.
9. **SE**: Conley 공간 HAC + 국가·연 2-way 클러스터 병기.

산출: Table "Exclusion-restriction diagnostics"(패널 A 플라시보 아웃컴 / B 호스레이스 / C 플라시보 도구 / D zero-FS / E 통제 궤적 = 항목 1~5; 항목 6~8은 ED) + ED Fig(RF 비교 바차트). 스크립트 `22_`, `co2_exclusion_suite.do`.

---

## 5. 원고 재구성 (LZ 5-layer)

| Layer | 내용 | 디스플레이 |
|---|---|---|
| 1 Causal effect | 국가 2SLS(현 Table 1) + 공항 이질성/집중도(2A·2B) + 인과 파일럿 결과 | T1, T(공항), Fig(집중도) |
| 2 Mechanism | 항등식 분해 표 + 워터폴 + 소득별 분해; 매개분석은 ED | T(분해), Fig(워터폴) |
| 3 Heterogeneity | 현 hetero(소득·연결·지역·집약도) + temporal 유지 | 현 coefplot 2 |
| 4 Spillover | own통제·밴드·지역·메커니즘 own vs nbr | T(스필오버 확장), Fig(감쇠), T(분해 대비) |
| 5 Policy | 귀속 356Mt·SCC·SAF 유지 + 허브 집중 기반 "상위 x% 공항 정책 커버리지" 반사실 1문단 | 현 지도·SAF 그림 |
| Methods | 식(1)(2) 분해, 배제제약 진단 표 전체 | T(진단) |

Nature 본문 디스플레이 한도 고려: 본문 표 3 + 그림 4~5, 나머지 ED/SI.

---

## 6. 실행 순서·의존성

| 순서 | 작업 | 신규 데이터 | 예상 |
|---|---|---|---|
| 1 | §1 분해 표·워터폴·소득별 (기존 CSV + do 1개) | 없음 | 0.5일 |
| 2 | §4-1,2,3,4 배제제약 핵심 4종 | EDGAR 섹터, 세계GDP·유가 시계열 (OWID 총CO2는 보유) | 1.5일 |
| 3 | §3B,C 밴드·지역 스필오버 + 플라시보 W | Natural Earth admin-0(인접), 지역블록 매핑 | 1.5일 |
| 4 | §2A,B 공항 이질성·집중도 | 없음(토폴로지 성분은 GACI 폴더 확인) | 1일 |
| 5 | §2C 공항 IV 파일럿 (2일 한도, 실패 시 공개 후 종료) | 국가 인구·좌표 | 1~2일 |
| 6 | §3A own통제 W 재정의 + §4-5~9 잔여 | 없음 | 1일 |
| 7 | tex 재구성(5-layer) + xlsx 시트 추가 + Overleaf 동기화 | | 1일 |

총 7~9 작업일. 스크립트 번호 18~22 + do-file 6개. 결과 xlsx는 `CO2_results_summary_20260902_LZ.xlsx`로 신규(기존 final 보존).

## 7. 리스크·미결

- 공항 IV는 다시 실패할 가능성 높음 → 원고는 "airport-level descriptive with country×year FE + concentration" 프레임을 기본으로 작성하고 성공 시 격상.
- 2-내생 스필오버 공선성은 W 재정의로도 안 풀릴 수 있음 → 옵션 1(own 외생 통제) 채택 + 투명 각주.
- 로드팩터는 구조적으로 불가(scheduled capacity) → 항등식에서 소거됨을 정면 명시, 감도만.
- 항공 기단연비 분리는 Fangyu 추가 집계 필요 → 요청 여부 결정 필요.
- 플라시보 아웃컴 데이터(EDGAR 섹터별)는 국가 커버리지·연도 정합 확인 필요(1996-2023, EDGAR v8은 2022까지).
