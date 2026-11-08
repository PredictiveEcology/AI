# Ignition, escape and burn

## The models

- Ignition and escape are xgboost boosters with objective `count:poisson`, fitted per ELF
  on coarse (about 1 km) pixel-years. The ignition model counts natural (and unknown-cause)
  ignitions; the escape model counts fires that reach `escapeSizeHa` (50 ha), fitted only
  on pixel-years that had ignitions.
- `fireSense_ignitionFit` only accepts xgboost (`modelAlgorithm`).
- The booster's objective is stored with the fit. `storedFitIsCompatible()` checks both the
  covariate names and the objective before a stored fit is reused.

## Where the randomness lives

The predict modules return expected values only (`ignitionProb`, `escapeProb`, and the
distribution they came from). All random draws are in `fireSense_burn`:

- ignitions: Poisson draws from the ignition mean (`drawCounts()`, which stops on any
  objective other than `count:poisson`, so a model whose family cannot be drawn from
  fails loudly);
- escapes: `rbinom(ignitions, q)` with `q = m * (1 - exp(-lambda)) / lambda`, capped at 1.
  An earlier `pmin(rpois(m), ignitions)` lost about a quarter of the expected escapes in one
  ELF, because the cap cut the upper tail;
- the year effects: each process gets its **own** year draw. One shared draw for
  ignitions and escapes compounded (escapes are drawn where ignitions fell) and inflated
  escapes by about 1.4x, while in the fit data the two year residuals were uncorrelated.
- the spread year effect is added to the linear predictor `x`, before the link. Adding it
  to the spread probability afterwards left pixels at `p = 0` unable to burn in any
  drought year.

## Traps found, with the symptom

**Predictions low after an objective change, and the fit is labelled correctly.** A
stale cache. The outer `Cache()` around the model build was keyed on its own body, not on
the function that set the xgboost objective, so after a Tweedie-to-Poisson change a
"refit" returned the old Tweedie boosters under a Poisson label. Check the booster itself
(`xgb.config(model)` objective), not the ledger's label. General rule: when a cached
function's behaviour lives in a callee, put that callee in the cache key.

**Totals right, years wrong.** Summed over years, predicted and observed ignitions agreed
(within 0.1%), yet quiet years were over-predicted about 3x and busy years under-predicted:
the booster's predictions are compressed on its own training years (sd of log expected
about a third of sd of log observed). Poisson draws add no extra year-to-year variance.
Check quiet and busy years separately, not only totals.

**Observed ignitions the model can never produce.** About 20% of observed natural
ignitions fell on coarse cells the fit had dropped, because a coarse cell with any
non-flammable pixel got `NA` fuel (aggregation without `na.rm`). Fixed by
`fireSenseUtils::fuelCovsToCoarse()`. Check that the set you score against is a set the
model can generate.

**Escape counts differ between fit and scorer.** The fit counted NFDB points of at least
50 ha; a scorer counted NBAC polygons of at least 50 ha. They differ (61 against 51 in
one ELF core). Use the fit's definition when scoring (`fireSenseUtils::hindcastObserved()`
uses the fit's own helpers), or report both.

**Escape count, not fire size, drives area.** In one ELF, simulated years with no escape
were 19% against 44% observed. Before blaming the spread model for an area bias, compare
escape counts per year.
