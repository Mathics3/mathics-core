# -*- coding: utf-8 -*-
"""
This module contains routines to simplify front-end use.

In particular we provide:

* a class to create a Mathics session,
* load the Mathics core settings files (written in  WL),
* read and set Mathics Settings.
"""

import os
import os.path as osp
from os.path import join as osp_join
from typing import Optional

from mathics_scanner.location import ContainerKind

from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation, Result
from mathics.core.parser import MathicsSingleLineFeeder, parse
from mathics.core.symbols import SymbolNull


def autoload_files(
    defs: Definitions,
    root_dir_path: str,
    autoload_dir: str,
    block_global_definitions: bool = True,
):
    """
    Load Mathics code from the autoload-folder files.
    """
    from mathics.eval.files_io.files import eval_Get

    for root, _, files in os.walk(osp_join(root_dir_path, autoload_dir)):
        for path in [osp_join(root, f) for f in files if f.endswith(".m")]:
            # Autoload definitions should be go in the System context
            # by default, rather than the Global context.
            defs.set_current_context("System`")
            eval_Get(path, Evaluation(defs))
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
                raise ValueError(f"autoload defined {name}.")

    # Move the user definitions to builtin:
    for symbol_name in defs.user:
        defs.builtin[symbol_name] = defs.get_definition(symbol_name)

    defs.user = {}
    defs.clear_cache()


def load_default_settings_files(
    definitions: Definitions, load_cli_settings: bool = True
):
    """
    Loads the system default settings for Mathics core.

    Other settings files may get loaded later and override these
    defaults.
    """
    root_dir = osp.realpath(osp.dirname(__file__))

    autoload_files(definitions, root_dir, "autoload", False)
    if load_cli_settings:
        autoload_files(definitions, root_dir, "autoload-cli", False)


def get_settings_value(definitions: Definitions, setting_name: str):
    """Get a Mathics Settings` value with name "setting_name" from
    definitions. If setting_name is not defined return None.
    """
    try:
        settings_value = definitions.get_ownvalue(setting_name)
    except ValueError:
        return None
    return settings_value.to_python(string_quotes=False)


def set_settings_value(definitions: Definitions, setting_name: str, value):
    """Set a Mathics Settings` with name "setting_name" from definitions to value
    "value".
    """
    return definitions.set_ownvalue(setting_name, value)


class MathicsSession:
    """A session stores definitions or evaluation results.  This class
    also simplifies the common activity of reading as string, parsing
    it and evaluating it in the context of the current session.
    """

    def __init__(
        self,
        add_builtin=True,
        catch_interrupt=False,
        form="InputForm",
        character_encoding: Optional[str] = None,
    ):
        # FIXME: This import is needed because
        # the first time we call self.reset,
        # the formats must be already loaded.
        # The need of importing this module here seems
        # to be related to an issue in the modularity design.
        import mathics.format

        if character_encoding is not None:
            mathics.settings.SYSTEM_CHARACTER_ENCODING = character_encoding
        self.form = form
        self.last_result = None
        self.reset(add_builtin, catch_interrupt)
        self.shell = None

    def reset(self, add_builtin=True, catch_interrupt=False):
        """
        reset the definitions and the evaluation objects.
        """
        try:
            self.definitions = Definitions(add_builtin)
        except KeyError:
            from mathics.core.load_builtin import import_and_load_builtins

            import_and_load_builtins()
            self.definitions = Definitions(add_builtin)

        self.evaluation = Evaluation(
            definitions=self.definitions, catch_interrupt=catch_interrupt
        )
        self.last_result = None

    def evaluate(self, str_expression, timeout=None, form=None):
        """Parse str_expression and evaluate using the `evaluate` method of the Expression"""
        self.evaluation.out.clear()
        self.evaluation.iteration_count = 0
        expr = parse(
            self.definitions,
            MathicsSingleLineFeeder(str_expression, ContainerKind.STREAM),
        )
        if form is None:
            form = self.form
        self.last_result = expr.evaluate(self.evaluation) if expr else SymbolNull
        return self.last_result

    def evaluate_as_in_cli(self, str_expression, timeout=None, form=None, src_name=""):
        """This method parse and evaluate the expression using the session.evaluation.evaluate method"""
        self.evaluation.out = []
        self.evaluation.iteration_count = 0
        query = self.evaluation.parse(str_expression, src_name)
        if query is not None:
            res = self.evaluation.evaluate(query, timeout=timeout, format=form)
        else:
            res = Result(
                self.evaluation.out,
                None,
                self.evaluation.definitions.get_line_no(),
                None,
                form,
            )
            self.evaluation.out = []
        self.evaluation.stopped = False
        return res

    def format_result(self, str_expression=None, timeout=None, form=None):
        if str_expression:
            self.evaluate(str_expression, timeout=None, form=None)

        res = self.last_result
        if form is None:
            form = self.form
        return res.do_format(self.evaluation, form)

    def parse(self, str_expression, src_name=""):
        """
        Just parse the expression
        """
        return parse(
            self.definitions, MathicsSingleLineFeeder(str_expression, src_name)
        )
