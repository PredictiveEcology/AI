## Use the shared CI actions, at the shared ref

CI should call the organisation's shared composite actions and reusable workflows,
referenced at the shared ref — for PredictiveEcology, `PredictiveEcology/actions@main`.
Never hand-roll or hand-patch a per-repo copy of setup that the shared action already
does.

When a shared action fails, resolve the pin before blaming the action. A stale tag, not
broken code, is the usual cause.

If the shared action is wrong, fix it there, once.

**Why:** divergent copies are how a bad pin survives. `install-spatial-deps` kept adding
the `ubuntugis-unstable` PPA in every tag from `v0.1` to `v0.5` for months after the
shared action on `main` had removed it, and repos pinned to those tags kept inheriting
it.
