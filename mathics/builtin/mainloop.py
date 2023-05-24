# -*- coding: utf-8 -*-
"""
The Main Loop

An interactive session operates a loop, called the "main loop" in this way:

<ul>
  <li>read input
  <li>process input
  <li>format and print results
  <li>repeat
</ul>

As part of this loop, various global objects in this section are consulted.

There are a variety of "hooks" that allow you to insert functions to be applied to the expressions at various stages \
in the main loop.

If you assign a function to the global variable '$PreRead' it will be applied with the input that is read in the first \
step listed above.

Similarly, if you assign a function to global variable '$Pre', it will be applied with the input before processing the \
input, the second step listed above.
"""

from mathics.builtin.base import Builtin
from mathics.core.attributes import A_LISTABLE, A_NO_ATTRIBUTES, A_PROTECTED

# This tells documentation how to sort this module
sort_order = "mathics.builtin.the-main-loop"


class HistoryLength(Builtin):
    """
    <url>:WMA: https://reference.wolfram.com/language/ref/$HistoryLength</url>
    <dl>
      <dt>'$HistoryLength'
      <dd>specifies the maximum number of 'In' and 'Out' entries.
    </dl>
    >> $HistoryLength
     = 100
    >> $HistoryLength = 1;
    >> 42
     = 42
    >> %
     = 42
    >> %%
     = %3
    >> $HistoryLength = 0;
    >> 42
     = 42
    >> %
     = %7
    """

    name = "$HistoryLength"

    rules = {
        "$HistoryLength": "100",
    }
    summary_text = "number of previous lines of input and output to keep"


class In(Builtin):
    """
    <url>:WMA: https://reference.wolfram.com/language/ref/In</url>
    <dl>
      <dt>'In[$k$]'
        <dd>gives the $k$th line of input.
      </dl>
    >> x = 1
     = 1
    >> x = x + 1
     = 2
    >> Do[In[2], {3}]
    >> x
     = 5
    >> In[-1]
     = 5
    >> Definition[In]
     = Attributes[In] = {Listable, Protected}
     .
     . In[6] = Definition[In]
     .
     . In[5] = In[-1]
     .
     . In[4] = x
     .
     . In[3] = Do[In[2], {3}]
     .
     . In[2] = x = x + 1
     .
     . In[1] = x = 1
    """

    attributes = A_LISTABLE | A_PROTECTED

    rules = {
        "In[k_Integer?Negative]": "In[$Line + k]",
    }
    summary_text = "Kth input"


class IOHookPreRead(Builtin):
    """
    <url>:WMA: https://reference.wolfram.com/language/ref/$PreRead</url>
    <dl>
      <dt>$PreRead
      <dd> is a global variable whose value, if set, is applied to the \
      text or box form of every input expression before it is fed to the parser.

      (Not implemented yet)
    </dl>
    """

    attributes = A_NO_ATTRIBUTES
    name = "$PreRead"
    summary_text = (
        "function applied to each input string before being fed to the Wolfram System"
    )


class IOHookPre(Builtin):
    """
    <url>:WMA: https://reference.wolfram.com/language/ref/$Pre</url>
    <dl>
      <dt>$Pre
      <dd>is a global variable whose value, if set, is applied to every input expression.
    </dl>

    Set $Timing$ as the $Pre function, stores the elapsed time in a variable,
    stores just the result in Out[$Line] and print a formatted version showing the elapsed time
    >> $Pre := (Print["[Processing input...]"];#1)&
    >> $Post := (Print["[Storing result...]"]; #1)&
     | [Processing input...]
     | [Storing result...]
    >> $PrePrint := (Print["The result is:"]; {TimeUsed[], #1})&
     | [Processing input...]
     | [Storing result...]
    >> 2 + 2
     | [Processing input...]
     | [Storing result...]
     | The result is:
     = {..., 4}
    >> $Pre = .; $Post = .;  $PrePrint = .;  $ElapsedTime = .;
     | [Processing input...]
    >> 2 + 2
     = 4
    """

    attributes = A_NO_ATTRIBUTES
    name = "$Pre"
    summary_text = "function applied to each input expression before evaluation"


class IOHookPost(Builtin):
    """
    <url>:WMA: https://reference.wolfram.com/language/ref/$Post</url>
    <dl>
      <dt>$Post
      <dd>is a global variable whose value, if set, is applied to every output expression.
    </dl>
    """

    attributes = A_NO_ATTRIBUTES
    name = "$Post"
    summary_text = "function applied to each expression after evaluation"


class IOHookPrePrint(Builtin):
    """
    <url>:WMA: https://reference.wolfram.com/language/ref/$PrePrint</url>
    <dl>
      <dt>$PrePrint
      <dd>is a global variable whose value, if set, is applied to every output expression before it is printed.
    </dl>
    """

    attributes = A_NO_ATTRIBUTES
    name = "$PrePrint"
    summary_text = (
        "function applied after 'Out[n]' is assigned, but before the result is printed"
    )


class IOHookSyntaxHandler(Builtin):
    """
    <url>:WMA: https://reference.wolfram.com/language/ref/$SyntaxHandler</url>
    <dl>
      <dt>$SyntaxHandler
      <dd>is a global variable whose value, if set, is applied to any input string that is found to contain a syntax \
          error.

    (Not implemented yet)
    </dl>
    """

    attributes = A_NO_ATTRIBUTES
    name = "$SyntaxHandler"
    summary_text = "function applied to any input line that yields a syntax error"


class Line(Builtin):
    """
    <url>:WMA: https://reference.wolfram.com/language/ref/$Line</url>
    <dl>
      <dt>'$Line'
      <dd>holds the current input line number.
    </dl>
    >> $Line
     = 1
    >> $Line
     = 2
    >> $Line = 12;
    >> 2 * 5
     = 10
    >> Out[13]
     = 10
    >> $Line = -1;
     : Non-negative integer expected.
    """

    name = "$Line"
    summary_text = "current line number"


class Out(Builtin):
    """
    <url>:WMA: https://reference.wolfram.com/language/ref/$Out</url>
    <dl>
      <dt>'Out[$k$]'
      <dt>'%$k$'
      <dd>gives the result of the $k$th input line.

      <dt>'%', '%%', etc.
      <dd>gives the result of the previous input line, of the line before the previous input line, etc.
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
        "    f:StandardForm|TraditionalForm|InputForm|OutputForm]": r'StringJoin[ConstantArray["%%", -k]]',
        "MakeBoxes[Out[k_Integer?Positive],"
        "    f:StandardForm|TraditionalForm|InputForm|OutputForm]": r'"%%" <> ToString[k]',
    }
    summary_text = "result of the Kth input line"
