#!/usr/bin/env python3
import argparse,json,subprocess,sys
from common import ROOT,sha
p=argparse.ArgumentParser();p.add_argument('--exhaustive',action='store_true');a=p.parse_args()
ptr=ROOT/'reports/synthesis/latest.json'
if not ptr.exists():raise SystemExit('No synthesis result. Run make synth first.')
d=ROOT/json.loads(ptr.read_text())['directory'];data=json.loads((d/'summary.json').read_text())
if data['status']!='PASS':raise SystemExit('Latest synthesis did not pass')
for name in ['rtl/alu_top.sv','rtl/alu_8bit.sv']:
    if data['source_hashes'][name]!=sha(ROOT/name):raise SystemExit('RTL changed since synthesis: rerun make synth')
cmd=[sys.executable,str(ROOT/'scripts/simulate.py'),'--gate',str(d/'alu_top_mapped.v'),'--models',str(d/'nangate45_functional.v')]
if a.exhaustive:cmd.append('--exhaustive')
raise SystemExit(subprocess.call(cmd,cwd=ROOT))
