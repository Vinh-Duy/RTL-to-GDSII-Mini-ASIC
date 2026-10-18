#!/usr/bin/env python3
import json,os,sys
from common import ROOT,new_run,run,sources,publish,sha,yosys,version,now

def main():
    d=new_run('synthesis');lib=ROOT/'.tools/NangateOpenCellLibrary_typical.lib'
    data={'status':'NOT RUN','started':now(),'commands':[],'source_hashes':sources(),
          'platform':'nangate45','corner':'typical 1.10 V 25 C',
          'orfs_revision':'7bcaf475c884e15f674e428aa04dbf92bd0426ed','timing_driven':False}
    publish('synthesis',d,data)
    try:
        if not lib.exists():raise RuntimeError('Missing Nangate45 library: run make setup')
        data['liberty_sha256']=sha(lib)
        if data['liberty_sha256']!='8d540a4d4cf6d09d27c87ad067857a9c0c2eeb023ab7a56e058cd3113db4e9b1':
            raise RuntimeError('Library differs from pinned baseline; restore it with make setup')
        exe=yosys();data['yosys_version']=version(exe,'-V')
        script=f'''read_liberty -lib {lib}
read_verilog -sv rtl/alu_8bit.sv rtl/alu_top.sv
hierarchy -check -top alu_top
synth -top alu_top -flatten -noabc
dfflibmap -liberty {lib}
abc -liberty {lib}
clean
delete t:$scopeinfo
check -assert
tee -o {d}/stat.json stat -json -liberty {lib}
write_verilog -noattr -noexpr {d}/alu_top_mapped.v
write_json {d}/netlist.json
'''
        (d/'synth.ys').write_text(script)
        result=run([exe,'-s',d/'synth.ys'],d/'synthesis.log',timeout=1800)
        data['commands'].append(result)
        data['warnings']=[x for x in (d/'synthesis.log').read_text().splitlines() if 'Warning:' in x]
        if result['exit_code']:raise RuntimeError('Yosys failed; inspect synthesis.log')
        net=json.loads((d/'netlist.json').read_text());cells=net['modules']['alu_top']['cells']
        if not cells or any(c['type'].startswith('$') or c['type'] not in net['modules'] for c in cells.values()):
            raise RuntimeError('Unmapped or undefined cells in netlist')
        stats=json.loads((d/'stat.json').read_text());m=stats['modules']['\\alu_top']
        seq=sum(c['type'].startswith(('DFF','SDFF')) for c in cells.values())
        if seq!=16 or len(cells)!=m['num_cells']:raise RuntimeError('Unexpected register/cell count')
        data['metrics']={'cell_count':len(cells),'sequential_cells':seq,'combinational_cells':len(cells)-seq,
                         'mapped_cell_area_um2':m['area'],'sequential_area_um2':m.get('sequential_area'),
                         'cell_types':m['num_cells_by_type']}
        data['netlist_sha256']=sha(d/'alu_top_mapped.v')
        # Translate actual Liberty functions/ff definitions. Missing-function clock gates are unused.
        (d/'models.ys').write_text(f'read_liberty -ignore_miss_func {lib}\nwrite_verilog -noattr {d}/nangate45_functional.v\n')
        model=run([exe,'-s',d/'models.ys'],d/'models.log',timeout=300)
        data['commands'].append(model);data['model_status']=model['status']
        if model['exit_code'] or not (d/'nangate45_functional.v').stat().st_size:raise RuntimeError('Liberty model generation failed')
        data['models_sha256']=sha(d/'nangate45_functional.v');data['status']='PASS'
    except (RuntimeError,OSError,ValueError,KeyError) as e:
        data['error']=str(e)
        if data['commands']:data['status']='FAIL'
    data['ended']=now();publish('synthesis',d,data)
    print(data['status'],d,data.get('error',''))
    if 'metrics' in data:print(json.dumps(data['metrics'],indent=2))
    return 0 if data['status']=='PASS' else 1
if __name__=='__main__':sys.exit(main())
