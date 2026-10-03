# GACI × CO2: 최종 결과 후보 메모 (2026-09-06)

후보 원고: `co2_overleaf_20260906\main_co2_nature_20260906.tex` (+ zip, Downloads 사본).
빌드: `32_spatial_models.py` → `33_spatial_table.py` → `34_assemble_20260906.py`.

## 0. 이번에 반영한 입력

| 입력 | 내용 | 반영 |
|---|---|---|
| Junya 메일 | SLX / SEM / SDM 추가 (Longfei 제안) | 본문 Table 3 `tab:spatial` (SLX·SAR·SEM·SDM·SDEM, ML 패널 + IV 패널), ED Table 10 (inverse-distance W, 국제선·집약도) |
| Junya 메일 | LTO CO2 · 50/50 CO2는 부록으로 | Table 1을 4열(Bunker · Intl · Seat-km · Intensity)로 축소, LTO·50/50은 ED Table 2 `tab:alloc` |
| JL docx | Discussion 5항 리라이트 | 그대로 채택 (3항에 공간모형 한 절만 추가). 주의: JL의 Discussion은 docx에만 있고 (2) tex에는 구판 Discussion이 들어 있었음 |
| JL docx | 이질성 문단 완화 ("Europe precisely estimated zero / carbon-neutral" → "small and indistinguishable from zero / smaller and less precisely estimated") | 반영 |
| (2) tex | Chunan·Fangyu 신규 Methods (식 1–24, 검증표 `tab:emissions_validation`) | 그대로 채택, 09-03판의 짧은 Methods 4절 대체 |
| 09-03 cl 결과 | LZ·Yifu 대응 (분해·공항·배제제약·함수형·귀속 민감도), 국가 클러스터 SE | 결과부 프로즈·표의 기반 |
| Ray·Lisa 메일 (09-04) | SAF를 교통량 고정이 아니라 성장 결합으로 | SAF 절·그림(`CO2_saf_growth.png`)·Methods 수식 교체 |

## 1. 추천 스토리라인 (후보 A = 조립된 원고)

본문 디스플레이 8개: 표 4 + 그림 4. (09-06 오전 유저 지시로 공항 절은 ED로 이동, 귀속 절에 요약 문단 1개만 남김.)

| 순서 | Results 소제목 | 본문 디스플레이 | 헤드라인 수치 (국가 클러스터 SE) |
|---|---|---|---|
| 1 | The emissions elasticity of connectivity is far above one | Table 1 (main, 4열) | 5.67 (1.12), KP F 18.4; 시기 5.61 / 3.01 → ED T1 |
| 2 | Frequency, not aircraft size or efficiency | Table 2 decomposition | flights 6.98 (1.38)***, gauge −0.30 ns, stage −0.60 ns, intensity −0.40 ns |
| 3 | Concentrated in newly connecting countries (+ take-off stage) | Fig 1 hetero coefplot | 소득 tercile 10.40 / 6.14 / 1.83, 상호작용 −3.33 (0.57); JL 완화 문구 |
| 4 | **Neighbours' connectivity, not neighbours' emissions (신규)** | **Table 3 spatial** | 아래 §2 |
| 5 | 42.5 percent of 2023 emissions (+ 공항 요약 문단) | Fig 2 attributed map, Table 4 SCC, Fig 3 mismatch | 356 Mt, $18–68bn/yr; 귀속 범위 294–353 Mt (ED T14); 공항 3.72·허브 2.0 vs 3.8·top 5% = 84.5% (ED T6·T7, ED F6·F7) |
| 6 | Only fuel switching lowers the level | Fig 4 SAF growth | no-SAF 2050 1,528 Mt; r65% 833 Mt(=2023 수준), r80% 672 Mt; 482 Mt 미달 |

## 2. 공간모형 결과 (W = 육지 인접, 아웃컴 = ln bunker CO2, N = 4,624)

| 모형 | own β | W·GACI θ | ρ (W·y) | λ (W·u) | direct | indirect | total |
|---|---|---|---|---|---|---|---|
| 2SLS | 5.70 (1.12) | | | | | | |
| SLX-IV | 3.49 (1.28) | 1.92 (0.69) | | | | | |
| SAR-IV | 5.72 (0.95) | | 0.03 (0.04) | | 5.73 | 0.16 | 5.89 |
| SEM-IV | 5.02 (1.19) | | | 0.10 | | | |
| SDM-IV | 4.95 (0.99) | 1.30 (0.67) | −0.02 (0.02) | | 4.94 | 0.94 (0.45) | 5.88 (0.93) |
| SDEM-IV | 3.16 (1.02) | 2.23 (0.67) | | 0.14 | | | |

읽는 법 (본문 문단 그대로):
1. 스필오버는 이웃의 배출(ρ≈0)이나 공통 쇼크(λ 0.10–0.14)가 아니라 이웃의 연결성(θ 1.3–2.2) 경유.
2. own 탄력성은 공간 스펙에 강건 (SAR 5.72 / SEM 5.02 / SDM direct 4.94 vs Table 1 5.67); θ를 넣으면 3.2–3.5로 내려가는 건 이웃 성장과 상관된 부분이 흡수되기 때문.
3. 네트워크 전체 총효과(direct+indirect) 5.88 = 단일식 탄력성과 동일; indirect 0.94가 국경 넘는 부분 → 국가 추정은 own 효과의 20–55%만큼 과소.

Panel A(비도구, ML)는 β 3.5 근처, ρ 0.08–0.12***, λ 0.13***로 "공간 상관은 있으나 작다"는 보조 증거. SLX-IV는 09-03 Stata joint contiguity 스펙(3.48 / 1.93, SE 1.29 / 0.69)을 그대로 재현.

## 3. Extended Data / Supplementary 배치

(09-06: 유저 지시로 ED·SI 디스플레이를 끝에 모으지 않고 첫 인용 문단 바로 뒤에 인라인, 번호는 등장 순서로 재부여. 아래 목록은 내용 기준.)

ED 표 14: T1 temporal · T2 allocation rules(신규) · T3 hetero · T4 mediation · T5 decomp hetero · T6 airport hetero · T7 airport concentration(본문→ED) · T8 spillover joint 2SLS(구 본문 Table→ED) · T9 spill structure · T10 spatial ext(신규) · T11 exclusion · T12 funcform · T13 gradient · T14 attribution sensitivity.
ED 그림 11: F1 temporal · F2 waterfall(→ED) · F3 gradient(→ED) · F4 attribution bars(→ED) · F5 levels map(→ED) · F6 efficiency curve(→ED) · F7 airport concentration(→ED) · F8 rf quintile · F9 spill decay · F10 spill placebo · F11 placebo RF.
SI 표 3: exclusion2 · airport IV pilot · accident IV. 삭제: dlngaci 지도, carbonprice 지도 (미인용).

## 4. 유저 결정이 필요한 항목

1. **SE 컨벤션**: 후보 A는 09-03 결정대로 국가 클러스터로 통일 (Table 1 s.e. 1.12, F 18.4; 집약도 −0.40은 ns). 유저의 (2) tex와 JL docx는 robust(0.41, F 154) 기준. JL의 Discussion 자체가 "under country-clustered inference"를 전제로 쓰였으므로 클러스터가 정합. robust로 되돌리려면 `CLSUF` 없는 프래그먼트로 34를 재조립하면 됨 (프로즈 수치는 손수 교체 필요).
2. **JL Discussion 3항에 삽입한 한 절** ("and it operates through neighbours' connectivity rather than through neighbours' emissions: spatial lag and spatial error models leave the own elasticity and the total effect unchanged") — JL에게 알릴 것.
3. **본문 디스플레이 대안**: 그림 2를 airport concentration 대신 efficiency curve로, 그림 4를 mismatch 대신 levels로, SAF를 성장결합판 대신 고정판으로 바꾸는 것은 34 스크립트에서 한 줄씩 교체 가능.
4. **인접국 없는 국가 수**: 파이썬 NE 매칭 39개국 vs Stata 31개국 (ED T8 노트) 불일치. 둘 다 "31"로 맞추려면 Stata의 contig 정의를 파이썬에 그대로 쓰면 되나 결과 차이는 미미(SLX-IV가 Stata와 일치).
5. **첫단계 F**: 공간모형에서 own connectivity의 SW F는 5–7 (SLX 7.3, SDM 6.1). 이웃 항의 SW F는 자체 계산(165)이 Stata(13.2)와 달라 표에서 뺐음. 표에는 own F만.
6. **ED T10 inverse-distance 패널**: own·이웃 쉬프터 공선으로 SAR-IV ρ≈1, total 127 같은 폭주값이 있음. "for completeness"로 두거나 Panel A를 삭제할지 결정 필요.
7. 본문 2SLS 5.70(공간 표본 4,624) vs Table 1 5.67(4,634) — 프로즈는 "against 5.67 in Table 1"로 처리.

## 5. 대안 후보

- **후보 B (최소판, 디스플레이 6)**: T1 main · T3 spatial · T4 SCC · F1 hetero · F3 attributed map · F5 SAF. decomposition 표·공항 그림·mismatch 지도를 ED로. 분해 결과는 프로즈 수치로만. Nature Comms 분량 압박이 클 때.
- **후보 C (풀판)**: 09-03 cl 원고 구조(5-layer, 본문 표 5 + 그림 10)에 spatial 표만 추가. 공저자 검토용으로 결과를 다 보여주고 싶을 때.
- 후보 A는 B와 C의 중간이며 JL Discussion의 5항(빈도·이질성·국경·공항·한계)과 1:1로 대응하는 디스플레이를 갖도록 골랐음.

## 6. 잔여 TODO

- Overleaf 컴파일 확인 (로컬 MiKTeX 고장). 새 그림: `CO2_saf_growth.png`.
- [TODO cite] 14곳 (Feyrer, ICAO/CORSIA, SCC 3종, IATA/OECD/BTS/Quadros, JL의 3개 placeholder).
- Chunan·Fangyu 검증표의 **[TBD]** BTS 값.
- 저자 순서, Data/Code availability.
