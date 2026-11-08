# Parent modules

A parent module groups other modules so a user can name one module instead of many.
It is a `defineModule()` with `childModules = c(...)` and no events. Scaffold one with
`SpaDES.core::newModule("<name>", path, type = "parent", children = c("child1", "child2"))`.

## What SpaDES does with a parent

- `simInit()` replaces the parent by its children (`.identifyChildModules()`,
  `SpaDES.core/R/simulation-simInit.R`). The parent itself is never in the `simList`:
  `simInit(parent)` gives the same modules, dependencies, parameters and events as
  `simInit(<its children>)`.
- Parents nest. A child may itself be a parent; both `simInit()` and
  `SpaDES.project::setupProject()` resolve the tree recursively.
- A child cannot switch off its siblings. Every child's `.inputObjects` runs during
  `simInit()`, before any event, and `setupProject()` fetches modules and installs
  their packages before it evaluates `params`. To run only part of a family, list the
  children you want, not the parent.

## How `childModules` entries choose what to fetch

`SpaDES.project` (`.childModuleSpec()`, `R/getModule.R`, development 1.2.0.9033):

| Entry in `childModules` | Fetched from |
|---|---|
| `owner/repo` or `owner/repo@branch` | as written |
| `name@branch` | the parent's GitHub account, that branch |
| `name` | the parent's account and the parent's branch |
| `name`, parent fetched at a release tag `vX.Y.Z` or with no ref | `v<version>`, where `<version>` is the child's entry in the parent's `version` list (when it is a release version) |
| any, parent is local only or sits in a subfolder of another repo | left as written |

Children kept inside the parent's own repository, in its `modules/` folder (as in
`PredictiveEcology/scfm`), are taken from the parent's copy at the parent's ref, not
fetched (`.placeInRepoChildren()`).

A module the user lists at top level is fetched as the user wrote it, not again as a child (`.getChildModules(explicit = )`, `R/getModule.R:450`).

So a plain child name means "the same branch as the parent". A parent on `development`
pulls every plain child's `development`; a parent on `main` pulls `main`. Use an
explicit `@branch` only for a child that must differ.

## Releasing a parent

The parent's `version` list names each child's release:

```r
version = list(myFamily = "1.1.0", childA = "1.2.0", childB = "2.2.0")
```

Tag the parent `v1.1.0`. `getModule("owner/myFamily@v1.1.0")` then fetches each plain
child at `v<its listed version>`, so what "v1.1.0" means is stated in one place. A child
listed with a development version (four components, e.g. `2.2.0.9000`) falls back to the
parent's ref.

Children must be released (tagged) before the parent release that lists them.
