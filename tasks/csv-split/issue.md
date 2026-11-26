`csvline.split_csv_line(line, sep=",")` splits a single CSV line into fields, but it breaks on quoted fields. Do not use the standard-library `csv` module; fix the parser itself.

- `'a,"b,c",d'` should give `['a', 'b,c', 'd']`
- doubled quotes inside a quoted field are a literal quote: `'"say ""hi""",x'` gives `['say "hi"', 'x']`
- empty fields are kept: `'a,,b,'` gives `['a', '', 'b', '']`, and `''` gives `['']`
- the `sep` argument must work, e.g. `sep=";"`
- whitespace inside fields is kept as is
- an unterminated quote, like `'a,"b'`, should raise `ValueError`
