# -*- coding: utf-8 -*-
"""README / decisions / menu text for the designs workbook (numbers from the result CSVs)."""
import pandas as pd
from _xlsx_text_designs_fixed import MENU, DECISIONS_BASE

rd = pd.read_csv("_res_designs.csv")
lf = pd.read_csv("_res_localfx.csv")
ts = pd.read_csv("_res_designs_ts.csv")

def st(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""

def g(df, **kw):
    m = df
    for k, v in kw.items():
        m = m[m[k] == v]
    return m.iloc[0]

def cs(x, d=4):
    return f"{x.b:.{d}f}{st(x.p)} (SE {x.se:.{d}f})"

d1 = lambda H, c, y="d12_ln_seats": g(rd, table="D1", panel=H, col=c, outcome=y, term="x")
d1j = lambda s, c, t, y="d12_ln_seats": g(rd, table="D1j", panel=s, col=c, outcome=y, term=t)
d2 = lambda H, l, y="d12_ln_seats": g(rd, table="D2", panel=H, outcome=y, label=l)
d3 = lambda H, c, l, y="d12_ln_seats": g(rd, table="D3", panel=H, col=c, outcome=y, label=l)
d45 = lambda H, c, l, y="d12_ln_seats": g(rd, table=("D4" if c.startswith("crude") else "D5"), panel=H, col=c, outcome=y, label=l)
L2 = lambda smp, H, y, t="x_q": g(lf, col=f"{smp}; exposure = {H}", outcome=y, term=t)
FS = "fuel burn per seat 1996 (z)"
ALL, EXC = "all countries", "excl. |D12 ln q| > 0.5"
KZ = "(c) Kaenzig news vs BH supply (RF, per 1 SD)"

README = [
    ("h1", "연료 충격 설계 다양화 (2026-09-29, 탐색 분석)"),
    ("p", "앞선 분석(세계 제트연료 가격 × 1996년 위치)을 세 방향으로 바꿔 돌렸습니다: 1) 누가 노출되는가(좌석당 연료소모·기단 효율·운항거리), "
          "2) 어떤 유가 변동인가(공급 vs 수요, 지속 vs 일시, 제트 고유, 비대칭·구간), 3) 나라마다 다른 연료비(실질환율로 만든 현지통화 가격). "
          "기본 사양은 T3와 같습니다. 먼저 '결정필요_표본정의'를 봐 주세요."),
    ("h2", "요약"),
    ("p", f"1) 연료비 노출(D1): 좌석당 연료소모 × 유가 OLS {cs(d1('z_fuelseat', 'OLS'))}, BH {cs(d1('z_fuelseat', '2SLS-BH'))}, Känzig {cs(d1('z_fuelseat', '2SLS-KZ'))}. "
          f"운항거리 × 유가 OLS {cs(d1('z_stage', 'OLS'))}. 방향은 연료 집약(장거리) 공항이 오히려 덜 줄이는 쪽이라 '노출 가설'과 반대. "
          f"국가×월 FE를 넣으면 {d1j('fuel/seat + GACI, country x month FE', 'OLS', 'x_z_fuelseat').b:.4f}(ns). 기단 효율(좌석km당 CO2)의 반응도 없음."),
    ("p", f"2) 공급 vs 수요(D2): 네 충격을 함께 넣으면 유의한 것은 세계 경기 충격뿐. GACI × 경기충격 {cs(d2('H_g', 'Economic activity (BH)'))}, "
          f"좌석당 연료 × 경기충격 {cs(d2('z_fuelseat', 'Economic activity (BH)'))}; 공급 충격은 {d2('H_g', 'Supply (BH, x -1)').b:.4f} / {d2('z_fuelseat', 'Supply (BH, x -1)').b:.4f}(ns). "
          "즉 유가와 허브·장거리 공항의 상대 성장이 함께 움직이는 것은 세계 경기 호황(유가와 장거리 수요를 같이 올림) 때문이고, 공급 주도 유가 상승에는 차등 반응이 없음. "
          "앞의 OLS가 0이나 양(+)으로 나온 이유를 설명함."),
    ("p", f"3) 지속 vs 일시(D3): 함께 넣으면 Känzig 뉴스충격 × GACI {cs(d3('H_g', KZ, 'Kaenzig news shock, 12-month sum (per SD)'))}, "
          f"BH 실현충격 {d3('H_g', KZ, 'BH supply shock x -1, 12-month sum (per SD)').b:.4f}(ns). 그러나 기대가격(12개월 후 WTI)으로 정의한 지속 성분은 "
          f"{d3('H_g', '(a) expected vs spot premium', 'D12 ln expected WTI, 12 months ahead (persistent)').b:.4f}(ns)이라 '지속 충격에만 반응' 가설은 한 가지 정의에서만 지지됨."),
    ("p", f"4) 제트 고유·비대칭·구간(D4~D5): 크랙스프레드 × GACI {d45('H_g', 'crude vs jet-specific', 'D12 ln crack spread x H').b:.4f}(p={d45('H_g', 'crude vs jet-specific', 'D12 ln crack spread x H').p:.2f}). "
          f"유가 하락기 × 좌석당 연료 {cs(d45('z_fuelseat', 'asymmetry', 'price falls x H'))}: 하락기에 연료 집약 공항이 덜 늘어남(하락기가 2001·2008~09 경기침체와 겹침). "
          f"고유가 구간 GACI × 유가 {d45('H_g', 'regime', 'D12 ln P x H, real jet > USD 2.5 (t-3)').b:.4f}(p={d45('H_g', 'regime', 'D12 ln P x H, real jet > USD 2.5 (t-3)').p:.2f})."),
    ("p", f"5) 현지통화 연료가격(L): 같은 나라·같은 달 안에서 실질환율 상승(현지 연료비 상승) 때 좌석당 연료가 큰 공항이 좌석을 더 줄이는가. "
          f"통화위기 구간 제외 시 전체 좌석 {cs(L2(EXC, FS, 'd12_ln_seats'))}, 국내선 {cs(L2(EXC, FS, 'd12_ln_seats_dom'))}, 국제선 {cs(L2(EXC, FS, 'd12_ln_seats_intl'))}. "
          f"전체 표본에서는 좌석 {L2(ALL, FS, 'd12_ln_seats').b:.4f}(ns), 국내선 {L2(ALL, FS, 'd12_ln_seats_dom').b:.4f}(ns), 국제선 {cs(L2(ALL, FS, 'd12_ln_seats_intl'))}. "
          "국내선 음(−)은 비용 경로, 국제선 양(+)은 통화 약세로 해외 방문 수요가 느는 경로로 읽힘. 통화위기 342개 국가-월 제외 여부에 결과가 달려 있음."),
    ("h2", "판단"),
    ("p", "가장 쓸모 있는 두 가지: (i) D2에서 유가와 허브 성장의 동조가 수요 주도임을 보였고, 공급 주도 유가 상승(탄소가격과 성격이 같은 비용 충격)에는 허브·장거리 차등이 없음. "
          "(ii) 현지통화 설계는 처음으로 '비용 경로'(연료 집약 공항의 국내선 감축)를 같은 나라 안 비교로 보여 줌. 단 통화위기 제외에 의존하므로 기준을 먼저 정해야 함. "
          "나머지(연료비 노출, 지속 충격, 비대칭)는 방향이 섞이거나 유의하지 않음."),
    ("h2", "시트 안내"),
    ("p", "설계메뉴(실행 여부) / D1 연료비 노출 / D2 공급 vs 수요 / D3 지속 vs 일시 / D4~D5 제트 고유·비대칭·구간 / L 현지통화 연료가격 / raw_*. "
          "스크립트: _prep_airport.py(공통 패널), 40_fuel_designs.py, 41_local_currency.py, 42_make_designs_xlsx.py."),
]
DECISIONS = DECISIONS_BASE
