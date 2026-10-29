#!/usr/bin/env python3
"""Plot only numeric measurements from executed, successful physical experiments."""
import argparse,json
from pathlib import Path
from common import new_run
p=argparse.ArgumentParser();p.add_argument('summary',type=Path);a=p.parse_args()
rows=json.loads(a.summary.read_text())
valid=[r for r in rows if r.get('status')=='PASS']
if not valid:
    print('No successful physical runs to plot; no figure generated')
    raise SystemExit(0)
try:import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
except ImportError:raise SystemExit('Install optional plotting dependency: .venv/bin/python -m pip install -r requirements-analysis.txt')
d=new_run('figures');count=0
for study,x,y,xlabel,ylabel in [
 ('utilization','core_utilization_percent','setup_worst_slack_ns','Requested core utilization (%)','Final worst setup slack (ns)'),
 ('utilization','core_utilization_percent','core_area_um2','Requested core utilization (%)','Physical core area (µm²)'),
 ('clock','clock_period_ns','setup_worst_slack_ns','Target clock period (ns)','Final worst setup slack (ns)')]:
    points=sorted((r[x],r[y]) for r in valid if r['study']==study and isinstance(r.get(y),(int,float)))
    if len(points)<2:continue
    fig,ax=plt.subplots(figsize=(6,4));ax.plot(*zip(*points),marker='o');ax.set(xlabel=xlabel,ylabel=ylabel)
    ax.grid(alpha=.2);fig.tight_layout();fig.savefig(d/(study+'-'+y+'.png'),dpi=160);plt.close(fig);count+=1
(d/'caption.txt').write_text('Source: '+str(a.summary.resolve())+'\nOnly PASS runs with available metrics. Lines connect observations; no causal or statistical generalization.\n')
if not count:
    print('Insufficient measured points; no plot generated')
    raise SystemExit(0)
print(d)
