#!/usr/bin/env python3
"""Add visible, continuous Word fields to DOCX display equations."""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
OMML_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
TABLE_CAPTION = "CodexEquationNumber"
SEQ_RE = re.compile(r"\bSEQ\s+Equation\b", re.IGNORECASE)


class EquationNumberingError(RuntimeError):
    """Raised when a DOCX cannot be numbered without risking corruption."""


def _qname(namespace: str, local_name: str) -> str:
    return f"{{{namespace}}}{local_name}"


def _register_source_namespaces(xml_bytes: bytes) -> None:
    """Preserve the source document's namespace prefixes during serialization."""
    for _, declaration in ElementTree.iterparse(
        io.BytesIO(xml_bytes), events=("start-ns",)
    ):
        prefix, uri = declaration
        try:
            ElementTree.register_namespace(prefix, uri)
        except ValueError:
            # ElementTree reserves automatically generated prefixes such as ns0.
            continue


def _word_element(local_name: str, **attributes: str) -> ElementTree.Element:
    return ElementTree.Element(
        _qname(WORD_NS, local_name),
        {
            _qname(WORD_NS, key.replace("_", "-")): value
            for key, value in attributes.items()
        },
    )


def _append_cell_properties(cell: ElementTree.Element, width: str) -> None:
    properties = _word_element("tcPr")
    properties.append(_word_element("tcW", w=width, type="pct"))
    properties.append(_word_element("vAlign", val="center"))
    cell.append(properties)


def _empty_paragraph() -> ElementTree.Element:
    return _word_element("p")


def _number_paragraph(number: int) -> ElementTree.Element:
    paragraph = _word_element("p")
    properties = _word_element("pPr")
    properties.append(_word_element("jc", val="right"))
    properties.append(_word_element("spacing", before="0", after="0"))
    paragraph.append(properties)

    opening = _word_element("r")
    opening_text = _word_element("t")
    opening_text.text = "("
    opening.append(opening_text)
    paragraph.append(opening)

    field = _word_element("fldSimple", instr=" SEQ Equation \\* ARABIC ")
    result_run = _word_element("r")
    result_text = _word_element("t")
    result_text.text = str(number)
    result_run.append(result_text)
    field.append(result_run)
    paragraph.append(field)

    closing = _word_element("r")
    closing_text = _word_element("t")
    closing_text.text = ")"
    closing.append(closing_text)
    paragraph.append(closing)
    return paragraph


def _equation_table(
    equation_paragraph: ElementTree.Element, number: int
) -> ElementTree.Element:
    """Lay out a centered equation and a right-aligned number without borders."""
    table = _word_element("tbl")
    properties = _word_element("tblPr")
    properties.append(_word_element("tblW", w="5000", type="pct"))
    properties.append(_word_element("tblLayout", type="fixed"))
    properties.append(_word_element("tblCaption", val=TABLE_CAPTION))
    borders = _word_element("tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        borders.append(
            _word_element(edge, val="nil", sz="0", space="0", color="auto")
        )
    properties.append(borders)
    table.append(properties)

    grid = _word_element("tblGrid")
    for width in ("630", "7740", "630"):
        grid.append(_word_element("gridCol", w=width))
    table.append(grid)

    row = _word_element("tr")
    left = _word_element("tc")
    _append_cell_properties(left, "350")
    left.append(_empty_paragraph())
    row.append(left)

    middle = _word_element("tc")
    _append_cell_properties(middle, "4300")
    middle.append(equation_paragraph)
    row.append(middle)

    right = _word_element("tc")
    _append_cell_properties(right, "350")
    right.append(_number_paragraph(number))
    row.append(right)

    table.append(row)
    return table


def _is_numbering_table(table: ElementTree.Element) -> bool:
    caption = table.find(
        f"./{_qname(WORD_NS, 'tblPr')}/{_qname(WORD_NS, 'tblCaption')}"
    )
    return (
        caption is not None
        and caption.attrib.get(_qname(WORD_NS, "val")) == TABLE_CAPTION
    )


def _has_numbering_table_ancestor(
    element: ElementTree.Element,
    parents: dict[ElementTree.Element, ElementTree.Element],
) -> bool:
    current = parents.get(element)
    while current is not None:
        if current.tag == _qname(WORD_NS, "tbl") and _is_numbering_table(current):
            return True
        current = parents.get(current)
    return False


def _field_values(root: ElementTree.Element) -> list[int]:
    values: list[int] = []
    for field in root.findall(f".//{_qname(WORD_NS, 'fldSimple')}"):
        instruction = field.attrib.get(_qname(WORD_NS, "instr"), "")
        if not SEQ_RE.search(instruction):
            continue
        text = "".join(
            node.text or "" for node in field.findall(f".//{_qname(WORD_NS, 't')}")
        ).strip()
        if text.isdigit():
            values.append(int(text))
    return values


def _number_document_xml(xml_bytes: bytes) -> tuple[bytes, int]:
    _register_source_namespaces(xml_bytes)
    try:
        root = ElementTree.fromstring(xml_bytes)
    except ElementTree.ParseError as exc:
        raise EquationNumberingError(f"word/document.xml 无法解析: {exc}") from exc

    parents = {child: parent for parent in root.iter() for child in parent}
    paragraphs = [
        paragraph
        for paragraph in root.iter(_qname(WORD_NS, "p"))
        if paragraph.find(f".//{_qname(OMML_NS, 'oMathPara')}") is not None
        and not _has_numbering_table_ancestor(paragraph, parents)
    ]
    if not paragraphs:
        return xml_bytes, 0

    existing_values = _field_values(root)
    next_number = max(existing_values, default=0) + 1
    inserted = 0
    for paragraph in paragraphs:
        parent = parents.get(paragraph)
        if parent is None:
            raise EquationNumberingError("无法定位行间公式的父节点")
        position = list(parent).index(paragraph)
        parent.remove(paragraph)
        parent.insert(position, _equation_table(paragraph, next_number))
        if (
            parent.tag == _qname(WORD_NS, "tc")
            and position == len(parent) - 1
        ):
            parent.insert(position + 1, _empty_paragraph())
        inserted += 1
        next_number += 1

    return (
        ElementTree.tostring(root, encoding="utf-8", xml_declaration=True),
        inserted,
    )


def number_docx_equations(docx: Path) -> int:
    """Number every unnumbered OMML display paragraph in-place, atomically."""
    resolved = docx.expanduser().resolve()
    if not resolved.is_file() or not zipfile.is_zipfile(resolved):
        raise EquationNumberingError(f"不是有效的 DOCX 文件: {resolved}")

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{resolved.stem}-equations-",
        suffix=".tmp.docx",
        dir=resolved.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(resolved, "r") as source_archive:
            try:
                document_xml = source_archive.read("word/document.xml")
            except KeyError as exc:
                raise EquationNumberingError("DOCX 缺少 word/document.xml") from exc
            numbered_xml, inserted = _number_document_xml(document_xml)
            if inserted == 0:
                return 0

            with zipfile.ZipFile(
                temporary, "w", compression=zipfile.ZIP_DEFLATED
            ) as destination_archive:
                destination_archive.comment = source_archive.comment
                for item in source_archive.infolist():
                    data = (
                        numbered_xml
                        if item.filename == "word/document.xml"
                        else source_archive.read(item.filename)
                    )
                    destination_archive.writestr(item, data)

        if not zipfile.is_zipfile(temporary):
            raise EquationNumberingError("编号后的临时 DOCX 不是有效 ZIP 包")
        os.replace(temporary, resolved)
        return inserted
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path, help="需要补充公式编号的 DOCX")
    args = parser.parse_args()
    try:
        inserted = number_docx_equations(args.docx)
    except EquationNumberingError as exc:
        parser.error(str(exc))
    print(json.dumps({"docx": str(args.docx.resolve()), "inserted": inserted}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
