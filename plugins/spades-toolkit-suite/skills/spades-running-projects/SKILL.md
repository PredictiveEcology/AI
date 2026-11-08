---
name: spades-running-projects
description: Operating SpaDES projects and campaigns day to day, as a user rather than a module author. Covers the global.R + launcher layout, launching experiment queue workers, stopping runs safely (by PID, the whole process tree, HOLD rows, relaunching on a new queue name), installing package updates while runs are live (dev libraries, branch pins that do not update, (HEAD) and version floors), caching as a user (what makes a cached run recompute, cache format, terra scratch files), data downloads that come back short, HPC/Slurm traps (tmpfs /tmp, proxies, open-file limits, memory per job), and diagnosing slow or hung runs. Use when a run is slow, hung, failing after an install, recomputing unexpectedly, or when the user asks how to launch, stop, restart, install into, or move a SpaDES project. For replicates, seeds and before/after comparisons use spades-experiments.
metadata:
  ecosystem: SpaDES
  version: "0.1"
---

# Running SpaDES projects

This skill is for people who run SpaDES projects: many `setupProject()` runs, queues
of jobs, long campaigns on several machines or an HPC cluster. Most of what goes
wrong there is not in the model. It is a process killed the wrong way, a package
installed under a running job, a cache that hit or missed when you did not expect it,
or a temp folder that was too small.

Scope:
- How to choose `experiment2()` / `experimentTmux()` / `experimentFuture()` /
  `experimentSBATCH()`, replicates, seeds and controlled comparisons:
  `spades-experiments`. This skill does not repeat it.
- Writing module code, declaring inputs and outputs, `.cacheExtra`:
  `spades-module-development` and `spades-module-anatomy`.

## The project layout that works

- **Two scripts.** `global.R` is one job: it calls `setupProject()` and runs the
  simulation. A launcher (e.g. `expt.R`) builds the queue `data.frame` and calls an
  `experiment*()` function. Workers `source("global.R")` once per row.
- **Settings reach a job as queue columns.** Every value that varies between jobs is a
  column of `df`; it arrives in the worker's `.GlobalEnv` before `global.R` runs. Do
  not read environment variables inside `global.R` for this. A column is recorded in
  the queue; an environment variable is not.
- **Per-machine values live in one small site file** (base path, hosts, cores per
  host) that `global.R` reads from the current folder. Keep host names and absolute
  paths out of `global.R`, so the same scripts run on a laptop, a workstation and an
  HPC login node. This is a convention, not a package requirement.
- **Launch `experimentTmux()` from inside tmux.** Outside a tmux session it prints
  "Not inside a tmux session; running first job sequentially in this R session" and
  runs one job in the launching process: no worker panes, and the row it claimed
  stays RUNNING. Check the launch log for that line and count panes within minutes.
- **Never edit a script in place while an `Rscript` runs it.** Rscript reads the file
  as it goes. After an in-place edit the job resumes at a stale byte offset and dies
  with "unexpected symbol", often hours later, just before it writes results. Write
  the new version to a new file and `mv` it over the old one (new inode), or check
  `ps` first.

## Stopping and restarting

Restarting is usually cheap: cached events and cached optimiser generations replay in
seconds. Do not hold back a fix or an install waiting for a run to end. Stop it,
install, relaunch. But stop it correctly. Details and commands:
`references/stopping-and-restarting.md`.

- **Kill by PID, never by a command-line pattern.** `pkill -f <pattern>` misses
  instances started with a different path, and can kill your own shell. Verify the
  kill with the same `ps` listing, not by rerunning the pattern.
- **Kill the whole tree.** A job is pane shell -> worker R -> job -> forks -> their
  forks. Killing two levels leaves the forks reparented to PID 1, spinning at 100%
  CPU for days. Collect the tree first (`pstree -p <pid>`), kill every PID, then look
  for leftover `ppid == 1` R processes of yours.
- **But a `ppid == 1` process is not proof of an orphan.** PSOCK clusters built with
  reverse ssh tunnels start one `ssh -R ...` process per remote worker with ppid 1 and
  the library path in its command line. Killing them cuts live workers. Read the
  command line and check for established sockets first.
- **Do not `tmux kill-session` on a server you share.** It has taken down the whole
  tmux server, including unrelated sessions. Kill the R PIDs, then close panes one at
  a time.
- **To stop new claims, set rows to a status workers skip.** Workers take only
  PENDING or INTERRUPTED rows, so `"HOLD"` stops new claims and leaves running jobs
  alone. If the queue has a Google Sheet (`ss_id`), the Sheet is the source of truth:
  a HOLD written only to the local `.rds` does nothing.
- **Relaunch on a new queue name** after a hold, errors or a package fix. A same-name
  relaunch keeps old HOLD/ERROR rows, so new workers find nothing and sit idle; with a
  Sheet, stale RUNNING rows can be reclaimed twice.
- **Queues do not know about each other.** Two campaigns can claim the same unit of
  work at once. If they write the same `outputPath` (no run or PID in the file names,
  `overwrite = TRUE`), they corrupt each other's rasters. Keep concurrent campaigns'
  work disjoint.

## Installing packages while runs are live

An install into a library that a running R session has loaded corrupts it: the job
dies with "lazy-load database ... is corrupt", sometimes much later. Details:
`references/packages-for-live-runs.md`.

- **Never install into the library a running job uses.** With SpaDES.project
  >= 1.2.0.9033, pass `devPackages =` to the `experiment*()` launcher: it builds a new
  dev library beside the project library (hard links plus the changed packages) and
  starts the workers on it. Running jobs keep their own library.
- **Any launch can be an install.** A launcher whose first step installs pinned
  branches installs every branch that moved since the last launch. Starting a second
  campaign while the first runs is then an install under it.
- **`pkg@branch` installs nothing if the package is already installed.** To get a new
  commit, give a version floor, `"owner/pkg@development (>= 1.2.0.9033)"`, or
  `(HEAD)`. Bump the package version after a merge so there is a floor to raise.
- **A long stall on "Installing any missing reqdPkgs" right after a module's
  `reqdPkgs` changed is Require resolving**, and it may install. It is quick only when
  the requirements match a previous successful call.

## Caching, as a user

Details: `references/caching-for-users.md`.

- **A changed `reqdPkgs` makes every cached event of that module
  rerun.** Updating modules "to head" between two stages of a campaign can silently
  rebuild the earlier stage. Check which modules changed `reqdPkgs` before
  updating.
- **A change inside a function the cached call calls does not invalidate it.**
  `Cache()` digests the called function's own body, not its callees. Stale results
  after a package fix usually mean this. The module fix is `.cacheExtra`.
- **To find why something missed, compare cache tags**, not guesses (recipe in
  `spades-module-caching`).
- **Leave `reproducible.cacheSaveFormat` unset in diagnostic scripts.** Since
  reproducible 3.2.1.9046 unset means "read what is on disk". Setting it to a format
  that differs from an entry's converts that entry on disk; older versions also
  dropped its tags.
- **Never delete terra temp files (`spat_*_<pid>_*`) because their PID is dead.**
  Cached and memoised rasters in other, live jobs still point at them. Deleting them
  broke every running job within minutes. Clean the scratch folder only when no job
  that reads the shared cache is running.
- **Keep terra results with `Cache()` or `writeRaster()`, never `saveRDS()`** (see
  `spades-module-caching`).
- **terra keeps rasters in RAM by default** (`todisk = FALSE`). `experiment*()`
  workers set `todisk = TRUE`; a plain `Rscript global.R` or interactive run does not
  unless your script sets it. Cache entries keep whatever they were saved as.

## Data, downloads and moving a project

- **A short download looks like a data error.** "too few values" in a crop or a
  raster that ends early: compare the file size with the source before debugging the
  model. reproducible downloads into `getOption("reproducible.tempPath")`, under
  `tempdir()`. If that is a small tmpfs, large files are cut at its size.
- **To move a project to another machine, copy the whole input folders and the cache
  entries**, or let the target download. A list of files traced from a cache-hit run
  misses every raw input that the hit never opened; the first key change on the
  target then recomputes and downloads everything.

## HPC and Slurm

Details: `references/hpc-slurm.md`.

- Set `TMPDIR` for every job to a large shared filesystem. Compute-node `/tmp` is
  often a tmpfs of a few hundred MB.
- Compute nodes often reach the internet only through a proxy. Without it, downloads
  time out, and terra (which turns PROJ's network on at load) can hang on a CRS
  transform waiting on curl. `experiment*()` workers set `projNetwork(FALSE)`.
- Slurm passes the submitting shell's limits to the job. A soft open-file limit of
  1024 kills terra-heavy runs; `experimentSBATCH()` raises it to the hard limit.
- After an `sbatch` "Socket timed out", the job may have been submitted. Check
  `squeue` before resubmitting.
- Size memory per job from a measured peak (`sacct` MaxRSS, `/usr/bin/time -v`), not
  a guess. When a host OOMs because your workers were too many, fix the allocation;
  do not drop the host.

## Diagnosing slow or hung runs

- **A profile is believable only if profiled wall time is close to unprofiled wall
  time.** `Rprof(memory.profiling = TRUE)` with the JIT off once ran 5x slower and
  inflated the allocation-heavy lines; the "52% saving" it showed was 10-27% in a
  same-seed before/after. Print both times. A speed-up is a finding only after that
  before/after.
- **An empty result from a probe is not evidence until the probe is shown to work.**
  `find ... 2>/dev/null` that errors prints nothing, which looks exactly like a
  stalled run. Do not hide stderr when the output decides something.
- **A hung process: look at its stack before theorising.** `gdb -p <pid>` then `bt`
  showed one "stall" waiting on curl and another deep in GEOS; CPU% alone could not
  tell them apart.
- **Cap threads per process.** Many R workers each running a multi-threaded BLAS or
  data.table oversubscribe a host: set `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`,
  `data.table::setDTthreads(1)` and count forks x threads against the cores you have.

## Reproducibility notes not in spades-experiments

- Code that calls `parallel::mclapply()` inside a run repeats from `set.seed()` only
  under `RNGkind("L'Ecuyer-CMRG")`. Under the default RNG each child is reseeded
  from a non-repeatable source, so two runs with the same seed differ. If package
  code samples in forked children, outputs made with it are not reproducible; when
  comparing against them, set L'Ecuyer-CMRG or expect differences that are not your
  change.

## Reference files

| File | Covers |
|---|---|
| `references/stopping-and-restarting.md` | commands to find and kill a job tree, HOLD rows, new queue names, checks after a relaunch |
| `references/packages-for-live-runs.md` | dev libraries, floors vs branch pins, when an install is safe |
| `references/caching-for-users.md` | what invalidates a cached run, diagnosing a miss, cache format, terra scratch |
| `references/hpc-slurm.md` | TMPDIR, proxies, ulimits, memory, job dependencies, submission timeouts |

## Related skills

- `spades-experiments` — choosing the experiment function, replicates, seeds,
  controlled comparisons.
- `spades-module-development` — when the fix belongs in a module.
