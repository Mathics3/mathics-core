# -*- coding: utf-8 -*-

from typing import Callable, Optional, Tuple

from mathics.core.definitions import SIDE_EFFECT_BUILTINS, Definition
from mathics.core.element import BaseElement, EvalMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression, from_python
from mathics.core.symbols import Symbol, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolBlank, SymbolInteger, SymbolReal
from mathics.eval.nevaluator import eval_N

try:
    from mathics.compile import CompileArg, CompileError, _compile
    from mathics.compile.types import bool_type, int_type, real_type

    use_llvm = True
    # _Complex not implemented
    permitted_types = {
        Expression(SymbolBlank, SymbolInteger): int_type,
        Expression(SymbolBlank, SymbolReal): real_type,
        SymbolTrue: bool_type,
        SymbolFalse: bool_type,
    }
except ImportError:
    use_llvm = False
    bool_type = bool
    int_type = int
    real_type = float

    permitted_types = {
        Expression(SymbolBlank, SymbolInteger): int,
        Expression(SymbolBlank, SymbolReal): float,
        SymbolTrue: bool,
        SymbolFalse: bool,
    }


class CompileDuplicateArgName(Exception):
    def __init__(self, symb):
        self.symb = symb


class CompileWrongArgType(Exception):
    def __init__(self, var):
        self.var = var


def evaluate_without_side_effects(
    expr: Expression, evaluation: Evaluation
) -> Expression:
    """
    Evaluate an expression leaving unevaluated subexpressions
    related with side-effects (assignments, loops).
    """
    definitions = evaluation.definitions
    # Temporarily remove the builtin definitions
    # of symbols with side effects
    for name, defin in SIDE_EFFECT_BUILTINS.items():
        # Change the definition by a temporal definition setting
        # just the name and the attributes.
        definitions.builtin[name] = Definition(
            name, attributes=defin.attributes, builtin=defin.builtin
        )
        definitions.clear_cache(name)
    try:
        result = expr.evaluate(evaluation)
    finally:
        # Restore the definitions
        for name, defin in SIDE_EFFECT_BUILTINS.items():
            definitions.builtin[name] = defin
    return result if result is not None else expr


def expression_to_callable(
    expr: Expression,
    args: Optional[list] = None,
    evaluation: Optional[Evaluation] = None,
) -> Optional[Callable]:
    """
    Return a Python callable from an expression. If llvm is available,
    tries to produce llvm code. Otherwise, returns a Python function.
    expr: Expression
    args: a list of CompileArg elements
    evaluation: an Evaluation object used if the llvm compilation fails
    """
    if evaluation is not None:
        expr = evaluate_without_side_effects(expr, evaluation)
    try:
        cfunc = _compile(expr, args) if (use_llvm and args is not None) else None
    except CompileError:
        cfunc = None

    if cfunc is None:
        if evaluation is None:
            raise CompileError
        try:

            def _pythonized_mathics_expr(*x):
                inner_evaluation = Evaluation(definitions=evaluation.definitions)
                x_mathics = (from_python(u) for u in x[: len(args)])
                vars = dict(list(zip([a.name for a in args], x_mathics)))
                pyexpr = expr.replace_vars(vars)
                pyexpr = eval_N(pyexpr, inner_evaluation)
                res = pyexpr.to_python()
                return res

            # TODO: check if we can use numba to compile this...
            cfunc = _pythonized_mathics_expr
        except Exception:
            cfunc = None
    return cfunc


def expression_to_callable_and_args(
    expr: Expression,
    vars: Optional[list] = None,
    evaluation: Optional[Evaluation] = None,
) -> Tuple[Optional[Callable], Optional[list]]:
    """
    Return a tuple of Python callable and a list of CompileArgs.
    expr: A Mathics Expression object
    vars: a list of Symbols or Mathics Lists of the form {Symbol, Type}
    """
    if vars is None:
        args = None
    else:
        args = []
        names = []
        for var in vars:
            if isinstance(var, Symbol):
                symb = var
                name = symb.get_name()
                typ = real_type
            elif var.has_form("List", 2):
                symb, typ = var.elements
                if isinstance(symb, Symbol) and typ in permitted_types:
                    name = symb.get_name()
                    typ = permitted_types[typ]
                else:
                    raise CompileWrongArgType(var)
            else:
                raise CompileWrongArgType(var)

            if name in names:
                raise CompileDuplicateArgName(symb)
            names.append(name)
            args.append(CompileArg(name, typ))

    return expression_to_callable(expr, args, evaluation), args
