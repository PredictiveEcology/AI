# Stopping and restarting SpaDES runs

## Is it safe to stop?

Almost always. A restarted job replays cached events and cached optimiser
generations quickly, and if the cache misses it is usually because of a change you
wanted in the rerun. The one case worth a word first is a long fit mid-generation
whose generations are not cached.

So when a library update or a fix is blocked by a running job: stop it, install,
relaunch. Do not plan around "wait until it finishes".

## Find the whole job before killing anything

A queue job is a tree:

```
tmux pane shell
└─ worker R (sources global.R)
   └─ forks: mclapply, PSOCK/fork cluster workers, terra/GDAL helpers
      └─ their forks
```

Collect every PID first, then kill:

```bash
pstree -p <panePidOrWorkerPid>                 # look at it
pids=$(pstree -p <pid> | grep -o '([0-9]\+)' | tr -d '()')
kill $pids                                     # then kill -9 any survivors
```

For tmux workers, `tmux list-panes -a -F '#{pane_id} #{pane_pid} #{pane_title}'`
gives each pane's shell PID.

Afterwards, look for your R processes whose parent is PID 1:

```bash
ps -o pid,ppid,etime,pcpu,rss,args -u "$USER" | awk '$2 == 1 && /exec\/R|R --/'
```

Forks of a killed job end up here and keep running at full CPU. Kill them by PID.

## Things that look like orphans but are not

- **Reverse ssh tunnels.** A PSOCK cluster with `revtunnel = TRUE` (as `clusters` and
  `parallelly` can build) starts one `ssh -R <port>:localhost:<port> ... Rscript ...`
  process per remote worker on the launching machine. Each has ppid 1 and the
  R library path in its command line, so a `pgrep -f <libraryPath>` count includes
  them. With several large clusters there can be hundreds. Each is ~9 MB. Killing
  them cuts the live workers of running jobs. Count real workers by matching the R
  executable, not the library path, and check `ss -tp` for established sockets
  before treating any ppid-1 process as abandoned.
- **Other users' sessions** (RStudio, Positron) on a shared host.

## Do not

- `pkill -f <pattern>` / `pgrep -f <pattern>` to stop a job. The pattern matches how
  one instance was started (relative vs absolute path) and misses others; a pattern
  that appears in your own command line kills your own shell. One surviving helper
  instance went on deleting live files for two hours while it was reported as
  stopped.
- `tmux kill-session` on a tmux server shared with other work. It has crashed the
  server, taking every session on it down, and left the jobs' cluster workers
  running.
- Delete terra scratch files or "dead-PID" temp files as part of the stop. See
  `caching-for-users.md`.

## Stopping a campaign from taking new work

Workers claim the topmost row whose `status` is `PENDING` or `INTERRUPTED`. Any other
value is skipped, and a status you set while a job runs is kept when it ends. So:

- Set PENDING rows to `"HOLD"` to stop new claims. Running jobs are untouched. Set
  them back to `"PENDING"` to resume.
- If the launcher was given `ss_id`, workers claim through the Google Sheet. Write
  the status there. Changing only the local queue `.rds` does nothing; the `.rds` is a
  mirror that can lag the Sheet.
- An `ERROR` row is not claimed again until you set it to `PENDING`.
- A RUNNING row whose worker died is demoted to `INTERRUPTED` and is claimable, so it
  restarts.

`experimentTmux()` has no stop file (`experimentSBATCH()` and `experimentFuture()`
do; see `killExperimentSBATCH()` / `killExperimentFuture()`). In its default
`pane_mode = "killAndNewPane"` each pane runs one job and is respawned for the next,
so closing a pane between jobs also stops it.

## Relaunching

- **Use a new queue file name** after a hold, after errors, or after a package fix.
  With the same name the old queue is reused (the new `df` is ignored), held rows
  stay held, and the new workers go idle. With a Sheet, a same-name relaunch after a
  kill can see stale RUNNING rows with dead PIDs; the stale-row reclaim has then
  given one row to two workers.
- **After any relaunch, check claims per worker** in the first minutes: one claimed
  row per worker, no row claimed twice, and the expected number of panes or jobs.
- **Two queues never exclude each other.** If two campaigns run at once, make their
  rows disjoint (different study areas or units) or stop one before their orders
  meet. Two jobs on the same `outputPath` overwrite each other's files: SpaDES output
  names carry no run or PID stamp, and `terra::writeRaster()` is not atomic, so a
  reader can see a half-written file. The reproducible cache itself is protected by
  per-entry file locks; the outputs are not.

## Editing scripts while jobs run

`Rscript file.R` reads `file.R` lazily. If you edit it in place (editor save, `sed
-i`, writing over it), a running job resumes at its old byte offset in the new text
and fails with a parse error, often after hours of work. Before editing a script,
check `ps` for jobs running it. If there are any, write the new file elsewhere and
`mv` it into place: the running jobs keep the old inode.
