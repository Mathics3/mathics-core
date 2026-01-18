"""
This module contains the structures and functions used to export
Mathics3 base elements into a formatted representation as plane text,
LaTeX, MathML and other markdown formatted text representations.
This process involves:

* Apply FormatValues rules
* Apply MakeBoxes rules to convert Mathics3 expressions into 
  different kind of Box Expressions
* Process Box expressions to convert them into a text strings following a certain format convension/encoding.

For example, to convert the expression `Plus[a, Times[-1, b], c]` into a text representation, `a - b + c`
1. Applying  format rules, the expression is reformatted as `Infix[{a, b, c},{"-", "+"}, 310, Left]` 
2. Apply MakeBoxes rules to build, for example, its `StandardForm` Box expression`RowBox[{"a", "-", "b", "+", "c"}]`
3. Finally, the Box expression is converted to the text string
 "a - b + c" calling functions from the module `mathics.format.export.text`

"""
