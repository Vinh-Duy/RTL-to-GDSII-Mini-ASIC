#!/usr/bin/env python3
import argparse,csv,json,sys
from pathlib import Path
from common import ROOT,new_run,write_json
from physical import backend,execute

def main():
    p=argparse.ArgumentParser();p.add_argument('--study',choices=['baseline','utilization','clock'],default='baseline')
    p.add_argument('--config',type=Path,default=ROOT/'experiments/configurations/study.json');a=p.parse_args()
    c=json.loads(a.config.read_text())
    # Preflight before creating experiment rows: an absent tool is not an executed experiment.
    try:backend()
    except Exception as e:print('NOT RUN:',e);return 2
    baseline=(c['baseline_clock_period_ns'],c['baseline_utilization_percent'])
    if a.study=='baseline':configs=[baseline]
    elif a.study=='utilization':configs=[(baseline[0],u) for u in c['utilizations_percent']]
    else:
        periods=c['clock_periods_ns']
        if len(periods)<3:p.error('Choose at least three periods from measured baseline timing first')
        configs=[(t,baseline[1]) for t in periods]
    d=new_run('experiments');rows=[];write_json(d/'configuration.json',c)
    for t,u in configs:
        directory,result=execute(t,u,c['placement_density'],c['timeout_seconds_per_stage'],c['threads'])
        if any('command' in stage for stage in result['stages'].values()):
            rows.append({'study':a.study,'clock_period_ns':t,'core_utilization_percent':u,
                         'status':result['status'],'directory':str(directory.relative_to(ROOT)),**result['metrics']})
            write_json(d/'summary.json',rows)
            with (d/'summary.csv').open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        if result['status']=='NOT RUN':break
    print(d)
    return 0 if len(rows)==len(configs) and all(r['status']=='PASS' for r in rows) else 1
if __name__=='__main__':sys.exit(main())
