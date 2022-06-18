#!/usr/bin/env python
# -*- coding: utf-8 -*-


from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.parser import MathicsSingleLineFeeder, parse

definitions = Definitions(add_builtin=True)

for i in range(4):
    evaluation = Evaluation(definitions=definitions, catch_interrupt=False)

    expr = parse(definitions, MathicsSingleLineFeeder(f"<< GS{i}.m"))
    expr.evaluate(evaluation)
