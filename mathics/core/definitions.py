# -*- coding: utf-8 -*-

import pickle

import os
import base64
import re
import bisect

from collections import defaultdict

import typing
from mathics.core.symbols import (
    fully_qualified_symbol_name,
    strip_context,
    Symbol,
    SymbolList,
)
from mathics.core.systemsymbols import SymbolInfinity

from mathics.core.expression import Expression
from mathics.core.atoms import String
from mathics_scanner.tokeniser import full_names_pattern

type_compiled_pattern = type(re.compile("a.a"))


def ensure_symbol(symbol):
    assert not isinstance(symbol, str)
    # if isinstance(symbol, str):
    #    symbol = Symbol(self.lookup_name(symbol))
    return symbol


def get_file_time(file) -> float:
    try:
        return os.stat(file).st_mtime
    except OSError:
        return 0


def valuesname(name) -> str:
    "'NValues' -> 'n'"

    assert name.startswith("System`"), name
    if name == "System`Messages":
        return "messages"
    else:
        return name[7:-6].lower()


def autoload_files(
    defs, root_dir_path: str, autoload_dir: str, block_global_definitions: bool = True
):
    from mathics.core.evaluation import Evaluation

    # Load symbols from the autoload folder
    for root, dirs, files in os.walk(os.path.join(root_dir_path, autoload_dir)):
        for path in [os.path.join(root, f) for f in files if f.endswith(".m")]:
            Expression("Get", String(path)).evaluate(Evaluation(defs))

    if block_global_definitions:
        # Move any user definitions created by autoloaded files to
        # builtins, and clear out the user definitions list. This
        # means that any autoloaded definitions become shared
        # between users and no longer disappear after a Quit[].
        #
        # Autoloads that accidentally define a name in Global`
        # could cause confusion, so check for this.

        for symbol in defs.definitions_dict:
            if isinstance(symbol, str):
                symbol = Symbol(symbol)
            if symbol.name.startswith("Global`"):
                raise ValueError("autoload defined %s." % symbol.name)


class PyMathicsLoadException(Exception):
    def __init__(self, module):
        self.name = module + " is not a valid pymathics module"
        self.module = module


def load_builtins(definitions):
    from mathics.builtin import modules, contribute
    from mathics.settings import ROOT_DIR

    contribute()
    for module in []:  # definitions.extension_modules:
        try:
            definitions.load_pymathics_module(module, remove_on_quit=False)
        except PyMathicsLoadException:
            raise
        except ImportError:
            raise

    autoload_files(definitions, ROOT_DIR, "autoload")

    # Move any user definitions created by autoloaded files to
    # builtins, and clear out the user definitions list. This
    # means that any autoloaded definitions become shared
    # between users and no longer disappear after a Quit[].
    #
    # Autoloads that accidentally define a name in Global`
    # could cause confusion, so check for this.
    #
    for symbol in definitions.definitions_dict:
        if symbol.name.startswith("Global`"):
            raise ValueError("autoload defined %s." % name)
    for symbol in definitions.definitions_dict:
        if symbol.builtin_definition is None:
            symbol.builtin_definition = definitions.definitions_dict[symbol]
    definitions.definitions_dict = {}
    definitions.clear_cache()


class Definitions(object):
    def __init__(
        self, add_builtin=False, builtin_filename=None, extension_modules=[]
    ) -> None:
        super(Definitions, self).__init__()
        self.definitions_dict = {}
        #        self.builtin = {}
        #        self.user = {}
        #        self.pymathics = {}
        self.definitions_cache = {}
        self.lookup_cache = {}
        self.proxy = defaultdict(set)
        self.now = 0  # increments whenever something is updated
        self._packages = []
        self.extension_modules = extension_modules

        if add_builtin:
            from mathics.builtin import modules, contribute
            from mathics.settings import ROOT_DIR

            loaded = False
            """
            if builtin_filename is not None:
                builtin_dates = [get_file_time(module.__file__) for module in modules]
                builtin_time = max(builtin_dates)
                if get_file_time(builtin_filename) > builtin_time:
                    builtin_file = open(builtin_filename, "rb")
                    self.builtin = pickle.load(builtin_file)
                    loaded = True
            """
            if not loaded:
                load_builtins(self)

        # FIXME load dynamically as we do other things
        import mathics.format.asy  # noqa
        import mathics.format.json  # noqa
        import mathics.format.svg  # noqa

    def load_pymathics_module(self, module, remove_on_quit=True):
        """
        Loads Mathics builtin objects and their definitions
        from an external Python module in the pymathics module namespace.
        """
        import importlib
        from mathics.builtin import is_builtin, builtins_by_module, Builtin

        # Ensures that the pymathics module be reloaded
        import sys

        if module in sys.modules:
            loaded_module = importlib.reload(sys.modules[module])
        else:
            loaded_module = importlib.import_module(module)

        builtins_by_module[loaded_module.__name__] = []
        vars = set(
            loaded_module.__all__
            if hasattr(loaded_module, "__all__")
            else dir(loaded_module)
        )

        newsymbols = {}
        if not ("pymathics_version_data" in vars):
            raise PyMathicsLoadException(module)
        for name in vars - set(("pymathics_version_data", "__version__")):
            var = getattr(loaded_module, name)
            if (
                hasattr(var, "__module__")
                and is_builtin(var)
                and not name.startswith("_")
                and var.__module__[: len(loaded_module.__name__)]
                == loaded_module.__name__
            ):  # nopep8
                instance = var(expression=False)
                if isinstance(instance, Builtin):
                    if not var.context:
                        var.context = "Pymathics`"
                    symbol_name = instance.get_name()
                    builtins_by_module[loaded_module.__name__].append(instance)
                    newsymbols[symbol_name] = instance

        for name in newsymbols:
            self.user.pop(name, None)

        for name, item in newsymbols.items():
            if name != "System`MakeBoxes":
                item.contribute(self, is_pymodule=True)

        onload = loaded_module.pymathics_version_data.get("onload", None)
        if onload:
            onload(self)

        return loaded_module

    def clear_pymathics_modules(self):
        from mathics.builtin import builtins_by_module

        for key in list(builtins_by_module.keys()):
            if not key.startswith("mathics."):
                del builtins_by_module[key]
        for key in self.pymathics:
            del self.pymathics[key]

        self.pymathics = {}
        return None

    def clear_cache(self, symbol=None):
        # the definitions cache (self.definitions_cache) caches (incomplete and complete) names -> Definition(),
        # e.g. "xy" -> d and "MyContext`xy" -> d. we need to clear this cache if a Definition() changes (which
        # would happen if a Definition is combined from a builtin and a user definition and some content in the
        # user definition is updated) or if the lookup rules change and we could end up at a completely different
        # Definition.

        # the lookup cache (self.lookup_cache) caches what lookup_name() does. we only need to update this if some
        # change happens that might change the result lookup_name() calculates. we do not need to change it if a
        # Definition() changes.

        # self.proxy keeps track of all the names we cache. if we need to clear the caches for only one name, e.g.
        # 'MySymbol', then we need to be able to look up all the entries that might be related to it, e.g. 'MySymbol',
        # 'A`MySymbol', 'C`A`MySymbol', and so on. proxy identifies symbols using their stripped name and thus might
        # give us symbols in other contexts that are actually not affected. still, this is a safe solution.

        if symbol is None:
            self.definitions_cache = {}
            self.lookup_cache = {}
            self.proxy = defaultdict(set)
        else:
            if isinstance(symbol, str):
                symbol = Symbol(self.lookup_name(symbol))

            definitions_cache = self.definitions_cache
            lookup_cache = self.lookup_cache
            tail = strip_context(symbol.name)
            for k in self.proxy.pop(tail, []):
                definitions_cache.pop(k, None)
                lookup_cache.pop(k.get_name(), None)

    def clear_definitions_cache(self, symbol) -> None:
        definitions_cache = self.definitions_cache
        symbol = ensure_symbol(symbol)
        tail = strip_context(symbol.name)
        for k in self.proxy.pop(tail, []):
            definitions_cache.pop(k, None)

    def has_changed(self, maximum, symbols):
        # timestamp for the most recently changed part of a given expression.
        ensured_symbols = []
        for symbol in ensured_symbols:
            if isinstance(symbol, str):
                if symbol == "" or symbol[-1] == "`":
                    continue
                ensured_symbols.append(Symbol(symbol))
            else:
                ensured_symbols.append(symbol)
        symbols = ensured_symbols

        for symbol in symbols:
            symb = self.get_definition(symbol, only_if_exists=True)
            if symb is None:
                # symbol doesn't exist so it was never changed
                pass
            else:
                changed = getattr(symb, "changed", None)
                if changed is None:
                    # must be system symbol
                    symb.changed = 0
                elif changed > maximum:
                    return True

        return False

    def get_current_context(self):
        # It's crucial to specify System` in this get_ownvalue() call,
        # otherwise we'll end up back in this function and trigger
        # infinite recursion.
        context_rule = self.get_ownvalue(Symbol("System`$Context"))
        if context_rule:
            context = context_rule.replace.get_string_value()
        else:
            context = "System`"
        assert context is not None, "$Context somehow set to an invalid value"
        return context

    def get_context_path(self):
        context_path_rule = self.get_ownvalue(Symbol("System`$ContextPath"))
        if context_path_rule is None:
            return ["System`"]
        context_path = context_path_rule.replace
        assert context_path.has_form("System`List", None)
        context_path = [c.get_string_value() for c in context_path.leaves]
        assert not any([c is None for c in context_path])
        return context_path

    def set_current_context(self, context) -> None:
        assert isinstance(context, str)
        self.set_ownvalue(Symbol("System`$Context"), String(context))
        self.clear_cache()

    def set_context_path(self, context_path) -> None:
        assert isinstance(context_path, list)
        assert all([isinstance(c, str) for c in context_path])
        self.set_ownvalue(
            Symbol("System`$ContextPath"),
            Expression(SymbolList, *[String(c) for c in context_path]),
        )
        self.clear_cache()

    def get_builtin_names(self):
        defined_symbols = Symbol.defined_symbols
        return set(
            symbol
            for symbol in defined_symbols
            if defined_symbols[symbol].builtin_definition
        )

    def get_user_names(self):
        return set(
            symbol.name
            for symbol in self.definitions_dict
            if symbol.builtin_definition is None
        )

    def get_pymathics_names(self):
        return set()
        # return set(self.pymathics)

    def get_names(self):
        return (
            self.get_builtin_names()
            # | self.get_pymathics_names()
            | self.get_user_names()
        )

    def get_accessible_contexts(self):
        "Return the contexts reachable though $Context or $ContextPath."
        accessible_ctxts = set(self.get_context_path())
        accessible_ctxts.add(self.get_current_context())
        return accessible_ctxts

    def get_matching_names(self, pattern) -> typing.List[str]:
        """
        Return a list of the symbol names matching a string pattern.

        A pattern containing a context mark (of the form
        "ctx_pattern`short_pattern") matches symbols whose context and
        short name individually match the two patterns. A pattern
        without a context mark matches symbols accessible through
        $Context and $ContextPath whose short names match the pattern.

        '*' matches any sequence of symbol characters or an empty
        string. '@' matches a non-empty sequence of symbol characters
        which aren't uppercase letters. In the context pattern, both
        '*' and '@' match context marks.
        """
        if isinstance(pattern, type_compiled_pattern):
            regex = pattern
        else:
            if re.match(full_names_pattern, pattern) is None:
                # The pattern contained characters which weren't allowed
                # in symbols and aren't valid wildcards. Hence, the
                # pattern can't match any symbols.
                return []

            # If we get here, there aren't any regexp metacharacters in
            # the pattern.

            if "`" in pattern:
                ctx_pattern, short_pattern = pattern.rsplit("`", 1)
                if ctx_pattern == "":
                    ctx_pattern = "System`"
                else:
                    ctx_pattern = (
                        (ctx_pattern + "`")
                        .replace("@", "[^A-Z`]+")
                        .replace("*", ".*")
                        .replace("$", r"\$")
                    )
            else:
                short_pattern = pattern
                # start with a group matching the accessible contexts
                ctx_pattern = "(?:%s)" % "|".join(
                    re.escape(c) for c in self.get_accessible_contexts()
                )

            short_pattern = (
                short_pattern.replace("@", "[^A-Z]+")
                .replace("*", "[^`]*")
                .replace("$", r"\$")
            )
            regex = re.compile("^" + ctx_pattern + short_pattern + "$")

        return [name for name in self.get_names() if regex.match(name)]

    def lookup_name(self, name) -> str:
        """
        Determine the full name (including context) for a symbol name.

        - If the name begins with a context mark, it's in the context
          given by $Context.
        - Otherwise, if it contains a context mark, it's already fully
          specified.
        - Otherwise, it doesn't contain a context mark: try $Context,
          then each element of $ContextPath, taking the first existing
          symbol.
        - Otherwise, it's a new symbol in $Context.
        """

        cached = self.lookup_cache.get(name, None)
        if cached is not None:
            return cached

        assert isinstance(name, str)

        # Bail out if the name we're being asked to look up is already
        # fully qualified.
        if fully_qualified_symbol_name(name):
            return name

        current_context = self.get_current_context()

        if "`" in name:
            if name.startswith("`"):
                return current_context + name.lstrip("`")
            return name

        with_context = current_context + name
        # if not self.have_definition(with_context):
        for ctx in self.get_context_path():
            n = ctx + name
            if self.have_definition(Symbol(n)):
                return n
        return with_context

    def get_package_names(self) -> typing.List[str]:
        packages = self.get_ownvalue(Symbol("System`$Packages"))
        packages = packages.replace
        assert packages.has_form("System`List", None)
        packages = [c.get_string_value() for c in packages.leaves]
        return packages

        # return sorted({name.split("`")[0] for name in self.get_names()})

    def shorten_name(self, name_with_ctx) -> str:
        if "`" not in name_with_ctx:
            return name_with_ctx

        def in_ctx(name, ctx):
            return name.startswith(ctx) and "`" not in name[len(ctx) :]

        if in_ctx(name_with_ctx, self.get_current_context()):
            return name_with_ctx[len(self.get_current_context()) :]
        for ctx in self.get_context_path():
            if in_ctx(name_with_ctx, ctx):
                return name_with_ctx[len(ctx) :]
        return name_with_ctx

    def have_definition(self, symbol) -> bool:
        if isinstance(symbol, str):
            assert False
            symbol = symbol(self.lookup_name(symbol))
        if symbol.builtin_definition:
            return True
        return self.get_definition(symbol, only_if_exists=True) is not None

    def get_definition(self, symbol, only_if_exists=False) -> "Definition":
        definition = self.definitions_cache.get(symbol, None)
        if definition is not None:
            return definition
        assert not isinstance(symbol, str)
        if isinstance(symbol, str):
            if symbol == "" or symbol[-1] == "`":
                return None
            name = symbol
            original_name = name
            name = self.lookup_name(name)
            lookup_symbol = Symbol(name)
        else:
            lookup_symbol = symbol
            name = symbol.name
            original_name = name

        definition = self.definitions_dict.get(lookup_symbol, None)
        if definition is not None:
            self.proxy[strip_context(name)].add(symbol)
            self.definitions_cache[symbol] = definition
            self.lookup_cache[original_name] = name
        elif not only_if_exists:
            assert symbol.name != "Global`False"
            definition = Definition(symbol=lookup_symbol, definitions=self)
            builtin = lookup_symbol.builtin_definition
            if builtin:
                definition.attributes.update(builtin.attributes)
                definition.options.update(builtin.options)
                definition.builtin = builtin.builtin
            self.definitions_dict[lookup_symbol] = definition

        return definition

    def get_attributes(self, symbol):
        # Attributes are always stored in the user definition
        # If the definition is reset, then the builtin values are copied
        if isinstance(symbol, str):
            lookup_name = self.lookup_name(symbol)
            symbol = Symbol(self.lookup_name(symbol))
        return self.get_definition(symbol).attributes

    def get_ownvalues(self, symbol):
        definition = self.get_definition(symbol)
        builtin = symbol.builtin_definition
        result = definition.ownvalues if definition else []
        return result + builtin.ownvalues if builtin else result

    def get_downvalues(self, symbol):
        definition = self.get_definition(symbol)
        builtin = symbol.builtin_definition
        result = definition.downvalues if definition else []
        return result + builtin.downvalues if builtin else result

    def get_subvalues(self, symbol):
        definition = self.get_definition(symbol)
        builtin = symbol.builtin_definition
        result = definition.subvalues if definition else []
        return result + builtin.subvalues if builtin else result

    def get_upvalues(self, symbol):
        definition = self.get_definition(symbol)
        builtin = symbol.builtin_definition
        result = definition.upvalues if definition else []
        return result + builtin.upvalues if builtin else result

    def get_nvalues(self, symbol):
        definition = self.get_definition(symbol)
        builtin = symbol.builtin_definition
        result = definition.nvalues if definition else []
        return result + builtin.nvalues if builtin else result

    def get_defaultvalues(self, symbol):
        definition = self.get_definition(symbol)
        builtin = symbol.builtin_definition
        result = definition.defaultvalues if definition else []
        return result + builtin.defaultvalues if builtin else result

    def get_formats(self, symbol, format=""):
        if isinstance(symbol, str):
            if symbol == "" or symbol[-1] == "`":
                return []
            symbol = Symbol(self.lookup_name(symbol))

        definition = self.get_definition(symbol)
        formats = self.get_definition(symbol).formatvalues
        result = formats.get(format, []) + formats.get("", [])
        # If the symbol is a builtin, add the corresponding formats:
        builtin = symbol.builtin_definition
        if builtin:
            formats = builtin.formatvalues
            result = result + formats.get(format, []) + formats.get("", [])
        result.sort()
        return result

    def get_value(self, symbol, pos, pattern, evaluation):
        symbol = ensure_symbol(symbol)
        pos = valuesname(pos)
        definition = self.get_definition(symbol)
        if definition:
            rules = definition.get_values_list(pos)
            for rule in rules:
                result = rule.apply(pattern, evaluation)
                if result is not None:
                    return result

    def get_user_definition(self, symbol, create=True) -> typing.Optional["Definition"]:
        symbol = ensure_symbol(symbol)

        existing = self.definitions_dict.get(symbol)
        if existing:
            return existing
        else:
            if not create:
                return None
            new_definition = Definition(symbol=symbol, definitions=self)
            self.definitions_dict[symbol] = new_definition
            self.clear_cache(symbol)
            return new_definition

    def get_options(self, symbol):
        if isinstance(symbol, str):
            symbol = Symbol(self.lookup_name(symbol))
        symbol = ensure_symbol(symbol)
        return self.get_definition(symbol).options

    def mark_changed(self, definition) -> None:
        self.now += 1
        definition.changed = self.now

    def reset_user_definition(self, symbol) -> None:
        if isinstance(symbol, str):
            symbol = Symbol(symbol)

        definition = self.definitions_dict.get(symbol, None)
        builtin = symbol.builtin_definition
        if definition:
            del self.definitions_dict[symbol]

        if builtin:
            # Notice that it is important to reset a new definition,
            # since the old definition could be hold in another place
            # to be restored later (for example, is what it happens in
            # `mathics.builtin.dynamical_scoping`)
            new_definition = Definition(
                symbol=symbol, builtin=builtin.builtin, definitions=self
            )
            new_definition.attributes.update(builtin.attributes)
            new_definition.options.update(builtin.options)
            # new_definition.reset_definition()
            self.definitions_dict[symbol] = new_definition

        self.clear_cache(symbol)
        # TODO fix changed

    def add_user_definition(self, symbol, definition) -> None:
        symbol = ensure_symbol(symbol)
        self.mark_changed(definition)
        self.definitions_dict[symbol] = definition
        self.clear_cache(symbol)

    def set_attribute(self, symbol, attribute) -> None:
        if isinstance(symbol, str):
            symbol = Symbol(self.lookup_name(symbol))
        symbol = ensure_symbol(symbol)
        definition = self.get_user_definition(symbol)
        definition.attributes.add(attribute)
        self.mark_changed(definition)
        self.clear_definitions_cache(symbol)

    def set_attributes(self, symbol, attributes) -> None:
        if isinstance(symbol, str):
            symbol = Symbol(self.lookup_name(symbol))
        symbol = ensure_symbol(symbol)

        definition = self.get_user_definition(symbol)
        definition.attributes = set(attributes)
        self.mark_changed(definition)
        self.clear_definitions_cache(symbol)

    def clear_attribute(self, symbol, attribute) -> None:
        if isinstance(symbol, str):
            symbol = Symbol(self.lookup_name(symbol))
        symbol = ensure_symbol(symbol)

        definition = self.get_user_definition(symbol)
        if attribute in definition.attributes:
            definition.attributes.remove(attribute)
        self.mark_changed(definition)
        self.clear_definitions_cache(symbol)

    def add_rule(self, symbol, rule, position=None):
        symbol = ensure_symbol(symbol)
        definition = self.get_user_definition(symbol)
        if position is None:
            result = definition.add_rule(rule)
        else:
            result = definition.add_rule_at(rule, position)
        self.mark_changed(definition)
        self.clear_definitions_cache(symbol)
        return result

    def add_format(self, symbol, rule, form="") -> None:
        symbol = ensure_symbol(symbol)
        definition = self.get_user_definition(symbol)
        if isinstance(form, tuple) or isinstance(form, list):
            forms = form
        else:
            forms = [form]
        for form in forms:
            if form not in definition.formatvalues:
                definition.formatvalues[form] = []
            insert_rule(definition.formatvalues[form], rule)
        self.mark_changed(definition)
        self.clear_definitions_cache(symbol)

    def add_nvalue(self, symbol, rule) -> None:
        symbol = ensure_symbol(symbol)
        definition = self.get_user_definition(symbol)
        definition.add_rule_at(rule, "n")
        self.mark_changed(definition)
        self.clear_definitions_cache(symbol)

    def add_default(self, symbol, rule) -> None:
        symbol = ensure_symbol(symbol)
        definition = self.get_user_definition(symbol)
        definition.add_rule_at(rule, "default")
        self.mark_changed(definition)
        self.clear_definitions_cache(symbol)

    def add_message(self, symbol, rule) -> None:
        symbol = ensure_symbol(symbol)
        definition = self.get_user_definition(symbol)
        definition.add_rule_at(rule, "messages")
        self.mark_changed(definition)
        self.clear_definitions_cache(symbol)

    def set_values(self, symbol, values, rules) -> None:
        symbol = ensure_symbol(symbol)
        definition = self.get_user_definition(symbol)
        pos = valuesname(values)
        definition.set_values_list(pos, rules)
        self.mark_changed(definition)
        self.clear_definitions_cache(symbol)

    def reset_user_definitions(self) -> None:
        self.definitions_dict = dict()
        self.clear_cache()
        # TODO changed

    def get_user_definitions(self):
        return base64.encodebytes(
            pickle.dumps(self.definitions_dict, protocol=2)
        ).decode("ascii")

    def set_user_definitions(self, definitions) -> None:
        if definitions:
            self.definitions_dict = pickle.loads(
                base64.decodebytes(definitions.encode("ascii"))
            )
        else:
            self.definitions_dict = {}
        self.clear_cache()

    def get_ownvalue(self, symbol):
        symbol = ensure_symbol(symbol)
        ownvalues = self.get_definition(symbol).ownvalues
        if ownvalues:
            return ownvalues[0]
        builtin = symbol.builtin_definition
        if builtin:
            ownvalues = builtin.ownvalues
            if ownvalues:
                return ownvalues[0]
        return None

    def set_ownvalue(self, symbol, value) -> None:
        from .expression import Symbol
        from .rules import Rule

        symbol = ensure_symbol(symbol)
        self.add_rule(symbol, Rule(symbol, value))
        self.clear_cache(symbol)

    def set_options(self, symbol, options) -> None:
        if isinstance(symbol, str):
            symbol = Symbol(self.lookup_name(symbol))
        symbol = ensure_symbol(symbol)
        definition = self.get_user_definition(symbol)
        definition.options = options
        self.mark_changed(definition)
        self.clear_definitions_cache(symbol)

    def unset(self, symbol, expr):
        symbol = ensure_symbol(symbol)
        definition = self.get_user_definition(symbol)
        result = definition.remove_rule(expr)
        self.mark_changed(definition)
        self.clear_definitions_cache(symbol)
        return result

    def get_config_value(self, symbol, default=None):
        "Infinity -> None, otherwise returns integer."
        if isinstance(symbol, str):
            symbol = Symbol(self.lookup_name(symbol))
        symbol = ensure_symbol(symbol)
        value = self.get_definition(symbol).ownvalues
        builtin = symbol.builtin_definition
        if len(value) == 0 and builtin:
            value = builtin.ownvalues
        if value:
            try:
                value = value[0].replace
            except AttributeError:
                return None
            if value is SymbolInfinity or value.has_form("DirectedInfinity", 1):
                return None

            return int(value.get_int_value())
        else:
            return default

    def set_config_value(self, symbol, new_value) -> None:
        from mathics.core.expression import Integer

        if isinstance(symbol, str):
            symbol = Symbol(self.lookup_name(symbol))
        symbol = ensure_symbol(symbol)

        self.set_ownvalue(symbol, Integer(new_value))

    def set_line_no(self, line_no) -> None:
        self.set_config_value(Symbol("$Line"), line_no)

    def get_line_no(self):
        return self.get_config_value(Symbol("$Line"), 0)

    def increment_line_no(self, increment: int = 1) -> None:
        self.set_config_value(Symbol("$Line"), self.get_line_no() + increment)

    def get_history_length(self):
        history_length = self.get_config_value(Symbol("$HistoryLength"), 100)
        if history_length is None or history_length > 100:
            history_length = 100
        return history_length


def get_tag_position(pattern, symbol) -> typing.Optional[str]:
    if isinstance(symbol, str):
        symbol = Symbol(symbol)
    if pattern.get_name() == symbol.name:
        return "own"
    elif pattern.is_atom():
        return None
    else:
        head_name = pattern.get_head_name()
        if head_name == symbol.name:
            return "down"
        elif head_name == "System`N" and len(pattern.leaves) == 2:
            return "n"
        elif head_name == "System`Condition" and len(pattern.leaves) > 0:
            return get_tag_position(pattern.leaves[0], symbol)
        elif pattern.get_lookup_name() == symbol.name:
            return "sub"
        else:
            for leaf in pattern.leaves:
                if leaf.get_lookup_name() == symbol.name:
                    return "up"
        return None


def insert_rule(values, rule) -> None:
    for index, existing in enumerate(values):
        if existing.pattern.sameQ(rule.pattern):
            del values[index]
            break
    # use insort_left to guarantee that if equal rules exist, newer rules will
    # get higher precedence by being inserted before them. see DownValues[].
    res = bisect.insort_left(values, rule)


class Definition(object):
    def __init__(
        self,
        symbol,
        definitions,
        rules=None,
        ownvalues=None,
        downvalues=None,
        subvalues=None,
        upvalues=None,
        formatvalues=None,
        messages=None,
        attributes=(),
        options=None,
        nvalues=None,
        defaultvalues=None,
        builtin=None,
    ) -> None:

        super(Definition, self).__init__()
        if isinstance(symbol, str):
            symbol = Symbol(symbol)

        self.definitions = definitions
        self.symbol = symbol

        if rules is None:
            rules = []
        if ownvalues is None:
            ownvalues = []
        if downvalues is None:
            downvalues = []
        if subvalues is None:
            subvalues = []
        if upvalues is None:
            upvalues = []
        if formatvalues is None:
            formatvalues = {}
        if options is None:
            options = {}
        if nvalues is None:
            nvalues = []
        if defaultvalues is None:
            defaultvalues = []
        if messages is None:
            messages = []

        self.ownvalues = ownvalues
        self.downvalues = downvalues
        self.subvalues = subvalues
        self.upvalues = upvalues
        self.formatvalues = dict((name, list) for name, list in formatvalues.items())
        self.messages = messages
        self.attributes = set(attributes)
        for a in self.attributes:
            assert "`" in a, "%s attribute %s has no context" % (name, a)
        self.options = options
        self.nvalues = nvalues
        self.defaultvalues = defaultvalues
        self.builtin = builtin
        for rule in rules:
            self.add_rule(rule)

    def get_values_list(self, pos):
        assert pos.isalpha()
        builtin = self.symbol.builtin_definition
        if pos == "messages":
            return self.messages + builtin.messages if builtin else self.messages
        else:
            key = "%svalues" % pos
            if builtin:
                return getattr(self, key) + getattr(builtin, key)
            else:
                return getattr(self, key)

    def get_user_values_list(self, pos):
        assert pos.isalpha()
        if pos == "messages":
            return self.messages
        else:
            key = "%svalues" % pos
            return getattr(self, key)

    def set_values_list(self, pos, rules) -> None:
        assert pos.isalpha()
        if pos == "messages":
            self.messages = rules
        else:
            setattr(self, "%svalues" % pos, rules)

    def add_rule_at(self, rule, position) -> bool:
        values = self.get_user_values_list(position)
        insert_rule(values, rule)
        return True

    def add_rule(self, rule) -> bool:
        pos = get_tag_position(rule.pattern, self.symbol)
        if pos:
            return self.add_rule_at(rule, pos)
        return False

    def remove_rule(self, lhs) -> bool:
        position = get_tag_position(lhs, self.symbol)
        if position:
            values = self.get_values_list(position)
            for index, existing in enumerate(values):
                if existing.pattern.expr.sameQ(lhs):
                    del values[index]
                    return True
        return False

    def reset_definition(self):
        self.ownvalues = []
        self.downvalues = []
        self.subvalues = []
        self.upvalues = []
        self.formatvalues = {}
        self.messages = []
        self.attributes = {}
        self.options = {}
        self.nvalues = []
        self.defaultvalues = []

    def __repr__(self) -> str:
        s = "<Definition: id:{}  name: {}, ownvalues: {}, downvalues: {}, formats: {}, attributes: {}>".format(
            id(self),
            self.symbol.get_name(),
            self.ownvalues,
            self.downvalues,
            self.formatvalues,
            self.attributes,
        )
        return s
