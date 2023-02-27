from test.helper import check_evaluation, evaluate_value

import pytest


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
            "{Q[a,1,b]/.rule, Q[a,1,b]/.ruled}",
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
