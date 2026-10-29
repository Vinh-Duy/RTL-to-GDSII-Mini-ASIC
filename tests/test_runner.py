"""Fixtures below test plumbing; they are never experimental observations."""
import json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import ROOT,run,sources
from collect_metrics import collect
from physical import backend,REV,STAGES
from run_experiments import select_configurations
class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'.tools/tmp');self.d=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def test_nonzero_propagates(self):
        self.assertEqual(run([sys.executable,'-c','raise SystemExit(7)'],self.d/'fail.log')['exit_code'],7)
    def test_timeout(self):
        r=run([sys.executable,'-c','import time; time.sleep(10)'],self.d/'timeout.log',timeout=.1)
        self.assertEqual(r['exit_code'],124);self.assertEqual(r['status'],'FAIL')
    def test_missing_executable(self):
        self.assertEqual(run(['/definitely-not-a-real-tool'],self.d/'missing.log')['exit_code'],127)
    def test_missing_metric_not_zero(self):
        self.assertIsNone(collect(self.d)['metrics']['setup_wns_ns'])
    def test_only_final_timing(self):
        p=self.d/'logs';p.mkdir()
        (p/'3_place.json').write_text(json.dumps({'timing__setup__ws':1.0}))
        self.assertIsNone(collect(self.d)['metrics']['setup_wns_ns'])
        (p/'6_report.json').write_text(json.dumps({'timing__setup__ws':-.2,'timing__setup__tns':-1.4}))
        r=collect(self.d);self.assertEqual(r['metrics']['setup_wns_ns'],-.2)
        self.assertIn('setup_wns_ns',r['metric_sources'])
    def test_positive_slack_is_not_negative_wns(self):
        p=self.d/'logs';p.mkdir();(p/'6_report.json').write_text(json.dumps({'timing__setup__ws':.3}))
        r=collect(self.d)['metrics'];self.assertEqual(r['setup_wns_ns'],0);self.assertEqual(r['setup_worst_slack_ns'],.3)
    def test_synth_and_final_cell_area_are_separate_sources(self):
        p=self.d/'logs';p.mkdir()
        (p/'1_2_yosys.json').write_text(json.dumps({'design__instance__area':879.9}))
        (p/'6_report.json').write_text(json.dumps({'design__instance__area':901.2,'design__core__area':3000}))
        r=collect(self.d)
        self.assertEqual(r['metrics']['synthesized_cell_area_um2'],879.9)
        self.assertEqual(r['metrics']['final_cell_area_um2'],901.2)
        self.assertEqual(r['metrics']['physical_cell_area_um2'],901.2)
        self.assertEqual(r['metrics']['core_area_um2'],3000)
    def test_route_vias_stay_unknown_without_verified_metric(self):
        self.assertIsNone(collect(self.d)['metrics']['via_count'])
    def test_preflight_rejects_mutable_image_tag(self):
        with patch.dict(os.environ,{'ORFS_IMAGE':'openroad/orfs:latest'},clear=True), \
             patch('physical.shutil.which',return_value='/usr/bin/docker'):
            with self.assertRaisesRegex(RuntimeError,'immutable'):
                backend()
    def test_orfs_revision_is_pinned(self):
        self.assertEqual(len(REV),40)
    def test_flow_uses_official_orfs_physical_targets(self):
        self.assertEqual([stage for stage,_ in STAGES],['synth','floorplan','place','cts','grt','route','finish'])
    def test_utilization_study_uses_existing_serial_points(self):
        config=json.loads((ROOT/'experiments/configurations/study.json').read_text())
        self.assertEqual(select_configurations('utilization',config),[(10.0,30),(10.0,45),(10.0,60)])
        self.assertEqual(config['placement_density'],0.70)
    def test_source_manifest_covers_experiment_and_workflow_inputs(self):
        manifest=sources()
        self.assertIn('Makefile',manifest)
        self.assertIn('experiments/configurations/study.json',manifest)
        self.assertIn('.github/workflows/physical-baseline.yml',manifest)
    def test_analyzer_skips_plot_when_no_physical_run_passed(self):
        summary=self.d/'empty-summary.json';summary.write_text('[]\n')
        result=run([sys.executable,str(ROOT/'scripts/analyze_results.py'),str(summary)],self.d/'analyze.log')
        self.assertEqual(result['exit_code'],0)
        self.assertIn('no figure generated',(self.d/'analyze.log').read_text())
if __name__=='__main__':unittest.main()
