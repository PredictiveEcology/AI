# Compute for spread fits

A spread fit runs a DEoptim cluster built by the `clusters` package, usually 40 workers
across one or more machines, for several hundred generations. Numbers below are
measured examples from one campaign; use them as orders of magnitude.

## Workers

- **A cluster never starts with fewer workers than requested.** It waits for cores and
  memory. A fit that started with the 2 workers left after others lost memory died.
- `cores` (the machines and core counts) is not in the cache key: it changes where the
  work runs, not the result. Same for `libPathDEoptim` and `objFunCoresInternal`. Adding a
  host should never cause a cache miss; if it does, a machine-specific value has entered a
  key.
- Leave about 2 cores free per host for other users (`clusters.keepFreeCores`).
- Capacity rule of thumb: about total cores / 100 fits at once on a shared fleet.
- Before adding fits, read each fit's per-host allocation messages ("Starting <host> x n"),
  not totals.
- If your own workers overload a host (out of memory, hung), fix the allocation; do not
  drop the host.

## Memory

- Measured over 457 workers: peak resident memory median 4.5 GB, 90th percentile 6.5 GB,
  maximum 14.1 GB. `fireSenseUtils::spreadFitWorkerMemoryGB` (14) is the budget before a
  fit has its own record; after its first chunk, the fit's own record is used
  (`clusters.workerMemoryGB` overrides).
- A flat high budget can make a big job impossible to place (14 GB x 64 workers did not
  fit a large node). On Slurm, size each ELF's memory from its record, and remember the
  partition's default memory per CPU is often small.
- Data-preparation jobs need more than you expect: an inputs-only job ran out at 28 GB in
  `prepSpreadFitData`.

## Threads

- R's OpenBLAS starts up to 64 threads per process. Each DEoptim worker then used 5-6
  CPUs while the allocator assumed 1; small matrix multiplies ran 2-3x slower and used
  30-45x the CPU. `clusters` starts workers with `OPENBLAS_NUM_THREADS=1`
  (`clusters.workerBlasThreads`). Setting it with `Sys.setenv()` after R starts is too
  late.
- That covers cluster workers only. The fit's main process and its forks inherit the
  full pool. Set `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1` in the environment of any
  analysis job too.
- **Hyperthreading costs.** Per-evaluation time rose 7-14% at 1-1.5 workers per physical
  core and 29-38% at 1.5-2. `clusters` weights a hyperthread at 0.75 of a core and also
  uses measured host speeds.
- A machine with more, slower cores is not a faster fit: on one comparison, an HPC node's
  generation was 1.6-2x slower than the local cluster's at 40 workers. HPC wins on how
  many fits run at once, not on per-fit speed.

## Shipping data to workers

- `parallelly` stores `sys.calls()` on every node object. A closure created in a frame that
  holds the cluster object ships the whole cluster with it: 9.6 GB per worker in one
  incident, 4.5 min per cluster build. Create functions sent to workers in the global
  environment. Diagnose a stalled send with `ss -tni` (bytes_acked); `/proc/<pid>/io` does
  not count socket sends.
- DEoptim generation sends are small (a few KB); the problem is only closures.

## Shared state

- `clusters` keeps its records (`coreReservations.rds`, `fitMemory.rds`, `hostSpeed.rds`)
  in one user folder shared by every installed version. Never add columns: an added column
  killed two live fits. Tests must set `options(clusters.reservationsPath = tempdir())`.
- Never install packages into a library that running workers load. Stop the fits, install,
  relaunch (generations are cached). An install under live workers gave "lazy-load
  database is corrupt" errors.

## Compute waste found and fixed (examples)

| Waste | Size | Cause | Fix |
|---|---|---|---|
| Input preparation rerun per replicate | about 60 h | replicate in `inputPath`, which is in prepared inputs' cache keys | `inputPath` per ELF only |
| Prep events rerun when only a run label changed | 9-29 h per event type | run labels (ledger suffix, rep, run name) in event keys | labels out of prep-event keys; keep the suffix only where the event writes the ledger |
| Cache misses after adding a host | whole events | `cores` in the key | `defineParameter(cacheKey = FALSE)` |
| DEoptim evaluated each generation twice | 2x | wrapper ran `DEoptim(itermax = 1)` from the previous population | one evaluation per generation |
| Later fits got 2-7 workers, hosts idle for hours | hours | live reservations counted twice in free cores | reservations decay with age |
| Records rewritten every generation | 2.9 s per generation | 8 MB file rewritten under a lock | written at rebalance and at the end |
| Threshold calibration before each fit | about 3 h per fit | a step the CRPS objective no longer used | removed |
| Power-law calibration in every hindcast | host load 180 | one fork per fire, in a job that only predicts | calibration only when the job fits or validates |

Pattern: most waste was a cache key that held something that does not change the result
(a path, a label, a core count), or work kept after the reason for it was gone. Measure
before engineering a fix.
