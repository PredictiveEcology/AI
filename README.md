# AI

Shared conventions, guidelines, and skills for AI-assisted development across
PredictiveEcology's projects. 

This repository is the team's source for how to work with a
Posit-Assistant-enabled Claude model on SpaDES toolkit packages, SpaDES applications
such as the LandR forest landscape model and related models, and other
related code. It holds four things:


- **`guidelines/`** — path-agnostic setup and convention docs. Start at
  [`guidelines/00-user-setup.md`](guidelines/00-user-setup.md); the reference docs are
  `00b-user-guidelines.md` (working *with* the assistant), `01-project-setup.md`
  (project folder + repo set), `02-guardrails.md` (permissions, hooks, `AGENTS.md`), and
  `03-skills.md` (getting, creating, and loading skills).
- **`skills/`** — the shared team skills: ecosystem-agnostic (`testing`,
  `code-documentation`), LandR-specific (`landr-*`), and SpaDES-toolkit-specific
  (`spades-*`). These are the primary source; get them before writing new ones.
- **`AGENTS-rules/`** — short, single-topic behavioural rules, one per file, to take or
  leave individually. `AGENTS.md` is always part team convention and part personal
  working style, so the unit you adopt is a rule, not a whole file. Start at
  [`AGENTS-rules/README.md`](AGENTS-rules/README.md), which also explains how a rule
  differs from a guideline and from a skill.
- **`AGENTS.md`** — a template project-memory file to copy into a workspace root and
  adapt (paths, repository set) to that workspace. It includes a LandR section, a SpaDES
  toolkit section, and shared conventions common to both — include only what your
  workspace needs.

**This repo is documentation + config — you don't run it.** It sets up your workspace and
your assistant to work on the *real* LandR module, SpaDES toolkit package, and other
project repos.

## Which parts apply to me?

- Working on the **SpaDES toolkit** itself → the SpaDES toolkit section of `AGENTS.md`,
  the `spades-*` skills, plus the shared skills.

- Working on **LandR** modules/packages → the LandR section of `AGENTS.md`, the
  `landr-*` skills, plus the shared skills and the SpaDES toolkit skills (used by default
  in LandR work).

- Everything in `guidelines/` applies regardless of ecosystem.

## Prerequisites

Software to have installed before you start (that's all — no R versions or package lists
to worry about; each ecosystem's own tooling and the assistant handle package setup):

- An AI-powered coding interface. This guide assumes using **Positron** with **Posit Assistant** enabled and Anthropic Claude models.
- **R**.
- **git**, and a **GitHub** account — recommended for cloning and contributing, but not
  required: you can also download this repo (and the LandR/SpaDES repos) as a zip from
  GitHub, and GitHub is not needed to *use* either ecosystem.

## Getting started

1. Read [`guidelines/00-user-setup.md`](guidelines/00-user-setup.md) — a short setup
   checklist.
2. You decide the project folder and which repos are in scope; then set up project
   memory + guardrails and fetch the skills.
3. Trust the workspace so project memory, settings, and hooks load.
4. Use [`guidelines/00b-user-guidelines.md`](guidelines/00b-user-guidelines.md) for
   day-to-day working habits.

Most of steps 2–3 in [`guidelines/00-user-setup.md`](guidelines/00-user-setup.md) can be done by asking the assistant — see the prompt examples.

The numbered `01`–`03` guideline  are reference documents for the AI assistant. You
remain responsible for the instructions and content the assistant is given, so read the
`01`–`03` documentation too — they define what the assistant is instructed to do on your behalf.

> **You are responsible for what the assistant does on your behalf** — the code it writes,
> the changes it makes, and the instructions it follows. Review its diffs and results, and
> the assistant-facing docs, before relying on them. See
> [`guidelines/00b-user-guidelines.md`](guidelines/00b-user-guidelines.md).

## Getting the skills

Clone or sync this repo's `skills/` into a local skills path so Posit Assistant
discovers them, e.g. `~/.agents/skills` or `~/.posit/assistant/skills/`. See
[`guidelines/03-skills.md`](guidelines/03-skills.md) for the full skill catalog and
precedence rules.

Alternatively, point your AI assistant to this repo and the `skills/` folder.

## Shared vs local

The docs here are **shared and path-agnostic**. Machine-specific records (concrete
paths, installed config) are kept as **local instances** — files named `*.local.md`
that stay out of this repo. See the "Local instances of these guidelines" section in
[`guidelines/00-user-setup.md`](guidelines/00-user-setup.md).

---

The documents in this repository — this README, the `guidelines/`, the `AGENTS.md`
template, and the `skills/` — were drafted with assistance from Claude (Posit Assistant).
