"""
Mathics Evaluation Functions

Routines here are core operations or functions that implement
evaluation. If there were an instruction interpreter, these functions
that start "eval_" would be the interpreter instructions.

These operatations then should include the most commonly-used Builtin-functions like
``N[]`` and routines in support of performing those evaluation operations/instructions.

Performance of the operations here can be important for overall interpreter performance.

It may be even be that some of the functions here should be written in faster
language like C, Cython, or Rust.

"""

# This module should not depend  on ``mathics.builtin``. Dependence goes only the other way around

# ``evaluation``, ``_rewrite_apply_eval_step``, ``set`` that in the current implementation
# requires to introduce local imports.

# Moving evaluation routines out of builtins allows us to test and profile code here.
