#!/usr/bin/env python3
"""Drive official ORFS targets; preflight never installs software or pulls images."""
import argparse,json,os,re,shutil,subprocess,sys,uuid
from pathlib import Path
from common import ROOT,new_run,run,sources,publish,version,sha,now
from collect_metrics import collect
REV='7bcaf475c884e15f674e428aa04dbf92bd0426ed'
STAGES=[('synth','1_2_yosys.v'),('floorplan','2_floorplan.odb'),('place','3_place.odb'),
        ('cts','4_cts.odb'),('grt','5_1_grt.odb'),('route','5_route.odb'),('finish','6_final.gds')]

def backend():
    image=os.environ.get('ORFS_IMAGE');native=os.environ.get('ORFS_ROOT')
    if image:
        if not shutil.which('docker'):raise RuntimeError('Docker is not installed. See docs/ENVIRONMENT.md.')
        if '@sha256:' not in image:raise RuntimeError('ORFS_IMAGE must use an immutable @sha256 digest; inspect/pull it explicitly first.')
        info=json.loads(subprocess.check_output(['docker','image','inspect',image],text=True,timeout=30))[0]
        if info['Os']!='linux' or info['Architecture']!='amd64':raise RuntimeError('This baseline expects linux/amd64; do not assume ARM compatibility.')
        subprocess.run(['docker','info'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True,timeout=30)
        name='alu-orfs-'+uuid.uuid4().hex[:12]
        prefix=['docker','run','--rm','--name',name,'--user',f'{os.getuid()}:{os.getgid()}','--pull=never','--platform','linux/amd64','--network','none',
                '-v',str(ROOT)+':/project','-w','/OpenROAD-flow-scripts/flow',image,
                'bash','-c','source /OpenROAD-flow-scripts/env.sh; exec "$@"','orfs-command']
        return {'mode':'docker','image':image,'image_id':info['Id'],'architecture':info['Architecture'],'container_name':name},prefix,'/project',Path('/OpenROAD-flow-scripts/flow')
    if not native:raise RuntimeError('OpenROAD/ORFS unavailable. Set ORFS_ROOT to a prepared pinned Linux checkout, or ORFS_IMAGE to a locally installed image digest. See docs/ENVIRONMENT.md.')
    root=Path(native).resolve()
    if not (root/'flow/Makefile').is_file():raise RuntimeError('ORFS_ROOT must contain flow/Makefile')
    revision=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    if revision!=REV:raise RuntimeError(f'ORFS revision mismatch: require {REV}, got {revision}')
    dirty=subprocess.check_output(['git','-C',str(root),'status','--porcelain','--untracked-files=no'],text=True).strip()
    if dirty:raise RuntimeError('ORFS tracked files must be clean')
    for exe in ['yosys','openroad','klayout']:
        if not shutil.which(exe):raise RuntimeError(f'{exe} missing from PATH; source ORFS env.sh first')
    return {'mode':'native','revision':revision,'tools':{t:version(t,'-version' if t in ['openroad'] else '-v' if t=='klayout' else '-V') for t in ['yosys','openroad','klayout']}},[],str(ROOT),root/'flow'

def execute(period=10.0,utilization=30,density=0.70,timeout=1800,threads=2,category='physical'):
    d=new_run(category)
    config={'clock_period_ns':period,'core_utilization_percent':utilization,'placement_density':density,'threads':threads,'platform':'nangate45','timeout_per_stage_seconds':timeout}
    data={'status':'NOT RUN','started':now(),'configuration':config,'source_hashes':sources(),
          'constraints':(ROOT/'constraints/timing.sdc').read_text(),'stages':{s:{'status':'NOT RUN'} for s,_ in STAGES},'gds_inspection':{'status':'NOT RUN'},'commands':[]}
    publish(category,d,data)
    try:
        meta,prefix,project,flow=backend();data['backend']=meta
        # Capture versions from inside the selected container, with no host tool assumptions.
        if prefix:
            data['backend']['tools']={}
            for t,flag in [('yosys','-V'),('openroad','-version'),('klayout','-v')]:
                v=run(prefix+[t,flag],d/(t+'-version.log'),timeout=120)
                data['commands'].append(v)
                if v['exit_code']:raise RuntimeError('Container tool preflight failed: '+t)
                data['backend']['tools'][t]=(d/(t+'-version.log')).read_text()
        work=project+'/'+str(d.relative_to(ROOT))
        args=[f'DESIGN_CONFIG={project}/flow/config.mk',f'PROJECT_ROOT={project}',f'WORK_HOME={work}',
              'FLOW_VARIANT=base',f'CLOCK_PERIOD={period}',f'CORE_UTILIZATION={utilization}',
              f'PLACE_DENSITY={density}',f'NUM_CORES={threads}']
        for stage,artifact in STAGES:
            result=run(prefix+['make',*args,stage],d/(stage+'.log'),timeout=timeout,cwd=ROOT if prefix else flow)
            data['commands'].append(result);data['stages'][stage]=dict(result)
            if result['exit_code']==124 and prefix:
                cleanup=run(['docker','rm','-f',meta['container_name']],d/'timeout-cleanup.log',timeout=30)
                data['commands'].append(cleanup)
            out=d/'results/nangate45/alu_top/base'/artifact
            data['stages'][stage]['artifact']=str(out.relative_to(ROOT))
            if result['exit_code'] or not out.is_file() or out.stat().st_size==0:
                data['stages'][stage]['status']='FAIL';raise RuntimeError(f'{stage} failed or expected output missing')
            data['stages'][stage]['sha256']=sha(out)
            if stage=='cts':
                report=d/'reports/nangate45/alu_top/base/clock_tree.rpt'
                content=report.read_text() if report.exists() else ''
                counts={}
                for label in ['Clock Roots','Buffers Inserted','Clock Subnets','Sinks']:
                    match=re.search(r'Total number of '+label+r':\s*(\d+)',content)
                    counts[label]=int(match.group(1)) if match else None
                data['stages'][stage]['clock_tree_counts']=counts
                if any(counts[k] is None or counts[k]<=0 for k in counts):
                    data['stages'][stage]['status']='FAIL'
                    raise RuntimeError('CTS output exists but a nonempty clock tree was not confirmed; inspect clock_tree.rpt')
            publish(category,d,data)
        gds=work+'/results/nangate45/alu_top/base/6_final.gds'
        inspection=run(prefix+['klayout','-b','-r',project+'/scripts/inspect_gds.py','-rd','gds='+gds,
                               '-rd','output='+work+'/gds-inspection.json'],d/'gds-inspection.log',timeout=120,cwd=ROOT if prefix else flow)
        data['commands'].append(inspection)
        if inspection['exit_code'] or not (d/'gds-inspection.json').exists():raise RuntimeError('GDS read-back failed')
        data['gds_inspection']=json.loads((d/'gds-inspection.json').read_text())
        data['status']='PASS'
    except (RuntimeError,OSError,subprocess.SubprocessError,ValueError,KeyError) as e:
        data['error']=str(e)
        if data['commands']:data['status']='FAIL'
    if data.get('backend',{}).get('mode')=='docker' and any(c.get('exit_code')==124 for c in data['commands']):
        cleanup=run(['docker','rm','-f',data['backend']['container_name']],d/'final-timeout-cleanup.log',timeout=30)
        data['commands'].append(cleanup)
    data.update(collect(d));data['ended']=now();publish(category,d,data)
    print(data['status'],d, data.get('error',''))
    return d,data
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--period',type=float,default=10.0);p.add_argument('--utilization',type=float,default=30)
    p.add_argument('--density',type=float,default=.70);p.add_argument('--timeout',type=int,default=1800)
    p.add_argument('--threads',type=int,default=2);a=p.parse_args()
    if a.period<=0 or not 0<a.utilization<100 or not 0<a.density<=1 or a.timeout<=0 or a.threads<1:p.error('Invalid flow parameter')
    _,data=execute(a.period,a.utilization,a.density,a.timeout,a.threads)
    sys.exit(0 if data['status']=='PASS' else 2)
