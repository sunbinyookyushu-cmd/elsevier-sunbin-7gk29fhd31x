# -*- coding: utf-8 -*-
"""Extra figures for the conference deck: network schematic, formula cards
   (GACI construction, IV, counterfactual), real first-stage binscatter,
   OLS-vs-IV comparison, decomposition, and the hub-quality distribution."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman'],
                     'mathtext.fontset': 'stix'})
NAVY = '#1f4e79'; RED = '#b2182b'; INK = '#1f1f1f'; GREY = '#6f6f6f'
LBLUE = '#cfe0f1'


# ----------------------------------------------------------------------
# helper: formula card
# ----------------------------------------------------------------------
def formula_card(fname, title, lines, figsize=(11, 6.2)):
    """lines: list of (text, kind) where kind in {'head','math','note'}."""
    fig = plt.figure(figsize=figsize); fig.patch.set_facecolor('white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis('off')
    ax.add_patch(FancyBboxPatch((0.02, 0.02), 0.96, 0.96,
                 boxstyle='round,pad=0.01,rounding_size=0.02',
                 fc='white', ec=NAVY, lw=2, transform=ax.transAxes))
    ax.text(0.5, 0.90, title, ha='center', va='center', fontsize=22,
            color=NAVY, fontweight='bold', transform=ax.transAxes)
    y = 0.78
    for text, kind in lines:
        if kind == 'head':
            ax.text(0.07, y, text, ha='left', va='center', fontsize=16,
                    color=NAVY, fontweight='bold', transform=ax.transAxes)
            y -= 0.085
        elif kind == 'math':
            ax.text(0.5, y, text, ha='center', va='center', fontsize=20,
                    color=INK, transform=ax.transAxes)
            y -= 0.115
        else:
            ax.text(0.5, y, text, ha='center', va='center', fontsize=13,
                    color=GREY, style='italic', transform=ax.transAxes)
            y -= 0.08
    fig.savefig(fname, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig); print('wrote', fname)


# 1. five centrality indicators
formula_card('fig_eq_centrality.png',
    'Step 1: five airport-level centrality indicators',
    [('Built on the weighted airport network  G(V, E),  link weight $w_{ij}$ = passenger seat capacity', 'note'),
     ('Degree', 'head'),
     (r'$d_i=\sum_{j} a_{ij}$   (number of direct connections)', 'math'),
     ('Flow betweenness  (hub / transfer role)', 'head'),
     (r'$F_b(i)=\frac{1}{N_B}\sum_{j\neq g}\tau_{jg}(i)$,   resistance $\propto 1/\bar{w}_{ij}$,   $\bar{w}_{ij}=\sqrt{(s_i/d_i)(s_j/d_j)}$', 'math'),
     ('Closeness, Eigenvector, Regional importance', 'head'),
     (r'$C_c(i)=\frac{N-1}{\sum_j \mathrm{Dist}(i,j)}$,    $C_E(i)=\frac{1}{\lambda}\sum_j W_{ij}C_E(j)$,    $C_R(i)=\overline{w}_{ij}^{\,\mathrm{region}}$', 'math'),
    ])

# 2. PCA aggregation
formula_card('fig_eq_pca.png',
    'Step 2: combine into one index by PCA',
    [('Each indicator is standardised (comparable within year and across years)', 'note'),
     ('Composite index', 'head'),
     (r'$\mathrm{GACI}=[\,D,\;C_c,\;F_b,\;C_E,\;C_R\,]\;\omega$', 'math'),
     (r'$\omega=$ first principal component (direction of maximum variance)', 'math'),
     ('The first component explains 65--68% of total variance', 'note'),
     ('Result: an airport-level, time-comparable connectivity score', 'note'),
    ])

# 3. country aggregation
formula_card('fig_eq_country.png',
    'From airports to countries',
    [('Two national summaries of the airport-level GACI', 'note'),
     ('Hub quality  (capacity-weighted mean) -- headline', 'head'),
     (r'$\ln\mathrm{GACI}^{cwm}_{c}=\ln\!\left(\dfrac{\sum_{a\in c} cap_a\,\mathrm{GACI}_a}{\sum_{a\in c} cap_a}\right)$', 'math'),
     ('Total connectivity  (country sum)', 'head'),
     (r'$\ln\mathrm{GACI}^{sum}_{c}=\ln\!\left(\sum_{a\in c}\mathrm{GACI}_a\right)$', 'math'),
     ('Panel: 184 countries  x  1996--2023  =  4{,}643 country-years', 'note'),
    ])

# 4. IV / estimating equation
formula_card('fig_eq_iv.png',
    'Identification: two-way FE 2SLS',
    [('Structural equation  (outcome y = openness, volume, or GDP)', 'head'),
     (r'$y_{it}=\beta\,\ln\mathrm{GACI}_{it}+\gamma\,\ln pop_{it}+\alpha_i+\delta_t+\varepsilon_{it}$', 'math'),
     ('Shift-share instrument  =  global tourism shift  x  fixed heritage share', 'head'),
     (r'$z_{it}=\tilde{D}_t\;\times\;\ln\!\left(1+H_i^{\,nat+mix}\right)$', 'math'),
     (r'$\tilde{D}_t$ = world tourist arrivals (scaled);   $H_i$ = natural + mixed UNESCO sites', 'note'),
     (r'First stage strong:  Kleibergen--Paap $F=18.0$;   identity  $\ln g=\ln(g/Y)+\ln Y$', 'note'),
    ])

# 5. counterfactual
formula_card('fig_eq_counterfactual.png',
    'Counterfactual: turning $\\beta$ into dollars',
    [('Country-level implied trade gain from its 1996--2023 connectivity rise', 'head'),
     (r'$\Delta\mathrm{trade}_i=\mathrm{trade}_{i,2023}\,\left(1-e^{-\beta_{int}\,\Delta\ln\mathrm{GACI}_i}\right),\quad \beta_{int}=1.302$', 'math'),
     ('World aggregate and one-year shock', 'head'),
     (r'$\sum_i \Delta\mathrm{trade}_i\approx\$7.8\,\mathrm{T}$;    $\mathrm{loss}_i=\mathrm{trade}_{i,2019}\left(1-e^{\beta_{sum}\,\Delta\ln\mathrm{GACI}_i}\right)$', 'math'),
     (r'Delta-method SE:  $\mathrm{SE}=\left|\partial g/\partial\beta\right|\,\mathrm{SE}(\beta)$', 'note'),
    ])


# ----------------------------------------------------------------------
# 6. network schematic (illustrative)
# ----------------------------------------------------------------------
def network_schematic():
    rng_pts = {
        'HUB': (0.0, 0.0), 'A': (1.5, 0.6), 'B': (1.3, -0.8), 'C': (-1.4, 0.7),
        'D': (-1.5, -0.6), 'E': (0.2, 1.6), 'F': (0.4, -1.6), 'G': (2.3, 0.0),
        'H2': (-0.9, 1.4), 'I': (-2.2, 0.1), 'J': (1.0, 1.3), 'K': (-0.7, -1.5),
        'L': (2.0, -1.1), 'M': (-2.0, -1.2),
    }
    # links: (a,b,weight)
    links = [('HUB', k, w) for k, w in
             [('A', 5), ('B', 4), ('C', 5), ('D', 3), ('E', 4), ('F', 3),
              ('G', 5), ('H2', 2), ('I', 3), ('J', 2), ('K', 2), ('L', 3), ('M', 2)]]
    links += [('A', 'G', 2), ('A', 'J', 1.5), ('C', 'I', 2), ('C', 'H2', 1.5),
              ('D', 'M', 1.5), ('B', 'L', 1.5), ('B', 'F', 1)]
    deg = {n: 0 for n in rng_pts}
    for a, b, w in links:
        deg[a] += 1; deg[b] += 1
    fig, ax = plt.subplots(figsize=(11, 6.5)); fig.patch.set_facecolor('white')
    for a, b, w in links:
        xa, ya = rng_pts[a]; xb, yb = rng_pts[b]
        ax.plot([xa, xb], [ya, yb], color='#9bb7d4', lw=0.7 + w*0.7, alpha=0.8, zorder=1,
                solid_capstyle='round')
    for n, (x, y) in rng_pts.items():
        size = 220 + deg[n]*150
        col = RED if n == 'HUB' else NAVY
        ax.scatter([x], [y], s=size, color=col, edgecolor='white', lw=1.5, zorder=3)
    ax.annotate('global hub\n(high degree, betweenness,\neigenvector)', xy=(0, 0),
                xytext=(0.05, -2.25), ha='center', fontsize=13, color=RED,
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.4))
    ax.text(0.99, 0.02, 'line width $\\propto$ passenger seat capacity     node size $\\propto$ degree',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=12, color=GREY, style='italic')
    ax.set_xlim(-2.7, 2.9); ax.set_ylim(-2.6, 2.1); ax.axis('off')
    fig.savefig('fig_network_schematic.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig); print('wrote fig_network_schematic.png')
network_schematic()


# ----------------------------------------------------------------------
# 7. real first-stage binscatter (partial out two-way FE + lnpop)
# ----------------------------------------------------------------------
def first_stage_binscatter():
    p = pd.read_csv('gaci_panel_hetero.csv')
    for c in ['ln_gaci_cwm', 'tourism_int', 'lnpop']:
        p[c] = pd.to_numeric(p[c], errors='coerce')
    d = p.dropna(subset=['ln_gaci_cwm', 'tourism_int', 'lnpop']).copy()
    C = pd.get_dummies(d['c'], drop_first=True).astype(float).values
    Y = pd.get_dummies(d['y'], drop_first=True).astype(float).values
    W = np.column_stack([np.ones(len(d)), d['lnpop'].values, C, Y])
    Q, _ = np.linalg.qr(W)
    def resid(v): return v - Q @ (Q.T @ v)
    zx = resid(d['tourism_int'].values.astype(float))
    gy = resid(d['ln_gaci_cwm'].values.astype(float))
    dd = pd.DataFrame({'z': zx, 'g': gy})
    dd['bin'] = pd.qcut(dd['z'], 20, labels=False, duplicates='drop')
    b = dd.groupby('bin').mean()
    slope, intercept = np.polyfit(dd['z'], dd['g'], 1)
    fig, ax = plt.subplots(figsize=(9.5, 6.2)); fig.patch.set_facecolor('white')
    ax.scatter(b['z'], b['g'], s=55, color=NAVY, edgecolor='white', lw=0.8, zorder=3)
    xs = np.linspace(dd['z'].min(), dd['z'].max(), 100)
    ax.plot(xs, intercept + slope*xs, color=RED, lw=2.2, zorder=2,
            label=f'slope = {slope:.3f}  (KP $F=18.0$)')
    ax.axhline(0, color='#c8c8c8', lw=0.7); ax.axvline(0, color='#c8c8c8', lw=0.7)
    ax.set_xlabel('Tourism--heritage instrument (residualised)', fontsize=14, color=INK)
    ax.set_ylabel('Hub quality $\\ln\\mathrm{GACI}_{cwm}$ (residualised)', fontsize=14, color=INK)
    ax.legend(fontsize=14, frameon=False, loc='upper left')
    ax.grid(True, color='#ececec', lw=0.7); ax.set_axisbelow(True)
    ax.tick_params(labelsize=12, colors=INK)
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']: ax.spines[sp].set_color('#888888')
    fig.tight_layout(); fig.savefig('fig_firststage.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig); print('wrote fig_firststage.png  (binscatter slope %.3f)' % slope)
first_stage_binscatter()


# ----------------------------------------------------------------------
# 8. OLS vs IV coefficient comparison (hub quality panel)
# ----------------------------------------------------------------------
def ols_iv():
    out = ['Trade\nopenness', 'Trade\nvolume', 'GDP']
    ols = [0.157, 1.144, 0.987]
    iv  = [1.302, 2.303, 1.001]
    se  = [0.662, 0.776, 0.680]
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(9.5, 6.0)); fig.patch.set_facecolor('white')
    ax.axhline(0, color='#c0c0c0', lw=0.8)
    ax.scatter(x-0.12, ols, s=90, color=GREY, marker='s', zorder=3, label='OLS')
    ax.errorbar(x+0.12, iv, yerr=[1.96*s for s in se], fmt='o', ms=10, color=NAVY,
                ecolor=NAVY, elinewidth=1.6, capsize=6, capthick=1.6, zorder=3,
                label='2SLS (IV), 95% CI')
    for xi, v in zip(x-0.12, ols): ax.annotate(f'{v:.2f}', (xi, v), textcoords='offset points', xytext=(-18,0), va='center', fontsize=12, color=GREY)
    for xi, v in zip(x+0.12, iv):  ax.annotate(f'{v:.2f}', (xi, v), textcoords='offset points', xytext=(14,0), va='center', fontsize=12, color=NAVY)
    ax.set_xticks(x); ax.set_xticklabels(out, fontsize=13)
    ax.set_ylabel('Elasticity w.r.t. hub quality', fontsize=14, color=INK)
    ax.legend(fontsize=13, frameon=False, loc='upper left')
    ax.grid(True, axis='y', color='#ececec', lw=0.7); ax.set_axisbelow(True)
    ax.tick_params(labelsize=12, colors=INK); ax.set_xlim(-0.5, 2.5)
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']: ax.spines[sp].set_color('#888888')
    fig.tight_layout(); fig.savefig('fig_ols_iv.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig); print('wrote fig_ols_iv.png')
ols_iv()


# ----------------------------------------------------------------------
# 9. decomposition: volume = openness + GDP
# ----------------------------------------------------------------------
def decomposition():
    fig, ax = plt.subplots(figsize=(9.0, 5.6)); fig.patch.set_facecolor('white')
    ax.bar(0, 1.302, width=0.6, color=NAVY, label='Trade openness (intensity)')
    ax.bar(0, 1.001, width=0.6, bottom=1.302, color='#9ec3e6', label='GDP (scale)')
    ax.bar(1, 2.303, width=0.6, color=RED, label='Trade volume (total)')
    ax.text(0, 1.302/2, 'openness\n1.30', ha='center', va='center', fontsize=13, color='white')
    ax.text(0, 1.302+1.001/2, 'GDP\n1.00', ha='center', va='center', fontsize=13, color=INK)
    ax.text(1, 2.303/2, 'volume\n2.30', ha='center', va='center', fontsize=13, color='white')
    ax.text(0.5, 2.45, '2.30  =  1.30  +  1.00', ha='center', fontsize=16, color=INK, fontweight='bold')
    ax.set_xticks([0, 1]); ax.set_xticklabels(['openness + GDP', 'volume'], fontsize=13)
    ax.set_ylabel('Elasticity w.r.t. hub quality', fontsize=14, color=INK)
    ax.set_ylim(0, 2.75); ax.tick_params(labelsize=12, colors=INK)
    ax.grid(True, axis='y', color='#ececec', lw=0.7); ax.set_axisbelow(True)
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']: ax.spines[sp].set_color('#888888')
    fig.tight_layout(); fig.savefig('fig_decomposition.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig); print('wrote fig_decomposition.png')
decomposition()


# ----------------------------------------------------------------------
# 10. distribution of country hub quality, 2023 (real, skew)
# ----------------------------------------------------------------------
def gaci_dist():
    p = pd.read_csv('gaci_panel.csv')
    v = pd.to_numeric(p[p.y == 2023]['ln_gaci_cwm'], errors='coerce').dropna()
    fig, ax = plt.subplots(figsize=(9.5, 5.6)); fig.patch.set_facecolor('white')
    ax.hist(v, bins=30, color=NAVY, edgecolor='white', lw=0.5)
    ax.set_xlabel('Country hub quality $\\ln\\mathrm{GACI}_{cwm}$, 2023', fontsize=14, color=INK)
    ax.set_ylabel('Number of countries', fontsize=14, color=INK)
    ax.tick_params(labelsize=12, colors=INK)
    ax.grid(True, axis='y', color='#ececec', lw=0.7); ax.set_axisbelow(True)
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']: ax.spines[sp].set_color('#888888')
    fig.tight_layout(); fig.savefig('fig_gaci_dist.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig); print('wrote fig_gaci_dist.png')
gaci_dist()

# ----------------------------------------------------------------------
# 11. build pipeline diagram
# ----------------------------------------------------------------------
def pipeline():
    steps = ['Airline\nschedules\n1996–2023',
             'Weighted\nairport\nnetwork',
             'Five\ncentrality\nindicators',
             'PCA\n(first\ncomponent)',
             'Airport GACI\n(standardised)',
             'Country panel\n(cwm, sum)']
    fig, ax = plt.subplots(figsize=(13.6, 3.1)); fig.patch.set_facecolor('white')
    n = len(steps); bw, bh, gap = 1.05, 0.70, 0.26
    x = 0.0
    centers = []
    for i, st in enumerate(steps):
        col = RED if i == 0 else (NAVY if i < n-1 else '#2f6f3e')
        ax.add_patch(FancyBboxPatch((x, 0), bw, bh,
                     boxstyle='round,pad=0.02,rounding_size=0.08',
                     fc=col, ec='none'))
        ax.text(x+bw/2, bh/2, st, ha='center', va='center', color='white',
                fontsize=11, fontweight='bold')
        centers.append(x+bw/2)
        if i < n-1:
            ax.annotate('', xy=(x+bw+gap, bh/2), xytext=(x+bw, bh/2),
                        arrowprops=dict(arrowstyle='-|>', color='#555555', lw=2))
        x += bw + gap
    ax.text(centers[2], -0.32, 'BUILD THE INDEX  (this paper’s data contribution)',
            ha='center', fontsize=12, color=NAVY, style='italic')
    ax.text(centers[5], -0.32, 'USE FOR TRADE', ha='center', fontsize=12,
            color='#2f6f3e', style='italic')
    ax.set_xlim(-0.15, x); ax.set_ylim(-0.55, bh+0.15); ax.axis('off')
    fig.savefig('fig_pipeline.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig); print('wrote fig_pipeline.png')
pipeline()


# ----------------------------------------------------------------------
# 12. network coverage growth 1996-2023 (real)
# ----------------------------------------------------------------------
def coverage():
    p = pd.read_csv('gaci_panel.csv')
    p['n_air'] = pd.to_numeric(p['n_air'], errors='coerce')
    g = p.groupby('y')['n_air'].sum()
    g = g[(g.index >= 1996) & (g.index <= 2023)]
    fig, ax = plt.subplots(figsize=(10.5, 5.4)); fig.patch.set_facecolor('white')
    ax.fill_between(g.index, g.values, color=NAVY, alpha=0.12)
    ax.plot(g.index, g.values, color=NAVY, lw=2.4, marker='o', ms=5)
    ax.annotate('COVID-19', xy=(2020, g.loc[2020]), xytext=(2012.5, g.loc[2020]-380),
                fontsize=12, color=RED,
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.3))
    ax.set_xlabel('Year', fontsize=14, color=INK)
    ax.set_ylabel('Airports with scheduled service (network nodes)', fontsize=13.5, color=INK)
    ax.set_xlim(1996, 2023); ax.tick_params(labelsize=12, colors=INK)
    ax.grid(True, color='#ececec', lw=0.7); ax.set_axisbelow(True)
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']: ax.spines[sp].set_color('#888888')
    fig.tight_layout(); fig.savefig('fig_coverage.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig); print('wrote fig_coverage.png')
coverage()


# ----------------------------------------------------------------------
# 13. flow-betweenness electrical analogy (self-made, after Cheung Fig 1 idea)
# ----------------------------------------------------------------------
def flow_betweenness():
    fig, ax = plt.subplots(figsize=(11, 5.4)); fig.patch.set_facecolor('white')
    P = {'LHR': (0.0, 0.0), 'HKG': (3.0, 0.0), 'PER': (6.0, 0.0),
         'SIN': (3.0, -1.8), 'DXB': (3.0, 1.7)}
    # edges: (a,b,intensity) -- thicker = higher passenger intensity (lower resistance)
    edges = [('LHR', 'HKG', 5), ('HKG', 'PER', 5),
             ('LHR', 'DXB', 2.4), ('DXB', 'PER', 2.4),
             ('LHR', 'SIN', 1.6), ('SIN', 'PER', 1.6)]
    for a, b, w in edges:
        xa, ya = P[a]; xb, yb = P[b]
        ax.plot([xa, xb], [ya, yb], color='#9bb7d4', lw=1.0 + w*1.1, alpha=0.9,
                solid_capstyle='round', zorder=1)
    for n, (x, y) in P.items():
        col = RED if n == 'HKG' else NAVY
        ax.scatter([x], [y], s=2200, color=col, edgecolor='white', lw=2, zorder=3)
        ax.text(x, y, n, ha='center', va='center', color='white', fontsize=15,
                fontweight='bold', zorder=4)
    ax.text(3.0, -3.05, 'most passenger "current" flows through HKG  (high flow betweenness)',
            ha='center', va='center', fontsize=13, color=RED)
    ax.text(0.5, 0.97, 'Network as an electrical circuit:  resistance $\\propto 1/$passenger intensity',
            transform=ax.transAxes, ha='center', va='top', fontsize=14, color=INK)
    ax.text(0.5, 0.06, 'line width $\\propto$ passenger intensity (thicker = lower resistance)',
            transform=ax.transAxes, ha='center', fontsize=12, color=GREY, style='italic')
    ax.set_xlim(-1.2, 7.2); ax.set_ylim(-3.6, 2.7); ax.axis('off')
    fig.savefig('fig_flowbetween.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig); print('wrote fig_flowbetween.png')
flow_betweenness()


# ----------------------------------------------------------------------
# 14. PCA loadings + variance explained (real, our 5 indicators)
# ----------------------------------------------------------------------
def pca_loadings():
    p = pd.read_csv('gaci_panel.csv')
    cols = ['deg_mean', 'close_mean', 'betw_mean', 'eig_mean', 'regimp_mean']
    lab = ['Degree', 'Closeness', 'Flow\nbetweenness', 'Eigenvector', 'Regional\nimportance']
    d = p[cols].apply(pd.to_numeric, errors='coerce').dropna()
    X = (d - d.mean()) / d.std()
    w, V = np.linalg.eigh(np.cov(X.values.T))
    idx = np.argsort(w)[::-1]; w = w[idx]; V = V[:, idx]
    pc1 = V[:, 0]
    if pc1.sum() < 0: pc1 = -pc1
    ve = 100 * w[0] / w.sum()
    fig, ax = plt.subplots(figsize=(9.6, 5.4)); fig.patch.set_facecolor('white')
    ax.bar(range(5), pc1, width=0.62, color=NAVY, edgecolor='white')
    for i, v in enumerate(pc1):
        ax.text(i, v + 0.012, f'{v:.2f}', ha='center', fontsize=13, color=INK)
    ax.set_xticks(range(5)); ax.set_xticklabels(lab, fontsize=12.5)
    ax.set_ylabel('Loading on first principal component', fontsize=14, color=INK)
    ax.set_ylim(0, 0.58)
    ax.text(0.5, 0.93, f'PC1 explains {ve:.0f}% of variance   (all five load positively and similarly)',
            transform=ax.transAxes, ha='center', fontsize=13.5, color=NAVY, fontweight='bold')
    ax.tick_params(labelsize=12, colors=INK)
    ax.grid(True, axis='y', color='#ececec', lw=0.7); ax.set_axisbelow(True)
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']: ax.spines[sp].set_color('#888888')
    fig.tight_layout(); fig.savefig('fig_pca_loadings.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig); print('wrote fig_pca_loadings.png  (PC1 %.0f%%)' % ve)
pca_loadings()


print('ALL METHOD FIGS DONE')
