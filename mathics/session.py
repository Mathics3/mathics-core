# -*- coding: utf-8 -*-
"""
This module contains routines to simplify front-end use.

In particular we provide:

* a class to create a Mathics session,
* load the Mathics core settings files (written in  WL),
* read and set Mathics Settings.
"""

import os.path as osp
from typing import Optional

from mathics.core.definitions import Definitions, autoload_files
from mathics.core.evaluation import Evaluation, Result
from mathics.core.parser import MathicsSingleLineFeeder, parse


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
        self.reset(add_builtin, catch_interrupt)

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
        expr = parse(self.definitions, MathicsSingleLineFeeder(str_expression))
        if form is None:
            form = self.form
        self.last_result = expr.evaluate(self.evaluation)
        return self.last_result

    def evaluate_as_in_cli(self, str_expression, timeout=None, form=None, src_name=""):
        """This method parse and evaluate the expression using the session.evaluation.evaluate method"""
        self.evaluation.out = []
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
