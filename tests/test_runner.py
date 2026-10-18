"""Fixtures below test plumbing; they are never experimental observations."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import ROOT,run
from collect_metrics import collect
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
if __name__=='__main__':unittest.main()
