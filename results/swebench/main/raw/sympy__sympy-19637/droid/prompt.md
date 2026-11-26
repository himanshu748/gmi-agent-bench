<pr_description>
Consider the following PR description:
kernS: 'kern' referenced before assignment
from sympy.core.sympify import kernS

text = "(2*x)/(x-1)"
expr = kernS(text)  
//  hit = kern in s
// UnboundLocalError: local variable 'kern' referenced before assignment

</pr_description>

Your task is to make changes to non-test files in /testbed (the current directory) so that the
issue in the PR description is resolved, in a way that is general and consistent with the codebase.
Do not modify tests or configuration files (pyproject.toml, setup.cfg, etc.). Do not commit.
The environment is already set up (use `python`; the testbed environment is active).
When you are done, stop.
