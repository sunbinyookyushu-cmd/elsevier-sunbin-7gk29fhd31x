# -*- coding: utf-8 -*-
"""README text for the resilience workbook; numbers read from the result CSVs."""
import pandas as pd
from _xlsx_text_resil_fixed import DECISIONS as _D, DESIGN

rs = pd.read_csv("_res_resil.csv")
rv = pd.read_csv("_res_resil_valid.csv")
rb = pd.read_csv("_res_resil_events_rob.csv")
sh = pd.read_csv("_res_resil_shrink.csv")
rep = pd.read_csv("_res_resil_replication.csv")
iu = pd.read_csv("_res_resil_invU.csv")
Rx = pd.read_csv("resilience_airport.csv")

def st(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""

def g(df, **kw):
    m = df
    for k, v in kw.items():
        m = m[m[k] == v]
    return m.iloc[0]

def cs(x, d=4):
    return f"{x.b:.{d}f}{st(x.p)} (SE {x.se:.{d}f})"

A = g(rep, group="All")
Hb = g(rep, group="Hub")
pk = g(rep, group="Peak (GACI)")
m = lambda v, c: g(rs, table="RS1", panel=v, outcome="d12_ln_seats", col=c, term="x")
b_sp_nog = g(rb, check="baseline", outcome="rec", gaci_control=False, term="spike")
b_sp = g(rb, check="baseline", outcome="rec", gaci_control=True, term="spike")
b_af = g(rb, check="baseline", outcome="rec", gaci_control=True, term="after")
c_sp = g(rb, check="excl. mainland China", outcome="rec", gaci_control=True, term="spike")
c_af = g(rb, check="excl. mainland China", outcome="rec", gaci_control=True, term="after")
plc = g(rb, check="placebo: 2021-07..12 vs 2021-01..06 (pre-period only)", outcome="rec", term="placebo")
dom = g(rb, check="excl. mainland China", outcome="rec_dom", gaci_control=True, term="spike")
raw = g(sh, moderator="raw R (no shrinkage)", term="spike")
n3 = g(sh, moderator="raw R + n_valid dummies x period", term="n3 x spike")
v_gfc = g(rv, resilience="R_pre2008", outcome="depth_GFC+H1N1", control="none")
v_cov = g(rv, resilience="R_pre2008", outcome="depth_COVID", control="none")
v_cov2 = g(rv, resilience="R_pre2008", outcome="depth_COVID", control="ln GACI at build end")
c = Rx[Rx.R_full.notna()]
corr_sh = c.R_full.corr(c.n_valid_full)
corr_raw = c.R_raw_full.corr(c.n_valid_full)
share_sh = (c.n_valid_full < 3).mean()
iu_raw = g(iu, outcome="R_raw_full", n_valid_dummies=False)
iu_ctl = g(iu, outcome="R_full", n_valid_dummies=True)
iu_ad = g(iu, outcome="adapt_full", n_valid_dummies=False)
iu_dp = g(iu, outcome="depth_full", n_valid_dummies=False)

README = [
    ("h1", "레질리언스 × 제트연료 가격 충격 (2026-09-29, 탐색 분석)"),
    ("p", "Zhang, Cheung & Zhang (2027, TR-E 217, 105192)의 공항 레질리언스 지수(깊이·속도·적응력, 위기 8개, 경험적 베이즈 축소)를 우리 GACI 패널로 다시 만들고, "
          "'레질리언스가 높은 공항은 연료가격 충격을 잘 견디는가'를 검정했습니다. 먼저 '결정필요_표본정의' 시트를 봐 주세요."),
    ("h2", "요약"),
    ("p", f"1) 지수 제작과 재현: 공항 {int(A.N):,}개(논문 {int(A.N_paper):,}), 평균 {A['mean']:.3f}(논문 {A.mean_paper:.3f}), 허브 {Hb['mean']:.3f}(논문 {Hb.mean_paper:.3f}). "
          f"GACI 2024에 대한 역U 정점 {pk['mean']:.2f}(SE {pk.sd:.2f}), 논문 1.85. 핵심 성질은 재현됨(R1)."),
    ("p", f"2) 연속 유가 검정(R2): 레질리언스가 높을수록 유가 상승기에 좌석을 덜 줄이는 방향이지만 작고 유의하지 않음. 1996~2007 자료로 만든 판(2008~2019 검정) "
          f"OLS {cs(m('pre2008', 'OLS'))}, BH {cs(m('pre2008', '2SLS-BH'))}, Känzig {cs(m('pre2008', '2SLS-KZ'))}. 1996~2003판·실시간판·논문판도 같은 양상(0.002~0.011, 모두 p>0.1). "
          "GACI·규모·국제선·운항거리 통제와 국가×월 FE를 넣으면 0 또는 음수(R3). 구성요소별로도 없음(R4)."),
    ("p", f"3) 2022년 급등(R5, R6): 코로나 이전 레질리언스가 1 SD 높은 공항은 2019년 같은 달 대비 좌석이 급등기에 {b_sp_nog.b:.3f}{st(b_sp_nog.p)} 더 많았고, "
          f"GACI×기간 통제 시 급등기 {b_sp.b:.3f}{st(b_sp.p)}, 이후 {b_af.b:.3f}(ns). 중국 제외 {c_sp.b:.3f}{st(c_sp.p)} / {c_af.b:.3f}, 사전기간 위약 {plc.b:.3f}(ns). "
          "월별 계수는 사전기간 평평, 2022년 4~10월 +0.02~0.03, 2023년에 소멸해서 유가 경로와 같은 모양(Fig in R6). 국내선만 보면 "
          f"{dom.b:.3f}(ns)."),
    ("p", f"4) 그러나 2022년 결과는 레질리언스 성과가 아니라 '겪은 위기 수'에서 나옴: 경험적 베이즈 축소 때문에 합성지수와 유효 위기 수의 상관이 높고(논문판 {corr_sh:.2f}, "
          f"축소 전 {corr_raw:.2f}; 공항의 {share_sh:.0%}가 축소 대상), 축소 전 지수로는 급등기 {raw.b:.4f}(p={raw.p:.2f}). 대신 유효 위기 3개 이상 더미 × 급등기 "
          f"{n3.b:.3f}{st(n3.p)}. 즉 1990년대부터 계속 운항하며 여러 위기를 겪은 오래된 공항이 2022년에 좌석을 더 지켰다는 결과에 가까움(R6 Panel B)."),
    ("p", f"5) 예측 타당도(R4 Panel C): 1996~2007 레질리언스가 높은 공항은 이후 금융위기에서 오히려 더 깊이 하락({v_gfc.b:.4f}{st(v_gfc.p)}), 코로나 깊이 {v_cov.b:.4f}{st(v_cov.p)}"
          f"(GACI 통제 시 {v_cov2.b:.4f}, ns). 과거 레질리언스가 다음 위기로 이어지지 않음(평균 회귀)."),
    ("p", f"6) 지수 자체에 대해 알게 된 점(R7): 역U는 축소 전 지수(정점 {iu_raw.peak:.2f})와 위기 수 통제(정점 {iu_ctl.peak:.2f})에서도 유지되지만, 구성요소로 보면 "
          f"적응력(순위 백분위 추세·상향폭, 정점 {iu_ad.peak:.2f})에서 나오고 깊이는 GACI가 클수록 단조 감소(1차 계수 {iu_dp.a1:.3f}). "
          "최상위 허브는 순위를 더 올릴 여지가 없어 적응력이 구조적으로 낮게 나올 수 있음. 저자에 Tommy Cheung이 있으므로 이 점은 비판이 아니라 지수의 특성으로만 기록."),
    ("h2", "판단"),
    ("p", "'레질리언스가 높으면 연료 충격에 잘 대비한다'는 현재 증거로는 지지되지 않음. 연속 검정은 방향만 맞고 유의하지 않으며, 유일하게 유의한 2022년 결과는 레질리언스가 "
          "아니라 공항의 운항 이력(겪은 위기 수)으로 설명됨. 이 이력 효과 자체(오래된 공항이 급등기에 좌석을 지킴)는 월별 패턴이 깨끗해서 별도로 볼 가치가 있음."),
    ("h2", "시트 안내"),
    ("p", "R1 재현검증 / R2 본분석(네 판) / R3 위치와 경쟁 / R4 구성요소·예측력 / R5 2022 급등 / R6 2022 강건성·축소 검정(+월별 그림) / R7 역U 분해 / "
          "Fig 레질리언스-GACI 산점도 / 레질리언스_지수값(공항별 네 판, 다른 분석에 바로 사용 가능) / raw_*."),
]

DECISIONS = _D + [
    ("h2", "7. 경험적 베이즈 축소를 쓸지 (새로 확인된 문제)"),
    ("p", f"논문 방식의 축소(유효 위기 1~2개면 0.5 쪽으로)는 공항의 {share_sh:.0%}에 적용되고, 그 결과 지수가 유효 위기 수와 {corr_sh:.2f} 상관(축소 전 {corr_raw:.2f}). "
          "조절변수로 쓰면 '레질리언스'와 '운항 이력'이 섞임. 선택지: (a) 논문 정의 유지 + 위기 수 통제, (b) 축소 전 지수 사용, (c) 유효 위기 3개 이상 공항만 사용. 추천: (b)와 (c)를 본분석, 논문 정의는 비교."),
]
