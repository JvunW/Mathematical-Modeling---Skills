from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "validate_repo.py"


class ValidateRepoTests(unittest.TestCase):
    def test_quick_validation_writes_machine_readable_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "validation.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--quick",
                    "--skip-tests",
                    "--json",
                    str(report),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "pass")
            self.assertEqual(data["skill_count"], 23)
            self.assertEqual(data["plugin_count"], 3)
            self.assertGreater(data["python_file_count"], 0)


if __name__ == "__main__":
    unittest.main()
