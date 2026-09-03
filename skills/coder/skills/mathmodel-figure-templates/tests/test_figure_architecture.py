from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
import json
import importlib.util
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"


class FigureArchitectureTests(unittest.TestCase):
    def test_engine_style_and_qa_layers_are_discoverable(self) -> None:
        expected = (
            "references/figure-engine/tikz.md",
            "references/figure-engine/matplotlib.md",
            "references/figure-engine/drawio.md",
            "references/figure-engine/mermaid.md",
            "references/figure-style/nature.md",
            "references/figure-style/science.md",
            "references/figure-style/ieee.md",
            "references/figure-style/mcm.md",
            "references/figure-style/cumcm.md",
            "references/figure-qa/qa-workflow.md",
            "references/figure-qa/visual-checklist.md",
        )
        missing = [relative for relative in expected if not (SKILL_ROOT / relative).is_file()]
        self.assertEqual(missing, [])

    def test_requested_tikz_components_are_packaged(self) -> None:
        expected = (
            "attention-heatmap.tex",
            "bar-chart.tex",
            "line-chart.tex",
            "formula-box.tex",
            "pipeline-stages.tex",
            "layer-stack.tex",
            "feedback-loop.tex",
            "multi-zone-palette.tex",
        )
        snippets = SKILL_ROOT / "assets" / "tikz-snippets"
        missing = [name for name in expected if not (snippets / name).is_file()]
        self.assertEqual(missing, [])
        self.assertTrue((SKILL_ROOT / "assets/example-skeletons/pipeline.tex").is_file())
        self.assertTrue((SKILL_ROOT / "assets/example-skeletons/central-hero.tex").is_file())

    def test_requested_tikz_components_compile_in_a_common_preamble(self) -> None:
        engine = shutil.which("xelatex")
        if not engine:
            self.skipTest("XeLaTeX is unavailable")
        snippets = SKILL_ROOT / "assets" / "tikz-snippets"
        names = (
            "attention-heatmap.tex", "bar-chart.tex", "line-chart.tex", "formula-box.tex",
            "pipeline-stages.tex", "layer-stack.tex", "feedback-loop.tex", "multi-zone-palette.tex",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in names:
                tex = root / name
                tex.write_text(
                    "\\documentclass{article}\n"
                    "\\usepackage[paperwidth=22cm,paperheight=12cm,margin=4mm]{geometry}\n"
                    "\\usepackage{amsmath}\n"
                    "\\usepackage{tikz}\n"
                    "\\usetikzlibrary{arrows.meta,positioning,fit,backgrounds}\n"
                    "\\pagestyle{empty}\n"
                    "\\begin{document}\\noindent\n"
                    "\\begin{tikzpicture}\n"
                    + (snippets / name).read_text(encoding="utf-8")
                    + "\n\\end{tikzpicture}\n\\end{document}\n",
                    encoding="utf-8",
                )
                completed = subprocess.run(
                    [engine, "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error", tex.name],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 0, f"{name}\n{completed.stdout[-3000:]}\n{completed.stderr[-3000:]}")

    def test_skill_entrypoint_encodes_conclusion_first_module_first_workflow(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8-sig")
        for phrase in (
            "Conclusion-first",
            "Hero",
            "主流程",
            "辅助 Panel",
            "完整编译",
            "视觉 QA",
        ):
            self.assertIn(phrase, text)

    def test_static_safety_checker_rejects_shell_escape(self) -> None:
        checker = SCRIPTS / "check_tikz_safety.py"
        with tempfile.TemporaryDirectory() as directory:
            tex = Path(directory) / "unsafe.tex"
            tex.write_text(
                "\\documentclass{article}\n"
                "\\immediate\\write18{powershell -Command whoami}\n"
                "\\begin{document}x\\end{document}\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, str(checker), str(tex)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 1)
        self.assertIn("shell escape", (completed.stdout + completed.stderr).lower())

    def test_compile_render_produces_pdf_and_png(self) -> None:
        if not shutil.which("xelatex") or not shutil.which("pdftoppm"):
            self.skipTest("XeLaTeX or pdftoppm is unavailable")
        compiler = SCRIPTS / "compile_render.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tex = root / "smoke.tex"
            tex.write_text(
                "\\documentclass{article}\n"
                "\\usepackage[paperwidth=4cm,paperheight=3cm,margin=2mm]{geometry}\n"
                "\\usepackage{tikz}\n"
                "\\pagestyle{empty}\n"
                "\\begin{document}\n"
                "\\begin{tikzpicture}\\node[draw] {QA};\\end{tikzpicture}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, str(compiler), str(tex), "--dpi", "96"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            output = completed.stdout + completed.stderr
            self.assertEqual(completed.returncode, 0, output)
            self.assertTrue((root / "smoke.pdf").is_file(), output)
            self.assertTrue((root / "smoke.png").is_file(), output)

    def test_qa_runner_writes_machine_readable_gate_report(self) -> None:
        if not shutil.which("xelatex") or not shutil.which("pdftoppm"):
            self.skipTest("XeLaTeX or pdftoppm is unavailable")
        runner = SCRIPTS / "run_figure_qa.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tex = root / "qa.tex"
            report = root / "qa-report.json"
            tex.write_text(
                "\\documentclass{article}\n"
                "\\usepackage[paperwidth=5cm,paperheight=3cm,margin=2mm]{geometry}\n"
                "\\usepackage{tikz}\n"
                "\\pagestyle{empty}\n"
                "\\begin{document}\n"
                "\\begin{tikzpicture}\\node[draw] (model) {Model};\\end{tikzpicture}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, str(runner), str(tex), "--report", str(report), "--dpi", "96"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            output = completed.stdout + completed.stderr
            self.assertEqual(completed.returncode, 0, output)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertIn(payload["status"], {"pass", "pass_with_skips", "pass_with_advisories"})
            self.assertEqual(payload["source"], str(tex.resolve()))

    def test_compile_render_rejects_accidental_multi_page_figure(self) -> None:
        if not shutil.which("xelatex") or not shutil.which("pdftoppm") or not shutil.which("pdfinfo"):
            self.skipTest("XeLaTeX or Poppler is unavailable")
        compiler = SCRIPTS / "compile_render.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tex = root / "multipage.tex"
            tex.write_text(
                "\\documentclass{article}\n"
                "\\usepackage{tikz}\n"
                "\\begin{document}\n"
                "\\begin{tikzpicture}\\node[draw] {One};\\end{tikzpicture}\n"
                "\\newpage\n"
                "\\begin{tikzpicture}\\node[draw] {Two};\\end{tikzpicture}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, str(compiler), str(tex), "--dpi", "72"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 1)
            self.assertIn("single-page", (completed.stdout + completed.stderr).lower())

    def test_nature_style_keeps_vector_text_and_verified_size_contract(self) -> None:
        source = SCRIPTS / "figure_style.py"
        spec = importlib.util.spec_from_file_location("figure_style", source)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        profile = module.get_profile("nature")
        self.assertEqual(profile.rcparams["svg.fonttype"], "none")
        self.assertEqual(profile.rcparams["pdf.fonttype"], 42)
        self.assertEqual(profile.panel_label_size_pt, 8.0)
        self.assertGreaterEqual(profile.single_column_width_mm, 88.0)
        self.assertLessEqual(profile.single_column_width_mm, 90.0)

    def test_nature_style_exports_editable_svg_pdf_and_preview(self) -> None:
        if importlib.util.find_spec("matplotlib") is None:
            self.skipTest("matplotlib is unavailable")
        source = SCRIPTS / "figure_style.py"
        spec = importlib.util.spec_from_file_location("figure_style_render", source)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.apply_profile("nature")
        import matplotlib.pyplot as plt

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            figure, axis = plt.subplots(figsize=module.figure_size("nature"))
            axis.plot([0, 1, 2], [0.2, 0.8, 0.6], marker="o", label="Model")
            axis.set_xlabel("Input")
            axis.set_ylabel("Response")
            module.add_panel_label(axis, "a", "nature")
            axis.legend()
            outputs = module.save_figure(figure, root / "nature-smoke", dpi=96)
            plt.close(figure)
            self.assertTrue(all(path.is_file() and path.stat().st_size > 500 for path in outputs))
            self.assertIn("<text", (root / "nature-smoke.svg").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
