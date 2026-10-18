#!/usr/bin/env python3
"""Fetch only the pinned 6.4 MB synthesis Liberty plus its platform license."""
import hashlib,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REV='7bcaf475c884e15f674e428aa04dbf92bd0426ed'
BASE=f'https://raw.githubusercontent.com/The-OpenROAD-Project/OpenROAD-flow-scripts/{REV}/flow/platforms/nangate45/'
FILES={'lib/NangateOpenCellLibrary_typical.lib':('NangateOpenCellLibrary_typical.lib','8d540a4d4cf6d09d27c87ad067857a9c0c2eeb023ab7a56e058cd3113db4e9b1'), 'LICENSE':('Nangate45-LICENSE',None)}
for source,(name,digest) in FILES.items():
    dest=ROOT/'.tools'/name;dest.parent.mkdir(exist_ok=True)
    if dest.exists() and (digest is None or hashlib.sha256(dest.read_bytes()).hexdigest()==digest):
        print('Already available:',name);continue
    with urllib.request.urlopen(BASE+source,timeout=60) as response: data=response.read()
    if digest and hashlib.sha256(data).hexdigest()!=digest:raise RuntimeError('Library checksum mismatch')
    dest.write_bytes(data);print('Downloaded',name,len(data),'bytes')
