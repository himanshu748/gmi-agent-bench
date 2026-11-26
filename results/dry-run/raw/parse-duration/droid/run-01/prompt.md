You are working in a small Python repository (the current directory).
Resolve the following issue.

<issue>
`duration.parse_duration(text)` should turn a human duration into whole seconds (an `int`), but only the exact form `"1h30m"` works.

It should accept:
- any combination of the units `d`, `h`, `m`, `s` in that order, each at most once: `"90s"`, `"2h"`, `"1d2h"`, `"1h30m15s"`
- optional whitespace between parts and around the string: `" 1h 5m "`
- decimal amounts: `"1.5h"` is 5400, `"0.5m"` is 30 (round to the nearest second)
- uppercase units: `"2H"`

It should raise `ValueError` for empty strings, unknown units (`"5x"`), numbers without a unit (`"10"`), repeated or out-of-order units (`"5m1h"`, `"1h1h"`), and negative values.
</issue>

Change the source code so the behaviour described in the issue is correct.
Hidden tests that check every point in the issue will be run after you finish,
and the existing tests in tests/ must keep passing. Do not edit or delete tests.
You can run the tests with `python -m pytest -q`. When you are done, stop.
