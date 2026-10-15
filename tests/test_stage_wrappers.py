"""Stage dispatch regressions: no generation, publish, or notification is run here."""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]


class StageWrapperTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.calls = self.root / 'calls.jsonl'
        self.python = self.root / 'fake-python'
        self.python.write_text('#!' + sys.executable + '\n' + '''import json, os, sys
if sys.argv[1] == '-c':
    from datetime import date
    try: date.fromisoformat(sys.argv[-1])
    except ValueError: sys.exit(2)
    sys.exit(0)
with open(os.environ['TEST_CALLS'], 'a') as handle:
    handle.write(json.dumps(sys.argv[1:]) + '\\n')
if os.environ.get('TEST_FAIL') and os.environ['TEST_FAIL'] in sys.argv[1:]:
    sys.exit(7)
''')
        self.python.chmod(0o700)
        self.environment = dict(os.environ, LUNA_NEWS_DIR=str(self.root),
                                LUNA_NEWS_PYTHON=str(self.python), TEST_CALLS=str(self.calls))
        self.environment.pop('TEST_FAIL', None)

    def run_stage(self, *args, script='daily.sh'):
        return subprocess.run(['bash', str(ROOT / 'scripts' / script), *args],
                              env=self.environment, capture_output=True, text=True)

    def recorded(self):
        return [json.loads(line) for line in self.calls.read_text().splitlines()] if self.calls.exists() else []

    def test_default_and_dry_are_only_local_read_checks(self):
        for arguments in ((), ('--dry',)):
            with self.subTest(arguments=arguments):
                self.assertEqual(self.run_stage(*arguments).returncode, 0)
        self.assertEqual(self.recorded(), [['scripts/issue_check.py', '--root', str(self.root / 'docs')]] * 2)
        self.assertFalse((self.root / 'logs').exists())

    def test_invalid_arguments_stop_before_any_stage(self):
        for arguments in (('--unknown',), ('--render', '--date'), ('--render', '--date', '2026-02-30'),
                          ('--prepare', '--publish'), ('--check', '--date', '2026-10-14', '--date', '2026-10-15')):
            with self.subTest(arguments=arguments):
                self.assertEqual(self.run_stage(*arguments).returncode, 2)
        self.assertEqual(self.recorded(), [])

    def test_failed_render_stops_before_acceptance_and_success_markers(self):
        self.environment['TEST_FAIL'] = 'scripts/rebuild_all.py'
        self.assertEqual(self.run_stage('--render', '--date', '2026-10-14').returncode, 7)
        self.assertEqual(self.recorded(), [['scripts/rebuild_all.py']])
        self.assertFalse((self.root / 'logs').exists())

    def test_watchdog_performs_one_public_check(self):
        self.assertEqual(self.run_stage('--date', '2026-10-14', script='watchdog.sh').returncode, 0)
        self.assertEqual(self.recorded(), [['scripts/issue_check.py', '--base-url',
                                          'https://nowonair.vercel.app', '--date', '2026-10-14']])
        self.assertFalse((self.root / 'logs').exists())


if __name__ == '__main__':
    unittest.main()
