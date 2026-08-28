from __future__ import annotations

import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "writing_check.py"
SPEC = importlib.util.spec_from_file_location("writing_check", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
writing_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(writing_check)


def scan_source(main_name: str, main_text: str) -> dict:
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name)
    paper = root / "paper"
    reports = root / "reports"
    paper.mkdir()
    reports.mkdir()
    main = paper / main_name
    main.write_text(main_text, encoding="utf-8")
    (reports / "PAPER_CONTENT_PLAN.md").write_text(
        "| 目标小节 | 核心论点 | 证据文件 | 预期表/图 | 状态 |\n",
        encoding="utf-8",
    )
    args = argparse.Namespace(
        paper_dir=paper,
        main=main,
        sections_dir=None,
        references=None,
        figures_dir=None,
        results_file=None,
        problem_analysis=None,
        all_results=None,
        json=False,
        output=None,
    )
    report = writing_check.scan(args)
    temporary.cleanup()
    return report


class EquationNumberingChecks(unittest.TestCase):
    def test_typst_requires_global_equation_numbering(self) -> None:
        report = scan_source("main.typ", "= Model\n\n$ x = 1 $\n")
        self.assertTrue(
            any("Typst 公式自动编号" in error for error in report["errors"]),
            report,
        )

    def test_latex_rejects_unnumbered_display_math(self) -> None:
        report = scan_source(
            "main.tex",
            "\\documentclass{article}\n\\begin{document}\n\\[x=1\\]\n\\end{document}\n",
        )
        self.assertTrue(
            any("未编号行间公式" in error for error in report["errors"]),
            report,
        )

    def test_latex_accepts_explicit_audited_unnumbered_display_math(self) -> None:
        report = scan_source(
            "main.tex",
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            "% equation-numbering: intentional-unnumbered reason=visual-definition\n"
            "\\[x=1\\]\n"
            "\\end{document}\n",
        )
        self.assertFalse(
            any("未编号行间公式" in error for error in report["errors"]),
            report,
        )


if __name__ == "__main__":
    unittest.main()
