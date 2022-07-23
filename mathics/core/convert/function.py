# -*- coding: utf-8 -*-

from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression, from_python
from mathics.core.evaluators import eval_N
from mathics.core.symbols import Symbol, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolBlank,
    SymbolInteger,
    SymbolReal,
)


from typing import Optional, Callable, Tuple


try:
    from mathics.builtin.compile.types import int_type, real_type, bool_type
    from mathics.builtin.compile import _compile, CompileArg, CompileError

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
                res = pyexpr.to_python(n_evaluation=inner_evaluation)
                return res

            # TODO: check if we can use numba to compile this...
            cfunc = _pythonized_mathics_expr
        except Exception:
            cfunc = None
    return cfunc


def expression_to_callable_and_args(
    expr: Expression, vars: list = None, evaluation: Optional[Evaluation] = None
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
