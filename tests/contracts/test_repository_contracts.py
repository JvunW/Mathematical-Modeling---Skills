from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = ROOT / "skills"


def skill_directories() -> list[Path]:
    return sorted(path.parent for path in SKILLS_ROOT.glob("*/skills/*/SKILL.md"))


class RepositoryContracts(unittest.TestCase):
    def test_workflow_exposes_all_three_delivery_routes(self) -> None:
        workflow = (
            SKILLS_ROOT
            / "modeler"
            / "skills"
            / "mathmodel-workflow"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        for phrase in ("Typst/PDF", "LaTeX/PDF", "Word/DOCX"):
            self.assertIn(phrase, workflow)
        self.assertIn("export-math-docx", workflow)

    def test_no_unresolved_legacy_skill_references_remain(self) -> None:
        offenders: list[str] = []
        forbidden = ("superpowers:", "statistical-power", "parallel-cli")
        for source in sorted(ROOT.rglob("*.md")):
            if any(part in {".git", "evals"} for part in source.parts):
                continue
            text = source.read_text(encoding="utf-8-sig")
            for token in forbidden:
                if token in text:
                    offenders.append(f"{source.relative_to(ROOT)}: {token}")
        self.assertEqual(offenders, [])

    def test_known_over_rigid_rules_are_removed(self) -> None:
        checks = {
            "skills/coder/skills/test-driven-development/SKILL.md": (
                "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST",
                "Delete code. Start over with TDD.",
            ),
            "skills/coder/skills/mathmodel-drawio/SKILL.md": (
                "至少需要一张 `fig_roadmap`",
            ),
            "skills/modeler/skills/mathmodel-references/references/math-modeling-norms.md": (
                "VIF > 10 说明严重共线，应用岭回归或删除高相关特征",
            ),
        }
        offenders: list[str] = []
        for relative, phrases in checks.items():
            text = (ROOT / relative).read_text(encoding="utf-8-sig")
            offenders.extend(
                f"{relative}: {phrase}" for phrase in phrases if phrase in text
            )
        self.assertEqual(offenders, [])

    def test_literature_review_has_one_screening_heading(self) -> None:
        source = (
            SKILLS_ROOT / "writer" / "skills" / "literature-review" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(source.count("### Screening and Selection"), 1)

    def test_high_load_skill_entrypoints_use_progressive_disclosure(self) -> None:
        maximum_lines = {
            "skills/writer/skills/mathmodel-writing/SKILL.md": 240,
            "skills/modeler/skills/statistical-analysis/SKILL.md": 220,
            "skills/modeler/skills/uncertainty-and-units/SKILL.md": 210,
            "skills/coder/skills/test-driven-development/SKILL.md": 190,
            "skills/writer/skills/mathmodel-verification/SKILL.md": 220,
            "skills/writer/skills/mathmodel-humanizer-zh/SKILL.md": 180,
            "skills/coder/skills/systematic-debugging/SKILL.md": 190,
            "skills/writer/skills/paper-lookup/SKILL.md": 190,
        }
        too_long = []
        for relative, maximum in maximum_lines.items():
            line_count = len((ROOT / relative).read_text(encoding="utf-8-sig").splitlines())
            if line_count > maximum:
                too_long.append(f"{relative}: {line_count} > {maximum}")
        self.assertEqual(too_long, [])

        writing_references = ROOT / "skills/writer/skills/mathmodel-writing/references"
        for name in (
            "content_planning.md",
            "numeric_claims_and_evidence.md",
            "typst_route.md",
            "latex_route.md",
            "word_route.md",
            "citation_policy.md",
            "equation_numbering.md",
        ):
            self.assertTrue((writing_references / name).is_file(), name)

    def test_every_skill_has_valid_local_ui_metadata(self) -> None:
        missing = []
        malformed = []
        for directory in skill_directories():
            metadata = directory / "agents" / "openai.yaml"
            if not metadata.is_file():
                missing.append(str(directory.relative_to(ROOT)))
                continue
            text = metadata.read_text(encoding="utf-8-sig")
            if "display_name:" not in text or "short_description:" not in text:
                malformed.append(str(metadata.relative_to(ROOT)))
        self.assertEqual(missing, [])
        self.assertEqual(malformed, [])

    def test_plugin_manifests_match_discovered_skills(self) -> None:
        manifests = sorted(SKILLS_ROOT.glob("*/.codex-plugin/plugin.json"))
        self.assertEqual(len(manifests), 3)
        release = json.loads((ROOT / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
        discovered_by_role = {
            role.name: len(list((role / "skills").glob("*/SKILL.md")))
            for role in SKILLS_ROOT.iterdir()
            if role.is_dir()
        }
        total = 0
        for manifest in manifests:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            role = manifest.parents[1].name
            self.assertEqual(data["name"], role)
            self.assertEqual(data["skills"], "./skills/")
            self.assertRegex(data["version"], r"^\d+\.\d+\.\d+(?:\+codex\..+)?$")
            self.assertEqual(data["version"], release["plugins"][role])
            total += discovered_by_role[role]
        self.assertEqual(total, 23)

    def test_readme_documents_validation_delivery_and_recovery(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for heading in (
            "## 三个插件与 23 个 Skill",
            "## Typst、LaTeX 与 Word 三种交付路线",
            "## 验证仓库",
            "## 状态恢复与结果追溯",
        ):
            self.assertIn(heading, readme)

    def test_display_equation_policy_has_auditable_exemption(self) -> None:
        writing = (
            SKILLS_ROOT / "writer" / "skills" / "mathmodel-writing" / "SKILL.md"
        ).read_text(encoding="utf-8")
        numbering = (
            SKILLS_ROOT
            / "writer"
            / "skills"
            / "mathmodel-writing"
            / "references"
            / "equation_numbering.md"
        ).read_text(encoding="utf-8")
        verification = (
            SKILLS_ROOT
            / "writer"
            / "skills"
            / "mathmodel-verification"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        marker = "equation-numbering: intentional-unnumbered"
        self.assertIn("references/equation_numbering.md", writing)
        self.assertIn(marker, numbering)
        self.assertIn(marker, verification)


if __name__ == "__main__":
    unittest.main()
