# convertToPackage() traps

During `testthat-module`, the module is converted to an R package and installed. These
are the failure modes that only appear on that path.

## Imports

`convertToPackage()` generates an `imports.R` holding `#' @import <pkg>` for every
`reqdPkgs` entry, so module code can call those packages unqualified. It then removes
any package already named in an explicit `@importFrom`
(`SpaDES.core/R/convertToPackage.R:352-360`). The intent is standard package practice:
if you are specific about one function, be specific about all of them.

The consequence is not obvious. One `@importFrom data.table set` in any `R/` file
means data.table gets no blanket import, and every other data.table call in the module
is unresolved at install time.

- **Symptom:** `could not find function "data.table"` (or `setDT`, `fwrite`, ...) in
  `testthat-module` only.
- **Confusing detail:** `:=`, `.N`, `.SD` and `by=` keep working. data.table's
  `cedta()` ("Calling Environment Data Table Aware") treats a namespace as aware if it
  imports *anything* from data.table, so the NSE machinery is happy while ordinary
  function lookup fails.
- **Fix:** add the missing functions to the `@importFrom`, in the file that uses them:

  ```r
  #' @importFrom data.table data.table
  noSpeciesCoreInputs <- function(rasterToMatch) { ... }
  ```

- **Do not** "fix" it by deleting the `@importFrom` to get the blanket import back.
  That works, and it reverses a deliberate convention.

The same applies to any package in `reqdPkgs`, not just data.table.

## Collate

`R CMD INSTALL` refuses a package whose `R/` holds a file the `Collate` field does not
list. A new helper file therefore needs a `DESCRIPTION` update in the same commit.
Nothing in a local `source()`-based workflow notices this.

## Helper naming

A module helper function whose name begins with the module's own name is rejected by
SpaDES. Rename the function (e.g. `synthBurnMap` -> `drawBurnMap` in a module called
`synthBurn`).

## Documents

The workflow calls `convertToPackage(..., buildDocuments = TRUE)`. With `FALSE` you get
the package but not the roxygen-generated `NAMESPACE`/`man`, so an import problem stays
invisible. Keep `TRUE` when reproducing locally.

## Read-only copies

`convertToPackage()` copies the functions defined in the main `<Module>.R` file into
`R/READONLYFromMainModuleFile.R`. Do not edit that file; edit `<Module>.R`.

## Tests that hide defects

`testthat` runs test files alphabetically within a module. A test file that calls
`library(data.table)` at the top attaches the package for every file after it, so an
unresolved import in a later file resolves anyway. Two modules with the same defect can
therefore differ in CI colour purely by test-file naming. When checking whether an
import problem is real, run the suspect test file on its own.
