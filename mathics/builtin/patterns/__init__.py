"""
Rules and Patterns

<url>:WMA link:
https://reference.wolfram.com/language/guide/RulesAndPatterns.html</url>


The concept of transformation rules for arbitrary symbolic patterns is key \
in \\Mathics.

Also, functions can get applied or transformed depending on whether or not \
functions arguments match.

Some examples:
    >> a + b + c /. a + b -> t
     = c + t
    >> a + 2 + b + c + x * y /. n_Integer + s__Symbol + rest_ -> {n, s, rest}
     = {2, a, b + c + x y}
    >> f[a, b, c, d] /. f[first_, rest___] -> {first, {rest}}
     = {a, {b, c, d}}

Tests and Conditions:
    >> f[4] /. f[x_?(# > 0&)] -> x ^ 2
     = 16
    >> f[4] /. f[x_] /; x > 0 -> x ^ 2
     = 16

Elements in the beginning of a pattern rather match fewer elements:
    >> f[a, b, c, d] /. f[start__, end__] -> {{start}, {end}}
     = {{a}, {b, c, d}}

Optional arguments using 'Optional':
    >> f[a] /. f[x_, y_:3] -> {x, y}
     = {a, 3}

Options using 'OptionsPattern' and 'OptionValue':
    >> f[y, a->3] /. f[x_, OptionsPattern[{a->2, b->5}]] -> {x, OptionValue[a], OptionValue[b]}
     = {y, 3, 5}

The attributes 'Flat', 'Orderless', and 'OneIdentity' affect pattern matching.
"""

# This tells documentation how to sort this module
sort_order = "mathics.builtin.rules-and-patterns"
