# -*- coding: utf-8 -*-
"""README text for the HSR oil-hedge workbook (numbers from the result CSVs)."""
import pandas as pd
from _xlsx_text_hsr_fixed import DECISIONS, SOURCES

lev = pd.read_csv("_res_hsr_level.csv")
es = pd.read_csv("_res_hsr_es.csv")
hed = pd.read_csv("_res_hsr_hedge.csv")
cov = pd.read_csv("data/station_date_coverage.csv").set_index("cc")
aph = pd.read_csv("data/airport_hsr.csv", parse_dates=["hsr_date_50"])


def st(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def L(o, smp="all", R=50):
    x = lev[(lev.outcome == o) & (lev["sample"] == smp) & (lev.radius == R)].iloc[0]
    return f"{x.b:.3f}{st(x.p_country)}"


def Hh(o, smp, e, R=50):
    x = hed[(hed.outcome == o) & (hed["sample"] == smp) & (hed.estimator == e) & (hed.radius == R)].iloc[0]
    return f"{x.b:.3f}{st(x.p)} (SE {x.se:.3f})"


E = lambda o, k: es[(es.outcome == o) & (es.rel_year == k)].iloc[0]
n_tr = int(((aph.hsr_date_50.dt.year >= 1997) & (aph.hsr_date_50.dt.year <= 2019)).sum())
pct = lambda b: 100 * (2.718281828 ** b - 1)
bdom = lev[(lev.outcome == "ln_seats_dom") & (lev["sample"] == "all") & (lev.radius == 50)].b.iloc[0]
bco2 = lev[(lev.outcome == "ln_co2") & (lev["sample"] == "all") & (lev.radius == 50)].b.iloc[0]

README = [
    ("h1", "고속철은 석유 충격의 보험인가: 전 세계 공항×월 분석 (2026-09-29, 탐색 분석)"),
    ("p", "전 세계 고속철역 개통 패널을 OSM + UIC + 일본 국토교통성 자료로 새로 만들고(위키백과 미사용), 공항 반경 안에 고속철역이 생긴 뒤 "
          "(1) 항공 좌석·CO2가 얼마나 줄고 (2) 유가 충격에 대한 민감도가 커지는지를 추정했습니다. 먼저 '결정필요_표본정의'를 봐 주세요."),
    ("h2", "요약"),
    ("p", f"1) 자료: 22개국 + 중국의 고속철 선로·역, 역 개통일 채움률 대만 {cov.share_dated.get('TW', 0):.0%}·한국 {cov.share_dated.get('KR', 0):.0%}·"
          f"일본 {cov.share_dated.get('JP', 0):.0%}·프랑스 {cov.share_dated.get('FR', 0):.0%}·중국 {cov.share_dated.get('CN', 0):.0%}. "
          f"중국 누적 연장은 UIC 공식치의 0.90~1.00. 공항 50km 안에 1997~2019년 고속철역이 생긴 공항 {n_tr}개."),
    ("p", f"2) 대체 효과(견고): 고속철역이 50km 안에 생기면 국내선 좌석 {L('ln_seats_dom')}(약 {pct(bdom):.0f}%), 전체 좌석 {L('ln_seats')}, "
          f"공항 CO2 {L('ln_co2')}(약 {pct(bco2):.0f}%). 중국 {L('ln_seats_dom', 'China')}, 중국 제외 {L('ln_seats_dom', 'excl. China')}, "
          f"자료 품질 표본 {L('ln_seats_dom', 'high-quality dates (CN JP KR TW FR)')}. 반경별 30km {L('ln_seats_dom', R=30)}, 100km {L('ln_seats_dom', R=100)}로 "
          "가까울수록 큼. 중국 공항은 국제선이 늘어(" + L('ln_seats_intl', 'China') + ") 국내선 자리를 국제선이 채움."),
    ("p", f"3) 사건연구: 국내선 좌석은 개통 전 6년 동안 평평(사전추세 없음), 개통 후 1년 {E('ln_seats_dom', 1).b:.3f}, 6년 {E('ln_seats_dom', 6).b:.3f}로 점점 커짐. "
          f"CO2는 개통 3~2년 전에 이미 {E('ln_co2', -3).b:.3f}·{E('ln_co2', -2).b:.3f}로 약간 줄기 시작(사전추세 주의), 개통 후 1년 {E('ln_co2', 1).b:.3f}, "
          f"4년 {E('ln_co2', 4).b:.3f}."),
    ("p", f"4) 석유 헤지(원래 가설)는 확인되지 않음: 고속철 개통 뒤 국내선 좌석의 유가 민감도 변화 = OLS {Hh('d12_ln_seats_dom', 'all', 'OLS')}, "
          f"2SLS(BH) {Hh('d12_ln_seats_dom', 'all', '2SLS-BH')}, 2SLS(Känzig) {Hh('d12_ln_seats_dom', 'all', '2SLS-KZ')}. 중국 "
          f"{Hh('d12_ln_seats_dom', 'China', 'OLS')}, 자료 품질 표본 {Hh('d12_ln_seats_dom', 'high-quality dates (CN JP KR TW FR)', 'OLS')}, 반경 30·100km도 0 부근. "
          "Känzig 2SLS는 일관되게 음(−)이지만 유의하지 않음."),
    ("h2", "판단"),
    ("p", "견고한 것은 '고속철이 전 세계 공항의 국내선 좌석과 CO2를 줄인다'는 대체·탈탄소 효과이고, '고속철이 석유 충격을 흡수하는 보험'이라는 가설은 "
          "현재 자료로 지지되지 않음. 에너지 저널용으로는 선생님 Energy Economics 논문(고속철의 부문별 탈탄소)의 글로벌 항공 확장, 즉 "
          "'Global evidence that HSR decarbonizes aviation' 쪽이 현실적. 전 세계 고속철역 개통 패널 자체도 공개 자료로서 기여."),
    ("h2", "시트 안내"),
    ("p", "결정필요_표본정의 / 자료출처 / H1 자료 검증(나라별 채움률·공식 연장 대비·UIC-OSM 일치) / H2 처치 공항 목록 / H3 수준 효과(좌석·CO2) / "
          "H4 사건연구(네이티브 차트) / H5 석유 헤지 / raw_*. 스크립트: 01~06, 05a(수준), 05b(헤지), 07(이 엑셀)."),
]
