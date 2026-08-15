---
name: typst-author
description: "Create, edit, compile and troubleshoot Typst documents. Use for .typ files, Typst syntax, formatting, templates, packages, compilation errors, document structure or migration from LaTeX."
---

# typst-author skill

## Overview

This skill helps agents generate, edit, and reason about Typst documents. It provides quick‑start examples, detailed workflows, and links to the full Typst documentation (guides, tutorials, reference).

## Minimal document example

```typst
#set document(title: "My Document", author: "Author Name")
#set page(numbering: "1")
#set text(lang: "en")

// Enable paragraph justification and character-level justification
#set par(
  justify: true,
  justification-limits: (
    tracking: (min: -0.012em, max: 0.012em),
    spacing: (min: 75%, max: 120%),
  )
)

#title[My Document]

= Heading 1

This is a paragraph in Typst.

== Heading 2

#lorem(50)
```

## Workflows

- **Creating a new Typst project**: Use the "Minimal document example" above as a starting point. Skim the tutorial for the basics ([references/typst-docs/tutorial/writing-in-typst.md](references/typst-docs/tutorial/writing-in-typst.md)), then create the `.typ` file(s). After each `.typ` edit, follow the post-edit formatting checks below when `typstyle` is available.
- **Editing existing content**: Locate the target text and apply changes; confirm syntax against the reference when needed ([references/typst-docs/reference/](references/typst-docs/reference/)). After each modified `.typ` file, follow the post-edit formatting checks below.
- **Formatting & Styling**: Consult the styling guide ([references/typst-docs/reference/styling.md](references/typst-docs/reference/styling.md)) for `set rule`, `show rule`, and custom themes.

## Documentation

- **Syntax & foundations**: `references/typst-docs/reference/syntax.md`
- **Styling & show/set rules**: `references/typst-docs/reference/styling.md`
- **Scripting & runtime behavior**: `references/typst-docs/reference/scripting.md`
- **Page setup & tables**: `references/typst-docs/guides/page-setup.md` and `references/typst-docs/guides/tables.md`
- **Task-oriented authoring help**: `references/typst-docs/tutorial/writing-in-typst.md`, `references/typst-docs/guides/*.md`, and `references/typst-docs/reference/**/*.md`

## Detailed instructions

1. **PRIORITY: Trust local documentation**. Your internal training data regarding Typst may be outdated or hallucinated. Always verify function names, parameters, and syntax against the bundled `references/typst-docs/` folder before generating code.
2. **Read the relevant documentation** using local file search and open tools on the paths above.
3. **Use local docs for syntax and reference questions**. Verify syntax, function names, parameters, and reference behavior from the bundled docs. Run a minimal Typst probe only when runtime or evaluation behavior remains unclear after checking the docs.
4. **Generate or modify the `.typ` source** according to the user's request.
5. **Run the post-edit formatting checks below** for every `.typ` file you created or edited in that pass.
6. **Validate** with `typst compile` after the formatting decision is complete when you created or edited `.typ` files, or when the user explicitly asks for verification (if tool access is allowed).
7. **Summarize touched files and outcomes**. Provide full `.typ` content only when the user requests it or when direct editing is not possible, and optionally include a rendered preview (PDF/HTML).

### Probing uncertain behavior

- Use a probe when the bundled docs do not settle runtime or evaluation behavior.
- Model the case with Typst scripting as described in [references/typst-docs/reference/scripting.md](references/typst-docs/reference/scripting.md).
- When a probe is necessary, prefer passing source through the current harness's stdin support; otherwise create a clearly named temporary `.typ` file in the workspace or OS temporary directory and remove it after the probe. Expose the value with `metadata(...) <probe>` and read it with `typst query <file-or-stdin> "<probe>" --field value --one`. See [references/typst-docs/reference/introspection/query.md](references/typst-docs/reference/introspection/query.md) and [references/typst-docs/reference/introspection/metadata.md](references/typst-docs/reference/introspection/metadata.md).

### Post-edit formatting checks

1. **Check whether `typstyle` is available** using the current harness's executable lookup or by running `typstyle --version`. If it is unavailable, skip the remaining formatting checks.
2. **After each `.typ` file modification, run `typstyle --check <file>`** for the file you just created or edited.
3. **If `typstyle --check` fails, inspect the formatter changes with `typstyle --diff <file>`** before deciding what to do.
4. **Apply formatting with `typstyle -i <file>`** only when the formatter changes are limited to a newly created file or to code you created or edited in the current task.
5. **Stop and ask the user when formatting would change untouched pre-existing code**. If the diff reaches outside your own edits, or if you cannot confidently prove that every formatter change is limited to your edits, ask instead of formatting.

## Quick syntax reference

### Critical distinctions

- **Arrays**: `(item1, item2)` (parentheses). See [references/typst-docs/reference/foundations/array.md](references/typst-docs/reference/foundations/array.md).
- **Dictionaries**: `(key: value, key2: value2)` (parentheses with colons). See [references/typst-docs/reference/foundations/dictionary.md](references/typst-docs/reference/foundations/dictionary.md).
- **Content blocks**: `[markup content]` (square brackets). See [references/typst-docs/reference/foundations/content.md](references/typst-docs/reference/foundations/content.md).
- **NO tuples**: Typst only has arrays.

### Hash usage (markup vs code)

- Use `#` to start a code expression inside markup or content blocks; it disambiguates code from text. This is required for content-producing function calls and field access in markup: `#figure[...]`, `#image("file.png")`, `text(...)[#numbering(...)]`.
- Do not use `#` inside code contexts (argument lists, code blocks, show-rule bodies). Example: `#figure(image("file.png"))` (no `#` before `image`).
- Reference: [references/typst-docs/reference/scripting.md](references/typst-docs/reference/scripting.md), [references/typst-docs/tutorial/writing-in-typst.md](references/typst-docs/tutorial/writing-in-typst.md)

```typst
// Incorrect (missing # inside content block)
text(...)[(numbering(...))]

// Correct
text(...)[(#numbering(...))]
```

### Styling rules: set vs show

- `set`: Set rule to configure optional parameters on element functions (style defaults scoped to the current block or file).
- `show`: Show rule to target selected elements and apply a set rule or transform/replace the element output.
- Use `set` for common styling; use `show` for selective or structural changes (e.g., `heading.where(level: 1)`, labels, text, regex).

```typst
// Set rule: configure optional parameters for an element type
#set heading(numbering: "I.")
#set text(font: "New Computer Modern")

// Show-set rule: apply a set rule only to selected elements
#show heading: set text(navy)

// Show transform rule: replace/reshape element output
#show heading: it => block[#emph(it.body)]
```

## Common mistakes to avoid

- Calling things "tuples" (Typst only has arrays).
- Using `[]` for arrays (use `()` instead).
- Accessing array elements with `arr[0]` (use `arr.at(0)`).
- Omitting `#` in markup/content blocks (e.g., `text(...)[numbering(...)]` should be `text(...)[#numbering(...)]`).
- Using `#` inside code contexts (e.g., `figure(#image("x.png"))` in an argument list).
- Mixing up content blocks `[]` with code blocks `{}`.
- Forgetting to include the namespace when accessing imported variables/functions (e.g., use `color.hsl` instead of just `hsl`).
- Using LaTeX syntax (do **NOT** use `\begin{...}`, `\section`, or other LaTeX commands).
- Hallucinating environments (e.g., `tabular` does not exist; use `table`).

## Advanced features

- **Custom themes**: See [references/typst-docs/reference/styling.md](references/typst-docs/reference/styling.md) for theme creation.
- **Scripting**: Use Typst's scripting capabilities ([references/typst-docs/reference/scripting.md](references/typst-docs/reference/scripting.md)) for automatic generation.
- **Math and visualisation**: Reference [references/typst-docs/reference/math/](references/typst-docs/reference/math/) and [references/typst-docs/reference/visualize/](references/typst-docs/reference/visualize/) for formulas and diagrams.

### For large projects

When working on large projects, consider organizing the project across multiple files.

- Use `#include "file.typ"` to split into multiple files
- Relevant documentation: [references/typst-docs/reference/foundations/module.md](references/typst-docs/reference/foundations/module.md)

## Troubleshooting

### Missing font warnings

If you see "unknown font family" warnings, remove the font specification to use system defaults. Note: Font warnings don't prevent compilation; the document will use fallback fonts.

### Template/Package not found

If import fails with "package not found":

- Verify exact package name and version on Typst Universe.
- Check for typos in `@preview/package:version` syntax.

### Compilation errors

Common fixes:

- **"expected content, found ..."**: You're using code where markup is expected - wrap in `#{ }` or use proper syntax.
- **"expected expression, found ..."**: Missing `#` (or `#(...)`) in markup/content blocks.
- **"unknown variable"**: Check spelling, ensure imports are correct.
- **Array/dictionary errors**: Review syntax - use `()` for both, dictionaries need `key: value`, singleton arrays are `(elem,)`.
