---
name: landr-code-documentation
description: Code-level documentation across the LandR ecosystem — in-code comments, SpaDES module metadata descriptions (defineModule description/keywords and the desc fields of defineParameter, expectsInput, createsOutput), package roxygen2 blocks (@param, @return, @export, @examples, @rdname, @importFrom), and NEWS.md prose. Use when documenting functions, describing parameters or input/output objects, writing or improving comments, or updating changelogs. For rendering package man/ and NAMESPACE, use landr-package-maintenance; for module/model manuals, use landr-manuals.
metadata:
  ecosystem: LandR
  version: "1.0"
---

# LandR code-level documentation

Covers documentation that lives inside code: comments, module metadata descriptions, and
package roxygen2 blocks. (Prose manuals are in `landr-manuals`; regenerating `man/` and
NAMESPACE is in `landr-package-maintenance`.)

## In-code comments

- Comment the *why*, not the *what*. Skip comments that merely restate the code.
- In pipelines, put the comment on the line **before** the step it explains.
- LandR code uses `##` for explanatory comments and single `#` inline sparingly.

## SpaDES module metadata descriptions

Metadata `desc` fields are the primary user-facing documentation of a module's interface;
write them carefully in `<Module>.R`:

- `defineModule(... description=, keywords=, authors=)` — a clear one-to-two sentence
  module summary and searchable keywords.
- `defineParameter(name, class, default, min, max, desc=)` — describe meaning, units,
  accepted values, and the effect of the default. For multi-line descriptions LandR uses
  `paste(...)` to assemble the string.
- `expectsInput(objectName, objectClass, desc=, sourceURL=)` and
  `createsOutput(objectName, objectClass, desc=)` — state what the object represents, its
  structure (e.g. `data.table` columns), and where inputs come from (`sourceURL`).

Keep these descriptions consistent with the module `.Rmd` manual and with any downstream
module that consumes the same object name.

## Package roxygen2 blocks

Functions in `LandR/`, `LandR.CS/`, `fireSenseUtils/` are documented with roxygen2
(`man/*.Rd` and `NAMESPACE` are generated — never edit by hand). Block pattern:

```r
#' Add cohorts to \code{cohortData} and \code{pixelGroupMap}
#'
#' One-line title above, then a paragraph describing what the function does.
#' Use \code{\link{otherFn}} to cross-reference and \enumerate{...} for steps.
#'
#' @param newPixelCohortData A \code{data.table} of new cohorts. Columns it must
#'   have: \code{pixelGroup}, \code{speciesCode}, \code{age}, \code{ecoregionGroup}.
#' @param pixelGroupMap A \code{RasterLayer} whose values are pixel-group ids.
#'
#' @return A \code{list} with updated \code{cohortData} and \code{pixelGroupMap}.
#'
#' @export
#' @importFrom data.table setkey
#' @examples
#' \dontrun{
#'   addCohorts(newPixelCohortData, cohortData, pixelGroupMap)
#' }
addCohorts <- function(newPixelCohortData, cohortData, pixelGroupMap) { ... }
```

Guidance:
- Every exported function needs a title, description, all `@param`, a `@return`, and
  `@export`. Document data-object columns explicitly (LandR functions pass rich
  `data.table`s).
- Use `@importFrom pkg fun` rather than editing NAMESPACE; run `devtools::document()` after.
- Group related functions with `@rdname` / `@describeIn` when they share a help page.
- Existing LandR code sometimes uses `\code{...}` (Rd) markup; match the surrounding style
  in a given file rather than mixing markdown and Rd.
- After writing blocks, regenerate docs via the `landr-package-maintenance` workflow.

## NEWS.md

- Add a user-facing entry for behavioral changes, new functions, or fixes.
- Modules and packages both keep `NEWS.md`; keep entries concise and grouped by version.
