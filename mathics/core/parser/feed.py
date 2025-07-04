# -*- coding: utf-8 -*-
from typing import List

from mathics_scanner import (
    FileLineFeeder,
    LineFeeder,
    MultiLineFeeder,
    SingleLineFeeder,
)


class MathicsLineFeeder(LineFeeder):
    messages: List[str]

    def send_messages(self, evaluation) -> list:
        evaluated_messages = []
        for message in self.messages:
            evaluated_messages.append(evaluation.message(*message))
        self.messages = []
        return evaluated_messages


class MathicsSingleLineFeeder(SingleLineFeeder, MathicsLineFeeder):
    "A feeder that feeds lines from an open location container object"


class MathicsFileLineFeeder(FileLineFeeder, MathicsLineFeeder):
    "A feeder that feeds lines from an open ``File`` object"


class MathicsMultiLineFeeder(MultiLineFeeder, MathicsLineFeeder):
    "A feeder that feeds lines from an open contianer object"
