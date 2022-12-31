"""
Mathics Evaluation Functions

Routines here are core operations or functions that implement evaluation. If there
were an instruction interpreter, these would be the instructions.

These operatations then should include the most commonly-used Builtin-functions like
``N[]`` and routines in support of performing those evaluation operations/instructions.

Performance of the operations here can be important for overall interpreter performance.

It may be even be that some of the functions here should be written in faster
language like C, Cython, or Rust.
"""

# Ideally, this module should depend on modules inside ``mathics.core`` but not in modules stored in ``mathics.builtin`` to avoid circular references.


# ``evaluation``, ``_rewrite_apply_eval_step``, ``set`` that in the current implementation
# requires to introduce local imports.
# This also would make easier to test and profile classes that store Expression-like objects and methods that produce the evaluation.
