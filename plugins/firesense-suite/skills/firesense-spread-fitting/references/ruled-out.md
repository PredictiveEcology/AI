# Spread fitting: ruled out, and retracted

Read before proposing a change to the objective, the link or the stop rule. Re-open one
of these only with new evidence, and say what the evidence is.

## Objectives and terms

| Tried | Result | Why dropped |
|---|---|---|
| Per-fire t log-likelihood + pooled AD + annual area + area distribution ("classic", `SNLL_FS`) | Objective minimum at an area ratio of about 0.6; in-sample area 0.55-0.95 | Under-burns. CRPS fits gave 0.94-1.09. `SNLL_FS` was removed and now stops the fit |
| Per-fire log score weighted by fire size (`weighted = TRUE` or `"sqrt"`) | 2.4-7.6x over-burn | A weighted log score is not a proper score; it rewards over-predicting large fires. Keep `weighted = FALSE` or use CRPS |
| Rank / kernel-density objective, independent of the buffers (fireSenseUtils #183) | Year-effect SD overshot by 0.4-0.5; hindcast area 32x | Abandoned |
| Threshold calibration before the fit (`estimateThreshold`) | 96 objective runs with 0 usable, 2.7-7 h per ELF | CRPS has no early-stop threshold to calibrate. Removed |

## Runaway fires and buffers

- **Replacing a runaway's size in every size term**: under-burned. Censoring was moved
  into the likelihood only.
- **`penaliseRunaways = TRUE`** (stop a fire at its buffer edge, give it no density):
  in known-truth tests it shrank the year-effect SD 3-4x (truth 0.25 recovered as
  0.03-0.11). Default is now FALSE.
- **Censoring inside the current terms**: no gain over not censoring.
- **Bigger buffers**: did not reduce the share of cut fires. An escaped simulated fire
  runs to the edge whatever the edge's distance.
- **Re-simulating only the cut fires**: merged and then reverted in favour of whole-landscape
  spread, which removes buffers, cut flags and re-simulation altogether.

Rule that came out of it: no censoring and no penalties for runaways. If fires are cut,
remove the cut (whole landscape), do not model around it.

## Links and parameters

- **Logistic link with a ceiling (`"ceiling"`)**: 59-77% of pixels sat within 0.01 of the
  ceiling every year, so climate barely moved spread between years. A hard-coded lower
  bound of 0.25 on the ceiling, above the percolation threshold of about 0.245-0.25, caused
  runaway hindcasts. Replaced by the power-law link with per-ELF bounds from calibration.
  Under the same objective, power law won on every seed tested.
- **Fitting `gamma`**: confounded with the coefficient scale. Fixed.
- **Narrow bounds as a modelling choice**: never. Held-out fits reached 25.7 of a bound of
  30 (climate), -23 of -30 (`youngAge`), 54.5 of 60 (fuel).
- **Capping the year-effect SD (e.g. at 1)**: not adopted. No absolute cap is needed.
- **Tighter stop thresholds (SE, MAD change)**: may never be met on a noisy objective, so a
  fit runs to `itermax`. Change `window` / `minGenerations` instead.
- **More members than workers with load balancing**: settled against. See the SKILL.

## DEoptim internals

- DEoptim 2.2.8 with `c > 0`: if a call's first generation has no successful trial,
  DEoptim's adaptive mean F becomes NaN and every later trial vector is NaN. The objective
  then fails on every worker at once with an error that points at the objective, not at
  DEoptim (seen as `quantile.default(): missing values and NaN's not allowed`). It only
  happens when several generations run per DEoptim call. Use `c = 0`, or guard against
  non-finite trial parameters.
- An earlier wrapper overrode the caller's NP and strategy and evaluated each generation
  twice. The caller's settings now win and the extra evaluation is gone.

## Retracted results

- **"Delta 0.5 over-burns in-sample, 0.75 is best, delta > 1 goes the wrong way."** All
  wrong. The in-sample simulation driver never passed `powerLawShape`, so every in-sample
  run at delta other than 1 ran at delta 1. Corrected: area 0.90-1.05 and top-10 about
  0.7-0.85 at every delta from 0.5 to 3. Lesson: when a sweep shows a pattern, first check
  that the swept parameter reached the simulator (outputs must differ between settings).
- **"Sign-unstable fuel coefficients mean fuel matters little."** Wrong inference; see
  "Unidentified is not unimportant" in the SKILL.
- **"A module update forces every fit to rerun."** Wrong; fit reuse is spatial (see
  `firesense-overview`).
