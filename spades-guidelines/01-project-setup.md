# Project-folder setup for AI-assisted work (reference)

> **Assistant-facing reference** — the assistant should study these and
> then consult to obtain detail to execute the steps in `00-user-setup.md`.

Reference for how a working folder is prepared for developing and maintaining the SpaDES
toolkit packages with a Posit-Assistant-enabled Claude model. For the short action
checklist, see `00-user-setup.md`.

> **Team resources.** Guidelines, the `AGENTS.md` template, and the shared skills all
> live in one repo:
> - SpaDES.ai repo: https://github.com/CeresBarros/SpaDES.ai
>   (`git@github.com:CeresBarros/SpaDES.ai.git`) — `guidelines/`, `AGENTS.md`, `skills/`.

## The working folder

Development is conducted from a **project folder** that collects many independent SpaDES
toolkit package repositories side by side (e.g. `SpaDES.core`, `SpaDES.tools`,
`reproducible`, `Require`, `SpaDES.project`, `quickPlot`, and companions).

The folder itself does **not** need to be a git repository. Each package is its own repo.
Optionally the project folder can itself be a git repo with the package repos as git
submodules.

Details to establish for the folder:
- The **path** of the project folder (working directory).
- Whether a **sibling reference folder** exists (e.g. a folder holding a SpaDES-based
  model system such as LandR) and where.
- Whether the model may read outside the project folder. With the guardrails installed,
  outside-project access prompts for confirmation each time; granting read access to a
  known reference folder up front is reasonable.

## Repository set (never assumed)

The set of repositories a folder contains is **confirmed, not assumed.** Only the toolkit
repos in active use are present in a given workspace; a machine may hold only some of them,
and the set changes over time. Never assume a canonical list.

Details to establish:
- Which **toolkit packages** are in scope (`SpaDES.core`, `SpaDES.tools`, `reproducible`,
  `Require`, `SpaDES.project`, `quickPlot`, `SpaDES.experiment`, `SpaDES.config`,
  `SpaDES.addins`, `SpaDES.install`, `SpaDES.docs`, the `SpaDES` meta-package, ...)?
- Which **accessory helper packages** (`pemisc`, `fireSenseUtils`, the `LandR` R package,
  ...)?
- Whether a **model-system** folder (e.g. LandR) should be available for reference.

### Where to look for repos

Look **first in the PredictiveEcology GitHub account**
(https://github.com/PredictiveEcology), which hosts the canonical SpaDES toolkit repos.
Confirm this with the user, and ask whether **other accounts** (personal forks, or other
organizations/collaborators) also need to be searched — some repos may live under a fork
or a different owner by design.

## Forks vs. upstream

For each repo, the fork situation is clarified before cloning or committing:
- Is the repo a **direct clone of upstream** (e.g. `PredictiveEcology/...`) or a **personal
  fork**?
- If a fork is used, the `upstream` vs `origin` remotes are noted so branch/PR workflows
  are correct (branch off `upstream`'s default branch, push to `origin`, PR to `upstream`).
- The **default branch** is confirmed. SpaDES toolkit repos are **mixed** — some use
  `main`, some `master` — so this must be checked per repo; new repos should use `main`.

These answers affect how commits, pushes, and PRs are handled later.

## Building a mental model

Once the repo set is confirmed, structure is explored **read-only** before any work.
A typical pass:
1. List the project folder (and any reference folder) to enumerate the packages present.
2. Read a package `DESCRIPTION`/`NAMESPACE` to learn its dependencies and the
   roxygen2/testthat conventions; skim its `R/` and `tests/testthat/`.
3. Skim the toolkit docs (https://spades.predictiveecology.org/) or a package's
   `vignettes/` for the usage model.
4. If a SpaDES module or model system is in scope for reference, inspect one module's
   `<Module>.R` to learn the module anatomy (see the `spades-module-anatomy` skill).

Read-only exploration subagents are preferred for breadth, with tool calls kept modest.

## Project memory and skills

- An **`AGENTS.md`** at the project root captures the toolkit map, package anatomy,
  run/test conventions, and pointers to skills (see `02-guardrails.md` and the SpaDES.ai
  `AGENTS.md` template).
- The relevant **skills** are obtained/loaded (see `03-skills.md`) so domain knowledge is
  available on demand.

## Trust and permissions

Posit Assistant prompts to **trust the workspace** on first open when it finds
`AGENTS.md` or `.posit/assistant/settings.json`. Trust is required for project memory,
project settings, and project hooks to load.

## Checklist

- [ ] Project folder path confirmed.
- [ ] Repository set confirmed (toolkit + accessory packages) — not assumed.
- [ ] Fork/upstream remotes and default branch recorded (mixed `main`/`master`).
- [ ] Reference-folder location and outside-folder read access clarified.
- [ ] Structure explored read-only (package `DESCRIPTION`/`NAMESPACE`, `R/`, `tests/`).
- [ ] `AGENTS.md` created (from the SpaDES.ai template).
- [ ] Skills obtained/loaded.
- [ ] Workspace trusted.
