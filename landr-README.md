# LandR.ai

Shared conventions, guidelines, and skills for AI-assisted development across the
**LandR** and **SpaDES** ecosystems of forest and forest-disturbance simulation
software.

This repository is the team's single source for how to work with a
Posit-Assistant-enabled Claude model on LandR modules, SpaDES packages, and related
code. It holds three things:

- **`guidelines/`** — path-agnostic setup and convention docs. Start at
  [`guidelines/00-user-setup.md`](guidelines/00-user-setup.md); the reference docs are
  `01-project-setup.md` (project folder + repo set), `02-guardrails.md` (permissions,
  hooks, `AGENTS.md`), and `03-skills.md` (getting, creating, and loading skills).
- **`AGENTS.md`** — a template project-memory file to copy into a workspace root and
  adapt (paths, repository set) to that workspace.
- **`skills/`** — the shared team skills. These are the primary source; get them before
  writing new ones.

**LandR.ai is documentation + config — you don't run it.** It sets up your workspace and
your assistant to work on the *real* LandR/SpaDES module and package repos.

## Prerequisites

Software to have installed before you start (that's all — no R versions or package lists
to worry about; LandR's own tooling and the assistant handle package setup):

- **Positron** with **Posit Assistant** enabled.
- **R**.
- **git**, and a **GitHub** account — recommended for cloning and contributing, but not
  required: you can also download this repo (and the LandR repos) as a zip from GitHub,
  and GitHub is not needed to *use* LandR.

## Getting started

1. Read [`guidelines/00-user-setup.md`](guidelines/00-user-setup.md) — a short setup
   checklist.
2. You decide the project folder and which repos are in scope; then set up project
   memory + guardrails and fetch the skills.
3. Trust the workspace so project memory, settings, and hooks load.
4. Use [`guidelines/00b-user-guidelines.md`](guidelines/00b-user-guidelines.md) for
   day-to-day working habits.

Most of steps 2–3 can be done by asking the assistant — see the prompt examples in
[`guidelines/00-user-setup.md`](guidelines/00-user-setup.md). The `00*` guidelines are
written for you; the numbered `01`–`03` docs are reference the assistant consults. They
aren't required reading to get set up, but they define what the assistant is instructed to
do, and you remain responsible for its actions — review them whenever you want to know or
change that.

> **You are responsible for what the assistant does on your behalf** — the code it writes,
> the changes it makes, and the instructions it follows. Review its diffs and results, and
> the assistant-facing docs, before relying on them. See
> [`guidelines/00b-user-guidelines.md`](guidelines/00b-user-guidelines.md).

## Getting the skills

The shared skills come from **two sister repos** — this repo (LandR.ai, the LandR skills)
and [`CeresBarros/SpaDES.ai`](https://github.com/CeresBarros/SpaDES.ai) (SpaDES toolkit
skills, used by default in LandR work). Clone or sync both into a local skills path so
Posit Assistant discovers them, e.g. `~/.agents/skills` or `~/.posit/assistant/skills/`.
See [`guidelines/03-skills.md`](guidelines/03-skills.md) for details and precedence rules.

## Shared vs local

The docs here are **shared and path-agnostic**. Machine-specific records (concrete
paths, installed config) are kept as **local instances** — files named `*.local.md`
that stay out of this repo. See the "Local instances of these guidelines" section in
[`guidelines/00-user-setup.md`](guidelines/00-user-setup.md).

---

The documents in this repository — this README, the `guidelines/`, the `AGENTS.md`
template, and the `skills/` — were drafted with assistance from Claude (Posit Assistant).
