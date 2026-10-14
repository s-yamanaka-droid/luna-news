import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


class LlmRecoveryTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('isolated_llm', ROOT / 'pipeline/llm.py')
        self.llm = importlib.util.module_from_spec(spec)
        with patch.dict('os.environ', {'LLM_PROVIDER': 'codex', 'LLM_FALLBACK_CHAIN': 'codex,claude'}):
            spec.loader.exec_module(self.llm)

    def test_default_fallback_has_no_paid_provider(self):
        spec = importlib.util.spec_from_file_location('default_llm', ROOT / 'pipeline/llm.py')
        module = importlib.util.module_from_spec(spec)
        import os
        with patch.dict(os.environ, clear=True):
            spec.loader.exec_module(module)
        self.assertEqual(module.FALLBACK_CHAIN, ['codex', 'claude'])

    def test_provider_error_body_is_not_logged_or_reraised(self):
        sensitive = 'private-provider-error-body'
        self.llm._dispatch = Mock(side_effect=RuntimeError(sensitive))
        with self.assertLogs(self.llm.log, level='WARNING') as logs:
            with self.assertRaises(RuntimeError) as error:
                self.llm.chat_json('system', 'user')
        self.assertNotIn(sensitive, '\n'.join(logs.output) + str(error.exception))

    def test_codex_uses_documented_stdin_route(self):
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, '[]', '')) as run:
            self.assertEqual(self.llm._codex('system', 'user'), '[]')
        self.assertEqual(run.call_args.args[0][-1], '-')
        self.assertEqual(run.call_args.kwargs['input'], 'system\n\nuser')

    def test_codex_error_does_not_expose_stderr(self):
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 1, '', 'private-provider-error-body')):
            with self.assertRaises(RuntimeError) as error:
                self.llm._codex('system', 'user')
        self.assertNotIn('private-provider-error-body', str(error.exception))


if __name__ == '__main__':
    unittest.main()
