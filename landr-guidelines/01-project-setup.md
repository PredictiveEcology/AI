# Project-folder setup for AI-assisted work (reference)

> **Assistant-facing reference** — the assistant should study this and then consult it to
> obtain detail to execute the steps in `00-user-setup.md`.

Reference for how a working folder is prepared for developing and maintaining LandR
modules, SpaDES packages, and related code with a Posit-Assistant-enabled Claude model.
It applies regardless of which system (LandR modules/packages or the SpaDES toolkit) is
under focus. For the short action checklist, see `00-user-setup.md`.

> **Team resources.** Guidelines, the `AGENTS.md` template, and the shared skills all
> live in one repo:
> - LandR.ai repo: https://github.com/CeresBarros/LandR.ai
>   (`git@github.com:CeresBarros/LandR.ai.git`) — `guidelines/`, `AGENTS.md`, `skills/`.

## The working folder

Development is conducted from a **project folder** that collects many independent
module and/or package repositories side by side (e.g. a LandR folder holding `Biomass_*`,
`fireSense_*`, the `LandR`/`LandR.CS`/`fireSenseUtils` packages, and `LandR-Manual`; or a
SpaDES folder holding SpaDES toolkit package repos).

The folder itself does **not** need to be a git repository. Each module/package is its
own repo. Optionally the project folder can itself be a git repo with the module/package
repos as git submodules.

Details to establish for the folder:
- The **path** of the project folder (working directory).
- Whether a **sibling reference folder** exists (e.g. a SpaDES toolkit folder alongside a
  LandR folder) and where.
- Whether the model may read outside the project folder. With the guardrails installed,
  outside-project access prompts for confirmation each time; granting read access to a
  known reference folder up front is reasonable.

## Repository set (never assumed)

The set of repositories a folder contains is **confirmed, not assumed.** LandR is open
source and modular: only the module families in active use are present in a given
workspace (e.g. the PredictiveEcology `Biomass_*` and `fireSense_*` families), while
other families maintained elsewhere (e.g. the `SCFM` fire modules) may be absent by
design. The same holds for a SpaDES toolkit folder — only the toolkit repos in use are
present. Never assume a canonical list.

Details to establish:
- Which **module families** are in scope (Biomass, fireSense, carbon, others)?
- Which **accessory packages** (`LandR`, `LandR.CS`, `fireSenseUtils`, ...)?
- Whether a **SpaDES toolkit** folder should be available for reference.

### Where to look for repos

Look **first in the PredictiveEcology GitHub account**
(https://github.com/PredictiveEcology), which hosts the canonical LandR modules,
accessory packages, and SpaDES toolkit repos. Confirm this with the user, and ask
whether **other accounts** (personal forks, or other organizations/collaborators) also
need to be searched — some repos may live under a fork or a different owner by design.

## Forks vs. upstream

For each repo, the fork situation is clarified before cloning or committing:
- Is the repo a **direct clone of upstream** (e.g. PredictiveEcology/...) or a **personal
  fork**?
- If a fork is used, the `upstream` vs `origin` remotes are noted so branch/PR workflows
  are correct.
- The **default development branch** is confirmed (many PredictiveEcology repos use
  `development`, not `main`).

These answers affect how commits, pushes, and PRs are handled later.

## Building a mental model

Once the repo set is confirmed, structure is explored **read-only** before any work.
A typical pass:
1. List the project folder (and any reference folder) to enumerate modules and packages.
2. Inspect one flagship module (e.g. `Biomass_core`) to learn the module anatomy: the
   `<Module>.R` (`defineModule` metadata + `doEvent` dispatcher + event functions),
   `R/` helpers, `tests/`, `data/CHECKSUMS.txt`, and the `<Module>.Rmd` manual.
3. Read an accessory package `DESCRIPTION`/`NAMESPACE` to learn dependencies and the
   roxygen2/testthat conventions.
4. Skim `LandR-Manual/index.Rmd` and `_bookdown.yml` for the documentation model.

Read-only exploration subagents are preferred for breadth, with tool calls kept modest.

## Project memory and skills

- An **`AGENTS.md`** at the project root captures the ecosystem map, module anatomy,
  run/test conventions, and pointers to skills (see `02-guardrails.md` and the template
  placeholder above).
- The relevant **skills** are obtained/loaded (see `03-skills.md`) so domain knowledge is
  available on demand.

## Trust and permissions

Posit Assistant prompts to **trust the workspace** on first open when it finds
`AGENTS.md` or `.posit/assistant/settings.json`. Trust is required for project memory,
project settings, and project hooks to load.

## Checklist

- [ ] Project folder path confirmed.
- [ ] Repository set confirmed (families + packages) — not assumed.
- [ ] Fork/upstream remotes and default branch recorded.
- [ ] Reference-folder location and outside-folder read access clarified.
- [ ] Structure explored read-only (module anatomy, packages, manual).
- [ ] `AGENTS.md` created (from template when available).
- [ ] Skills obtained/loaded.
- [ ] Workspace trusted.
