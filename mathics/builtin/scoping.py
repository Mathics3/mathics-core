# -*- coding: utf-8 -*-
"""
Scoping Constructs
"""


from mathics.builtin.base import Builtin, Predefined
from mathics.core.assignment import get_symbol_list
from mathics.core.atoms import Integer, String
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED, attribute_string_to_number
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, fully_qualified_symbol_name


def get_scoping_vars(var_list, msg_symbol="", evaluation=None):
    def message(tag, *args):
        if msg_symbol and evaluation:
            evaluation.message(msg_symbol, tag, *args)

    if not var_list.has_form("List", None):
        message("lvlist", var_list)
        return
    vars = var_list.elements
    scoping_vars = set()
    for var in vars:
        var_name = None
        if var.has_form("Set", 2):
            var_name = var.elements[0].get_name()
            new_def = var.elements[1]
            if evaluation:
                new_def = new_def.evaluate(evaluation)
        elif isinstance(var, Symbol):
            var_name = var.get_name()
            new_def = None
        if not var_name:
            message("lvsym", var)
            continue
        if var_name in scoping_vars:
            message("dup", Symbol(var_name))
        else:
            scoping_vars.add(var_name)
            yield var_name, new_def


def dynamic_scoping(func, vars, evaluation: Evaluation):
    """
    Changes temporarily the value of a set of symbols listed in vars,
    and evaluates func(evaluation)
    """
    original_definitions = {}
    for var_name, new_def in vars.items():
        assert fully_qualified_symbol_name(var_name)
        original_definitions[var_name] = evaluation.definitions.get_user_definition(
            var_name
        )
        evaluation.definitions.reset_user_definition(var_name)
        if new_def is not None:
            new_def = new_def.evaluate(evaluation)
            evaluation.definitions.set_ownvalue(var_name, new_def)
    try:
        result = func(evaluation)
    finally:
        for name, definition in original_definitions.items():
            evaluation.definitions.add_user_definition(name, definition)
    return result


class Begin(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Begin.html</url>

    <dl>
      <dt>'Begin'[$context$]
      <dd>temporarily sets the current context to $context$.
    </dl>

    >> Begin["test`"]
     = test`
    ## X> {$Context, $ContextPath}
    ## >> Context[newsymbol]
    ##  = test`
    >> End[]
     = test`
    >> End[]
     : No previous context defined.
     = Global`

    ## #> Begin["`test`"]
    ##  = Global`test`
    ## #> Context[]
    ##  = Global`test`
    ## #> End[]
    ##  = Global`test`
    """

    rules = {
        "Begin[context_String]": """
             Unprotect[System`Private`$ContextStack];
             System`Private`$ContextStack = Append[System`Private`$ContextStack, $Context];
             Protect[System`Private`$ContextStack];
             $Context = context;
             $Context
        """,
    }
    summary_text = "temporarily set the current context"


class BeginPackage(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/BeginPackage.html</url>

    <dl>
      <dt>'BeginPackage'[$context$]
      <dd>starts the package given by $context$.
    </dl>

    The $context$ argument must be a valid context name. 'BeginPackage' changes \
    the values of '$Context' and '$ContextPath', setting the current context to $context$.

    ## >> BeginPackage["test`"]
    ##  = test`
    """

    messages = {"unimpl": "The second argument to BeginPackage is not yet implemented."}

    rules = {
        "BeginPackage[context_String]": """
             Unprotect[System`Private`$ContextPathStack, System`$Packages];
             Begin[context];
             System`Private`$ContextPathStack =
                 Append[System`Private`$ContextPathStack, $ContextPath];
             $ContextPath = {context, "System`"};
             $Packages = If[MemberQ[System`$Packages,$Context],
                            $Packages,
                            System`$Packages=Join[{$Context}, System`$Packages]];
             Protect[System`Private`$ContextPathStack, System`$Packages];
             context
        """,
    }
    summary_text = "temporarily set the context and clean the context path"


class Block(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Block.html</url>

    <dl>
      <dt>'Block[{$x$, $y$, ...}, $expr$]'
      <dd>temporarily removes the definitions of the given variables, evaluates \
          $expr$, and restores the original definitions afterwards.

      <dt>'Block[{$x$=$x0$, $y$=$y0$, ...}, $expr$]'
      <dd>assigns temporary values to the variables during the evaluation of $expr$.
    </dl>

    >> n = 10
     = 10
    >> Block[{n = 5}, n ^ 2]
     = 25
    >> n
     = 10

    Values assigned to block variables are evaluated at the beginning of the block.
    Keep in mind that the result of 'Block' is evaluated again, so a returned block variable
    will get its original value.

    >> Block[{x = n+2, n}, {x, n}]
     = {12, 10}

    If the variable specification is not of the described form, an error message is raised.
    >> Block[{x + y}, x]
     : Local variable specification contains x + y, which is not a symbol or an assignment to a symbol.
      = x

    Variable names may not appear more than once:
    >> Block[{x, x}, x]
      : Duplicate local variable x found in local variable specification.
      = x
    """

    attributes = A_HOLD_ALL | A_PROTECTED

    messages = {
        "lvsym": (
            "Local variable specification contains `1`, "
            "which is not a symbol or an assignment to a symbol."
        ),
        "dup": (
            "Duplicate local variable `1` found in local variable " "specification."
        ),
        "lvlist": "Local variable specification `1` is not a List.",
    }
    summary_text = "evaluate an expression using local values for some given symbols"

    def eval(self, vars, expr, evaluation: Evaluation):
        "Block[vars_, expr_]"

        vars = dict(get_scoping_vars(vars, "Block", evaluation))
        result = dynamic_scoping(expr.evaluate, vars, evaluation)
        return result


class Context_(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/$Context.html</url>
    <dl>
      <dt>'$Context'
      <dd>is the current context.
    </dl>

    >> $Context
    = Global`

    #> InputForm[$Context]
    = "Global`"

    ## Test general context behaviour
    #> Plus === Global`Plus
     = False
    #> `Plus === Global`Plus
     = True
    """

    messages = {"cxset": "`1` is not a valid context name ending in `."}
    name = "$Context"
    rules = {
        "$Context": '"Global`"',
    }
    summary_text = "the current context"


class Contexts(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Contexts.html</url>

    <dl>
      <dt>'Contexts[]'
      <dd>yields a list of all contexts.
    </dl>

    ## this assignment makes sure that a definition in Global` exists
    ## >> x = 5;
    ## X> Contexts[] // InputForm
    """

    summary_text = "list all the defined contexts"

    def eval(self, evaluation: Evaluation):
        "Contexts[]"

        contexts = set()
        for name in evaluation.definitions.get_names():
            contexts.add(String(name[: name.rindex("`") + 1]))

        return ListExpression(*sorted(contexts))


class ContextPath_(Predefined):
    """
    <url>
    :WMA link
    :https://reference.wolfram.com/language/ref/$ContextPath.html</url>
    <dl>
      <dt>'$ContextPath'
      <dd>is the search path for contexts.
    </dl>

    X> $ContextPath // InputForm

    ## #> x`x = 1; x
    ##  = x
    ## #> $ContextPath = {"x`"};
    ## #> x
    ##  = 1
    ## #> System`$ContextPath
    ##  = {x`}
    ## #> $ContextPath = {"System`", "Global`"};
    """

    messages = {"cxlist": "`1` is not a list of valid context names ending in `."}
    name = "$ContextPath"
    rules = {
        "$ContextPath": '{"System`", "Global`"}',
    }
    summary_text = "the current context search path"


class ContextPathStack(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ContextPathStack.html</url>

    <dl>
      <dt>'System`Private`$ContextPathStack'
      <dd>is an internal variable tracking the values of '$ContextPath' \
          saved by 'Begin' and 'BeginPackage'.
    </dl>
    """

    context = "System`Private`"
    name = "$ContextPathStack"

    rules = {
        "System`Private`$ContextPathStack": "{}",
    }
    summary_text = "internal variable tracking $ContextPath values"


class ContextStack(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ContextStack.html</url>
    <dl>
        <dt>'System`Private`$ContextStack'
        <dd>is an internal variable tracking the values of '$Context'
        saved by 'Begin' and 'BeginPackage'.
    </dl>
    """

    context = "System`Private`"
    name = "$ContextStack"

    rules = {
        "System`Private`$ContextStack": "{}",
    }
    summary_text = "internal variable tracking $Context values"


class End(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/End.html</url>

    <dl>
      <dt>'End[]'
      <dd>ends a context started by 'Begin'.
    </dl>
    """

    messages = {
        "noctx": "No previous context defined.",
    }

    rules = {
        "End[]": """
             Block[{System`Private`old=$Context},
                   If[Length[System`Private`$ContextStack] === 0,
                     (* then *) Message[End::noctx]; $Context,
                     (* else *) Unprotect[System`Private`$ContextStack];
                                {$Context, System`Private`$ContextStack} =
                                    {Last[System`Private`$ContextStack],
                                     Most[System`Private`$ContextStack]};
                                Protect[System`Private`$ContextStack];
                                System`Private`old]]
        """,
    }
    summary_text = "revert to the context previous to the nearest 'Begin' statement"


class EndPackage(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/EndPackage.html</url>

    <dl>
      <dt>'EndPackage[]'
      <dd>marks the end of a package, undoing a previous 'BeginPackage'.
    </dl>

    After 'EndPackage', the values of '$Context' and '$ContextPath' at the \
    time of the 'BeginPackage' call are restored, with the new package\'s context prepended to $ContextPath.
    """

    messages = {
        "noctx": "No previous context defined.",
    }

    rules = {
        "EndPackage[]": """
             Block[{System`Private`newctx=Quiet[End[], {End::noctx}]},
                   If[Length[System`Private`$ContextPathStack] === 0,
                      (* then *) Message[EndPackage::noctx],
                      (* else *) Unprotect[System`Private`$ContextPathStack];
                                 {$ContextPath, System`Private`$ContextPathStack} =
                                     {Prepend[Last[System`Private`$ContextPathStack],
                                              System`Private`newctx],
                                      Most[System`Private`$ContextPathStack]};
                                 Protect[System`Private`$ContextPathStack];
                                 Null]]
        """,
    }
    summary_text = "restore the context and the context path to the state before the nearest call to 'BeginPackage'"


class Module(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Module.html</url>

    <dl>
      <dt>'Module[{$vars$}, $expr$]'
      <dd>localizes variables by giving them a temporary name of the form \
          'name$number', where number is the current value of '$ModuleNumber'. \
          Each time a module is evaluated, '$ModuleNumber' is incremented.
    </dl>

    ## FIXME: fix and go over
    ## >> x = 10;
    ## >> Module[{x=x}, x=x+1; x]
    ##  = 11
    ## >> x
    ##  = 10
    ## >> t === Module[{t}, t]
    ## = False

    ## Initial values are evaluated immediately:
    ## >> Module[{t=x}, x = x + 1; t]
    ##  = 10
    ## >> x
    ##  = 11

    ## Variables inside other scoping constructs are not affected by the renaming of 'Module':
    ## >> Module[{a}, Block[{a}, a]]
    ##  = a
    ## >> Module[{a}, Block[{}, a]]
    ##  = a$5

    ## #> Module[{n = 3}, Module[{b = n * 5}, b * 7]]
    ##  = 105

    ## #> Module[{a = 3}, Module[{c = If[ToString[Head[a]] == "Integer", a * 5, Abort[]]}, c]]
    ## = 15

    """

    attributes = A_HOLD_ALL | A_PROTECTED

    messages = {
        "lvsym": (
            "Local variable specification contains `1`, "
            "which is not a symbol or an assignment to a symbol."
        ),
        "dup": (
            "Duplicate local variable `1` found in local variable " "specification."
        ),
        "lvlist": "Local variable specification `1` is not a List.",
    }
    summary_text = "generates symbols with names of the form x$nnn to represent each local variable."

    def eval(self, vars, expr, evaluation: Evaluation):
        "Module[vars_, expr_]"

        scoping_vars = get_scoping_vars(vars, "Module", evaluation)
        replace = {}
        number = Symbol("$ModuleNumber").evaluate(evaluation).get_int_value()
        if number is None:
            number = 1
        evaluation.definitions.set_ownvalue("$ModuleNumber", Integer(number + 1))
        for name, new_def in scoping_vars:
            new_name = "%s$%d" % (name, number)
            if new_def is not None:
                evaluation.definitions.set_ownvalue(new_name, new_def.copy())
            replace[name] = Symbol(new_name)
        new_expr = expr.replace_vars(replace, in_scoping=False)
        result = new_expr.evaluate(evaluation)
        return result


class ModuleNumber_(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/$ModuleNumber.html</url>
    <dl>
      <dt>'$ModuleNumber'
      <dd>is the current "serial number" to be used for local module variables.
    </dl>


    <ul>
      <li>'$ModuleNumber' is incremented every time 'Module' or 'Unique' is called.
      <li> a Mathics session starts with '$ModuleNumber' set to 1.
      <li> You can reset $ModuleNumber to a positive machine integer, but if \
      you do so, naming conflicts may lead to inefficiencies.
    </li>

    ## Fixme: go over and adjuset
    ## Each use of 'Module' increments '$ModuleNumber':
    ## >> {$ModuleNumber, Module[{y}, y], $ModuleNumber}
    ##  = {..., ...}

    ## FIXME and go over
    ## You can reset $ModuleNumber:
    ## >> $ModuleNumber = 17; {Module[{x}, x], $ModuleNumber}
    ##  = {x$17, 18}
    ##
    ## >> $ModuleNumber = x;
    ## : Cannot set $ModuleNumber to x; value must be a positive integer.
    """

    name = "$ModuleNumber"

    messages = {
        "set": (
            "Cannot set $ModuleNumber to `1`; " "value must be a positive integer."
        ),
    }

    rules = {
        "$ModuleNumber": "1",
    }
    summary_text = "serial number of the current local module"


class Unique(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Unique.html</url>

    <dl>
      <dt>'Unique[]'
      <dd>generates a new symbol and gives a name of the form '$number'.

      <dt>'Unique[x]'
      <dd>generates a new symbol and gives a name of the form 'x$number'.

      <dt>'Unique[{x, y, ...}]'
      <dd>generates a list of new symbols.

      <dt>'Unique["xxx"]'
      <dd>generates a new symbol and gives a name of the form 'xxxnumber'.
    </dl>

    Create a unique symbol with no particular name:
    >> Unique[]
    = $...

    Create a unique symbol whose name begins with x:
    >> Unique["x"]
    = x...

    #> Unique[{}]
    = {}

    ## FIXME: include the rest of these in test/builtin/test-unique.py
    ## Each use of Unique[symbol] increments $ModuleNumber:
    ## >> {$ModuleNumber, Unique[x], $ModuleNumber}
    ##  = ...

    ## Unique[symbol] creates symbols in the same way Module does:
    ## >> {Module[{x}, x], Unique[x]}
    ##  = ...

    ## Unique with more arguments
    ## >> Unique[{x, "s"}, Flat ^ Listable ^ Orderless]
    ## : Flat ^ Listable ^ Orderless is not a known attribute.
    ## = Unique[{x, s}, Flat ^ Listable ^ Orderless]

    ## Unique call without symbol argument
    ## >> Unique[x + y]
    ## : x + y is not a symbol or a valid symbol name.
    ##  = Unique[x + y]

    ## #> Unique[1]
    ## : 1 is not a symbol or a valid symbol name.
    ## = Unique[1]

    ## #> Unique[{m, "s", n}, {Flat, Listable, Orderless}]
    ##  = {m$7, s5, n$8}

    ## #> Attributes[{m$7, s5, n$8}]
    ##  = {{Flat, Listable, Orderless}, {Flat, Listable, Orderless}, {Flat, Listable, Orderless}}

    ## #> Unique[{x, "s", 1}, {Flat ^ Listable ^ Orderless}]
    ##  : 1 is not a symbol or a valid symbol name.
    ## = Unique[{x, s, 1}, {Flat ^ Listable ^ Orderless}]

    ## #> Unique[{"s"}, Flat]
    ## = {s6}

    ## #> Attributes[s6]
    ##  = {Flat}
    """

    attributes = A_PROTECTED
    messages = {
        "usym": "`1` is not a symbol or a valid symbol name.",
        "argrx": "Unique called with `1` arguments; 0 or 1 argument are expected.",
        "attnf": "`1` is not a known attribute.",
    }

    rules = {
        "Unique[x_Symbol]": "Module[{x}, x]",
    }
    seq_number = 1
    summary_text = "generate a new symbols with a unique name"

    def eval(self, evaluation: Evaluation):
        "Unique[]"

        new_name = "$%d" % (self.seq_number)
        self.seq_number += 1
        # Next symbol in case of new name is defined before
        while evaluation.definitions.get_definition(new_name, True) is not None:
            new_name = "$%d" % (self.seq_number)
            self.seq_number += 1
        return Symbol(new_name)

    def eval_symbol(self, vars, attributes, evaluation: Evaluation):
        "Unique[vars_, attributes___]"

        from mathics.core.parser import is_symbol_name

        attributes = attributes.get_sequence()
        if len(attributes) > 1:
            evaluation.message("Unique", "argrx", Integer(len(attributes) + 1))
            return

        # Check valid symbol variables
        symbols = vars.elements if vars.has_form("List", None) else [vars]
        for symbol in symbols:
            if not isinstance(symbol, Symbol):
                text = symbol.get_string_value()
                if text is None or not is_symbol_name(text):
                    evaluation.message("Unique", "usym", symbol)
                    return

        # Check valid attributes
        attrs = []
        if len(attributes) > 0:
            attrs = get_symbol_list(
                attributes[0], lambda item: evaluation.message("Unique", "attnf", item)
            )
            if attrs is None:
                return None

        # Generate list new symbols
        list = []
        for symbol in symbols:
            if isinstance(symbol, Symbol):
                list.append(Module(ListExpression(symbol), symbol).evaluate(evaluation))
            else:
                new_name = f"{symbol.get_string_value()}{self.seq_number}"
                self.seq_number += 1
                # Next symbol in case of new name is defined before
                while evaluation.definitions.get_definition(new_name, True) is not None:
                    new_name = f"{symbol.get_string_value()}{self.seq_number}"
                    self.seq_number += 1
                list.append(Symbol(new_name))
        for symbol in list:
            for att in attrs:
                evaluation.definitions.set_attribute(
                    symbol.get_name(), attribute_string_to_number.get(att, 0)
                )

        if vars.has_form("List", None):
            return ListExpression(*list)
        else:
            return list[0]


class With(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/With.html</url>

    <dl>
      <dt>'With[{$x$=$x0$, $y$=$y0$, ...}, $expr$]'
      <dd>specifies that all occurrences of the symbols $x$, $y$, ... in \
          $expr$ should be replaced by $x0$, $y0$, ...
    </dl>

    ## >> n = 10
    ##  = 10

    ## Evaluate an expression with x locally set to 5:

    ## 'With' works even without evaluation:
    ## >> With[{x = a}, (1 + x^2) &]
    ##  = 1 + a ^ 2&

    ## Use 'With' to insert values into held expressions
    ## >> With[{x=y}, Hold[x]]
    ##  = Hold[y]

    ## >> Table[With[{i=j}, Hold[i]],{j,1,4}]
    ##  = {Hold[1], Hold[2], Hold[3], Hold[4]}
    ## >> x=5; With[{x=x}, Hold[x]]
    ##  = Hold[5]
    ## >> {Block[{x = 3}, Hold[x]], With[{x = 3}, Hold[x]]}
    ##  = {Hold[x], Hold[3]}
    ## >> x=.; ReleaseHold /@ %
    ##  = {x, 3}
    ## >> With[{e = y}, Function[{x,y}, e*x*y]]
    ##  = Function[{x$, y$}, y x$ y$]

    """

    attributes = A_HOLD_ALL | A_PROTECTED

    messages = {
        "lvsym": (
            "Local variable specification contains `1`, "
            "which is not a symbol or an assignment to a symbol."
        ),
        "dup": (
            "Duplicate local variable `1` found in local variable " "specification."
        ),
        "lvlist": "Local variable specification `1` is not a List.",
    }
    summary_text = "replace variables by some constant values"

    def eval(self, vars, expr, evaluation: Evaluation):
        "With[vars_, expr_]"

        vars = dict(get_scoping_vars(vars, "With", evaluation))
        result = expr.replace_vars(vars)
        result.evaluate(evaluation)
        return result
