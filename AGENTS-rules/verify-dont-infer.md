## Verify claims; do not infer them

Before attributing a failure to the environment — timing, load, flakiness, "unrelated"
— run the controlled comparison: same code, same isolation, one variable changed.

"Probably flaky" is a hypothesis, not a finding. State it as one, and either test it or
say it is untested.

**Why:** asserting a cause that was never tested sends the next person down the same
path, and the experiment that would have settled it is almost always cheaper than the
time spent arguing about it. The same applies to a null result: "no effect" and "the
changed code never ran in this configuration" look identical in the output and mean
entirely different things.
