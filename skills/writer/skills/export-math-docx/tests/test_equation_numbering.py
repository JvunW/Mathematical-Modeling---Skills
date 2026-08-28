from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from verify_omml import inspect_docx  # noqa: E402


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml"
    ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""


def write_docx(path: Path, equation_count: int) -> None:
    equations = "".join(
        f"""
        <w:p>
          <m:oMathPara><m:oMath><m:r><m:t>x={index}</m:t></m:r></m:oMath></m:oMathPara>
        </w:p>
        """
        for index in range(1, equation_count + 1)
    )
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <w:document
      xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
      xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
      <w:body>{equations}<w:sectPr/></w:body>
    </w:document>
    """
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("word/document.xml", document)


def load_numbering_module():
    module_path = SCRIPTS_DIR / "number_equations.py"
    if not module_path.is_file():
        raise AssertionError("missing deterministic DOCX equation-numbering module")
    spec = importlib.util.spec_from_file_location("number_equations", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EquationNumberingTests(unittest.TestCase):
    def test_verifier_rejects_unnumbered_display_equations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "paper.md"
            docx = root / "paper.docx"
            source.write_text("$$\nx=1\n$$\n\n$$\ny=2\n$$\n", encoding="utf-8")
            write_docx(docx, 2)

            report = inspect_docx(docx, source=source)

            self.assertFalse(report.valid)
            self.assertEqual(report.expected_numbered_equations, 2)
            self.assertEqual(report.equation_number_fields, 0)
            self.assertTrue(any("公式编号" in error for error in report.errors))

    def test_numberer_adds_continuous_fields_and_is_idempotent(self) -> None:
        number_equations = load_numbering_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "paper.md"
            docx = root / "paper.docx"
            source.write_text("$$\nx=1\n$$\n\n$$\ny=2\n$$\n", encoding="utf-8")
            write_docx(docx, 2)

            first = number_equations.number_docx_equations(docx)
            second = number_equations.number_docx_equations(docx)
            report = inspect_docx(docx, source=source)

            self.assertEqual(first, 2)
            self.assertEqual(second, 0)
            self.assertTrue(report.valid, report.errors)
            self.assertEqual(report.equation_number_fields, 2)
            self.assertEqual(report.equation_number_values, [1, 2])


if __name__ == "__main__":
    unittest.main()
