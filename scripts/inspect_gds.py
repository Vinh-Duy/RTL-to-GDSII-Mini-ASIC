# Executed by KLayout: klayout -b -r inspect_gds.py -rd gds=... -rd output=...
import json
import pya
from pathlib import Path
layout=pya.Layout()
layout.read(gds)
tops=layout.top_cells()
if len(tops)!=1 or tops[0].name!='alu_top' or tops[0].bbox().empty():
    raise RuntimeError('Expected one nonempty alu_top GDS top cell')
Path(output).write_text(json.dumps({'status':'PASS','top':tops[0].name,
    'cell_count':layout.cells(),'dbu_um':layout.dbu,'bbox_dbu':str(tops[0].bbox()),
    'scope':'Readable nonempty layout, not DRC/LVS signoff'},indent=2)+'\n')
