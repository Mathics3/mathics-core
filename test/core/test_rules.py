from test.helper import check_evaluation, evaluate_value

import pytest

"""
In WL, pattern matching and rule application is dependent on the evaluation context.
This happens at two levels. On the one hand, patterns like `PatternTest[pat, test]`
matches with `expr` depending both on the `pat` and the result of the evaluation of `test`.

On the other hand, attributes like `Orderless` or `Flat` in the head of the pattern 
also affects how patterns are applied to expressions. However, in WMA, the effect
of these parameters are established in the point in which a rule is created, and not
when it is applied.

For example, if we execute in WMA:

```
In[1]:= rule = Q[a, _Symbol, _Integer]->True; SetAttributes[Q, {Orderless}]; Q[a,1,b]/.rule
Out[1]=Q[1, a, b]
```
the application fails because it does not take into account the `Orderless` attribute, because
the rule was created *before* the attribute is set.
On the other hand,
```
In[2]:=SetAttributes[Q, {Orderless}]; rule = Q[a, _Symbol, _Integer]->True; Attributes[Q]={}; Q[a,1,b]/.rule
Out[2]= True
```
because it ignores that the attribute is clean at the time in which the rule is applied.


In Mathics, on the other hand, attributes are taken into accout just at the moment of the replacement, 
so the output of both expressions are the opposite.


This set of tests are proposed to drive the behaviour of Rules in Mathics closer to the one in WMA.
In particular, the way in which `Orderless` and `Flat` attributes affects evaluation are currently tested.

For the case of `Flat`, there is still another issue in Mathics, since by not it is not taken into account
at the pattern matching level. For example, in WMA,

```
In[3]:=SetAttributes[Q,{Flat}]; rule=Q[a,_Integer]->True; Q[a,1,b]/.rule
Out[3]=Q[True, b]
``` 

The xfail mark can be removed once these issues get fixed.
"""


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (None, None, None),
        (
            "rule = Q[a, _Symbol, _Integer]->True;\
	 ruled = Dispatch[{rule}];\
	 {Q[a,1,b], Q[a,1,b]/.rule, Q[a,1,b]/.ruled}",
            "{Q[a,1,b], Q[a,1,b], Q[a,1,b]}",
            "1. Check the rules. Here are not applied.",
        ),
        (
            "SetAttributes[Q, {Orderless}];\
          {Q[a,1,b], Q[a,1,b]/.rule, Q[a, 1, b]/.ruled}",
            "{Q[1, a, b], Q[a, 1, b], Q[a, 1, b]}",
            "2. Set the attribute. Application is not affected.",
        ),
        (
            "rule = Q[a, _Symbol, _Integer]->True;\
  	  ruled = Dispatch[{rule}];\
	  {Q[a, 1, b], Q[a, 1, b]/.rule, Q[a, 1, b]/.ruled}",
            "{Q[1, a, b], True, True}",
            "3 .Rebuilt rules. Rules applied.",
        ),
        (
            "Attributes[Q] = {};\
          {Q[a, 1, b], Q[a, 1, b]/.rule, Q[a, 1, b]/.ruled}",
            "{Q[a, 1, b], True, True}",
            "4. Unset the attribute. Application is not affected.",
        ),
        (
            "rule = Q[a, _Symbol, _Integer]->True;\
  	  ruled = Dispatch[{rule}];\
	  {Q[a, 1, b], Q[a, 1, b]/.rule, Q[a, 1, b]/.ruled}",
            "{Q[a, 1, b], Q[a, 1, b], Q[a, 1, b]}",
            "5. Rebuilt rules. Rules applied.",
        ),
        (None, None, None),
    ],
)
@pytest.mark.xfail
def test_orderless_on_rules(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (None, None, None),
        (
            "rule = Q[_Integer,_Symbol]->True;\
	 ruled = Dispatch[{rule}];\
	 {Q[a,1,b]/.rule, Q[a,1,b]/.ruled}",
            "{Q[a,1,b],Q[a,1,b]}",
            "1. Check the rules. Here are not applied.",
        ),
        (
            "SetAttributes[Q, {Flat}];\
            {Q[a,1,b]/.rule, Q[a,1,b]/.ruled}",
            "{Q[a,1,b], Q[a,1,b]}",
            "2. Set the attribute. Application is not affected.",
        ),
        (
            "rule = Q[_Integer,_Symbol]->True;\
  	  ruled = Dispatch[{rule}];\
	  {Q[a, 1, b]/.rule, Q[a, 1, b]/.ruled}",
            "{Q[a, True],Q[a, True]}",
            "3 .Rebuilt rules. Rules applied.",
        ),
        (
            "Attributes[Q] = {};\
          {Q[a,1,b]/.rule, Q[a,1,b]/.ruled}",
            "{Q[a,1,b], Q[a,1,b]}",
            "4. Unset the attribute. Application is not affected.",
        ),
        (
            "rule = Q[a, _Integer,_Symbol]->True;\
  	  ruled = Dispatch[{rule}];\
	  {Q[a,1,b]/.rule, Q[a,1,b]/.ruled}",
            "{Q[a, 1, b],Q[a, 1, b]}",
            "5. Rebuilt rules. Rules applied.",
        ),
        (None, None, None),
    ],
)
@pytest.mark.xfail
def test_flat_on_rules(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (None, None, None),
        (
            "rule = Q[x_,y_.]->{x, y};\
	 ruled = Dispatch[{rule}];\
	 {Q[a]/.rule, Q[a]/.ruled}",
            "{Q[a],Q[a]}",
            "1. Check the rules. Here are not applied.",
        ),
        (
            "Default[Q]=37;\
          {Q[a]/.rule, Q[a]/.ruled}",
            "{Q[a], Q[a]}",
            "2. Set the Default value. Application is not affected.",
        ),
        (
            "rule = Q[x_,y_.]->{x,y};\
  	  ruled = Dispatch[{rule}];\
	  {Q[a]/.rule, Q[a]/.ruled}",
            "{{a, 37}, {a, 37}}",
            "3 .Rebuilt rules. Rules applied.",
        ),
        (
            "Default[Q] = .;\
            {Q[a]/.rule, Q[a]/.ruled}",
            "{{a, 37}, {a, 37}}",
            "4. Unset the attribute. Application is not affected.",
        ),
        (
            "rule = Q[x_,y_.]->{x,y};\
  	    ruled = Dispatch[{rule}];\
	    {Q[a]/.rule, Q[a]/.ruled}",
            "{Q[a],Q[a]}",
            "5. Rebuilt rules. Rules not applied.",
        ),
        (None, None, None),
    ],
)
@pytest.mark.xfail
def test_default_optional_on_rules(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg)
