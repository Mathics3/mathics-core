"""
This module contains the structures and functions used to turn Mathics3 expressions into
renderable output.

The three-step process is:

1. Apply any rewrite rules that are set by default or specified by rules explicitly given using builtin function `Format`.
2. Box the these resulting expression giving boxed expressions.
3. Render the boxed expressions to strings

For example, to format the expression `Plus[a, Times[-1, b], c]` in `StandardForm`:

1. Format rules from `mathics.format.form_rule` rewrite as  `Infix[{a, b, c}, {"-", "+"}, 310, Left]`.
2. Boxing rules based on a particular Form are run. For `StandardForm`, the Box expression of the above is `RowBox[{"a", "-", "b", "+", "c"}]`
3. Box expressions using functions from the module `mathics.format.render.text` render this as string: `a - b + c`
"""
