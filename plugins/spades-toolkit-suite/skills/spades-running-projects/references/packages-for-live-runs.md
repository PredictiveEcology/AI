# Installing packages while SpaDES runs are live

## The failure

R loads a package's code lazily from its installed `.rdb` files. An install replaces
those files. A running session that later loads a function from the replaced package
fails with

```
Error: lazy-load database '.../R/<pkg>.rdb' is corrupt
```

or with a missing package or namespace. It can happen hours after the install, so it
is easy to blame something else. Jobs that start *during* an install can also see a
half-installed package.

Seen in practice: an install into a shared library while 28 fits ran broke them; a
second campaign launched while one was running reinstalled moved branches and killed
13 running fits; HPC hindcast jobs failed with missing `terra` and `SpaDES.project`
while the shared library was being changed.

## The fix: give each launch its own library

SpaDES.project >= 1.2.0.9033 does this in the launchers:

```r
experimentTmux(df, global_path = "global.R",
               devPackages = c("PredictiveEcology/reproducible@development (>= 3.2.1.9063)"))
```

`devPackages` builds `<projectLibrary>_dev/<id>`: hard links to the current dev
library, plus only the packages that changed. Every worker starts with
`.libPaths(c(<dev>, <project library>))` and `options(spades.packagePath = ...)`, so
`setupProject()` in `global.R` needs no `packagePath`. Nothing writes to a library a
running job uses. `sweepDevLibraries(keep = ...)` removes the ones no job needs.
See `?devLibrary`.

Check a launch did this: the generated worker script must contain
`options(spades.packagePath = c(<dev>, <stable>)`. An older SpaDES.project silently
accepts `devPackages` through `...` and ignores it.

Jobs started before this existed still load from the shared library. Before
installing, list running jobs whose `.libPaths()[1]` is the project library itself;
installing will break them.

## Any launch may be an install

If the launcher's first step installs pinned packages (a `pak` or `Require` line at
the top of the launcher, or `setupProject()` resolving `packages`), every launch
installs whatever moved since the last one. Starting a second campaign then installs
under the first. Before launching while runs are live, compare the installed
`RemoteSha` in each pinned package's `DESCRIPTION` with the branch head, or launch
with installs turned off.

## Branch pins do not update

```r
"PredictiveEcology/reproducible@development"            # installs nothing if reproducible is installed
"PredictiveEcology/reproducible@development (>= 3.2.1.9082)"  # installs if the installed one is older
"PredictiveEcology/reproducible@development (HEAD)"     # always checks the branch head
```

A bare branch pin is satisfied by any installed version. To get a merged fix onto a
machine, bump the package version after the merge, then raise the floor (in
`setupProject(packages = )`, the launcher, or the module's `reqdPkgs`). `(HEAD)`
works too but asks GitHub on every call, which is slow when many workers start.

## "Installing any missing reqdPkgs" that takes ten minutes

`setupProject()` prints this heading and runs Require unless
`spades.useRequire` is FALSE. Require skips the work when the full set of
requirements matches a previous successful call. Change any module's `reqdPkgs` (a
new floor, a new package) and the next worker does a full resolution: minutes at full
CPU, and it may install. That is expected; it is not a hang. `experiment*()` workers
set `SPADES_USE_REQUIRE=false` on recent SpaDES.project to skip it in workers.

## One install, then launch

- Install once, from one process, then launch. Many workers each resolving and
  installing at start is slow and races.
- On a cluster, build the dev library before any job is queued, on a filesystem every
  node can see.
- If the install is blocked by running jobs, stopping them is usually the cheapest
  option; see `stopping-and-restarting.md`.
