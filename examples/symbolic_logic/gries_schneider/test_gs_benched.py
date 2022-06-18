#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mathics.core.util import timeit

from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.parser import MathicsSingleLineFeeder, parse

definitions = Definitions(add_builtin=True)


@timeit
def run_gs(definitions: Definitions, path: str):
    evaluation = Evaluation(definitions=definitions, catch_interrupt=False)
    expr = parse(definitions, MathicsSingleLineFeeder(path))
    expr.evaluate(evaluation)


@timeit
def main():
    for i in range(4):
        run_gs(definitions, f"<< GS{i}.m")


if __name__ == "__main__":
    main()
