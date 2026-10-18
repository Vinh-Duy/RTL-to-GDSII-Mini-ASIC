#!/usr/bin/env python3
"""Integration failure-injection checks; intentionally bad DUTs never enter rtl/."""
import json,subprocess,sys
from common import ROOT,new_run,run,publish

def main():
    d=new_run('validation');checks=[]
    checks.append(('corrupt_expectation',[sys.executable,'scripts/simulate.py','--corrupt-expected']))
    alu=(ROOT/'rtl/alu_8bit.sv').read_text()
    wrong=d/'wrong_add.sv';wrong.write_text(alu.replace('a_extended + b_extended','a_extended ^ b_extended'))
    checks.append(('wrong_add',[sys.executable,'scripts/simulate.py','--rtl',str(wrong)]))
    async_reset=d/'async_reset.sv';async_reset.write_text((ROOT/'rtl/alu_top.sv').read_text().replace('@(posedge clk)','@(posedge clk or negedge rst_n)'))
    checks.append(('asynchronous_reset',[sys.executable,'scripts/simulate.py','--top',str(async_reset)]))
    latency=d/'wrong_latency.sv';latency.write_text((ROOT/'rtl/alu_top.sv').read_text().replace('wire [15:0] combinational_result;','wire [15:0] combinational_result;\n    reg [15:0] delayed;\n    always @(posedge clk) delayed <= combinational_result;').replace('result <= combinational_result','result <= delayed'))
    checks.append(('extra_pipeline_stage',[sys.executable,'scripts/simulate.py','--top',str(latency)]))
    outcomes=[]
    for name,cmd in checks:
        r=run(cmd,d/(name+'.log'))
        content=(d/(name+'.log')).read_text()
        rejected=r['exit_code']==1 and 'FATAL:' in content and ('Mismatch' in content or 'Reset must be synchronous' in content)
        outcomes.append({'test':name,'status':'PASS' if rejected else 'FAIL','expected':'Simulator rejects injected fault','execution':r})
        print(name,outcomes[-1]['status'])
    publish('validation',d,{'status':'PASS' if all(x['status']=='PASS' for x in outcomes) else 'FAIL','checks':outcomes})
    return 0 if all(x['status']=='PASS' for x in outcomes) else 1
if __name__=='__main__':sys.exit(main())
