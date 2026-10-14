import importlib.util
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class DeployRecoveryTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('isolated_deploy', ROOT / 'pipeline/deploy.py')
        self.deploy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.deploy)
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.deploy.REPO_DIR = Path(self.temp.name)
        (self.deploy.REPO_DIR / 'docs').mkdir()
        (self.deploy.REPO_DIR / 'docs/index.html').write_text('reviewed candidate')
        self.branch = 'main'
        self.pre_staged = False
        self.push_failure = False
        self.unselected = ''
        self.calls = []

    def git(self, cmd, **kwargs):
        self.calls.append(cmd)
        args = cmd[3:]
        text, status = '', 0
        if args == ['branch', '--show-current']:
            text = self.branch
        elif args[:3] == ['remote', 'get-url', 'origin']:
            text = 'https://github.com/s-yamanaka-droid/luna-news.git'
        elif args[:3] == ['diff', '--cached', '--quiet']:
            status = 1 if self.pre_staged else 0
        elif args[:2] == ['diff', '--name-only']:
            text = self.unselected
        elif args[:1] == ['push']:
            status = 1 if self.push_failure else 0
        elif args[:1] == ['rev-parse']:
            text = 'a' * 40
        elif args[:1] == ['ls-remote']:
            text = 'a' * 40 + '\trefs/heads/main'
        return subprocess.CompletedProcess(cmd, status, text, '')

    def publish(self):
        import sys
        sys.path.insert(0, str(ROOT / 'scripts'))
        with patch('subprocess.run', side_effect=self.git), patch('issue_check.check_local', return_value={'ok': True}):
            return self.deploy.git_push('reviewed release', paths=['docs/index.html'], date_str='2026-10-14')

    def test_chat_branch_is_rejected_before_staging_or_push(self):
        self.branch = 'chat/other-task'
        self.assertFalse(self.publish())
        self.assertFalse(any(cmd[3] in ('add', 'push', 'commit') for cmd in self.calls))

    def test_preexisting_staging_is_not_committed(self):
        self.pre_staged = True
        self.assertFalse(self.publish())
        self.assertFalse(any(cmd[3] in ('add', 'push', 'commit') for cmd in self.calls))

    def test_unchanged_candidate_still_pushes_unpushed_head(self):
        self.assertTrue(self.publish())
        self.assertTrue(any(cmd[3] == 'push' for cmd in self.calls))
        self.assertFalse(any(cmd[3] == 'commit' for cmd in self.calls))
        staged = next(cmd[3:] for cmd in self.calls if cmd[3] == 'add')
        self.assertEqual(staged, ['add', '--', 'docs/index.html'])

    def test_push_failure_is_non_success(self):
        self.push_failure = True
        self.assertFalse(self.publish())

    def test_unselected_dirty_docs_cannot_validate_an_unpublished_candidate(self):
        self.unselected = 'docs/news/2026-10-14/articles.json\0'
        self.assertFalse(self.publish())
        self.assertFalse(any(cmd[3] in ('add', 'push', 'commit') for cmd in self.calls))


if __name__ == '__main__':
    unittest.main()
