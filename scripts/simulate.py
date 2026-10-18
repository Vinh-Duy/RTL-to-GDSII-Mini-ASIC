#!/usr/bin/env python3
import argparse,csv,random,sys
from pathlib import Path
from common import ROOT,new_run,run,sources,publish,version,sha

def reference(a,b,op):
    return (a+b, (a-b)%65536, a*b, 0 if b==0 else a//b,
            a&b, a|b, a^b, a*2**(b%8))[op]
def main():
    p=argparse.ArgumentParser();p.add_argument("--exhaustive",action="store_true")
    p.add_argument("--gate",type=Path);p.add_argument("--models",type=Path)
    p.add_argument("--top",type=Path);p.add_argument("--rtl",type=Path);p.add_argument("--corrupt-expected",action="store_true")
    args=p.parse_args();d=new_run("gate" if args.gate else "simulation")
    vectors=[]
    with (ROOT/"tb/known_answers.csv").open() as f:
        for row in csv.DictReader(f):
            a,b,op,e=[int(row[k]) for k in ["a","b","opcode","expected"]]
            assert reference(a,b,op)==e
            vectors.append((a,b,op,e))
    if args.exhaustive:
        vectors.extend((a,b,op,reference(a,b,op)) for op in range(8) for a in range(256) for b in range(256))
    else:
        boundary=[0,1,2,7,8,15,16,127,128,248,254,255]
        vectors.extend((a,b,op,reference(a,b,op)) for op in range(8) for a in boundary for b in boundary)
        rng=random.Random(2026)
        for i in range(4096):
            a,b=rng.randrange(256),rng.randrange(256);op=i%8
            vectors.append((a,b,op,reference(a,b,op)))
    if args.corrupt_expected:
        a,b,op,e=vectors[0];vectors[0]=(a,b,op,e^1)
    (d/"vectors.txt").write_text("".join("%d %d %d %d\n"%v for v in vectors))
    inputs=[args.gate,args.models] if args.gate else [args.rtl or ROOT/"rtl/alu_8bit.sv",args.top or ROOT/"rtl/alu_top.sv"]
    if any(x is None or not x.is_file() for x in inputs):p.error("Missing RTL, netlist or cell models")
    commands=[]
    commands.append(run(["iverilog","-g2012","-Wall","-s","tb_alu_top","-o",d/"sim.vvp",*inputs,ROOT/"tb/tb_alu_top.sv"],d/"compile.log"))
    if commands[-1]["exit_code"]==0:
        commands.append(run(["vvp",d/"sim.vvp","+VECTORS="+str(d/"vectors.txt"),"+COUNT="+str(len(vectors)),"+VCD="+str(d/"waveform.vcd")],d/"simulation.log",timeout=1800))
    passed=len(commands)==2 and commands[-1]["exit_code"]==0 and f"PASS vectors={len(vectors)} " in (d/"simulation.log").read_text()
    data={"status":"PASS" if passed else "FAIL","vectors":len(vectors),"exhaustive":args.exhaustive,"seed":2026,"commands":commands,"source_hashes":sources(),"input_hashes":{str(x):sha(x) for x in inputs},"simulator":version("iverilog","-V"),"negative_test":args.corrupt_expected}
    publish("gate" if args.gate else "simulation",d,data)
    print(data["status"],len(vectors),"vectors",d)
    if not passed and (d/"simulation.log").exists():print((d/"simulation.log").read_text())
    return 0 if passed else 1
if __name__=="__main__":sys.exit(main())
