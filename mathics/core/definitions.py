# -*- coding: utf-8 -*-
"""
Objects that represent the `Definition` associated with a `Symbol` and
groups of `Definitions`.
"""

import base64
import bisect
import os
import os.path as osp
import pickle
import re
from collections import defaultdict
from os.path import join as osp_join
from typing import Dict, List, Optional, Sequence, Set, Tuple, Union

from mathics_scanner.tokeniser import full_names_pattern

from mathics.core.atoms import Integer, String
from mathics.core.attributes import A_NO_ATTRIBUTES
from mathics.core.convert.expression import to_mathics_list
from mathics.core.element import fully_qualified_symbol_name
from mathics.core.expression import Expression
from mathics.core.load_builtin import definition_contribute, mathics3_builtins_modules
from mathics.core.pattern import BasePattern, ExpressionPattern
from mathics.core.rules import Rule
from mathics.core.symbols import Atom, Symbol, strip_context
from mathics.core.systemsymbols import SymbolGet
from mathics.core.util import canonic_filename
from mathics.settings import ROOT_DIR

type_compiled_pattern = type(re.compile("a.a"))

# The contents of $OutputForms. FormMeta in mathics.base.forms adds to this.
OutputForms: Set[Symbol] = set()

# The contents of $PrintForms. FormMeta in mathics.base.forms adds to this.
PrintForms: Set[Symbol] = set()


def get_file_time(file) -> float:
    """Return the last time that a file was accessed"""
    try:
        return os.stat(file).st_mtime
    except OSError:
        return 0


def valuesname(name) -> str:
    """'NValues' -> 'n'"""

    assert name.startswith("System`"), name
    if name == "System`Messages":
        return "messages"
    return name[7:-6].lower()


def autoload_files(
    defs, root_dir_path: str, autoload_dir: str, block_global_definitions: bool = True
):
    """
    Load Mathics code from the autoload-folder files.
    """
    from mathics.core.evaluation import Evaluation

    for root, _, files in os.walk(osp_join(root_dir_path, autoload_dir)):
        for path in [osp_join(root, f) for f in files if f.endswith(".m")]:
            # Autoload definitions should be go in the System context
            # by default, rather than the Global context.
            defs.set_current_context("System`")
            Expression(SymbolGet, String(path)).evaluate(Evaluation(defs))
            # Restore default context to Global
            defs.set_current_context("Global`")

    if block_global_definitions:
        # Move any user definitions created by autoloaded files to
        # builtins, and clear out the user definitions list. This
        # means that any autoloaded definitions become shared
        # between users and no longer disappear after a Quit[].
        #
        # Autoloads that accidentally define a name in Global`
        # could cause confusion, so check for this.

        for name in defs.user:
            if name.startswith("Global`"):
                raise ValueError("autoload defined %s." % name)

    # Move the user definitions to builtin:
    for symbol_name in defs.user:
        defs.builtin[symbol_name] = defs.get_definition(symbol_name)

    defs.user = {}
    defs.clear_cache()


class Definition:
    """
    A Definition is a collection of ``Rule``s and attributes which are associated with ``Symbol``.

    The ``Rule``s are internally organized in terms of the context of application in
    ``ownvalues``, ``upvalues``,  ``downvalues``,  ``subvalues``, ``nvalues``,  ``format``, etc.
    """

    def __init__(
        self,
        name,
        rules=None,
        ownvalues=None,
        downvalues=None,
        subvalues=None,
        upvalues=None,
        formatvalues=None,
        messages=None,
        attributes=A_NO_ATTRIBUTES,
        options=None,
        nvalues=None,
        defaultvalues=None,
        builtin=None,
        is_numeric=False,
    ) -> None:
        super(Definition, self).__init__()
        self.name = name

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

        self.is_numeric = is_numeric
        self.ownvalues = ownvalues
        self.downvalues = downvalues
        self.subvalues = subvalues
        self.upvalues = upvalues
        self.formatvalues = dict((name, list) for name, list in formatvalues.items())
        self.messages = messages
        self.attributes = attributes
        self.options: Dict[str, str] = options
        self.nvalues = nvalues
        self.defaultvalues = defaultvalues
        self.builtin = builtin
        self.changed = 0
        for rule in rules:
            if not self.add_rule(rule):
                print(f"{rule.pattern.expr} could not be associated with {self.name}")

    def get_values_list(self, pos: str):
        assert pos.isalpha()
        if pos == "messages":
            return self.messages
        return getattr(self, "%svalues" % pos)

    def set_values_list(self, pos: str, rules) -> None:
        assert pos.isalpha()
        if pos == "messages":
            self.messages = rules
        else:
            setattr(self, "%svalues" % pos, rules)

    def add_rule_at(self, rule, position: str) -> bool:
        values = self.get_values_list(position)
        insert_rule(values, rule)
        return True

    def add_rule(self, rule) -> bool:
        pos = get_tag_position(rule.pattern, self.name)
        if pos:
            return self.add_rule_at(rule, pos)
        return False

    def remove_rule(self, lhs) -> bool:
        position = get_tag_position(lhs, self.name)
        if position:
            values = self.get_values_list(position)
            for index, existing in enumerate(values):
                if existing.pattern.expr.sameQ(lhs):
                    del values[index]
                    return True
        return False

    def __repr__(self) -> str:
        repr_str = "<Definition: name: {}, downvalues: {}, formats: {}, attributes: {}>".format(
            self.name, self.downvalues, self.formatvalues, self.attributes
        )
        return repr_str


class Definitions:
    """The state of one instance of the Mathics3 interpreter is stored in this object.

    The state is then stored as ``Definition`` object of the different
    symbols defined during the runtime.

    In the current implementation, the ``Definitions`` object stores
    ``Definition`` s in four dictionaries:

    - builtins: stores the definitions of the ``Builtin`` symbols
    - pymathics: stores the definitions of the ``Builtin`` symbols added from pymathics
      modules.
    - user: stores the definitions created during the runtime.
    - definition_cache: keep definitions obtained by merging builtins, pymathics, and
      user definitions associated with the same symbol.

    Note: we want Rules to be serializable so that we can dump and
    restore Rules in order to make startup time faster.
    """

    def __init__(
        self,
        add_builtin: bool = False,
        builtin_filename: Optional[str] = None,
        extension_modules: list = [],
    ) -> None:
        super(Definitions, self).__init__()
        self.builtin: Dict[str, Definition] = {}
        self.user: Dict[str, Definition] = {}
        self.pymathics: Dict[str, Definition] = {}
        self.definitions_cache: Dict[str, Definition] = {}
        self.lookup_cache: Dict[str, str] = {}
        self.proxy: Dict[str, Set[str]] = defaultdict(set)
        self.now = 0  # increments whenever something is updated
        self._packages: List[str] = []
        self.current_context = "Global`"
        self.context_path: Tuple[str, ...] = (
            "System`",
            "Global`",
        )
        self.inputfile = ""

        # Importing "mathics.format" populates the Symbol of the
        # PrintForms and OutputForms sets.
        #
        # If "importlib" is used instead of "import", then we get:
        #   TypeError: boxes_to_text() takes 1 positional argument but
        #   2 were given
        # Rocky: this smells of something not quite right in terms of
        # modularity.
        import mathics.format  # noqa
        from mathics.eval.pymathics import PyMathicsLoadException, load_pymathics_module

        self.printforms = list(PrintForms)
        self.outputforms = list(OutputForms)
        self.trace_evaluation = False
        self.timing_trace_evaluation = False

        if add_builtin:
            loaded = False
            if builtin_filename is not None:
                builtin_dates = [
                    get_file_time(module.__file__)
                    for module in mathics3_builtins_modules
                ]
                builtin_time = max(builtin_dates)
                if get_file_time(builtin_filename) > builtin_time:
                    with open(builtin_filename, "rb") as builtin_file:
                        self.builtin = pickle.load(builtin_file)
                    loaded = True
            if not loaded:
                definition_contribute(self)
                for module in extension_modules:
                    try:
                        load_pymathics_module(self, module)
                    except PyMathicsLoadException:
                        raise
                    except ImportError:
                        raise

                if builtin_filename is not None:
                    with open(builtin_filename, "wb") as builtin_file:
                        pickle.dump(self.builtin, builtin_file, -1)

            autoload_files(self, ROOT_DIR, "autoload")

    def clear_cache(self, name: Optional[str] = None):
        """Clear the definitions cache. If `name` is provided,
        just remove the definition for `name` from the definition cache.
        """
        # The definitions cache (self.definitions_cache) caches
        # (incomplete and complete) names -> Definition(), e.g. "xy"
        # -> d and "MyContext`xy" -> d. we need to clear this cache if
        # a Definition() changes (which would happen if a Definition
        # is combined from a builtin and a user definition and some
        # content in the user definition is updated) or if the lookup
        # rules change, and we could end up at a completely different
        # Definition.

        # The lookup cache (self.lookup_cache) caches what
        # lookup_name() does. we only need to update this if some
        # change happens that might change the result lookup_name()
        # calculates. we do not need to change it if a Definition()
        # changes.

        # self.proxy keeps track of all the names we cache. if we need
        # to clear the caches for only one name, e.g.  'MySymbol',
        # then we need to be able to look up all the entries that
        # might be related to it, e.g. 'MySymbol', 'A`MySymbol',
        # 'C`A`MySymbol', and so on. proxy identifies symbols using
        # their stripped name and thus might give us symbols in other
        # contexts that are actually not affected. still, this is a
        # safe solution.

        if name is None:
            self.definitions_cache = {}
            self.lookup_cache = {}
            self.proxy = defaultdict(set)
        else:
            definitions_cache = self.definitions_cache
            lookup_cache = self.lookup_cache
            tail = strip_context(name)
            for k in self.proxy.pop(tail, []):
                definitions_cache.pop(k, None)
                lookup_cache.pop(k, None)

    def clear_definitions_cache(self, name: str) -> None:
        """
        Remove from the definition cache all the entries
        associated with a `name`
        """
        definitions_cache = self.definitions_cache
        tail = strip_context(name)
        for k in self.proxy.pop(tail, []):
            definitions_cache.pop(k, None)

    def is_uncertain_final_value(self, last_evaluated_time: int, symbols: set) -> bool:
        """
        Used in Evaluate_do_format() to
        determine if we should (re)evaluate an expression.

        Here, for a definitions object, we check if any symbol in the
        symbols has changed. `last_evaluated_time` indicates when the
        evaluation started. If a symbol has a time greater than
        that, then things have changed since the evaluation started
        and evaluation may lead to a different result.
        """
        for name in symbols:
            try:
                symbol = self.get_definition(name, only_if_exists=True)
            except KeyError:
                # "symbol" doesn't exist, so it was never changed.
                continue
            # Get timestamp for the most-recently changed part of the given expression.
            if symbol.changed > last_evaluated_time:
                return True

        return False

    def get_current_context(self):
        return self.current_context

    def get_context_path(self):
        return self.context_path

    def get_inputfile(self) -> str:
        return self.inputfile if hasattr(self, "inputfile") else ""

    def set_current_context(self, context) -> None:
        assert isinstance(context, str)
        self.set_ownvalue("System`$Context", String(context))
        self.current_context = context
        self.clear_cache()

    def set_context_path(self, context_path: Sequence[str]) -> None:
        assert all(isinstance(c, str) for c in context_path)
        self.set_ownvalue(
            "System`$ContextPath",
            to_mathics_list(*context_path, elements_conversion_fn=String),
        )
        self.context_path = tuple(context_path)
        self.clear_cache()

    def set_inputfile(self, path: str) -> None:
        """Set the input file to `path`"""
        self.inputfile = osp.normpath(osp.abspath(path))
        self.inputfile = canonic_filename(self.inputfile)

    def get_builtin_names(self) -> set:
        """Return a set of builtin symbol names"""
        return set(self.builtin)

    def get_user_names(self) -> set:
        """Return a set of user symbol names"""
        return set(self.user)

    def get_pymathics_names(self) -> set:
        """Return a set of the names of symbols defined in Mathics3 modules"""
        return set(self.pymathics)

    def get_names(self) -> set:
        """
        Return a set with the names of all the symbols
        defined in the system
        """
        return (
            self.get_builtin_names()
            | self.get_pymathics_names()
            | self.get_user_names()
        )

    def get_accessible_contexts(self) -> set:
        """Return the contexts reachable though $Context or $ContextPath."""
        accessible_ctxts = set(ctx for ctx in self.context_path)
        accessible_ctxts.add(self.current_context)
        return accessible_ctxts

    def get_matching_names(self, pattern: str) -> List[str]:
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

    def lookup_name(self, name: str) -> str:
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

        current_context = self.current_context

        if "`" in name:
            if name.startswith("`"):
                return current_context + name.lstrip("`")
            return name

        with_context = current_context + name
        # if not self.have_definition(with_context):
        for ctx in self.context_path:
            n = ctx + name
            if self.have_definition(n):
                return n
        return with_context

    def get_package_names(self) -> List[str]:
        packages = self.get_ownvalue("System`$Packages")
        packages = packages.replace
        assert packages.has_form("System`List", None)
        packages = [c.get_string_value() for c in packages.elements]
        return packages

        # return sorted({name.split("`")[0] for name in self.get_names()})

    def shorten_name(self, name_with_ctx: str) -> str:
        if "`" not in name_with_ctx:
            return name_with_ctx

        def in_ctx(name: str, ctx: str):
            return name.startswith(ctx) and "`" not in name[len(ctx) :]

        current_context = self.current_context
        if in_ctx(name_with_ctx, current_context):
            return name_with_ctx[len(current_context) :]
        for ctx in self.context_path:
            if in_ctx(name_with_ctx, ctx):
                return name_with_ctx[len(ctx) :]
        return name_with_ctx

    def have_definition(self, name: str) -> bool:
        try:
            self.get_definition(name, only_if_exists=True)
        except KeyError:
            return False
        return True

    def get_definition(self, name: str, only_if_exists: bool = False) -> Definition:
        """
        Return the definition associated with the Symbol `name`.
        If `only_if_exists` is `True` and the symbol does not
        have an associated `Definition`, raise a `KeyError` exception.
        Otherwise, creates a temporary definition, which is not
        stored into the `Definitions` object.

        Parameters
        ----------
        name : str
            The name of the Symbol.
        only_if_exists : bool, optional
            If True, and the symbol was not already defined, raise a KeyError
            exception. Otherwise, Creates a temporary Definition for
            the symbol, but does not store it. The default is False.

        Raises
        ------
        KeyError
            DESCRIPTION.

        Returns
        -------
        Definition
            A definition for the requested Symbol name.

        """
        definition = self.definitions_cache.get(name, None)
        if definition is not None:
            return definition

        original_name = name
        name = self.lookup_name(name)
        user = self.user.get(name, None)
        pymathics = self.pymathics.get(name, None)
        builtin = self.builtin.get(name, None)

        candidates = [user] if user else []
        builtin_instance = None

        if pymathics:
            builtin_instance = pymathics.builtin
            candidates.append(pymathics)
        if builtin:
            candidates.append(builtin)
            if builtin_instance is None:
                builtin_instance = builtin.builtin

        definition = candidates[0] if len(candidates) == 1 else None
        if len(candidates) > 0 and not definition:
            if user:
                is_numeric = user.is_numeric
                attributes = user.attributes
            elif pymathics:
                is_numeric = pymathics.is_numeric
                attributes = pymathics.attributes
            elif builtin:
                is_numeric = builtin.is_numeric
                attributes = builtin.attributes
            else:
                is_numeric = False
                attributes = A_NO_ATTRIBUTES

            options = {}
            formatvalues: Dict[str, list] = {
                "": [],
            }
            # Merge definitions
            its = list(candidates)
            while its:
                # This behaviour for options is wrong:
                # because of this, ``Unprotect[Expand]; ClearAll[Expand]; Options[Expand]``
                # returns the builtin options of ``Expand`` instead of an empty list, like
                # in WMA. This suggests that this idea of keeping different dicts for builtin
                # and user definitions is pointless.
                curr = its.pop()
                options.update(curr.options)
                for form, rules in curr.formatvalues.items():
                    if form in formatvalues:
                        formatvalues[form].extend(rules)
                    else:
                        formatvalues[form] = rules
            # Build the new definition
            definition = Definition(
                name=name,
                ownvalues=sum((c.ownvalues for c in candidates), []),
                downvalues=sum((c.downvalues for c in candidates), []),
                subvalues=sum((c.subvalues for c in candidates), []),
                upvalues=sum((c.upvalues for c in candidates), []),
                formatvalues=formatvalues,
                messages=sum((c.messages for c in candidates), []),
                attributes=attributes,
                options=options,
                nvalues=sum((c.nvalues for c in candidates), []),
                defaultvalues=sum((c.defaultvalues for c in candidates), []),
                builtin=builtin_instance,
                is_numeric=is_numeric,
            )

        if definition is None:
            if only_if_exists:
                raise KeyError

            definition = Definition(name=name)
            if name[-1] != "`":
                self.user[name] = definition
        else:
            self.proxy[strip_context(original_name)].add(original_name)
            self.definitions_cache[original_name] = definition
            self.lookup_cache[original_name] = name

        return definition

    def get_attributes(self, name: str) -> int:
        return self.get_definition(name).attributes

    def get_ownvalues(self, name: str) -> list:
        return self.get_definition(name).ownvalues

    def get_downvalues(self, name: str) -> list:
        return self.get_definition(name).downvalues

    def get_subvalues(self, name: str) -> list:
        return self.get_definition(name).subvalues

    def get_upvalues(self, name: str) -> list:
        return self.get_definition(name).upvalues

    def get_formats(self, name: str, format_name="") -> list:
        """
        Return a list of format rules associated with `name`.
        if `format_name` is given, looks to the rules associated
        to that format.
        """
        formats = self.get_definition(name).formatvalues
        result = formats.get(format_name, []) + formats.get("", [])
        result.sort()
        return result

    def get_nvalues(self, name: str):
        return self.get_definition(name).nvalues

    def get_defaultvalues(self, name: str):
        return self.get_definition(name).defaultvalues

    def get_value(self, name: str, pos: str, pattern, evaluation):
        assert isinstance(name, str)
        assert "`" in name
        rules = self.get_definition(name).get_values_list(valuesname(pos))
        for rule in rules:
            result = rule.apply(pattern, evaluation)
            if result is not None:
                return result
        return None

    def get_user_definition(self, name: str, create: bool = True) -> Definition:
        """
        Return a user definition for `name`. If `create` is `False`
        and a user definition is not available, raise a KeyError exception.

        Otherwise, tries to create a definition from a definition existing
        into the space of builtin definitions.

        Parameters
        ----------
        name : str
            The name of the requested symbol.
        create : bool, optional
            If `True` and the symbol does not have a definition, create it.
            Otherwise, raise a KeyError exception. The default is True.

        Raises
        ------
        KeyError

        Returns
        -------
        Optional[Definition]
            The definition of the symbol.

        """

        assert not isinstance(name, Symbol)

        existing = self.user.get(name)
        if existing:
            return existing

        if not create:
            raise KeyError(name)
        builtin = self.builtin.get(name)
        if builtin:
            attributes = builtin.attributes
            is_numeric = builtin.is_numeric
        else:
            attributes = A_NO_ATTRIBUTES
            is_numeric = False
        self.user[name] = Definition(
            name=name,
            attributes=attributes,
            is_numeric=is_numeric,
        )
        self.clear_cache(name)
        return self.user[name]

    def mark_changed(self, definition: Definition) -> None:
        self.now += 1
        definition.changed = self.now

    def reset_user_definition(self, name: str) -> None:
        assert not isinstance(name, Symbol)
        fullname = self.lookup_name(name)
        if fullname in self.user:
            del self.user[fullname]
        self.clear_cache(fullname)
        # TODO fix changed

    def add_user_definition(self, name: str, definition: Definition) -> None:
        assert not isinstance(name, Symbol)
        self.mark_changed(definition)
        fullname = self.lookup_name(name)
        self.user[fullname] = definition
        self.clear_cache(fullname)

    def set_attribute(self, name: str, attribute: int) -> None:
        definition = self.get_user_definition(self.lookup_name(name))
        if definition is not None:
            definition.attributes |= attribute
            self.mark_changed(definition)
        self.clear_definitions_cache(name)

    def set_attributes(self, name: str, attributes: int) -> None:
        definition = self.get_user_definition(self.lookup_name(name))
        if definition is not None:
            definition.attributes = attributes
            self.mark_changed(definition)
        self.clear_definitions_cache(name)

    def clear_attribute(self, name: str, attribute: int) -> None:
        definition = self.get_user_definition(self.lookup_name(name))
        if definition is not None:
            definition.attributes &= ~attribute
            self.mark_changed(definition)
        self.clear_definitions_cache(name)

    def add_rule(self, name: str, rule, position: Optional[str] = None):
        definition = self.get_user_definition(self.lookup_name(name))
        if position is None:
            result = definition.add_rule(rule)
        else:
            result = definition.add_rule_at(rule, position)
        self.mark_changed(definition)
        self.clear_definitions_cache(name)
        return result

    def add_format(self, name: str, rule, form_names: Union[str, list] = "") -> None:
        """Add a format rule"""
        definition = self.get_user_definition(self.lookup_name(name))
        forms = form_names if isinstance(form_names, (tuple, list)) else [form_names]
        if definition is not None:
            for form in forms:
                if form not in definition.formatvalues:
                    definition.formatvalues[form] = []
                insert_rule(definition.formatvalues[form], rule)
            self.mark_changed(definition)
        self.clear_definitions_cache(name)

    def add_nvalue(self, name: str, rule) -> None:
        definition = self.get_user_definition(self.lookup_name(name))
        if definition is not None:
            definition.add_rule_at(rule, "n")
            self.mark_changed(definition)
        self.clear_definitions_cache(name)

    def add_default(self, name: str, rule) -> None:
        definition = self.get_user_definition(self.lookup_name(name))
        if definition is not None:
            definition.add_rule_at(rule, "default")
            self.mark_changed(definition)
        self.clear_definitions_cache(name)

    def add_message(self, name: str, rule) -> None:
        definition = self.get_user_definition(self.lookup_name(name))
        if definition is not None:
            definition.add_rule_at(rule, "messages")
            self.mark_changed(definition)
        self.clear_definitions_cache(name)

    def set_values(self, name: str, values, rules) -> None:
        pos = valuesname(values)
        definition = self.get_user_definition(self.lookup_name(name))
        if definition is not None:
            definition.set_values_list(pos, rules)
            self.mark_changed(definition)
        self.clear_definitions_cache(name)

    def get_options(self, name):
        return self.get_definition(self.lookup_name(name)).options

    def reset_user_definitions(self) -> None:
        self.user = {}
        self.clear_cache()
        # TODO changed

    def get_user_definitions(self):
        return base64.encodebytes(pickle.dumps(self.user, protocol=2)).decode("ascii")

    def set_user_definitions(self, definitions) -> None:
        if definitions:
            self.user = pickle.loads(base64.decodebytes(definitions.encode("ascii")))
        else:
            self.user = {}
        self.clear_cache()

    def get_ownvalue(self, name: str):
        ownvalues = self.get_definition(self.lookup_name(name)).ownvalues
        if ownvalues:
            return ownvalues[0]
        return None

    def set_ownvalue(self, name: str, value) -> None:
        """Set an ownvalue for name"""
        name = self.lookup_name(name)
        self.add_rule(name, Rule(Symbol(name), value))
        self.clear_cache(name)

    def set_options(self, name: str, options) -> None:
        definition = self.get_user_definition(self.lookup_name(name))
        if definition is not None:
            definition.options = options
            self.mark_changed(definition)
        self.clear_definitions_cache(name)

    def unset(self, name: str, expr):
        definition = self.get_user_definition(self.lookup_name(name))
        result = definition.remove_rule(expr)
        self.mark_changed(definition)
        self.clear_definitions_cache(name)
        return result

    def get_config_value(
        self, name: str, default: Optional[int] = None
    ) -> Optional[int]:
        "Infinity -> None, otherwise returns integer."
        value = self.get_definition(name).ownvalues
        if value:
            try:
                value = value[0].replace
            except AttributeError:
                return None
            if value.get_name() == "System`Infinity" or value.has_form(
                "DirectedInfinity", 1
            ):
                return None

            return int(value.get_int_value())

        return default

    def set_config_value(self, name: str, new_value: int) -> None:
        """Set the (own)value of an integer variable"""
        self.set_ownvalue(name, Integer(new_value))

    def set_line_no(self, line_no: int) -> None:
        self.set_config_value("$Line", line_no)

    def get_line_no(self):
        return self.get_config_value("$Line", 0)

    def increment_line_no(self, increment: int = 1) -> None:
        self.set_config_value("$Line", self.get_line_no() + increment)

    def get_history_length(self):
        history_length = self.get_config_value("$HistoryLength", 100)
        if history_length is None or history_length > 100:
            history_length = 100
        return history_length


def get_tag_position(pattern, name: str) -> Optional[str]:
    """
    Determine the position of a pattern in
    the definition of the symbol ``name``
    """
    blanks = (
        "System`Blank",
        "System`BlankSequence",
        "System`BlankNullSequence",
    )

    def strip_pattern_name_and_condition(pat) -> BasePattern:
        """
        In ``Pattern[name_, pattern_]`` and
        ``Condition[pattern_, cond_]``
        the tag is determined by pat.
        This function strips it to ensure that
        ``pat`` does not have that form.
        """

        # Is "pat" as ExpressionPattern or an AtomPattern?
        # Note: the below test could also be on ExpressionPattern or
        # AtomPattern, but using hasattr is more flexible if more
        # kinds of patterns are added.
        if not hasattr(pat, "head"):
            return pat

        if hasattr(pat, "elements"):
            # We have to use get_head_name() below because
            # pat can either SymbolCondition or <AtomPattern: System`Condition>.
            # In the latter case, comparing to SymbolCondition is not sufficient.
            if pat.get_head_name() == "System`Condition":
                if len(pat.elements) > 1:
                    return strip_pattern_name_and_condition(pat.elements[0])
            # The same kind of get_head_name() check is needed here as well and
            # is not the same as testing against SymbolPattern.
            if pat.get_head_name() == "System`Pattern":
                if len(pat.elements) == 2:
                    return strip_pattern_name_and_condition(pat.elements[1])

        return pat

    def is_pattern_a_kind_of(pattern: ExpressionPattern, pattern_name: str) -> bool:
        """
        Returns `True` if `pattern` or any of its alternates is a
        pattern with name `pattern_name` and `False` otherwise."""

        if pattern_name == pattern.get_lookup_name():
            return True

        # Try again after stripping Pattern and Condition wrappers:
        head = strip_pattern_name_and_condition(pattern.get_head())
        head_name = head.get_lookup_name()
        if pattern_name == head_name:
            return True

        # The head is of the form ``_SymbolName|__SymbolName|___SymbolName``
        # If name matches with SymbolName, then it is a kind of:
        if head_name in blanks:
            if isinstance(head, Symbol):
                return False
            assert hasattr(head, "elements")
            sub_elements = head.elements
            if len(sub_elements) == 1:
                head_name = head.elements[0].get_name()
                if head_name == pattern_name:
                    return True
        return False

    # If pattern is a Symbol, and coincides with
    # name, it is an ownvalue:

    if pattern.get_name() == name:
        return "own"
    # If pattern is an ``Atom``, does not have
    # a position
    if isinstance(pattern, Atom):
        return None

    # The pattern is an Expression.
    head_name = pattern.get_head_name()
    # If the name is the head name, is a downvalue:
    if head_name == name:
        return "down"

    # Handle special cases
    if head_name == "System`N":
        if len(pattern.elements) == 2:
            return "n"

    # The pattern has the form `_SymbolName | __SymbolName | ___SymbolName`
    # Then it only can be a downvalue
    if head_name in blanks:
        elements = pattern.elements
        if len(elements) == 1:
            head_name = elements[0].get_name()
            return "down" if head_name == name else None

    # TODO: Consider process format_values

    if head_name != "":
        # Check
        strip_pattern = strip_pattern_name_and_condition(pattern)
        if strip_pattern is not pattern:
            return get_tag_position(strip_pattern, name)

    # The head is not a symbol. Is pattern is "name" kind of pattern?
    if is_pattern_a_kind_of(pattern, name):
        return "sub"

    # If we are here, pattern is not an Ownvalue, DownValue, SubValue or NValue
    # Let's check the elements for UpValues
    for element in pattern.elements:
        lookup_name = element.get_lookup_name()
        if lookup_name == name:
            return "up"

        # Strip Pattern and Condition wrappers and check again
        if lookup_name in (
            "System`Condition",
            "System`Pattern",
        ):
            element = strip_pattern_name_and_condition(element)
            lookup_name = element.get_lookup_name()
            if lookup_name == name:
                return "up"
        # Check if one of the elements is not a "Blank"

        if element.get_head_name() in blanks:
            sub_elements = element.elements
            if len(sub_elements) == 1:
                if sub_elements[0].get_name() == name:
                    return "up"
    # ``pattern`` does not have a tag position in the Definition
    return None


def insert_rule(values, rule) -> None:
    for index, existing in enumerate(values):
        if existing.pattern.sameQ(rule.pattern):
            del values[index]
            break
    # use insort_left to guarantee that if equal rules exist, newer rules will
    # get higher precedence by being inserted before them. see DownValues[].
    bisect.insort_left(values, rule)
