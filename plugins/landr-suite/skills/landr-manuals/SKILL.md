---
name: landr-manuals
description: Authoring and maintaining LandR module and model manuals — each module's own .Rmd manual and their aggregation into multi-module bookdown manuals such as LandR-Manual. Covers the module .Rmd structure (YAML, setup/badge chunks, text references, bibliography/CSL, figures/tables) and bookdown wiring (_bookdown.yml, _output.yml, forewords, rmd_files order). Use when writing or editing module documentation prose, building a combined manual, or adding a module chapter to LandR-Manual.
metadata:
  ecosystem: LandR
  version: "1.0"
---

# LandR module and model manuals

There are two levels of manual documentation, and this skill covers both.

## 1. Per-module manuals (`<Module>.Rmd`)

Each module folder has `<Module>.Rmd` (with rendered `.md`/`.html`). These are
bookdown-style R Markdown documents describing the module's purpose, parameters,
inputs/outputs, algorithms, and usage.

Standard structure (see `Biomass_core/Biomass_core.Rmd`):

```yaml
---
title: "LandR _Biomass_core_ Manual"
date: "Last updated: `r Sys.Date()`"
output:
  bookdown::html_document2:
    toc: true
    toc_float: true
    toc_depth: 4
    theme: sandstone
    number_sections: false
    df_print: paged
    keep_md: yes
bibliography: citations/references_Biomass_core.bib
citation-style: citations/ecology-letters.csl
link-citations: true
always_allow_html: true
---
```

Then, in order:
- **Text references** for LaTeX-safe captions: `(ref:Biomass-core) *Biomass_core*`.
- **`setup` chunk** (`include = FALSE`): sets `knitr::opts_chunk$set(echo = TRUE,
  eval = FALSE, cache = TRUE, ...)`, downloads the CSL if missing, and `Require()`s
  packages used for rendering (`SpaDES.core`, `data.table`, `kableExtra`, `SpaDES.docs`).
  Set `cache.rebuild = TRUE` when module code/metadata changed.
- **Badge chunk** (`eval = TRUE`): generates version/issue badges into `figures/`.
- **Body sections**: overview, parameters, input/output objects (often rendered from the
  module metadata via helpers), algorithm descriptions, and runnable examples.

Editing guidance:
- Keep the manual in sync with `defineModule()` metadata — parameter/input/output tables
  should reflect the current `.R`. When you change metadata, update the `.Rmd`.
- Citations go in the module's `citations/*.bib`; the CSL controls formatting.
- Prefer `eval = FALSE` for heavy code chunks unless a rendered result is needed.

## 2. Multi-module manuals (bookdown, e.g. `LandR-Manual`)

`PredictiveEcology/LandR-Manual` aggregates selected module manuals into one book. The
module sources are not stored in it: the `landr-manual.yaml` workflow checks each module
out (from `development`, set by `MODULE_REF`) into `modules/<Module>/`, and `build.R`
generates the chapters with `SpaDES.docs::prepManualRmds()`.

- `index.Rmd` — book front matter (`site: bookdown::bookdown_site`), preface, cover image,
  global bibliography/CSL.
- `_bookdown.yml` — book assembly:
  ```yaml
  book_filename: LandRManual
  output_dir: "docs"
  before_chapter_script: _common.R
  rmd_files:
    - index.Rmd
    - _manual_rmds/Biomass_core2.Rmd
    - LandR-dataModulesForeword.Rmd
    - _manual_rmds/Biomass_speciesData2.Rmd
    - ...
  ```
  The `rmd_files` list is the chapter order; forewords (`LandR-*Foreword.Rmd`) separate
  groups (data modules, validation modules).
- `_output.yml` — output formats (`bookdown::bs4_book` HTML; PDF via krantz.cls).
- `_common.R` — shared setup run before each chapter.
- Chapter sources `_manual_rmds/<Module>2.Rmd` are generated from each module's own
  `.Rmd` by `prepManualRmds()` during the build and deleted afterwards. Edit the module's
  `.Rmd`, not these.

### Adding a module to `LandR-Manual`

1. Add an `actions/checkout` step for the module to `.github/workflows/landr-manual.yaml`
   (path `modules/<Module>`).
2. Add `_manual_rmds/<Module>2.Rmd` to `rmd_files` in `_bookdown.yml` at the desired
   position (under the appropriate foreword).
3. Ensure its bibliography entries are available to the book's global bib/CSL.
4. Build with `source("build.R")`, which runs `bookdown::render_book()`; output goes to
   `docs/`.

Keep heading levels consistent so chapters nest correctly, and reuse text references for
figure/table captions that must survive PDF rendering.
