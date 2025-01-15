#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.load_builtin import import_and_load_builtins
from mathics.core.parser import MathicsSingleLineFeeder, parse

import_and_load_builtins()
definitions = Definitions(add_builtin=True)

for i in range(0, 4):
    evaluation = Evaluation(definitions=definitions, catch_interrupt=False)

    expr = parse(definitions, MathicsSingleLineFeeder(f"<< GS{i}.m"))
    expr.evaluate(evaluation)
