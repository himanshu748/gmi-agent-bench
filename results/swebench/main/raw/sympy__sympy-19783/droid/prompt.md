<pr_description>
Consider the following PR description:
Dagger() * IdentityOperator() is not simplified
As discussed on the mailing list the following does not work.
```
from sympy.physics.quantum.dagger import Dagger
from sympy.physics.quantum.operator import Operator
from sympy.physics.quantum import IdentityOperator
A = Operators('A')
Identity = IdentityOperator()
A * Identity #This gives A, correctly
B = Dagger(A)
B * Identity #This returns A^\dagger I 
```


</pr_description>

Your task is to make changes to non-test files in /testbed (the current directory) so that the
issue in the PR description is resolved, in a way that is general and consistent with the codebase.
Do not modify tests or configuration files (pyproject.toml, setup.cfg, etc.). Do not commit.
The environment is already set up (use `python`; the testbed environment is active).
When you are done, stop.
