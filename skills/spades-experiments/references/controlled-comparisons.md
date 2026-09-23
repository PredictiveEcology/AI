# Controlled comparisons: does this change alter the results?

A replicate experiment asks "how variable is the model?". This asks a different
question: "is arm A different from arm B, and is the difference the change I made?"
The design has to make every other explanation impossible.

## The design

**Two arms, both present at once.** Put each code version in its own git worktree, so
you are not checking branches in and out under a running job:

```
worktrees/<name>/base/modules/<Module>    # development
worktrees/<name>/fix/modules/<Module>     # the branch under test
```

Point the run at one or the other through `paths$modulePath`. Nothing else in the
driver differs between arms.

**One start state, frozen.** Compute the initial conditions once, write them to disk
(`.rds` for tables, `.tif` for rasters), and have both arms load the same files. If
each arm builds its own start state, a difference in the results may be a difference in
the inputs. Note that a `SpatRaster` read from disk keeps its file path and the
simulation will mutate it — `terra::deepcopy()` it after loading.

**Same seed per replicate, in both arms.** Seed by replicate number, and set it both
for the driver (`set.seed(rep)`) and for the module (`.seed = list(init = rep)`).
Three replicates per arm is a reasonable floor; it tells you whether an observed
difference is larger than run-to-run noise.

**Caching off.** `reproducible.useCache = FALSE` for the runs. A cached intermediate is
the single most effective way to produce a convincing null result that means nothing.

**Snapshots, not just the end.** Save the state object (e.g. `cohortData`) every N
years through the `outputs` argument, and compute a metric row per snapshot. An effect
that appears at year 50 and washes out by year 400 is invisible in a final-state
comparison.

## The metric table

One row per (arm, replicate, year), with the quantities the change should move and a
few that it should not. For a cohort model that might be: number of cohorts, number of
pixel groups, cohorts per pixel group (mean / median / max), total biomass, mean age.

Include a column that counts **how often the changed code could act at all**. This is
the column that saves you. In the `calculateSumB()` case it was "cohort-years where a
cohort younger than `successionTimestep` shares a pixel group with an older one" —
the only rows where the old and new rules can differ.

## Reading a null result

If the arms come out the same, there are three possibilities and they need different
responses:

1. **The change genuinely does not matter** for anything measured.
2. **The changed line never executed.** Check the exposure column. In a landscape run
   with no disturbance, for example, LandR cohorts are created at age
   `successionTimestep + 1` and never younger, so code that only acts on younger
   cohorts has nothing to act on.
3. **The configuration excluded it.** Stand-replacing disturbance leaves no survivors,
   so burned pixels contain only new cohorts and a rule about mixed-age groups still
   never fires. Partial mortality is what produces mixed-age groups.

Cases 2 and 3 are not evidence that the change is unnecessary. Report which one you
are in, with the exposure number, and say what configuration *would* exercise the
change. A comment that reports the null landscape result without linking the focused
measurement makes a defensible change look pointless.

## When to reach for this

Worth the setup when a change alters a shared data structure or a rule applied every
timestep, and cheap alternatives have been exhausted. Before building it, ask whether a
unit test on the changed function answers the question — often it does, in minutes
rather than hours. The experiment earns its cost when the question is about emergent
behaviour over time, not about one function's output.

## Housekeeping

The driver scripts for one of these are disposable: a fixture module that supplies
disturbance, a prepare-inputs script, a run-one script, a shell loop. Keep them out of
the module repository — they are experiment apparatus, not module code — and record
in the session log where they lived and what they produced, so the numbers can be
traced after the scratch directories are deleted.
