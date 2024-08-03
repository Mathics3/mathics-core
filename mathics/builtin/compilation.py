# -*- coding: utf-8 -*-
"""Code Compilation

Code compilation allows Mathics functions to be run faster.

When LLVM and Python libraries are available, compilation \
produces LLVM code.
"""

import ctypes
from types import FunctionType

from mathics.builtin.box.compilation import CompiledCodeBox
from mathics.core.atoms import Integer, String
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.function import (
    CompileDuplicateArgName,
    CompileError,
    CompileWrongArgType,
    expression_to_callable_and_args,
)
from mathics.core.convert.python import from_python
from mathics.core.element import ImmutableValueMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Atom, Symbol, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolCompiledFunction

# This tells documentation how to sort this module
sort_order = "mathics.builtin.code-compilation"


class Compile(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Compile.html</url>

    <dl>
      <dt>'Compile[{$x1$, $x2$, ...}, $expr$]'
      <dd>Compiles $expr$ assuming each $xi$ is a $Real$ number.

      <dt>'Compile[{{$x1$, $t1$} {$x2$, $t1$} ...}, $expr$]'
      <dd>Compiles assuming each $xi$ matches type $ti$.
    </dl>

    Compilation is performed using llvmlite , or Python's builtin
    "compile" function.


    >> cf = Compile[{x, y}, x + 2 y]
     = CompiledFunction[{x, y}, x + 2 y, -CompiledCode-]
    >> cf[2.5, 4.3]
     = 11.1

    >> cf = Compile[{{x, _Real}}, Sin[x]]
     = CompiledFunction[{x}, Sin[x], -CompiledCode-]
    >> cf[1.4]
     = 0.98545

    Compile supports basic flow control:
    >> cf = Compile[{{x, _Real}, {y, _Integer}}, If[x == 0.0 && y <= 0, 0.0, Sin[x ^ y] + 1 / Min[x, 0.5]] + 0.5]
     = CompiledFunction[{x, y}, ..., -CompiledCode-]
    >> cf[3.5, 2]
     = 2.18888

    Loops and variable assignments are supported usinv Python builtin "compile" function:
    >> Compile[{{a, _Integer}, {b, _Integer}}, While[b != 0, {a, b} = {b, Mod[a, b]}]; a]       (* GCD of a, b *)
     =  CompiledFunction[{a, b}, a, -PythonizedCode-]
    """

    attributes = A_HOLD_ALL | A_PROTECTED

    messages = {
        "invar": "Variable `1` should be {symbol, type} annotation.",
        "invars": "Variables should be a list of {symbol, type} annotations.",
        "comperr": "Expression `1` could not be compiled.",
        "fdup": "Duplicate parameter `1` found in `2`.",
    }

    requires = ("llvmlite",)
    summary_text = "compile an expression"

    def eval(self, vars, expr, evaluation: Evaluation):
        "Compile[vars_, expr_]"

        if not vars.has_form("List", None):
            evaluation.message("Compile", "invars")
            return

        try:
            cfunc, args = expression_to_callable_and_args(
                expr, vars.elements, evaluation
            )
        except CompileDuplicateArgName as e:
            # duplicated argument
            evaluation.message("Compile", "fdup", e.symb, vars)
            return None
        except CompileWrongArgType as e:
            evaluation.message("Compile", "invar", e.var)
            return None
        except CompileError:
            cfunc = None

        code = CompiledCode(cfunc, args)
        arg_names = to_mathics_list(
            *(arg.name for arg in args), elements_conversion_fn=Symbol
        )
        return Expression(SymbolCompiledFunction, arg_names, expr, code)


class CompiledCode(Atom, ImmutableValueMixin):
    class_head_name = "System`CompiledCode"
    summary_text = "CompiledCode object"

    def __init__(self, cfunc, args, **kwargs):
        super(CompiledCode, self).__init__(**kwargs)
        self.cfunc = cfunc
        self.args = args

    # FIXME: is this right? We don't check that the actual code is the same?
    # just that we hhave some sort of compiled code?
    def equal2(self, rhs):
        return isinstance(rhs, CompiledCode)

    def __str__(self):
        if type(self.cfunc) is FunctionType:
            return "-PythonizedCode-"
        return "-CompiledCode-"

    def boxes_to_text(self, elements=None, **options):
        if not elements:
            elements = self._elements
        return "-CompiledCode-"

    def do_copy(self):
        return CompiledCode(self.cfunc, self.args)

    def default_format(self, evaluation, form):
        return str(self)

    def get_sort_key(self, pattern_sort=False) -> tuple:
        if pattern_sort:
            return super(CompiledCode, self).get_sort_key(True)
        else:
            return (0, 3, hex(id(self)))

    def sameQ(self, rhs) -> bool:
        """Mathics SameQ"""
        return self is rhs

    def to_python(self, *args, **kwargs):
        return None

    def to_sympy(self, *args, **kwargs):
        raise NotImplementedError

    def __hash__(self):
        return hash(("CompiledCode", ctypes.addressof(self.cfunc)))  # XXX hack

    def atom_to_boxes(self, f, evaluation: Evaluation):
        return CompiledCodeBox(String(self.__str__()), evaluation=evaluation)


class CompiledFunction(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/CompiledFunction.html</url>

    <dl>
      <dt>'CompiledFunction[$args$...]'
      <dd>represents compiled code for evaluating a compiled function.
    </dl>

    >> sqr = Compile[{x}, x x]
     = CompiledFunction[{x}, x ^ 2, -CompiledCode-]
    >> Head[sqr]
     = CompiledFunction
    >> sqr[2]
     = 4.

    """

    messages = {"argerr": "Invalid argument `1` should be Integer, Real or boolean."}
    summary_text = "A CompiledFunction object."

    def eval(self, argnames, expr, code, args, evaluation: Evaluation):
        "CompiledFunction[argnames_, expr_, code_CompiledCode][args__]"

        argseq = args.get_sequence()

        if len(argseq) != len(code.args):
            return

        py_args = []
        for arg in argseq:
            if isinstance(arg, Integer):
                py_args.append(arg.get_int_value())
            elif arg.sameQ(SymbolTrue):
                py_args.append(True)
            elif arg.sameQ(SymbolFalse):
                py_args.append(False)
            else:
                py_args.append(arg.round_to_float(evaluation))
        try:
            result = code.cfunc(*py_args)
        except (TypeError, ctypes.ArgumentError):
            evaluation.message("CompiledFunction", "argerr", args)
            return
        return from_python(result)
