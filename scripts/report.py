#!/usr/bin/env python3
"""Read recorded evidence, check freshness, export a compact machine-readable index."""
import argparse,json,sys
from common import ROOT,sha,write_json
p=argparse.ArgumentParser();p.add_argument('--timing',action='store_true');a=p.parse_args()
result={}
for category in ['simulation','synthesis','gate','validation','physical']:
    pointer=ROOT/'reports'/category/'latest.json'
    if not pointer.exists():result[category]={'status':'NOT RUN'};continue
    d=ROOT/json.loads(pointer.read_text())['directory']
    data=json.loads((d/'summary.json').read_text())
    result[category]={'status':data['status'],'directory':str(d.relative_to(ROOT))}
    if 'metrics' in data:result[category]['metrics']=data['metrics']
    if 'vectors' in data:result[category]['vectors']=data['vectors']
    if 'error' in data:result[category]['error']=data['error']
    if 'stages' in data:result[category]['stages']={k:v['status'] for k,v in data['stages'].items()}
    if 'source_hashes' in data:
        for f in ['rtl/alu_8bit.sv','rtl/alu_top.sv']:
            if data['source_hashes'].get(f)!=sha(ROOT/f):
                result[category]['status']='FAIL';result[category]['error']='Evidence is stale for current RTL'
if a.timing:
    phys=result['physical'];m=phys.get('metrics',{})
    if phys['status']!='PASS' or m.get('setup_worst_slack_ns') is None:
        print('NOT RUN: no successful final timing measurement. Run make physical in a prepared environment.');sys.exit(2)
    print(json.dumps(m,indent=2));sys.exit(0)
write_json(ROOT/'reports/current-status.json',result)
print(json.dumps(result,indent=2))
