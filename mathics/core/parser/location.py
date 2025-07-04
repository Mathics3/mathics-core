"""
Provides location tracking in parser.
"""

from typing import Callable, Optional

import mathics_scanner
from mathics_scanner.location import (
    EVAL_METHODS,
    ContainerKind,
    SourceRange,
    SourceRange2,
)

from mathics.core.parser.ast import Node


def track_location(func: Callable) -> Callable:
    """Python decorator for a parse method that adds location tracking
    on non-leaf-nodes when TRACK_LOCATION is set. Otherwise, we just
    run the parse method.

    """

    def wrapper(self, *args) -> Optional[Node]:
        if not mathics_scanner.location.TRACK_LOCATIONS:
            return func(self, *args)

        # Save location information
        # For expressions which make their way to
        # FunctionApplyRule, saving a position here is
        # extraneous because the FunctionApplyRule is
        # the position.  But deal with this redundancy
        # after the dust settles, and we have experience
        # on what is desired.
        start_column = self.tokeniser.pos
        start_line = self.feeder.lineno
        parsed_node = func(self, *args)

        if parsed_node is not None and hasattr(parsed_node, "location"):
            if self.feeder.container_kind == ContainerKind.PYTHON:
                parsed_node.location = self.feeder.container
                if self.feeder.container not in EVAL_METHODS:
                    EVAL_METHODS.add(parsed_node.location)
            else:
                end_pos = self.tokeniser.pos
                end_line = self.feeder.lineno
                if start_line == end_line:
                    parsed_node.location = SourceRange2(
                        start_line=start_line,
                        start_pos=start_column,
                        end_pos=end_pos,
                        container=self.feeder.container_index,
                    )
                else:
                    parsed_node.location = SourceRange(
                        start_line=start_line,
                        start_pos=start_column,
                        end_line=end_line,
                        end_pos=end_pos,
                        container=self.feeder.container_index,
                    )

        return parsed_node

    return wrapper


def track_token_location(func: Callable) -> Callable:
    """Python decorator for a parse method that adds location
    tracking to leaf-nodes, i.e. tokens. This happens though only TRACK_LOCATION is set. Otherwise, we just run the
    normal parse method.

    """

    def wrapper(self, token) -> Optional[Node]:
        if not mathics_scanner.location.TRACK_LOCATIONS:
            return func(self, token)

        # Save location information
        # For expressions which make their way to
        # FunctionApplyRule, saving a position here is
        # extraneous because the FunctionApplyRule is
        # the position.  But deal with this redundancy
        # after the dust settles, and we have experience
        # on what is desired.
        start_column = token.pos
        start_line = self.feeder.lineno
        parsed_node = func(self, token)

        if (
            self.feeder.container_kind == ContainerKind.PYTHON
            and self.feeder.container not in EVAL_METHODS
        ):
            location = self.feeder.container
            EVAL_METHODS.add(location)

        end_line = self.feeder.lineno
        if start_line == end_line:
            parsed_node.location = SourceRange2(
                start_line=start_line,
                start_pos=start_column,
                end_pos=start_column + len(token.text) - 1,
                container=self.feeder.container_index,
            )
        else:
            parsed_node.location = SourceRange(
                start_line=start_line,
                start_pos=start_column,
                end_line=self.feeder.lineno,
                end_pos=start_column + len(token.text) - 1,
                container=self.feeder.container_index,
            )
        return parsed_node

    return wrapper
