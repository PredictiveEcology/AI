# Running SpaDES projects on an HPC cluster (Slurm)

Site details vary; the traps below have each cost real runs. Check your own site's
documentation for the exact values (partition limits, proxy address).

## Temporary directory

Compute-node `/tmp` is often a small tmpfs (hundreds of MB to a few GB), and R's
`tempdir()` is under `/tmp` unless `TMPDIR` is set. reproducible downloads and
post-processes in `getOption("reproducible.tempPath")` = `file.path(tempdir(),
"reproducible")`, so a large download is cut at the tmpfs size. The symptom is a data
error far from the cause: a 3.4 GB GeoTIFF that was exactly 524,210,176 bytes, then
`crop` failing with "too few values". A second job waiting on the same file can
accept the short copy as "local file matches remote version".

- Export `TMPDIR` to a directory on the shared, large filesystem for every job (with
  `experimentSBATCH()`, `sbatch_opts = list(export = "ALL,TMPDIR=<path>")` or the
  equivalent in your job script). Check from inside a job that `tempdir()` is there.
- Recent reproducible checks the size against the server's `Content-Length` when the
  server sends one. When a file looks wrong, compare its size with the source before
  debugging anything else, and delete the short file and its `CHECKSUMS.txt` row
  before retrying.
- Login nodes have a `/tmp` too. Launches killed by a timeout leave `Rtmp*` folders
  behind; a full login-node `/tmp` makes the next install fail ("Failed to
  uncompress"). Only remove folders whose owning R process is gone and that hold no
  terra files a live job uses.

## Internet from compute nodes

Many sites give compute nodes no direct outbound access, or access only through a
proxy. Without it, downloads, GitHub installs and Google Drive calls time out.

- Set `https_proxy`, `http_proxy` and `no_proxy` (include `localhost,127.0.0.1` and
  the site's internal domain, so PSOCK workers and node-to-node traffic skip the
  proxy) in the job environment. Test with a tiny job before relying on it.
- terra turns PROJ's network access on when it loads. With no route out, a CRS
  transform (e.g. in `expanse()`) can wait on curl to fetch a grid from cdn.proj.org,
  and the job looks hung at a few % CPU. Call `terra::projNetwork(FALSE)` (workers
  started by recent `experiment*()` do), or set `PROJ_NETWORK=OFF`.
- A transfer or data partition with internet may have a short time cap, too short for
  large downloads in a full setup.

## Limits that Slurm copies from your shell

With `PropagateResourceLimits=ALL` (common), a job gets the submitting shell's soft
limits. An open-file soft limit of 1024 killed terra-heavy runs by the hundred.
`experimentSBATCH()` raises `ulimit -n` to the hard limit in its job script; a
hand-written job script should do the same.

## Memory per job

- `--mem=0` may be refused and `--time` may be required even on "infinite"
  partitions. Read the partition's `MaxMemPerCPU`.
- Measure the peak first: `sacct -j <id> --format=JobID,MaxRSS,State` after a run, or
  `/usr/bin/time -v Rscript global.R` on a workstation. A workstation peak is a good
  estimate for the same job on the cluster.
- The cgroup limit is hard: a job is OOM-killed at its request. Leave room for the
  controller process and any cluster workers it starts on the same node.
- Memory varies a lot between study areas. Keep a record per unit of work and size
  each job from it rather than one value for all.
- When a host or job runs out of memory because your own workers were placed too
  densely, fix the allocation. Do not exclude the host.

## Submitting and chaining jobs

- `sbatch` can report "Socket timed out" and still submit the job. Check `squeue`
  before resubmitting, or you run it twice.
- `--dependency=afterok:<id>` trusts the exit code. A setup step that fails but exits
  0 lets the dependent job start on broken inputs; make sure your `global.R` errors
  out (non-zero exit) when it fails. A dependent job whose parent failed sits PENDING
  forever (`DependencyNeverSatisfied`); cancel it.
- On multi-cluster Slurm sites, `squeue` / `sacct` / `scancel` may need `-M
  <cluster>`; without it they show nothing.
- Stop a Slurm campaign with `killExperimentSBATCH()` (stop files, then `force =
  TRUE` for `scancel`), or `scancel` the job IDs. Then reset or re-queue rows as in
  `stopping-and-restarting.md`.

## Shared libraries and modules on the cluster

- Jobs that start while a shared library is being changed fail with missing packages
  or corrupt lazy-load databases. Do not install into a library while queued jobs
  may start; use dev libraries (`packages-for-live-runs.md`).
- Updating a module folder that later-starting jobs will read changes their cache
  keys (`caching-for-users.md`): they recompute, and may try to download. A restart
  is a new `simInit()`, so it also sees the new module.

## Threads

Each R worker that uses a multi-threaded BLAS, OpenMP or data.table can start as many
threads as the node has cores. With many workers per node that oversubscribes it
badly. Set `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1` and
`data.table::setDTthreads(1)` in workers unless you have planned the thread budget,
and count forks x threads per job against `--cpus-per-task`.
