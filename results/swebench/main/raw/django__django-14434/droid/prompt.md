<pr_description>
Consider the following PR description:
Statement created by _create_unique_sql makes references_column always false
Description
	
This is due to an instance of Table is passed as an argument to Columns when a string is expected.

</pr_description>

Your task is to make changes to non-test files in /testbed (the current directory) so that the
issue in the PR description is resolved, in a way that is general and consistent with the codebase.
Do not modify tests or configuration files (pyproject.toml, setup.cfg, etc.). Do not commit.
The environment is already set up (use `python`; the testbed environment is active).
When you are done, stop.
