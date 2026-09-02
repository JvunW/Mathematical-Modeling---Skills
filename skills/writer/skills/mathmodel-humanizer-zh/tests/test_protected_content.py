from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
CHECKER = SKILL_ROOT / "scripts" / "check_protected_content.py"


class ProtectedContentCheckerTests(unittest.TestCase):
    def run_checker(self, before_text: str, after_text: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            before = root / "before.tex"
            after = root / "after.tex"
            report = root / "report.json"
            before.write_text(before_text, encoding="utf-8")
            after.write_text(after_text, encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(CHECKER),
                    str(before),
                    str(after),
                    "--json",
                    str(report),
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            payload = json.loads(report.read_text(encoding="utf-8")) if report.exists() else {}
        return completed, payload

    def test_style_only_rewrite_preserves_protected_content(self) -> None:
        before = r"""
实验包含 120 个样本，准确率为 93.5%。
模型满足 $x_1 + x_2 \le 10$，目标函数见式 \ref{eq:objective}。
\begin{equation}\label{eq:objective} z=2x_1+3x_2 \end{equation}
该方法来源于文献 \cite{smith2024}，结果见图 \includegraphics{figures/result.png}。
"""
        after = r"""
本次实验共使用 120 个样本，准确率达到 93.5%。
约束为 $x_1 + x_2 \le 10$，目标函数列于式 \ref{eq:objective}。
\begin{equation}\label{eq:objective} z=2x_1+3x_2 \end{equation}
方法依据文献 \cite{smith2024}，对应结果见图 \includegraphics{figures/result.png}。
"""
        completed, payload = self.run_checker(before, after)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["differences"], [])

    def test_changed_number_equation_and_citation_are_rejected(self) -> None:
        before = r"""
实验包含 120 个样本，准确率为 93.5%。
模型满足 $x_1 + x_2 \le 10$，参见 \cite{smith2024}。
"""
        after = r"""
实验包含 125 个样本，准确率为 95.0%。
模型满足 $x_1 + x_2 \le 12$，参见 \cite{smith2025}。
"""
        completed, payload = self.run_checker(before, after)
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        self.assertEqual(payload["status"], "fail")
        categories = {item["category"] for item in payload["differences"]}
        self.assertTrue({"numbers", "math", "citations"}.issubset(categories))

    def test_changed_chinese_unit_is_rejected_when_number_is_unchanged(self) -> None:
        before = "设备最大载荷为 50 千克。"
        after = "设备最大载荷为 50 克。"
        completed, payload = self.run_checker(before, after)
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        categories = {item["category"] for item in payload["differences"]}
        self.assertIn("measurements", categories)


if __name__ == "__main__":
    unittest.main()
