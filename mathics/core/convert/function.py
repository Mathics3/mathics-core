# -*- coding: utf-8 -*-
from typing import Callable, List, Optional, Tuple

import numpy

from mathics.core.convert.lambdify import (
    CompileError as LambdifyCompileError,
    lambdify_compile,
)
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression, from_python
from mathics.core.symbols import Symbol, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolAlternatives,
    SymbolBlank,
    SymbolComplex,
    SymbolInteger,
    SymbolReal,
)
from mathics.eval.nevaluator import eval_N

PERMITTED_TYPES = {
    Expression(SymbolBlank, SymbolInteger): int,
    Expression(SymbolBlank, SymbolReal): float,
    Expression(SymbolBlank, SymbolComplex): complex,
    Expression(SymbolAlternatives, SymbolTrue, SymbolFalse): bool,
    Expression(SymbolAlternatives, SymbolFalse, SymbolTrue): bool,
}


try:
    from mathics.compile import CompileArg, CompileError, _compile
    from mathics.compile.types import bool_type, int_type, real_type

    USE_LLVM = True
    # _Complex not implemented
    LLVM_TYPE_TRANSLATION = {
        int: int_type,
        float: real_type,
        bool: bool_type,
    }
except ImportError:
    USE_LLVM = False


class CompileDuplicateArgName(Exception):
    def __init__(self, symb):
        self.symb = symb


class CompileWrongArgType(Exception):
    def __init__(self, var):
        self.var = var


def expression_to_llvm(
    expr: Expression,
    args: Optional[list] = None,
    evaluation: Optional[Evaluation] = None,
):
    """
    Convert an expression to LLVM code. None if it fails.
    expr: Expression
    args: a list of CompileArg elements
    evaluation: an Evaluation object used if the llvm compilation fails
    """
    try:
        return _compile(expr, args) if (USE_LLVM and args is not None) else None
    except CompileError:
        return None


def expression_to_python_function(
    expr: Expression,
    args: Optional[list] = None,
    evaluation: Optional[Evaluation] = None,
) -> Callable:
    """
    Return a Python function from an expression.
    expr: Expression
    args: a list of CompileArg elements
    evaluation: an Evaluation object used if the llvm compilation fails
    """
    def _pythonized_mathics_expr(*x):
        inner_evaluation = Evaluation(definitions=evaluation.definitions)
        x_mathics = (from_python(u) for u in x[: len(args)])
        vars = dict(list(zip([a.name for a in args], x_mathics)))
        pyexpr = expr.replace_vars(vars)
        pyexpr = eval_N(pyexpr, inner_evaluation)
        res = pyexpr.to_python()
        return res

    # TODO: check if we can use numba to compile this...
    return _pythonized_mathics_expr


def collect_args(vars) -> Optional[List[CompileArg]]:
    """
    Convert a List expression into a list of CompileArg objects.
    """
    if vars is None:
        return None
    else:
        args = []
        names = []
        for var in vars:
            name: str
            t_typ: type
            if isinstance(var, Symbol):
                symb = var
                name = symb.get_name()
                t_typ = float
            elif var.has_form("List", 2):
                symb, typ = var.elements
                if isinstance(symb, Symbol) and typ in PERMITTED_TYPES:
                    name = symb.get_name()
                    t_typ = PERMITTED_TYPES[typ]
                else:
                    print(symb, typ, var)
                    raise CompileWrongArgType(var)
            else:
                raise CompileWrongArgType(var)

            if name in names:
                raise CompileDuplicateArgName(symb)
            names.append(name)
            args.append(CompileArg(name, t_typ))
    return args


def expression_to_callable_and_args(
    expr: Expression,
    vars: Optional[list] = None,
    evaluation: Optional[Evaluation] = None,
    debug: int = 0,
    vectorize=False,
) -> Tuple[Callable, Optional[list]]:
    """
    Return a tuple of Python callable and a list of CompileArgs.
    expr: A Mathics Expression object
    vars: a list of Symbols or Mathics Lists of the form {Symbol, Type}
    """
    args = collect_args(vars)

    # If vectorize is requested, first, try to lambdify the expression:
    if vectorize:
        try:
            cfunc = lambdify_compile(
                evaluation,
                expr,
                [] if args is None else [arg.name for arg in args],
                debug,
            )
            return cfunc, args
        except LambdifyCompileError:
            pass

    # Then, try with llvm if available
    if USE_LLVM:
        try:
            llvm_args = (
                None
                if args is None
                else [
                    CompileArg(
                        compile_arg.name, LLVM_TYPE_TRANSLATION[compile_arg.type]
                    )
                    for compile_arg in args
                ]
            )
            cfunc = expression_to_llvm(expr, llvm_args, evaluation)
            if cfunc is not None:
                if vectorize:
                    cfunc = numpy.vectorize(cfunc)
                return cfunc, args
        except KeyError:
            pass
        except RuntimeError:
            pass

    # Last resource
    cfunc = expression_to_python_function(expr, args, evaluation)
    if vectorize:
        cfunc = numpy.vectorize(cfunc)
    return cfunc, args
