# GACI-CO2: Junya 코멘트 반영안 (2026-09-25)

기준 원고: Overleaf `main_co2_nature_20260908.tex` (Junya Methods 들어간 버전, `Downloads/GACI_CO2 (1).zip`)
붙여넣기 텍스트: `paste_blocks_20260925.tex` (BLOCK 1–12)

## 1. 코멘트별 반영

| # | Junya 코멘트 | 결정 | 반영 위치 | 블록 |
|---|---|---|---|---|
| Q1 | air MA 계산법(국가 평균인가) | 국가 단위 직접 계산으로 식 명시 | Methods > Instruments 식 (eq:seama), (eq:feyrer) | 3 |
| Q2 | sea MA 계산법 | CERDI 해상거리, 당해 인구 시변 통제로 명시 | 같은 곳 | 2a, 3 |
| Q3 | heritage IV 출처·계산 | 설명 대신 삭제 (P1) | - | 5, 6, 9 |
| Q4 | a_t 정의·출처 | OAG 세계 좌석용량, min-max. 대체 시계열 출처를 표 주석에 추가 | Instruments 본문, Supp Table 주석 | 3, 9 |
| Q5 | 기술통계 표 | 신규 Supplementary Table (tab:sumstat) | Supplementary Tables 맨 앞 | 1, 11 |
| P1 | heritage IV 삭제 | 수용. Methods 문장, Supp Table 1 Panel C 3행, 공항 heritage 문장 삭제 | | 5, 6, 9 |
| P2 | leads 삭제 | 수용. Supp Table 1 Panel B, Methods 괄호문 삭제 | | 4, 9 |
| P3 | ED Table 8 하단 삭제 | 부분 수용. 하단 블록 삭제, contiguity AR 집합 [0.2, 3.0]은 주석으로 이동 (joint KP F 3.3이라 필수) | ED Table 8, Methods 공간 절 | 7, 8 |

기타: Methods "Six further checks" 문단에서 "horse race ... supports our specification"은 ED Panel B(세계 GDP·수출 사이클을 넣으면 1단계 F 0.2/0.0)와 맞지 않아 caveat로 고쳐 씀 (BLOCK 4).

## 2. 작업 중 발견한 문제 (Junya 코멘트 외)

1. **추정 표본 국가 수 184 → 182.** Stata 로그상 클러스터 182개, 싱글턴 1개(NCL 2015) 제거 후 4,634. 원고 GACI 절과 Junya Estimation 절의 "184"는 오류 (BLOCK 1, 2b). SCC 표의 "184 countries"는 귀속 계산 국가 수라 그대로 둠.
2. **베네수엘라 trade/GDP 1996–2011이 0으로 들어감.** WDI API가 결측 대신 0을 반환. ED Table exclusion Panel E의 "plus trade/GDP" 이후 행과 본문 "4.4 to 4.6"에 영향. 재추정 필요.
3. **사고 IV 표(tab:accident_iv)가 robust SE로 추정됨.** do-file은 `robust`인데 표 주석은 "clustered by country". heritage IV를 빼면 과대식별 검정은 이것 하나뿐이라 클러스터로 재추정 필요.

## 3. Stata 재추정 결과 (2026-09-25 실행 완료, 오류 없음)

- `co2_exclusion_suite_cl_20260925.do` → `_exclusion_suite_cl_20260925.csv`: VEN 16개 관측치 결측 처리. 바뀐 것은 Panel E뿐. plus trade 4.43→4.45(1.40), urban 4.35→4.38, FDI 4.54→4.57, arrivals 4.64→4.72, 공통표본 5.62→5.69; 전부 1% 유의 유지. 범위 "4.4–4.6" → "4.4–4.7" (BLOCK 4, 13).
- `co2_asn_cl_20260925.do` → `_asn_iv_results_cl.csv`: 계수는 동일, 클러스터 SE로 커짐. joint 5.09 (0.40→1.07), KP F 66.8→9.2, Hansen p 0.82/0.96 (기존 0.81/0.95). 사망자 단독 2SLS는 10% 유의 → 유의하지 않음, joint intensity −0.34***→ 유의하지 않음 (BLOCK 5, 10).

## 4. 주의: 버전 병합

Overleaf = 9/08판 + Junya Methods. 로컬 `FINAL_20260923_figLZ` = Longfei 통합그림 + 예전 Methods.
로컬 tex로 Overleaf를 덮어쓰지 말 것. Overleaf에 위 블록을 반영하고, 그림(Figure1-2, ED_Fig1-4)과 그림 블록만 9/23판에서 옮길 것.

## 5. Junya 답장 초안 (일본어)

Junyaさん

お疲れ様です。Estimation部分ありがとうございます。コードで確認し、コメントへの対応案を作りました。

【質問への回答】
1. Air market access：空港レベルの平均ではなく、国レベルで直接計算しています。airMA_{c,1996} = Σ_{j≠c} Pop_{j,1996} / d_{cj}（θ=1）。d_{cj} は各国の航空重心（ネットワーク内空港の緯度経度の単純平均）間の大圏距離、Pop は WDI 総人口です。操作変数は Z_{ct} = a_t × ln airMA_{c,1996} です。
2. Sea market access：seaMA_{ct} = Σ_{j≠c} Pop_{jt} / dsea_{cj}。dsea は CERDI-seadistance の港湾間海上距離（Bertoli et al. 2016）で、コントロールは当年人口による時変の値です。
3. Tourism-heritage：世界の国際観光客到着数（min-max）× ln(1 + UNESCO 自然・複合遺産数) ですが、ご提案どおり削除します。
4. a_t：はい、OAG スケジュールから集計した世界の年間座席容量を 1996–2023 で min-max 正規化したものです。world flights・seat-km・fuel efficiency も自前の OAG インベントリから作っています。
5. Summary statistics：Supplementary Table として追加しました。

以上の定義は Methods の Instruments 節に式として追加しました。

【ご提案への対応】
- Heritage IV：削除します（Methods、Supp. Table 1 Panel C、空港レベルの一文）。過剰識別は事故IVで示します。
- Leads：削除します。国FEの下では lead と当期値がほぼ共線で情報がなく、有意な lead を残すとプレトレンドの問題に見えるためです。
- ED Table 8 下段：削除しますが、contiguity の Anderson–Rubin 95%集合 [0.2, 3.0] だけ注記に残します。joint の KP F が 3.3 と弱いので、隣国係数の弱IV頑健な根拠として必要なためです。

【確認中に見つかった点】
- 推定サンプルは 184 か国ではなく 182 か国でした（クラスター数も 182）。Estimation の "184 clusters" も修正します。
- ベネズエラの trade/GDP（1996–2011）が WDI で 0 になっていたため欠損に直して、開発コントロールの推定を再実行しました。
- 事故IVの表が robust SE で推定されていたので、クラスターで再推定しました。

上記2点は再推定済みで、開発コントロールの推定値は 4.4–4.7（すべて1%有意）、事故IVとの同時推定の Hansen J p値は 0.82 と 0.96 でした。数値は原稿に反映します。よろしくお願いします。
