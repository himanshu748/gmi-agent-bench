`semver.compare(a, b)` gives wrong answers.

- `compare("1.10.0", "1.9.0")` returns `-1`, but 1.10.0 is newer, so it should return `1`.
- Pre-release versions are not handled. Per Semantic Versioning 2.0.0, `1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-beta < 1.0.0-rc.1 < 1.0.0`. Numeric pre-release identifiers compare numerically and rank below alphanumeric ones.
- Build metadata (`+build.5`) must be ignored for ordering.
- `sort_versions(list)` should use the same ordering.
- Malformed input such as `"1.2"` or `"a.b.c"` should raise `ValueError`.

`compare` returns -1, 0 or 1.
