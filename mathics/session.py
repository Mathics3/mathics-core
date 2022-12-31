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

import mathics.settings
from mathics.core.definitions import Definitions, autoload_files
from mathics.core.evaluation import Evaluation
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
    """Get a Mathics Settings` value with name "setting_name" from definitions. If setting_name is not defined return None"""
    settings_value = definitions.get_ownvalue(setting_name)
    if settings_value is None:
        return None
    return settings_value.replace.to_python(string_quotes=False)


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
        character_encoding=Optional[str],
    ):
        if character_encoding is not None:
            mathics.settings.SYSTEM_CHARACTER_ENCODING = character_encoding
        self.form = form
        self.reset(add_builtin, catch_interrupt)

    def reset(self, add_builtin=True, catch_interrupt=False):
        """
        reset the definitions and the evaluation objects.
        """
        self.definitions = Definitions(add_builtin)
        self.evaluation = Evaluation(
            definitions=self.definitions, catch_interrupt=catch_interrupt
        )
        self.last_result = None

    def evaluate(self, str_expression, timeout=None, form=None):
        self.evaluation.out.clear()
        expr = parse(self.definitions, MathicsSingleLineFeeder(str_expression))
        if form is None:
            form = self.form
        self.last_result = expr.evaluate(self.evaluation)
        return self.last_result

    def format_result(self, str_expression=None, timeout=None, form=None):
        if str_expression:
            self.evaluate(str_expression, timeout=None, form=None)

        res = self.last_result
        if form is None:
            form = self.form
        return res.do_format(self.evaluation, form)
