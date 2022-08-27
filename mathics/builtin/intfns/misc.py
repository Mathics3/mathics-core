from mathics.builtin.arithmetic import _MPMathFunction

from mathics.core.attributes import (
    listable as A_LISTABLE,
    numeric_function as A_NUMERIC_FUNCTION,
    protected as A_PROTECTED,
    read_protected as A_READ_PROTECTED,
)


class BernoulliB(_MPMathFunction):
    """
    <dl>
      <dt>'BernoulliB[$n$]'
      <dd>represents the Bernouilli number B_$n$.

      <dt>'BernouilliB[$n$, $x$]'
      <dd>represents the Bernouilli polynomial B_$n[x]$.
    </dl>

    >> BernoulliB[42]
     = 1520097643918070802691 / 1806

    First five Bernoulli numbers:

    >> Table[BernoulliB[k], {k, 0, 5}]
     = {1, -1 / 2, 1 / 6, 0, -1 / 30, 0}

    First five Bernoulli polynomials:

    >> Table[BernoulliB[k, z], {k, 0, 3}]
     = {1, -1 / 2 + z, 1 / 6 - z + z ^ 2, z / 2 - 3 z ^ 2 / 2 + z ^ 3}
    """

    attributes = A_PROTECTED | A_LISTABLE
    mpmath_name = "bernoulli"
    nargs = {1, 2}
    summary_text = "Bernoulli number and function"
    sympy_name = "bernoulli"
