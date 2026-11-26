You are working in a small Python repository (the current directory).
Resolve the following issue.

<issue>
`csvline.split_csv_line(line, sep=",")` splits a single CSV line into fields, but it breaks on quoted fields. Do not use the standard-library `csv` module; fix the parser itself.

- `'a,"b,c",d'` should give `['a', 'b,c', 'd']`
- doubled quotes inside a quoted field are a literal quote: `'"say ""hi""",x'` gives `['say "hi"', 'x']`
- empty fields are kept: `'a,,b,'` gives `['a', '', 'b', '']`, and `''` gives `['']`
- the `sep` argument must work, e.g. `sep=";"`
- whitespace inside fields is kept as is
- an unterminated quote, like `'a,"b'`, should raise `ValueError`
</issue>

Change the source code so the behaviour described in the issue is correct.
Hidden tests that check every point in the issue will be run after you finish,
and the existing tests in tests/ must keep passing. Do not edit or delete tests.
You can run the tests with `python -m pytest -q`. When you are done, stop.
