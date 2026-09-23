---
name: spades-experiments
description: Running a SpaDES simulation many times — replicates of a stochastic model, scenario comparisons, parameter sweeps, and controlled before/after regression tests. Covers the SpaDES.project experiment family (experiment(), experiment2() in memory; experimentTmux(), experimentFuture(), experimentSBATCH() driven by a global.R and a shared job queue), which to pick, how replicates and seeds work, collecting results with as.data.table() on a simLists, and how to design a comparison whose difference can only be the change under test. Use when the user asks to run replicates, compare scenarios, sweep parameters, run on a cluster, or test whether a code change alters simulation results. For writing the module being run use spades-module-development.
metadata:
  ecosystem: SpaDES
  version: "1.0"
---

# SpaDES experiments

An "experiment" is running a simulation more than once with something varied:
replicates of a stochastic model, alternative inputs, scenarios, or parameter values.
`SpaDES.project` provides five functions for this. (They came from the now-deprecated
`SpaDES.experiment`; do not use that package.)

Start at the simple end. Most questions need `experiment2()` and nothing else.

## Just run some replicates

You have a working `simInit()` call. You want to run it three times because the model
is stochastic.

```r
library(SpaDES.core)
library(SpaDES.project)

mySim <- simInit(times = list(start = 0, end = 10),
                 modules = "<Module>", params = params,
                 paths = list(modulePath = "..", outputPath = "outputs"))

sims <- experiment2(mySim, replicates = 3)
```

`sims` is a `simLists` object — the plural of `simList`. Pull numbers out of it with
`as.data.table()`, naming the values you want:

```r
dt <- as.data.table(sims, vals = c("nPixelsBurned",
                                   nCohorts = quote(nrow(cohortData))))
```

Three things to know before you trust the output:

- **Each replicate needs its own output directory**, or they overwrite each other.
  `experiment2()` handles this by default (`createUniquePaths = "outputPath"`). Leave
  it alone unless you know why you are changing it.
- **Caching is off by default** (`useCache = FALSE`), and should stay off. A cached
  run returns the same answer every time, which is the opposite of a replicate.
- **Replicates differ because the model is stochastic**, not because a seed is set per
  replicate. Every replicate gets the same parameters, so a module's `.seed` parameter
  makes the replicates **identical** for that event: with `.seed = list(step = 123)`,
  every replicate draws the same numbers in `step`, at every recurrence. Do not set
  `.seed` on events you are replicating.

### Replicating from a simList that has already run

Replicate only what should vary. If `init` (or any event) has already run in the
`simList` you pass in, its stochastic results are baked in, and every replicate starts
from the same draw. On SpaDES.core 3.2.0 and SpaDES.project 1.2.0, `experiment()` and
`experiment2()` give the replicates different random streams after that point, but all
of them share the draws already made. This was checked by running `init` with
`simInit()` + `spades(events = "init")` and with `simInitAndSpades(events = "init")`,
under sequential and multisession `future` plans. In 2022–23 all replicates were
reported identical in this situation; that no longer reproduces, but if the stochastic
output you care about is made in `init`, the effect is the same.

When some modules should run once and the rest should be replicated, run the first
group on its own and start a fresh `simList` for the second:

```r
## run once: the modules whose outputs every replicate should share
simA <- simInitAndSpades(times = times, modules = c("A", "B", "C"), ...)

## replicate: a new simList for the rest, fed the shared outputs as objects
simD <- simInit(times = times, modules = c("D", "E", "F"),
                objects = mget(c("objFromA", "objFromB"), envir(simA)), ...)
sims <- experiment2(simD, replicates = 10)
```

Check that the replicates really differ before trusting a spread of results: compare
one stochastic output across two replicates.

## Vary something, not just the seed

`experiment()` builds the variation for you from one base `simList`: give it
alternative `params`, `modules`, `inputs` or `objects` and it runs the fully factorial
set.

```r
sims <- experiment(mySim,
                   params = list(fireSpread = list(spreadprob = c(0.2, 0.3))),
                   replicates = 2)
```

If you would rather build the varied `simList`s yourself — often clearer — make them
with several `simInit()` calls and hand them all to `experiment2()`:

```r
sims <- experiment2(low = simLow, high = simHigh, replicates = 3)
```

Both return a `simLists`. Both hold every result in RAM, which is the limit: they suit
a modest number of short runs where you want the objects back in your session.

## When the runs get big: the queue functions

Past a few dozen runs, long runs, several machines, or anything you need to resume
after a crash, switch to the second group. These do not take `simList`s. They take:

- a **`data.frame`** (`df`) where one row is one job, and each column name becomes a
  variable assigned in the worker's `.GlobalEnv`; and
- a **`global.R`** (usually your `setupProject()` script) that each worker `source()`s
  after assigning that row's variables.

```r
df <- expand.grid(.scenario = c("A", "B"), .rep = 1:3, stringsAsFactors = FALSE)
ef <- experimentFuture(df = df, global_path = "global.R",
                       n_workers = 4L, log_dir = "logs")
```

Worker 1 runs `.scenario <- "A"; .rep <- 1; source("global.R")`, and so on. A
file-locked queue records each row as PENDING / RUNNING / DONE, so two workers never
claim the same row and a relaunch skips finished rows.

The three differ only in how workers are spawned:

| Function | Use it when | Stop it with |
|---|---|---|
| `experimentTmux()` | You are still debugging and want to watch workers live (`tmux attach`). Needs `tmux` installed. | `tmuxKillPanes()` |
| `experimentFuture()` | The script is stable. Background R processes via `callr::r_bg()` locally, or `future::cluster` (an SSH PSOCK cluster) when workers are on other machines. | `killExperimentFuture()` |
| `experimentSBATCH()` | You are on an HPC cluster with `sbatch`/`squeue`. Preview the generated job scripts with `dry_run = TRUE`. | `killExperimentSBATCH()` |

The parallel-backend one is `experimentFuture()` — there is no `experimentPSOCK()`;
PSOCK is what it uses underneath for remote hosts. Swapping between the three changes
one function call and the worker arguments (`cores` / `n_workers` / `sbatch_opts`);
the rest of the driver script is unchanged.

Useful shared arguments: `queue_path` (keep it to resume; use a new name to start
over, because `df` is ignored when the queue file already exists), `runNameLabel` (how
runs are named in logs and pane titles), and `ss_id` (mirror the queue to a Google
Sheet so a collaborator can watch; omit it and nothing touches Google). With `ss_id`
set, an existing sheet of the same name wins over the local file, so deleting
`queue_path` alone does not start over; pass `forceLocalQueueToGS = TRUE` or pick a new
name. `experimentTmux()` also takes `statusCalculate` (inspect outputs to report
progress — `statusCalculate_LandR` is prebuilt).

`?experiment_family` documents all five together, including why this is worth more
than a loop of `Rscript -e` calls. Read it before building your own bookkeeping.

## Comparing two versions of the code

A different job from the above: you changed something and want to know whether results
changed. That needs a design, not just replicates — see
`references/controlled-comparisons.md`. The short version:

- One arm per code version, in separate git worktrees, so both arms exist at once.
- One start state, computed once and frozen, loaded by both arms.
- Same seed per replicate in both arms, so a difference is the change and nothing else.
- Caching **off**. A cached year-200 result silently defeats the whole comparison.
- Record a metric table per snapshot year, not just the final state.

And the rule that matters most: **if the difference comes out near zero, find out
why before reporting it.** "No detectable effect" and "the changed line never
executed in this configuration" look identical in the output table and mean entirely
different things.

## Common pitfalls

- **Plotting on.** Set `.plots = NA` and `.plotInitialTime = NA` for batch runs.
- **Caching on.** Fine for `.inputObjects` and data prep; wrong for the runs
  themselves, and wrong for anything stochastic.
- **Saved output filenames.** SpaDES appends `_year<NN>` to files written through the
  `outputs` argument. Match saved files by pattern rather than reconstructing the name
  you asked for.
- **Everything in RAM.** `experiment2()` keeps every `simList`; use `clearSimEnv =
  TRUE` or move to the queue functions when that stops fitting.

## Reference files

| File | Covers |
|---|---|
| `references/controlled-comparisons.md` | designing a before/after regression experiment, and reading a null result honestly |

## Related skills

- `spades-module-development` — building and debugging the module being run.
- `testing` — unit and integration tests, which are a different tool from an
  experiment: tests assert, experiments measure.
