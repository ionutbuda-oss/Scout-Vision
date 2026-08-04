from __future__ import annotations
import base64, html, math, re, unicodedata
from typing import Any
import pandas as pd
from .model_source import ROLE_MODELS

class CardDataError(RuntimeError): pass

def safe_filename(value: object) -> str:
    s=unicodedata.normalize('NFKD',str(value)).encode('ascii','ignore').decode('ascii')
    return re.sub(r'[^A-Za-z0-9]+','_',s).strip('_').lower() or 'unknown'

def clean_text(value: object, default='N/A') -> str:
    if value is None or pd.isna(value): return default
    s=str(value).strip()
    return default if not s or s.lower() in {'nan','none','<na>'} else s

def number(value: object, default=0.0) -> float:
    x=pd.to_numeric(pd.Series([value]),errors='coerce').iloc[0]
    return float(default if pd.isna(x) else x)

def integer(value: object, default=0) -> int: return int(round(number(value,default)))

def format_metric(metric: str, value: object) -> str:
    x=pd.to_numeric(pd.Series([value]),errors='coerce').iloc[0]
    if pd.isna(x): return 'N/A'
    x=float(x)
    if '%' in metric: return f'{x:.1f}%'
    if 'per 90' in metric.lower(): return f'{x:.2f}'
    return f'{x:.2f}'

def score_label(s: float) -> str:
    return 'ELITE' if s>=85 else 'VERY GOOD' if s>=75 else 'GOOD' if s>=65 else 'AVERAGE' if s>=55 else 'DEVELOPMENT'

def score_tone(s: float) -> str:
    return 'blue' if s>=75 else 'cyan' if s>=65 else 'amber' if s>=55 else 'red'

def display_metric_name(metric: str) -> str:
    return {
      'Accurate progressive passes, %':'Accurate progressive passes',
      'Accurate passes to final third, %':'Accurate final-third passes',
      'Accurate forward passes, %':'Accurate forward passes',
      'Accurate smart passes, %':'Accurate smart passes',
      'Accurate through passes, %':'Accurate through passes',
      'Successful dribbles, %':'Successful dribbles',
      'Defensive duels won, %':'Defensive duels won',
      'Offensive duels won, %':'Offensive duels won',
      'Accurate crosses, %':'Accurate crosses',
      'Goal conversion, %':'Goal conversion',
    }.get(metric,metric)

def _lines(label:str):
    words=label.split()
    if len(label)<=15 or len(words)==1:return [label]
    m=max(1,len(words)//2);return [' '.join(words[:m]),' '.join(words[m:])]

def radar_svg_data_uri(comps:list[dict[str,Any]])->str:
    W,H,cx,cy,R,LR=500,440,250,220,126,158
    n=len(comps); ang=[-math.pi/2+2*math.pi*i/n for i in range(n)]
    def p(a,s):return cx+math.cos(a)*R*s,cy+math.sin(a)*R*s
    grids=[]
    for level in (.25,.5,.75,1):
        pts=' '.join(f'{x:.1f},{y:.1f}' for x,y in [p(a,level) for a in ang])
        grids.append(f'<polygon points="{pts}" fill="none" stroke="#27415f" stroke-width="1"/>')
    axes=''.join(f'<line x1="{cx}" y1="{cy}" x2="{p(a,1)[0]:.1f}" y2="{p(a,1)[1]:.1f}" stroke="#223c59"/>' for a in ang)
    scored=[p(a,c['score']/100) for a,c in zip(ang,comps)]
    poly=' '.join(f'{x:.1f},{y:.1f}' for x,y in scored)
    nodes=''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#2f80ff" stroke="#84b7ff" stroke-width="2"/>' for x,y in scored)
    labels=[]
    for a,c in zip(ang,comps):
        lx,ly=cx+math.cos(a)*LR,cy+math.sin(a)*LR
        anchor='start' if math.cos(a)>.3 else 'end' if math.cos(a)<-.3 else 'middle'
        lines=_lines(c['name']); y0=ly-(7 if len(lines)==2 else 0)
        tsp=''.join(f'<tspan x="{lx:.1f}" dy="{0 if i==0 else 16}">{html.escape(t)}</tspan>' for i,t in enumerate(lines))
        sy=y0+(27 if len(lines)==2 else 19)
        labels.append(f'<text x="{lx:.1f}" y="{y0:.1f}" text-anchor="{anchor}" fill="#eef6ff" font-family="Arial" font-size="13" font-weight="600">{tsp}</text><text x="{lx:.1f}" y="{sy:.1f}" text-anchor="{anchor}" fill="#55a3ff" font-family="Arial" font-size="14" font-weight="800">{c["score_display"]}</text>')
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs><linearGradient id="a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2388ff" stop-opacity=".42"/><stop offset="1" stop-color="#123b77" stop-opacity=".28"/></linearGradient></defs>{''.join(grids)}{axes}<polygon points="{poly}" fill="url(#a)" stroke="#2f80ff" stroke-width="3"/>{nodes}{''.join(labels)}</svg>'''
    return 'data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode()

def build_card_context(row:pd.Series,*,competition_name:str)->dict[str,Any]:
    required={'Player','Team','Position','Position Group','Age','Matches played','Performance Score','Recruitment Score'}
    miss=sorted(required.difference(row.index))
    if miss:raise CardDataError('Missing required columns: '+', '.join(miss))
    group=clean_text(row['Position Group'])
    if group not in ROLE_MODELS:raise CardDataError(f'No model for {group}')
    comps=[]; kpis=[]
    for name,cfg in ROLE_MODELS[group].items():
        col=f'{name} Score'
        if col not in row.index:raise CardDataError(f'Missing {col}; regenerate rankings after terminology changes.')
        s=number(row[col]); comps.append({'name':name,'score':round(s,2),'score_display':f'{s:.0f}'})
        metrics=[]
        for metric,w in cfg['metrics'].items():
            if metric not in row.index:raise CardDataError(f'Missing real KPI: {metric}')
            metrics.append({'source_name':metric,'name':display_metric_name(metric),'value':format_metric(metric,row[metric]),'weight':f'{float(w)*100:.0f}%'})
        kpis.append({'name':name,'weight':f'{float(cfg["weight"])*100:.0f}%','metrics':metrics})
    recruitment=number(row['Recruitment Score']); performance=number(row['Performance Score'])
    ctx={'player':{'name':clean_text(row['Player']),'team':clean_text(row['Team']),'position':clean_text(row['Position']),'position_group':group,'competition':competition_name,'age':integer(row['Age']),'foot':clean_text(row.get('Foot')).title(),'minutes':f'{integer(row.get("Minutes played")):,}' if integer(row.get('Minutes played'))>0 else 'N/A','matches':integer(row['Matches played'])},'score':{'value':recruitment,'display':f'{recruitment:.1f}','performance':f'{performance:.1f}','label':score_label(recruitment),'tone':score_tone(recruitment)},'competencies':comps,'kpi_groups':kpis,'strength':max(comps,key=lambda x:x['score']),'development':min(comps,key=lambda x:x['score'])}
    ctx['radar_uri']=radar_svg_data_uri(comps);return ctx
