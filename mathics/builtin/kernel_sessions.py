# -*- coding: utf-8 -*-
"Kernel Sessions"

from mathics.core.atoms import Integer
from mathics.core.attributes import A_LISTABLE, A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation


class Out(Builtin):
    r"""
    <url>:WMA: https://reference.wolfram.com/language/ref/Out</url>
    <dl>
      <dt>'$\%k$' or 'Out'[$k$]
      <dd>gives the result of the $k$-th input line.

      <dt>'%'
      <dd>gives the last result.

      <dt>''%%'
      <dd>gives the result before the previous input line.
    </dl>

    >> 42
     = 42
    >> %
     = 42
    >> 43;
    >> %
     = 43
    >> 44
     = 44
    >> %1
     = 42
    >> %%
     = 44
    >> Hold[Out[-1]]
     = Hold[%]
    >> Hold[%4]
     = Hold[%4]
    >> Out[0]
     = Out[0]

    #> 10
     = 10
    #> Out[-1] + 1
     = 11
    #> Out[] + 1
     = 12
    """

    attributes = A_LISTABLE | A_PROTECTED

    rules = {
        "Out[k_Integer?Negative]": "Out[$Line + k]",
        "Out[]": "Out[$Line - 1]",
        "MakeBoxes[Out[k_Integer?((-10 <= # < 0)&)],"
        "    f:StandardForm|TraditionalForm]": r'StringJoin[ConstantArray["%%", -k]]',
        "MakeBoxes[Out[k_Integer?Positive],"
        "    f:StandardForm|TraditionalForm]": r'"%%" <> ToString[k]',
    }
    summary_text = "result of the Kth input line"


class Quit(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Quit.html</url>

    <dl>
      <dt>'Quit'[]
      <dd> Terminates the Mathics session.

      <dt>'Quit'[$n$]
      <dd> Terminates the mathics session with exit code $n$.
    </dl>

    'Quit' is the same thing as 'Exit'.
    """

    summary_text = "terminate the session"

    def eval(self, evaluation: Evaluation, n):
        "%(name)s[n___]"
        exitcode = 0
        if isinstance(n, Integer):
            exitcode = n.get_int_value()
        raise SystemExit(exitcode)


class Exit(Quit):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Exit.html</url>

    <dl>
      <dt>'Exit'[]
      <dd> Terminates the Mathics session.

      <dt>'Exit'[$n$]
      <dd> Terminates the mathics session with exit code $n$.
    </dl>

    'Exit' is the same thing as 'Quit'.
    """
