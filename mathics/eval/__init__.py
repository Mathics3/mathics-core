"""

mathics.eval

This module contains routines that implement different kind of evaluations over expressions, like

  * eval_N
  * eval_makeboxes
  * numerify
  * test helpers that check properties on expressions.

"""

# Ideally, this module should depend on modules inside ``mathics.core`` but not in modules stored in ``mathics.builtin`` to avoid circular references.


# ``evaluation``, ``_rewrite_apply_eval_step``, ``set`` that in the current implementation
# requires to introduce local imports.
# This also would make easier to test and profile classes that store Expression-like objects and methods that produce the evaluation.
