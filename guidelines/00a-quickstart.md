# Quick setup

A one-page guide to getting started. It takes about 15 minutes. Each step has a fuller
explanation in [`00-user-setup.md`](00-user-setup.md) if you want the reasoning.

<!-- Maintainers: this is a condensed view of 00-user-setup.md "Steps". Keep the two in sync. -->

**We recomend using** Positron with Posit Assistant or Claude + Claude Code, and R. Git and a GitHub account are
helpful but not required. Other AI interfaces are possible, but not tested.

You make the choices in steps 1 and 2. In steps 3 and 4 you can ask the assistant to do
the work; it should show you what it plans to change and wait for your approval.

## 1. Pick your project folder

Choose one folder to hold the module or package repositories you work on, side by side,
and open it in Positron. Decide whether the assistant may look at files outside it
(by default, it asks every time).

## 2. Trust the workspace

When Positron asks whether you trust the folder, accept. Without this, your project
memory, settings and safety rules will not load.

## 3. List the repositories you need

Write down which repositories you will work on. For each one, note whether it is your
own copy (a fork) or the original (a clone), and its main branch name (`main` or
`master`; this varies).

## 4. Give the assistant its project memory and safety rules

Paste these into the assistant, one at a time:

> Copy the `AGENTS.md` template from the `PredictiveEcology/AI` repo into this project folder, adapt the
> paths and repository list to my project, and show me the changes before writing.

> Set up the recommended safety guardrails from the `PredictiveEcology/AI` repo (`AGENTS-rules/enforced/default/`).
> Back up my `settings.json` first and show me the changes before applying.

Then **start a new conversation**; the changes only take effect in a new one.

## 5. Install skills

Skills are add-on instruction packs that teach the assistant about SpaDES and LandR. You
install them yourself from Posit Assistant:

1. In the assistant's chat box, type `/plugin` (or `/marketplace`).
2. Add a marketplace and enter `PredictiveEcology/AI`.
3. Browse the plugins it lists and install the ones you need:
   - `shared-conventions`: for everyone.
   - `spades-toolkit-suite`: if you work on the SpaDES toolkit, or on LandR.
   - `landr-suite`: if you work on LandR.
4. To check, ask the assistant: *"What skills are available to you?"*

If this does not work for you, see the manual alternative in [`03-skills.md`](03-skills.md).

## Next

- Read [`00b-user-guidelines.md`](00b-user-guidelines.md) for good day-to-day habits.
- Keep the [cheat sheet](../cheatsheet/cheatsheet.md) handy for commands, and for what to
  do when a safety rule blocks something.

Drafted with assistance from Claude (Posit Assistant).
