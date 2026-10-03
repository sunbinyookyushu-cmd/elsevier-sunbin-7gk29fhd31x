# GACI x CO2: Longfei 그림 교체본 (2026-09-23)

## 1. 한 일

- 기준 원고: 오늘 받은 Overleaf 다운로드 `GACI_CO2.zip` 안의 `main_co2_nature_20260908.tex` (9/09 사용자 마커 반영본). Dropbox `FINAL_20260908`의 tex보다 새 버전이라 이걸 기준으로 삼음.
- 그림: `Figures_LZ_260923.zip` (Longfei, 9/20 작성).
- 결과: `co2_overleaf_20260923/main_co2_nature_20260923.tex` + 새 그림 6장 + `refs_co2.bib`.

### 그림 매핑 (기존 11장 → 새 6장)

| 새 번호 | 파일 | 패널 | 대체한 기존 그림 (label) |
|---|---|---|---|
| Fig. 1 | Figure1.png | a | 기존 ED 분해 waterfall (`fig:waterfall`) |
| | | b–d | 기존 Fig. 1 이질성 A–C (`fig:hetero`), **기존 D 패널(소득별 intensity)은 빠짐** |
| Fig. 2 | Figure2.png | a | 기존 ED 국가별 귀속 막대 (`fig:bars`) |
| | | b | 기존 Fig. 2 귀속 지도 (`fig:attributed`) |
| | | c, d | 기존 Fig. 3 SAF 경로 (`fig:saf`) |
| ED Fig. 1 | ED_Fig1.png | a | 기존 ED temporal split (`fig:temporal`) |
| | | b, c | 기존 ED 공항 집중도 (`fig:airportconc`) |
| ED Fig. 2 | ED_Fig2.png | | 기존 ED gradient (`fig:gradient`) |
| ED Fig. 3 | ED_Fig3.png | a, b | 기존 ED spillover decay (`fig:spilldecay`) |
| ED Fig. 4 | ED_Fig4.png | a–c | 기존 ED 순열 플라시보 (`fig:spillplacebo`) |
| | | d | 기존 ED 비항공 배출 reduced form (`fig:placeborf`) |

- 본문 디스플레이: 표 4 + 그림 2 = 6개 (기존 7개, 9/08 README의 "6개 한도" 문제 해소). ED 그림 8장 → 4장.
- 첫 인용 순서 = 번호 순서 (Fig. 1 → 2, ED 1 → 2 → 3 → 4) 확인.
- 캡션 6개를 새 패널 구성과 새 색 규칙(빨강 채움 = p<0.05 등)에 맞게 새로 씀.
- 본문·Methods·ED 표 주석의 그림 참조 13곳을 새 번호 + 패널 문자로 바꿈 (gradient, spilldecay 참조 4곳은 번호만 자동으로 바뀌어 그대로 둠). 미정의 `\ref` 0개, 기존 그림 파일명 참조 0개 확인.
- 기존 Fig. 1 D 패널이 빠졌으므로 "The efficiency margin ... is not significant in any group" 문장 뒤에 `(Extended Data Table~\ref{tab:hetero}, Panel D)` 추가. 지역 문장 뒤에 `(Fig. 1d)` 추가.
- 새 그림의 숫자를 tex 표와 대조: 5.35 / 6.76, −0.34, −0.78, −0.29 / 9.43, 6.12, 1.89 / 7.48, 5.07, 4.03 / −0.47, 5.05, 4.54, 2.93 / 85.9 ~ −14.7 Mt / SAF 2050 993, 833, 672 및 788, 661, 534 / 순열 t 3.46, 7.18, 5.35 (p .188, .000, .018) 모두 일치.
- 그림 참조와 위 두 괄호 외에 본문 문장·숫자는 건드리지 않음. 수정 전후 전체 차이는 `diff_tex_20260908_to_20260923.txt`.

## 2. 확인할 것 (우선순위 순)

### A. Longfei에게 요청해야 하는 것

1. **Figure 2a UAE 라벨 오류.** "24.5 Mt"가 "2.4 5 M" 형태로 깨져 있음 (PNG, PDF 둘 다). 본문 대표 그림이라 반드시 수정.
2. **Figure 2c, d 음영 밴드의 정의.** 9/14 코드(`31_saf_growth.py`)에 없던 새 요소. 캡션에 `[TODO: band definition from Longfei]`로 비워 둠. 역산하면 무-SAF 경로 밴드 상단(2050년 약 2,240 Mt)은 β ≈ 4.86에 해당하는데, 성숙기 탄성치 2.948(군집 SE 1.199)의 90% 상한(4.92, 2,266 Mt)이나 95% 상한(5.30)과 맞지 않음. 정의를 받아 캡션을 채우고 Methods "Attribution and fuel-switching scenarios"에 한 문장 추가 필요.
3. **499 Mt 수평선이 그림에서 빠짐.** 본문 "No path reaches the 499 Mt that would remain after removing the emissions attributed to past connectivity growth"의 시각적 근거가 사라짐. 선을 되살릴지(Longfei), 문장만 둘지 결정. 또 r = 80% 밴드 하한은 2050년에 499 Mt 아래로 내려가므로, 밴드를 유지한다면 이 문장은 "중심 경로 기준"임을 밝히는 편이 안전.

### B. 원고 쪽에서 판단할 것

4. **ED Fig. 4d의 Coal CO2(0.89), Cement CO2(0.67)가 이제 채운 점(p<0.05)으로 보임.** 기존 그림은 같은 수치였지만 유의 표시가 없었음. Methods "non-aviation emissions do not respond to the instrument"는 총 화석 CO2(0.05)만 언급하므로, 심사자가 두 계열을 짚을 수 있음. 11개 계열 중 2개라는 점 등 한 줄 설명을 넣을지 판단.
5. **ED Fig. 2에서 Q3–Q5 "unidentified" 표기가 삭제됨.** 캡션에 KP F 4.8, 0.0, 2.1과 ED Table 참조를 넣어 보완함. 다만 본문 "3.3 to 4.0 above them"은 약한 1단계 추정치(Q3, Q5)를 그대로 인용하는 기존 문장이라 필요하면 완화.
6. **ED Fig. 1이 temporal split + 공항 집중도라는 서로 다른 주제의 조합.** Nature ED 그림 한도(10장)에 여유가 있으니 둘로 나눌지, 이대로 갈지.
7. **ED Fig. 1b 범례 "Attributed (country b)/(airport b)".** 'b'가 β 뜻인데 패널 b와 헷갈림. β로 바꾸는 사소한 수정(Longfei).

### C. Overleaf에서 눈으로 볼 것

8. 컴파일 후 그림 폭(0.85~0.98 textwidth), `[H]` 배치로 생기는 페이지 빈 공간, 캡션 줄바꿈.
9. 색 규칙 통일 여부: Fig. 1b–d는 빨강 채움 = 유의, 파랑 빈 원 = 비유의 / ED Fig. 1a는 빨강 빈 원 = 비유의, 회색 = 비제한 표본 / ED Fig. 4d는 빨강 = 항공, 파랑 = 비항공.

## 3. 참고

- Longfei가 같이 보낸 4장(`CO2_map_levels_2023`, `CO2_map_mismatch_2023`, `CO2_efficiency_curve`, `CO2_rf_concentration_combined`)은 9/09에 삭제한 ED 그림(levels, mismatch, effcurve, rfquintile)의 재작업본이라 tex에 넣지 않음. `figures_LZ_260923_original/`에 원본 그대로 보관.
- 원고에는 PNG(300 dpi)를 씀. 최종 제출 때 벡터 파일이 필요하면 Longfei PDF를 사용 (Figure1.pdf는 26 MB로 큼, ED Fig. 2와 3은 PDF 없음).
- 로컬에 LaTeX가 없어 여기서는 컴파일하지 못했음. 참조, 중괄호 균형, figure 환경 짝은 스크립트로 검사함.

## 4. 폴더 구성

- `co2_overleaf_20260923/`: Overleaf에 올릴 파일 (tex, bib, 그림 6장)
- `GACI_CO2_overleaf_20260923.zip`: 위 폴더 + 이 README 압축본. Overleaf > New Project > Upload Project
- `figures_LZ_260923_original/`: Longfei 원본 14개 (PDF 포함, 미사용 4장 포함)
- `_prev_overleaf_download_20260923/`: 수정 전 Overleaf 다운로드 원본 (되돌리기용)
- `diff_tex_20260908_to_20260923.txt`: tex 수정 전후 차이
