# Third-Party Notices

This distribution contains adapted open-source Agent Skills and documentation. Local adaptations include frontmatter normalization, role integration, portable paths, Codex metadata, and cross-platform wording or helper scripts.

## K-Dense Scientific Agent Skills

Source: <https://github.com/K-Dense-AI/scientific-agent-skills>

Included or adapted skills:

- `experimental-design`
- `literature-review`
- `paper-lookup`
- `statistical-analysis`
- `uncertainty-and-units`

Upstream author: K-Dense Inc.  
Upstream license: MIT. The upstream repository and the included skills identify the MIT license.  
Copyright notice reported by upstream: Copyright (c) 2025 K-Dense Inc.

## Superpowers

Source: <https://github.com/obra/superpowers>

Included or adapted skills:

- `systematic-debugging`
- `test-driven-development`
- `verification-before-completion`

Upstream author: Jesse Vincent / Prime Radiant.  
Upstream license: MIT.  
Copyright notice reported by upstream: Copyright (c) 2025 Jesse Vincent.

## CiteCheck

Source: <https://github.com/color4-alt/CiteCheck>

Included or adapted skill:

- `citation-verification`

Upstream license: MIT.  
Copyright notice reported by upstream: Copyright (c) 2026 Paper Citation Check Team.

## Typst documentation

Source: <https://github.com/typst/typst>

The `typst-author/references/typst-docs/` directory contains documentation derived from the Typst project.  
Upstream license: Apache License 2.0.

## humanizer-zh

Source: <https://github.com/ai-zixun/humanizer-zh>

Included or adapted skill:

- `mathmodel-humanizer-zh`

Pinned upstream release: `v1.3.0` (`0ba21f7`).
Upstream license: MIT.
Copyright notice reported by upstream: Copyright (c) 2026 aizixun.

The local adaptation keeps neutral Chinese prose guidance for both initial drafting and final polishing while adding mathematical-paper evidence protection, academic-integrity boundaries, and a deterministic protected-content checker. Author-voice profiles, named-author imitation, blog/newsletter corpus routing, and AI-detection-evasion claims are not included.

## Academic figure system references

The expanded `mathmodel-figure-templates` skill adapts architecture and workflow ideas from the following MIT-licensed sources:

- `0xE1337/thesis-figure-skill`, pinned revision `ffe6d07c7d4bfd7429d2e2437198013fb8e6f27a`, MIT. Local adaptations include Conclusion-first and Module-first figure design, reusable TikZ component categories, skeleton-driven composition, and compile/lint/diff QA concepts.
- `RTCartist/paper-suite`, pinned revision `4e505bb988e6c77d7d25b6ac268b9dcfc7eea640`, MIT. Local adaptations include engine routing, venue/style profiles, Figure Contract separation, and anti-defect QA layers.
- `SyntaxSmith/nature-writing-skill`, pinned revision `c1a8716047b6304d922b9528a18421203e3e7acc`. Its README declares the code/Markdown structure and extraction framework MIT. Local files do not reproduce its verbatim paper quotations or extracted corpus text.

Two additional repositories informed clean-room design review only: `Noi1r/tikz-academic` at `720e801f2af0b6731ca0aed35c44565c481ebcab` and `Patrick-Healy/tikz-diagrams-skill` at `abfcb38914bc93a7448c63ef8c12506e04f9254b`. No root license file was found in those pinned revisions, so their source code, templates, and prose are not copied into this distribution.

## License preservation

Redistributors must preserve the copyright notices and license terms required by each upstream project. Complete license texts are included in [`licenses/MIT.txt`](licenses/MIT.txt) and [`licenses/Apache-2.0.txt`](licenses/Apache-2.0.txt). This notice does not change the license of original MathModel Skills content.
