#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from mathics.core.expression import Expression
from mathics.core.atoms import Integer, Rational
from mathics.core.symbols import Symbol
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.parser import MathicsSingleLineFeeder, parse

definitions = Definitions(add_builtin=True)

for i in range(1, 4):
    evaluation = Evaluation(definitions=definitions, catch_interrupt=False)

    expr = parse(definitions, MathicsSingleLineFeeder(f"<< GS{i}.m"))
    expr.evaluate(evaluation)
