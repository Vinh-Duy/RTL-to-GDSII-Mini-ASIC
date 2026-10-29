"""Small execution/evidence helpers; commands never run through a shell."""
import datetime, hashlib, json, os, shutil, signal, subprocess, time, uuid
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("YOWASP_CACHE_DIR",str(ROOT/".tools/yowasp-cache"))
os.environ.setdefault("YOWASP_MOUNT",f"/={ROOT}:{ROOT}={ROOT}")
(ROOT/".tools/tmp").mkdir(parents=True,exist_ok=True)
os.environ.setdefault("TMPDIR",str(ROOT/".tools/tmp"))
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True)+"\n")
def new_run(category):
    p=ROOT/"reports"/category/(datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+uuid.uuid4().hex[:8])
    p.mkdir(parents=True); return p

def sources():
    files=[ROOT/"Makefile"]
    for folder in ["rtl","tb","tests","scripts","constraints","flow","experiments/configurations",".github/workflows"]:
        files.extend(sorted((ROOT/folder).rglob("*")))
    return {str(p.relative_to(ROOT)):sha(p) for p in files if p.is_file()
            if "__pycache__" not in p.parts}
def version(exe, flag="--version"):
    try: return subprocess.check_output([exe,flag],stderr=subprocess.STDOUT,text=True,timeout=120).strip()
    except (OSError,subprocess.SubprocessError) as e: return str(e)
def yosys():
    explicit=os.environ.get("YOSYS")
    if explicit: return explicit
    native=shutil.which("yosys")
    if native:return native
    local=ROOT/".venv/bin/yowasp-yosys"
    if local.exists():return str(local)
    raise RuntimeError("Yosys missing; run make setup or set YOSYS=/path/to/yosys")
def run(cmd, log, timeout=300, cwd=ROOT):
    started=now(); t=time.monotonic()
    with Path(log).open("w") as out:
        try:
            p=subprocess.Popen([str(x) for x in cmd],cwd=cwd,stdout=out,stderr=subprocess.STDOUT,
                               start_new_session=True)
        except OSError as e:
            out.write(str(e)); return {"command":list(map(str,cmd)),"exit_code":127,"status":"FAIL","started":started,"ended":now(),"seconds":time.monotonic()-t}
        try: code=p.wait(timeout=timeout); status="PASS" if code==0 else "FAIL"
        except subprocess.TimeoutExpired:
            os.killpg(p.pid,signal.SIGTERM)
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
            code=124;status="FAIL";out.write("\nTIMEOUT\n")
    return {"command":list(map(str,cmd)),"exit_code":code,"status":status,"started":started,"ended":now(),"seconds":time.monotonic()-t}
def publish(category, directory, data):
    write_json(directory/"summary.json",data)
    write_json(ROOT/"reports"/category/"latest.json",{"directory":str(directory.relative_to(ROOT))})
