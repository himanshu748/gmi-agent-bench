`duration.parse_duration(text)` should turn a human duration into whole seconds (an `int`), but only the exact form `"1h30m"` works.

It should accept:
- any combination of the units `d`, `h`, `m`, `s` in that order, each at most once: `"90s"`, `"2h"`, `"1d2h"`, `"1h30m15s"`
- optional whitespace between parts and around the string: `" 1h 5m "`
- decimal amounts: `"1.5h"` is 5400, `"0.5m"` is 30 (round to the nearest second)
- uppercase units: `"2H"`

It should raise `ValueError` for empty strings, unknown units (`"5x"`), numbers without a unit (`"10"`), repeated or out-of-order units (`"5m1h"`, `"1h1h"`), and negative values.
