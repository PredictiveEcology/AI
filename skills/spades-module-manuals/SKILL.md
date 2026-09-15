---
name: spades-module-manuals
description: Per-module manuals for SpaDES modules — the module .Rmd/.md/.html manual that documents a single module (its purpose, parameters, inputs/outputs, and usage), and how such manuals may be aggregated. Use when writing or building a SpaDES module's own manual. PLACEHOLDER — to be written; for roxygen2 function docs and module-metadata `desc` fields use spades-code-documentation.
metadata:
  ecosystem: SpaDES
  version: "0.0"
---

# SpaDES module manuals

> **Placeholder — not yet written.** This skill will cover the **per-module manual** that
> ships with a SpaDES module — the `.Rmd` (rendered to `.md`/`.html`) that describes a
> single module: its purpose, parameters, inputs/outputs, and how to run it.

Each module scaffolded by `SpaDES.project::newModule()` includes a `<Module>.Rmd` manual
alongside the module `.R`. This skill will describe writing and building that manual, and
how a model system built on the toolkit (e.g. LandR) may aggregate per-module manuals into
a larger document.

For now, use the related skills:

- `spades-code-documentation` — roxygen2 function docs, in-code comments, and the
  module-metadata `desc` fields the manual draws on.
- `spades-module-anatomy` — the structure of the module `.R` the manual documents.
