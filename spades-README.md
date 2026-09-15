# SpaDES.ai

Shared conventions, guidelines, and skills for AI-assisted development on the
**SpaDES toolkit** — the R packages that implement Spatial Discrete Event System
(`SpaDES.core`, `SpaDES.tools`, `SpaDES.project`, `reproducible`, `Require`, and their
companions).

This repository is the team's single source for how to work with a
Posit-Assistant-enabled Claude model on the SpaDES toolkit packages and related code.
It holds three things:

- **`guidelines/`** — path-agnostic setup and convention docs. Start at
  [`guidelines/00-user-setup.md`](guidelines/00-user-setup.md); the reference docs are
  `00b-user-guidelines.md` (working *with* the assistant), `01-project-setup.md`
  (project folder + repo set), `02-guardrails.md` (permissions, hooks, `AGENTS.md`),
  and `03-skills.md` (getting, creating, and loading skills).
- **`AGENTS.md`** — a template project-memory file to copy into a SpaDES workspace root
  and adapt (paths, repository set) to that workspace.
- **`skills/`** — the shared team skills (`spades-*`). These are the primary source;
  get them before writing new ones.

## Prerequisites

SpaDES.ai is **documentation and configuration, not something you run** — these are the
tools you need for the SpaDES work itself:

- **Positron** with **Posit Assistant** enabled (the IDE + AI assistant).
- **R**.
- **git**, and a **GitHub** account.

You do **not** need to install SpaDES R packages by hand or match specific versions — the
SpaDES tooling (`Require`, `SpaDES.project::setupProject()`, and each module's package
list) handles that for you, and the assistant can help. See
[`guidelines/00-user-setup.md`](guidelines/00-user-setup.md) for detail.

## Getting started

1. Read [`guidelines/00-user-setup.md`](guidelines/00-user-setup.md).
2. **You decide** the project folder and which repositories it holds; then **ask the
   assistant** to set up project memory and guardrails and to fetch the skills.
3. Trust the workspace so project memory, settings, and hooks load.
4. Use `00b-user-guidelines.md` for day-to-day habits.

Most of the setup can be done by asking the assistant — see the prompt examples in
`00-user-setup.md`. The `00*` docs are written for you; the numbered `01`–`03` docs are
reference the assistant consults. You remain responsible for the instructions and content
the assistant is given, so read the `01`–`03` docs too — they are what the assistant is
told to do on your behalf.

## Shared vs local

The docs here are **shared and path-agnostic**. Machine-specific records (concrete
paths, installed config) are kept as **local instances** — files named `*.local.md`
that stay out of this repo. See the "Local instances of these guidelines" section in
[`guidelines/00-user-setup.md`](guidelines/00-user-setup.md).

## Related work

[LandR.ai](https://github.com/CeresBarros/LandR.ai) is an **example** of a SpaDES-based
system (the LandR module/model ecosystem) that has built its own AI-assisted-development
support docs and tools.

---

The documents in this repository — this README, the `guidelines/`, the `AGENTS.md`
template, and the `skills/` — were drafted with assistance from Claude (Posit Assistant).
