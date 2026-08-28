from __future__ import annotations

import re
import unittest
from pathlib import Path


TEMPLATES = Path(__file__).resolve().parents[1] / "assets" / "templates"
TYPST_NUMBERING = re.compile(
    r"#set\s+math\.equation\s*\([^)]*numbering\s*:\s*\"\(1\)\"",
    re.DOTALL,
)
LATEX_UNNUMBERED = re.compile(
    r"(?<!\\)\\\[|\\begin\{(?:equation|align|alignat|gather|multline)\*\}",
    re.DOTALL,
)
LATEX_NUMBERED_ENV = re.compile(
    r"\\begin\{(?:equation|align|alignat|gather|multline)\}(.*?)"
    r"\\end\{(?:equation|align|alignat|gather|multline)\}",
    re.DOTALL,
)


class TemplateEquationNumberingTests(unittest.TestCase):
    def test_every_typst_template_enables_equation_numbering(self) -> None:
        invalid = []
        for main in sorted(TEMPLATES.rglob("main.typ")):
            count = len(TYPST_NUMBERING.findall(main.read_text(encoding="utf-8-sig")))
            if count != 1:
                invalid.append(f"{main.relative_to(TEMPLATES)}: {count}")
        self.assertEqual(invalid, [])

    def test_latex_templates_have_no_unnumbered_display_math(self) -> None:
        offenders = []
        for source in sorted(TEMPLATES.rglob("*.tex")):
            if LATEX_UNNUMBERED.search(source.read_text(encoding="utf-8-sig")):
                offenders.append(str(source.relative_to(TEMPLATES)))
        self.assertEqual(offenders, [])

    def test_latex_numbered_equations_have_labels(self) -> None:
        offenders = []
        for source in sorted(TEMPLATES.rglob("*.tex")):
            text = source.read_text(encoding="utf-8-sig")
            for index, body in enumerate(LATEX_NUMBERED_ENV.findall(text), start=1):
                if not re.search(r"\\label\{eq:[^}]+\}", body):
                    offenders.append(f"{source.relative_to(TEMPLATES)}#{index}")
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
