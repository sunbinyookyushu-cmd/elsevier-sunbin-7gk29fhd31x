# -*- coding: utf-8 -*-
"""README / 결정필요 / 연구설계 sheet text for 20_make_xlsx.py. Key numbers are read from the result CSVs."""
import numpy as np
import pandas as pd

ra = pd.read_csv("_res_airport.csv")
rc = pd.read_csv("_res_country.csv")
rev = pd.read_csv("_res_events.csv")
rlp = pd.read_csv("_res_lp.csv")
rfs = pd.read_csv("_res_first_stage.csv")

def st(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""

def g(df, **kw):
    m = df
    for k, v in kw.items():
        m = m[m[k] == v]
    return m.iloc[0]

def cs(x, d=4):
    return f"{x.b:.{d}f}{st(x.p)} (SE {x.se:.{d}f})"

A = lambda **kw: g(ra, table=kw.pop("t", "A1"), term=kw.pop("term", "x"), **kw)
C = lambda **kw: g(rc, table=kw.pop("t", "C1"), term=kw.pop("term", "x"), **kw)
a_ols, a_kz, a_bh = [A(panel="H_g", outcome="d12_ln_seats", col=c) for c in ["OLS", "2SLS-KZ", "2SLS-BH"]]
h_kz = A(panel="Hub10", outcome="d12_ln_seats", col="2SLS-KZ")
h_kz_co2 = A(panel="Hub10", outcome="d12_ln_co2", col="2SLS-KZ")
c_ols, c_kz, c_bh = [C(panel="H_cwm", outcome="d_ln_seats", col=c) for c in ["OLS", "2SLS-KZ", "2SLS-BH"]]
c_intl = C(t="C2", outcome="d_ln_seats_intl", col="OLS")
rob = lambda pnl, col: g(ra, table="A5", panel=pnl, col=col, term="x")
ev = lambda e, o, fe, pr: g(rev, event=e, outcome=o, fe=fe, period=pr)
FE1, FE2 = "apt x cal-month + country x month", "+ intl share(base) x month"
e22s, e22a = ev("2022 spike", "ln_seats", FE1, "spike (2022-03..12)"), ev("2022 spike", "ln_seats", FE1, "after (2023-01..2024-06)")
e22s2, e22a2 = ev("2022 spike", "ln_seats", FE2, "spike (2022-03..12)"), ev("2022 spike", "ln_seats", FE2, "after (2023-01..2024-06)")
e22d, e22da = ev("2022 spike", "ln_seats_dom", FE2, "spike (2022-03..12)"), ev("2022 spike", "ln_seats_dom", FE2, "after (2023-01..2024-06)")
e14 = ev("2014 crash", "ln_seats", FE1, "low (2015-01..2016-12)")
e08 = ev("2008 spike", "ln_seats", FE1, "spike (2007-10..2008-09)")
lp18 = g(rlp, h=18, outcome="ln_seats", shock="s_kz")
lp18b = g(rlp, h=18, outcome="ln_seats", shock="s_bh")
lp0 = g(rlp, h=0, outcome="ln_seats", shock="s_kz")
fsA = rfs[(rfs.level == "airport-month") & (rfs.position == "H_g")]
fsC = rfs[(rfs.level == "country-year") & (rfs.position == "H_cwm")]
F_cl_A = fsA[(fsA.shock == "kz_s12_l3") & (fsA.vc.str.startswith("('cl',"))].F.iloc[0]
F_cl_C = fsC[(fsC.shock == "d_kz_cum") & (fsC.vc.str.startswith("('cl',"))].F.iloc[0]
dlnP = np.log((1.88 + 0.957) / 1.88)
gap = lambda b: 100 * (np.exp(b * dlnP) - 1)
b_ = pd.read_csv("airport_base.csv")
b_ = b_[b_.GACI_96.notna() & (b_.seats_96 > 0)]
corr_air = b_[["GACI_96", "ln_airma96"]].corr().iloc[0, 1]
c6 = g(rc, table="C6", outcome="d_ln_seats")

README = [
    ("h1", "GACI × 제트연료 가격 충격: 허브와 스포크의 반응 차이 (2026-09-29, 탐색 분석)"),
    ("p", "폴더: Research Box ^-^/2026/GACI/GACI_FuelShock/ . 모든 표는 스크립트로 재생성됨(01~03 자료 구축, 11 국가×연도, 12 공항×월, "
          "13 사건연구, 14 국소투영, 15 요약통계, 16 1단계, 20 이 엑셀). 추정기는 _est.py(pyfixest 결과와 계수·SE 일치 확인, 10_validate_est.py)."),
    ("p", "먼저 '결정필요_표본정의' 시트를 봐 주세요. 표본 기간, 단위, 가격 시차, 도구, 추론 방식 등 제가 임시로 정한 선택 12개가 정리되어 있습니다. "
          "각 선택의 대안 결과도 T8에 함께 넣었습니다."),
    ("h2", "요약"),
    ("p", f"1) 공항×월 본분석(1997~2019, {int(a_ols.n):,} 공항-월, {int(a_ols.n_air):,}개 공항): 연료가격 12개월 로그변화(3개월 시차) × GACI 1996(z)의 계수는 "
          f"OLS {cs(a_ols)}, 2SLS(BH) {cs(a_bh)}로 0에 가깝다. OLS 95% 구간은 [{a_ols.b - 1.96 * a_ols.se:.4f}, {a_ols.b + 1.96 * a_ols.se:.4f}]."),
    ("p", f"2) 2SLS(Känzig)에서만 음의 계수: GACI 1 SD당 {cs(a_kz)}(KP F {a_kz.F:.1f}), 상위10% 허브 {cs(h_kz)}, 상위10% 허브의 CO2 {cs(h_kz_co2)}. "
          f"연료가격이 오르면 허브의 좌석 증가율이 다른 공항보다 조금 더 낮아지는 방향. 이 결과는 권역×월 FE {rob('region x month FE', '2SLS-KZ').b:.4f}(p={rob('region x month FE', '2SLS-KZ').p:.2f}), "
          f"국가×월 FE {rob('country x month FE', '2SLS-KZ').b:.4f}(p={rob('country x month FE', '2SLS-KZ').p:.2f}), 미국 제외 {rob('excl. USA', '2SLS-KZ').b:.4f}(p={rob('excl. USA', '2SLS-KZ').p:.2f}), "
          f"Känzig 코로나 이전 버전 {rob('Kaenzig pre-Covid vintage', '2SLS-KZ').b:.4f}(p={rob('Kaenzig pre-Covid vintage', '2SLS-KZ').p:.2f})에서 유의하지 않다. 시차 6~12개월, 브렌트, 명목가격, 균형패널에서는 −0.013~−0.017로 유지."),
    ("p", f"3) 탄소가격 환산(T3 Panel D): 톤당 100달러 = 갤런당 0.957달러 = Δln P {dlnP:.3f}. Känzig 계수 기준 상위10% 허브의 좌석 증가율이 다른 공항보다 "
          f"{gap(h_kz.b):.1f}% 낮음(90% 구간 {gap(h_kz.b - 1.645 * h_kz.se):.1f}~{gap(h_kz.b + 1.645 * h_kz.se):.1f}%). OLS·BH 기준은 0% 부근."),
    ("p", f"4) 국가×연도(150개국, 1997~2019): GACI cwm 1996(z) 계수 OLS {cs(c_ols)}, 2SLS(Känzig) {cs(c_kz)}(F {c_kz.F:.1f}, 약한 도구), "
          f"2SLS(BH) {cs(c_bh)}(F {c_bh.F:.1f}). 국제선 좌석만 보면 OLS {cs(c_intl)}. 공항 수·공항 간 집중도(HHI)·GACI 자체의 반응은 없음(T4)."),
    ("p", "5) 경로·마진(T4)과 경쟁회귀(T5): 기체 크기·운항거리·좌석km당 CO2·국제선 비중의 반응은 체계적이지 않음. 1996년 평균 운항거리 × 가격은 OLS에서 "
          "+0.020~+0.024(p≈0.07~0.09)로 장거리 공항이 오히려 덜 줄이는 방향이며, 이 변수와 소득을 넣으면 위치 계수는 0으로 수렴."),
    ("p", f"6) 사건연구(T6): 2008년 급등({e08.b:.4f}, p={e08.p:.2f})과 2014년 급락({e14.b:.4f}, p={e14.p:.2f})에서 허브·스포크 차이 없음. "
          f"2022년은 같은 나라 안에서 허브 좌석이 급등기 {e22s.b:.3f}{st(e22s.p)}, 이후(2023~2024.6) {e22a.b:.3f}{st(e22a.p)} 높았고, 국제선 비중×월 통제 시 "
          f"{e22s2.b:.3f}{st(e22s2.p)} / {e22a2.b:.3f}{st(e22a2.p)}, 국내선만 {e22d.b:.3f}{st(e22d.p)} / {e22da.b:.3f}{st(e22da.p)}. "
          "그러나 월별 계수(Fig_사건연구)는 격차가 유가 급등 전인 2021년 초부터 커지고 유가가 내려간 2023~2024년에도 계속 커져서, 코로나 이후 회복 경로와 구분되지 않는다."),
    ("p", f"7) 국소투영(T7): 1 SD Känzig 충격은 유가를 h=0에서 {100 * lp0.g_price:.1f}% 올리고, GACI 1 SD 높은 공항의 좌석은 14~18개월 뒤 "
          f"{lp18.b:.4f}{st(lp18.p)} 더 줄어듦(h=18 함의 탄력성 {lp18.implied_elast:.3f}). BH 충격은 전 구간 0 부근(h=18 {lp18b.b:.4f})."),
    ("p", f"8) 준비된 위치 도구변수(ln air MA 1996, Feyrer 재료)는 공항 단위에서 GACI 1996과 상관 {corr_air:.2f}, 국가 단위 1단계 F {c6.F:.1f}로 약함(A3). "
          "이 설계는 위치(노출)는 사전결정으로 두고 충격의 외생성에 기대는 구조라 위치 도구변수 없이도 성립하지만, 선생님이 말씀하신 '만들어 둔 도구변수'가 "
          "다른 것이라면 알려 주시면 추가하겠습니다."),
    ("p", f"9) 추론 주의: 가격 충격이 모든 단위에 공통인 시계열 하나라서 국가 클러스터만 쓰면 1단계 F가 공항 {F_cl_A:,.0f}, 국가 {F_cl_C:,.0f}로 과대하게 나온다. "
          "본표의 별표는 국가 클러스터 + 시간 Newey-West(Thompson 2011) 기준이며, 국가 클러스터 SE는 [ ]로 병기했다."),
    ("h2", "시트 안내"),
    ("p", "결정필요_표본정의: 임시 선택과 대안 / 연구설계: 질문·식·식별·위협과 대응·다음 단계 / T1 요약통계 / T2 국가×연도 본분석 / T3 공항×월 본분석(+탄소가격 환산) / "
          "T4 마진(기체·거리·연료효율·국내외·집중도) / T5 경쟁회귀(위치 vs 규모·국제선·운항거리·기체·소득·오일렌트) / T6 사건연구(2022·2014·2008) / "
          "T7 국소투영 / T8 강건성 / A1 1단계 / A2 분위별 / A3 위치 도구변수 / Fig_* 그림 자료(엑셀 네이티브 차트) / raw_* 전체 결과."),
]

DECISIONS = [
    ("h1", "표본·정의 선택 (확인 필요)"),
    ("p", "아래는 이번 탐색 분석에서 제가 임시로 정한 선택입니다. 어느 것도 확정이 아니며, 대안 결과는 T8(강건성)이나 해당 표에 함께 있습니다. "
          "원고에 들어가기 전에 각 항목을 정해 주세요."),
    ("h2", "1. 연속처치 분석 기간: 1997~2019 (2020~2024 제외)"),
    ("p", f"이유: 2020~2021년은 유가 급락과 국제선 붕괴가 겹쳐 위치×가격 계수가 기계적으로 양(+)으로 끌려감. 대안(1997~2024 포함) 공항 OLS "
          f"{rob('incl. 2020-2024', 'OLS').b:.4f}{st(rob('incl. 2020-2024', 'OLS').p)}, Känzig {rob('incl. 2020-2024', '2SLS-KZ').b:.4f}, BH {rob('incl. 2020-2024', '2SLS-BH').b:.4f}. "
          "추천: 1997~2019 본분석, 2022년은 사건연구로 따로."),
    ("h2", "2. 분석 단위와 제외"),
    ("p", f"공항: 1996년 GACI가 있고 1996년 좌석이 양수인 공항 3,351개(Δ12 표본 {int(a_ols.n_air):,}개). 1997년 이후 신규 공항은 사전 위치가 없어 제외. "
          "ISO3 코드가 매칭되지 않는 공항은 제외(전체 6,356개 중 160개, 대부분 소형). 국가: 1996년 GACI가 있는 150개국(패널 184개국 중). "
          "대안: 첫 관측연도 위치 사용(미실시)."),
    ("h2", "3. 좌석 0인 공항-월"),
    ("p", f"로그 차분에서 빠짐(취항 개시·중단은 반영 안 됨). 대안: 288개월 모두 운항한 균형패널(1,875개 공항) 결과 OLS {rob('balanced airports', 'OLS').b:.4f}, "
          f"Känzig {rob('balanced airports', '2SLS-KZ').b:.4f}{st(rob('balanced airports', '2SLS-KZ').p)}, BH {rob('balanced airports', '2SLS-BH').b:.4f}. PPML 등 수준 모형은 미실시."),
    ("h2", "4. 가격 변수와 시차"),
    ("p", "실질(미국 CPI-U, 2019달러) 걸프코스트 제트연료. 공항: 3개월 시차 12개월 로그차분(스케줄은 수개월 앞서 정해짐). 국가: 연평균 로그차분. "
          "대안: 시차 0·1·6·9·12개월, 브렌트, 명목, 크랙스프레드(T8). 시차 3을 본 사양으로 할지 결정 필요."),
    ("h2", "5. 도구변수: Känzig vs BH"),
    ("p", f"두 도구의 결과가 다름(공항: Känzig {a_kz.b:.4f}{st(a_kz.p)}, F {a_kz.F:.1f} / BH {a_bh.b:.4f}, F {a_bh.F:.1f}). Känzig는 OPEC 발표일 선물가격 반응 기반의 "
          "뉴스 충격(외생성 논거가 강함, 1단계는 상대적으로 약함), BH는 VAR 구조 공급충격(가격과 동시 식별이라 1단계가 강함). 추천: 둘 다 본표에 보고."),
    ("h2", "6. 위치 정의"),
    ("p", "공항: GACI 1996 z점수(본), 상위10% 허브 더미, ln(1+betweenness) z점수. 국가: GACI cwm 1996 z점수(본), GACI max, ln(1+평균 betweenness). "
          "z점수는 1996년 표본 단면 기준."),
    ("h2", "7. 추론(가장 중요)"),
    ("p", "본표 별표 = 국가 클러스터 + 시간 Newey-West(공항 L=12개월, 국가 L=2년; Thompson 2011), 이원 분산이 일원 분산보다 작으면 큰 쪽으로 하한. "
          f"국가 클러스터만 쓰면 1단계 F가 공항 {F_cl_A:,.0f}, 국가 {F_cl_C:,.0f}로 과대(공통 시계열 하나를 나라 수만큼 독립 관측으로 취급; Adão, Kolesár, Morales 2019 QJE 문제). "
          "기존 GACI 논문들은 국가 클러스터가 기본이었으므로 이 논문에서 무엇을 본 SE로 할지 결정 필요. 추천: HAC를 본 SE, 국가 클러스터는 [ ] 병기."),
    ("h2", "8. 오일렌트 통제"),
    ("p", "WDI 석유렌트/GDP의 1996~1998 평균(1996 단년 결측 보완). 이 통제가 있는 열은 결측국 제외(공통표본)."),
    ("h2", "9. 가중치"),
    ("p", f"무가중 본분석. 1996 좌석 가중 결과: OLS {rob('seat-weighted (1996)', 'OLS').b:.4f}, Känzig {rob('seat-weighted (1996)', '2SLS-KZ').b:.4f}{st(rob('seat-weighted (1996)', '2SLS-KZ').p)}, "
          f"BH {rob('seat-weighted (1996)', '2SLS-BH').b:.4f}."),
    ("h2", "10. 사건연구 설계"),
    ("p", "위치 = 사건 직전 기준연도 GACI(2022→2019, 2014→2013, 2008→2007), 공항×달력월 FE + 국가×월 FE. 2022는 2019 같은 달 대비 회복률과 국내선만도 추정. "
          "사건 구간 정의(급등 2022.3~12 등)는 월별 유가를 보고 제가 정함."),
    ("h2", "11. 극단값"),
    ("p", f"Δ12 절단 없음. |Δ12 ln seats|>1 절단 결과 OLS {rob('trim |D12| > 1', 'OLS').b:.4f}, Känzig {rob('trim |D12| > 1', '2SLS-KZ').b:.4f}{st(rob('trim |D12| > 1', '2SLS-KZ').p)}."),
    ("h2", "12. 국가 패널 권역"),
    ("p", "권역×연도 FE와 공항 권역×월 FE는 GACI 자료의 17개 권역 코드(EU1, AS4 등) 사용."),
]

DESIGN = [
    ("h1", "연구설계: 연료가격 충격과 네트워크 위치"),
    ("h2", "1. 질문과 두 가설"),
    ("p", "제트연료 가격이 오를 때 허브와 스포크의 운항(좌석·편수·좌석km·CO2)이 다르게 반응하는가. "
          "완충 가설: 허브는 대형기·높은 탑승률·연료 헤징 덕분에 덜 줄인다 → 아래 식의 b > 0. "
          "노출 가설: 허브는 장거리·국제선 비중이 커서 연료비 비중이 높고 더 줄인다 → b < 0. "
          "탄소가격은 연료가격 상승과 같은 방식으로 작동하므로(톤당 100달러 ≈ 갤런당 0.96달러), b는 탄소가격이 네트워크 위계를 바꾸는 방향을 알려준다."),
    ("h2", "2. 기본 식 (공통 충격 × 사전 노출, shift-share)"),
    ("p", "공항×월: Δ12 ln y_it = a_i + d_t + b (Δ12 ln P_(t−3) × H_i,1996) + e_it\n"
          "국가×연도: Δ ln y_ct = a_c + d_t + b (Δ ln P_t × H_c,1996) + e_ct\n"
          "d_t가 모든 공항에 공통인 가격 반응을 흡수하므로 평균 탄력성은 식별되지 않고 허브와 스포크의 차이(b)만 식별된다. "
          "a_i는 차분식에서 공항별 성장 추세를 흡수한다. H는 가격 상승기(2000년대) 이전인 1996년 값으로 고정."),
    ("h2", "3. 도구변수"),
    ("p", "유가는 세계 수요 호황(예: 2003~2008 중국)과 함께 움직이고 그 호황이 특정 허브에 치우칠 수 있다. 그래서 가격을 공급 측 충격으로 도구화한다: "
          "(a) Känzig(2021 AER) OPEC 발표 기반 석유 공급 뉴스 충격, (b) Baumeister-Hamilton(2019 AER) 구조 공급충격(부호 반전). "
          "도구 = 충격의 12개월 합(3개월 시차) × H_i. 위치 자체의 도구(ln air MA 1996)는 1단계가 약해 부록(A3)으로만."),
    ("h2", "4. 위협과 대응"),
    ("p", "① 허브의 다른 특성(규모·장거리·국제선·소득·산유국) → 각 특성 × 가격을 함께 넣는 경쟁회귀(T5). "
          "② 권역별 수요 충격이 유가와 상관 → 권역×월, 국가×월 FE(T8). "
          "③ 코로나 → 연속처치는 2019년까지, 2022년은 사건연구로 분리(T6). "
          "④ 공통 충격 하나라 유효 관측은 기간 수 → 국가 클러스터 + 시간 HAC(1단계 F도 같은 기준). "
          "⑤ 2022년 급등은 국제선 재개방과 겹침 → 국가×월 FE로 같은 나라 안 비교, 국제선 비중×월 통제, 국내선만, 2019 같은 달 대비 회복률, 월별 사전추세 확인. "
          "⑥ 대칭성: 2014년 급락을 반대 방향 실험으로, 가격 상승·하락 분리(T8 asymmetry)."),
    ("h2", "5. 자료"),
    ("p", "OAG 스케줄 기반 공항×월(1996.1~2024.6, Fangyu 8/18 전달분): 출발 편수·좌석·좌석km·단계별 CO2·국내/국제. GACI 공항 패널 1996~2024(위치). "
          "국가 패널 gaci_co2_panel(184개국). 유가: FRED MJFUELUSGULF(EIA 걸프코스트 제트연료), MCOILBRENTEU, CPIAUCSL. 충격: Känzig GitHub 2025M12판, "
          "Baumeister 홈페이지 BH 공급충격(2026M3까지). 오일렌트: WDI NY.GDP.PETR.RT.ZS."),
    ("h2", "6. 결과가 말하는 것 (현재)"),
    ("p", "위치에 따른 연료가격 반응 차이는 작고 사양에 따라 달라진다. OLS·BH는 0, Känzig는 허브 쪽 음(−)이나 고정효과를 촘촘히 하면 사라진다. "
          "2008·2014 사건에서도 차이가 없고, 2022년 허브 우위는 회복 추세와 구분되지 않는다. 현재 자료로는 '연료가격·탄소가격이 허브-스포크 위계를 크게 바꾼다'는 "
          "근거를 찾지 못했고, 반대로 차이의 크기에 대한 상한(공항 OLS 95% 구간 ±0.012/SD)은 제시할 수 있다."),
    ("h2", "7. 설계를 강화하려면 (다음 단계 후보)"),
    ("p", "A. 노선 단위 자료: Fangyu의 편 단위 자료(Origin/Destination 포함)로 노선×월 좌석을 만들면 같은 공항 안에서 노선 거리·환승/직항·허브 연결 여부별 "
          "비교가 가능(공항×월 FE). 연료비 비중이 거리에 따라 달라지는 점을 직접 이용하는 가장 강한 설계. "
          "B. 현지통화 연료가격: 달러 가격 × 환율로 나라마다 다른 연료비 변동을 만들면 공통 시계열 하나에 기대지 않는 식별이 가능(환율의 수요 효과는 통제 필요). "
          "C. 정책 실험: EU ETS 항공 편입(2012, 역내선)이나 CORSIA를 노선 자료와 결합한 탄소가격 DiD. "
          "D. 헤징·탑승률: 항공사 연차보고서 헤지 비율, 미국 T-100(탑승률)으로 완충 경로 직접 검정(미국 한정). "
          "우선순위 추천: A(자료 요청만 하면 됨) → C → B."),
]
