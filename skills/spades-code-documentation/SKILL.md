---
name: spades-code-documentation
description: Code-level documentation for the SpaDES toolkit — in-code comments, SpaDES module metadata descriptions (defineModule description/keywords/authors and the desc fields of defineParameter, expectsInput, createsOutput), and package roxygen2 blocks (@param, @return, @export, @keywords internal, @importFrom, @rdname). Use when documenting functions, describing parameters or input/output objects, writing or improving comments, or updating NEWS.md. For per-module manuals use spades-module-manuals; for the package build/check and man/ + NAMESPACE regeneration use spades-package-development.
metadata:
  ecosystem: SpaDES
  version: "1.0"
---

# SpaDES code-level documentation

Covers documentation that lives inside code: in-code comments, SpaDES module metadata
descriptions, and package roxygen2 blocks. Prose module manuals are in
`spades-module-manuals`; the build/check workflow that regenerates `man/` and `NAMESPACE`
is in `spades-package-development`.

## Audience and style

SpaDES is used by people who are **not primarily programmers**. Write docs for ecologists
and scientists of other disciplines that are not computer scientists/software engineers:
minimize jargon, and briefly define any technical term you must use.

**Respect the existing documentation style.** Match the surrounding file's tone, level of
detail, wording, and markup. When a change to the established style or structure seems
warranted, check it with the user and justify it before applying — do not silently
restyle existing docs.

## In-code comments

- Comment the *why*, not the *what*. Skip comments that merely restate the code.
- In pipelines, put the comment on the line **before** the step it explains, not inline.
- Match the comment convention already used in the file (SpaDES code commonly uses `#` for
  explanatory comments; some files use `##`). Do not introduce a new convention mid-file.

## SpaDES module metadata descriptions

The metadata `desc` fields in `<Module>.R` are the primary user-facing documentation of a
module's interface — often the first thing another modeller reads. Write them carefully:

- `defineModule(... description=, keywords=, authors=)` — a clear one-to-two-sentence
  module summary, searchable keywords, and correct authorship. Preserve existing authors.
- `defineParameter(name, class, default, min, max, desc=)` — describe the parameter's
  meaning, **units**, accepted values, and the effect of its default. For multi-line
  descriptions, match how the module already assembles the string (e.g. `paste(...)`).
- `expectsInput(objectName, objectClass, desc=, sourceURL=)` and
  `createsOutput(objectName, objectClass, desc=)` — state what the object represents, its
  structure (e.g. the columns of a `data.table`), and, for inputs, where it comes from
  (`sourceURL`).

Keep these descriptions consistent with the module's `.Rmd` manual and with any downstream
module that consumes the same object name — a shared object name is a contract.

## Package roxygen2 blocks

Functions in the toolkit packages (`SpaDES.core`, `SpaDES.tools`, `reproducible`,
`Require`, `SpaDES.project`, `quickPlot`, and companions) — and a module's own functions
in its `R/` folder — are documented with roxygen2. `man/*.Rd` and `NAMESPACE` are
**generated — never edit them by hand**.

```r
#' One-line title
#'
#' A paragraph describing what the function does. Cross-reference with
#' \code{\link{otherFn}} and lay out steps with \enumerate{...} where it helps.
#'
#' @param a a function parameter, with a description of its structure (e.g. the columns of a
#'   \code{data.table} or the elements of a \code{list}).
#' @param b another function parameter.
#'
#' @return type/class of returned object and short description if needed.
#'
#' @export
#' @importFrom pkg fun
#' @examples
#' \dontrun{
#'   a <- 1
#'   b <- 2
#'   myFunction(a, b)
#' }
myFunction <- function(a, b) { ... }
```

Guidance:

- Every **exported** function needs a title, a description, all `@param`, a `@return`, and
  `@export`. Document the columns/structure of any rich data object a function takes or
  returns.
- **Mark internal (non-exported) functions with `@keywords internal`** (and `@noRd` if no
  help page is wanted), so the reference site stays focused on the user-facing API. Apply
  this even where existing code is inconsistent about it. **Before adding `@keywords
  internal` to an *exported* function, check with the user** — it changes how that function
  is surfaced.
- Use `@importFrom pkg fun` rather than editing `NAMESPACE`; run the
  `spades-package-development` document/check workflow afterward.
- Group related functions on one help page with `@rdname` / `@describeIn`.
- Use `@inheritParams` to avoid duplicating parameter docs shared across functions. Before
  doing so, confirm the inherited parameter genuinely matches — same meaning, class, and
  accepted values — in both the source and target function.
- **Never reorder a function's arguments** as part of a documentation change.
- Some toolkit code uses `\code{...}` Rd markup; match the surrounding file rather than
  mixing markdown and Rd in one block.

## NEWS.md

- Add a user-facing entry for behavioral changes, new functions, or fixes. Group changes by type (e.g. enhancements, bug fixes, new functions, etc.)
- Both packages and modules keep a `NEWS.md`; keep entries concise and grouped by version.
- Write entries in plain language for the non-programmer reader, as above.

<!--Note to Ceres: request input from Eliot and Alex.-->
