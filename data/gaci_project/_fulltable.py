# -*- coding: utf-8 -*-
def star(p):
    p=float(p)
    return '***' if p<.01 else '**' if p<.05 else '*' if p<.1 else ''
OUT=['g_int','g_vol','g_shr','lnpc','lngdp']
OL={'g_int':'openness','g_vol':'volume','g_shr':'share','lnpc':'GDPpc','lngdp':'GDP'}
DEC={'g_int':3,'g_vol':3,'g_shr':2,'lnpc':3,'lngdp':3}
comb={}
for ln in open('gaci_tourism_hetero_iv.log',encoding='utf-8',errors='replace'):
    if ln.startswith('HET3|'):
        q=ln.strip().split('|')
        if q[3] in ('main','inter'): comb[(q[1],q[2],q[3])]=(float(q[4]),float(q[5]),float(q[6]),q[7])
sep={}
for ln in open('gaci_natmix_overid.log',encoding='utf-8',errors='replace'):
    if ln.startswith('HNM|'):
        q=ln.strip().split('|')
        if len(q)>6 and q[3] in ('main','inter'): sep[(q[1],q[2],q[3])]=(float(q[4]),float(q[5]),float(q[6]),q[7])
def fmt(d,key):
    if key not in d: return '.'
    b,se,p,F=d[key]; dec=DEC[key[1]]
    return "%.*f%s (%.*f)"%(dec,b,star(p),dec,se)
for mod in ['income','baseconn']:
    for spec,d in [('COMBINED nat+mixed (1 instrument)',comb),('SEPARATE nat,mixed (over-ID)',sep)]:
        Fk=d.get((mod,'g_vol','main')); F=Fk[3] if Fk else '?'
        print("\n=== %s | %s | F=%s ==="%(mod.upper(),spec,F))
        print("%-22s"%""+"".join("%20s"%OL[o] for o in OUT))
        for term,lab in [('main','Connectivity(mean)'),('inter','x '+mod)]:
            print("%-22s"%lab+"".join("%20s"%fmt(d,(mod,o,term)) for o in OUT))
