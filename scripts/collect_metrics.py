#!/usr/bin/env python3
"""Keep raw ORFS metrics and exact provenance; missing measurements stay null."""
import argparse,json,math
from pathlib import Path
# OpenROAD report_design_area / report_timing_metrics keys, final_report stage.
KEYS={
 'synthesized_cell_area_um2':'design__instance__area',
 'final_cell_area_um2':'design__instance__area',
 'setup_wns_ns':'timing__setup__ws',
 'setup_tns_ns':'timing__setup__tns',
 'hold_worst_slack_ns':'timing__hold__ws',
 'hold_tns_ns':'timing__hold__tns',
 'setup_violating_endpoints':'timing__setup__violating__endpoints',
 'hold_violating_endpoints':'timing__hold__violating__endpoints',
 'core_area_um2':'design__core__area',
 'die_area_um2':'design__die__area',
 'instance_count':'design__instance__count',
 'buffer_count':'design__instance__count__class:buffer',
 'register_count':'design__instance__count__class:sequential',
 'wirelength_um':'route__wirelength',
 'routing_violations':'route__drc_errors',
}
def collect(directory):
    directory=Path(directory);raw={}
    for p in sorted((directory/'logs').rglob('*.json')):
        try: data=json.loads(p.read_text())
        except (ValueError,OSError):continue
        raw[str(p.relative_to(directory))]=data
    out={'metrics':{key:None for key in KEYS},'metric_sources':{},'raw_metrics':raw}
    # Deliberately prefer final-report timing; never label placement slack as final.
    for path,data in raw.items():
        if not isinstance(data,dict):continue
        for label,key in KEYS.items():
            if label=='synthesized_cell_area_um2':
                accepted=Path(path).name=='1_2_yosys.json'
            elif label in ['routing_violations','wirelength_um']:
                accepted=Path(path).name=='5_2_route.json'
            else:accepted=Path(path).name=='6_report.json'
            if not accepted:continue
            # report_metrics prefixes keys with the stage, e.g. finish__timing__setup__ws.
            matches=[(k,v) for k,v in data.items() if k==key or k.endswith('__'+key)]
            if len(matches)!=1:continue
            k,v=matches[0]
            if isinstance(v,(float,int)) and math.isfinite(v):
                out['metrics'][label]=v;out['metric_sources'][label]={'file':path,'key':k}
    # Compatibility name used by existing status output; it denotes final
    # standard-cell area, never core or die area.
    out['metrics']['physical_cell_area_um2']=out['metrics']['final_cell_area_um2']
    if 'final_cell_area_um2' in out['metric_sources']:
        out['metric_sources']['physical_cell_area_um2']=out['metric_sources']['final_cell_area_um2']
    # ORFS route JSON schemas do not consistently expose a via total. Keep this
    # null unless a future inspected schema adds an explicit, tested source.
    out['metrics']['via_count']=None
    # WNS convention: no negative slack -> zero. Preserve raw worst slack separately.
    ws=out['metrics']['setup_wns_ns']
    out['metrics']['setup_worst_slack_ns']=ws
    if ws is not None:out['metrics']['setup_wns_ns']=min(0.0,ws)
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);args=p.parse_args()
    out=collect(args.directory);(args.directory/'metrics.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out['metrics'],indent=2))
