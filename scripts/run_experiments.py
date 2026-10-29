#!/usr/bin/env python3
import argparse,csv,hashlib,json,platform,sys
from pathlib import Path
from common import ROOT,new_run,write_json,sha,sources,now
from physical import backend,execute,REV

def select_configurations(study,c):
    baseline=(c['baseline_clock_period_ns'],c['baseline_utilization_percent'])
    if study=='baseline':return [baseline]
    if study=='utilization':return [(baseline[0],u) for u in c['utilizations_percent']]
    periods=c['clock_periods_ns']
    if len(periods)<3:raise ValueError('Choose at least three periods from measured baseline timing first')
    return [(t,baseline[1]) for t in periods]

def main():
    p=argparse.ArgumentParser();p.add_argument('--study',choices=['baseline','utilization','clock'],default='baseline')
    p.add_argument('--config',type=Path,default=ROOT/'experiments/configurations/study.json');a=p.parse_args()
    c=json.loads(a.config.read_text())
    # Preflight before creating experiment rows: an absent tool is not an executed experiment.
    try:backend()
    except Exception as e:print('NOT RUN:',e);return 2
    try:configs=select_configurations(a.study,c)
    except ValueError as e:p.error(str(e))
    d=new_run('experiments');rows=[];write_json(d/'configuration.json',c)
    canonical=json.dumps(c,sort_keys=True,separators=(',',':')).encode()
    try:config_path=str(a.config.resolve().relative_to(ROOT))
    except ValueError:config_path=str(a.config.resolve())
    manifest={'schema_version':1,'status':'RUNNING','study':a.study,'started':now(),
        'orfs_revision':REV,'configuration_path':config_path,
        'configuration_file_sha256':sha(a.config),
        'configuration_sha256':hashlib.sha256(canonical).hexdigest(),
        'configuration':c,'source_hashes':sources(),
        'environment':{'system':platform.platform(),'machine':platform.machine(),'python':sys.version.split()[0]},
        'seed_policy':'No explicit placement seed configured; tool default recorded by source/configuration.',
        'runs':[]}
    write_json(d/'manifest.json',manifest)
    for t,u in configs:
        directory,result=execute(t,u,c['placement_density'],c['timeout_seconds_per_stage'],c['threads'])
        run_config=result['configuration']
        run_hash=hashlib.sha256(json.dumps(run_config,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        entry={'clock_period_ns':t,'core_utilization_percent':u,'configuration':run_config,
            'configuration_sha256':run_hash,'status':result['status'],
            'run_directory':str(directory.relative_to(ROOT)),
            'summary_path':str((directory/'summary.json').relative_to(ROOT)),
            'source_hashes':result['source_hashes'],'toolchain':result.get('backend',{}),
            'stages':result['stages'],'metric_sources':result.get('metric_sources',{}),
            'metrics':result.get('metrics',{}),'gds_inspection':result.get('gds_inspection',{}),
            'started':result['started'],'ended':result['ended'],
            'runtime_seconds':sum(command.get('seconds',0) for command in result.get('commands',[]))}
        manifest['runs'].append(entry)
        write_json(d/'manifest.json',manifest)
        if any('command' in stage for stage in result['stages'].values()):
            rows.append({'study':a.study,'clock_period_ns':t,'core_utilization_percent':u,
                         'status':result['status'],'directory':str(directory.relative_to(ROOT)),**result['metrics']})
            write_json(d/'summary.json',rows)
            with (d/'summary.csv').open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        if result['status']!='PASS':
            manifest['status']=result['status'];manifest['ended']=now()
            manifest['stopped_after']=entry['run_directory']
            write_json(d/'manifest.json',manifest)
            break
    else:
        manifest['status']='PASS';manifest['ended']=now();write_json(d/'manifest.json',manifest)
    print(d)
    return 0 if manifest['status']=='PASS' and len(manifest['runs'])==len(configs) else 1
if __name__=='__main__':sys.exit(main())
