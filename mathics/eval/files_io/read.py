"""
Functions to support Read[]
"""

import io
from typing import Callable, Optional, Tuple

from mathics.builtin.atomic.strings import to_python_encoding
from mathics.core.atoms import Integer, String
from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import MessageException
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.streams import Stream, path_search, stream_manager
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import (
    SymbolEndOfFile,
    SymbolFailed,
    SymbolHoldExpression,
    SymbolInputStream,
    SymbolOutputStream,
    SymbolReal,
)

# TODO: Improve docs for these Read[] arguments.


READ_TYPES = [
    Symbol(k)
    for k in [
        "Byte",
        "Character",
        "Expression",
        "Number",
        "Record",
        "String",
        "Word",
    ]
] + [SymbolHoldExpression, SymbolReal]


class MathicsOpen(Stream):
    """
    Context manager for reading files.

    Use like this::

        with MathicsOpen(path, "r") as f:
            # read from f
            ...

    The ``file``, ``mode``, and ``encoding`` fields are the same as those
    in the Python builtin ``open()`` function.
    """

    def __init__(
        self,
        path: str,
        mode: str = "r",
        name=None,
        encoding=None,
        is_temporary_file: bool = False,
    ):
        if encoding is not None:
            encoding = to_python_encoding(encoding)
            if "b" in mode:
                # We should not specify an encoding for a binary mode
                encoding = None
            elif encoding is None:
                raise MessageException("General", "charcode", self.encoding)
        self.encoding = encoding
        if name is None:
            name = path
        super().__init__(name, mode=mode, path=path, encoding=self.encoding)
        self.is_temporary_file = is_temporary_file

        # The following are set in __enter__ and __exit__
        self.old_inputfile_var = None
        self.stream = None
        self.fp = None

    def __enter__(self, is_temporary_file=False):
        # find path
        path, _ = path_search(self.name)
        if path is None and self.mode in ["w", "a", "wb", "ab"]:
            path = self.name
        if path is None:
            raise IOError(self.name)

        # Open the file
        self.fp = io.open(path, self.mode, encoding=self.encoding)

        # Add to our internal list of streams
        self.stream = stream_manager.add(
            name=self.name,
            mode=self.mode,
            path=path,
            encoding=self.encoding,
            io=self.fp,
            num=stream_manager.next,
            is_temporary_file=is_temporary_file,
        )

        # return a handle ot the openend file
        return self.fp

    def __exit__(self, type, value, traceback):
        if self.fp is not None:
            self.fp.close()
        if self.stream is not None:
            stream_manager.delete_stream(self.stream)
        super().__exit__(type, value, traceback)


def channel_to_stream(channel, mode="r"):
    if isinstance(channel, String):
        name = channel.get_string_value()
        opener = MathicsOpen(name, mode)
        opener.__enter__()
        n = opener.n
        if mode in ["r", "rb"]:
            head = SymbolInputStream
        elif mode in ["w", "a", "wb", "ab"]:
            head = SymbolOutputStream
        else:
            raise ValueError(f"Unknown format {mode}")
        return Expression(head, channel, Integer(n))
    elif channel.has_form("InputStream", 2):
        return channel
    elif channel.has_form("OutputStream", 2):
        return channel
    else:
        return None


def parse_read_options(options) -> dict:
    """
    Parses and checks Read[] or ReadList[] options
    """
    # Options
    # TODO Proper error messages

    result = {}
    keys = list(options.keys())

    # AnchoredSearch
    if "System`AnchoredSearch" in keys:
        anchored_search = options["System`AnchoredSearch"].to_python(
            string_quotes=False
        )
        assert anchored_search in [True, False]
        result["AnchoredSearch"] = anchored_search

    # IgnoreCase
    if "System`IgnoreCase" in keys:
        ignore_case = options["System`IgnoreCase"].to_python(string_quotes=False)
        assert ignore_case in [True, False]
        result["IgnoreCase"] = ignore_case

    # WordSearch
    if "System`WordSearch" in keys:
        word_search = options["System`WordSearch"].to_python(string_quotes=False)
        assert word_search in [True, False]
        result["WordSearch"] = word_search

    # RecordSeparators
    if "System`RecordSeparators" in keys:
        record_separators = options["System`RecordSeparators"].to_python(
            string_quotes=False
        )
        assert isinstance(record_separators, list)
        # assert all(
        #     isinstance(s, str) and s[0] == s[-1] == '"' for s in record_separators
        # )
        record_separators = [s[1:-1] for s in record_separators]
        result["RecordSeparators"] = record_separators

    # WordSeparators
    if "System`WordSeparators" in keys:
        word_separators = options["System`WordSeparators"].to_python(
            string_quotes=False
        )
        assert isinstance(word_separators, list)
        result["WordSeparators"] = word_separators

    # NullRecords
    if "System`NullRecords" in keys:
        null_records = options["System`NullRecords"].to_python(string_quotes=False)
        assert null_records in [True, False]
        result["NullRecords"] = null_records

    # NullWords
    if "System`NullWords" in keys:
        null_words = options["System`NullWords"].to_python(string_quotes=False)
        assert null_words in [True, False]
        result["NullWords"] = null_words

    # TokenWords
    if "System`TokenWords" in keys:
        token_words = options["System`TokenWords"].to_python(string_quotes=False)
        result["TokenWords"] = token_words

    return result


def close_stream(stream: Stream, stream_number: int):
    """
    Close stream: `stream` and delete it from the list of streams we manage.
    If the stream was to a temporary file, remove the temporary file.
    """
    if stream.io is not None:
        stream.io.close()
    stream_manager.delete(stream_number)


def read_name_and_stream(stream_designator, evaluation: Evaluation) -> tuple:
    if stream_designator.has_form("OutputStream", 2):
        evaluation.message("General", "openw", stream_designator)
        return None, None, None

    try:
        strm = channel_to_stream(stream_designator, "r")

        if strm is None:
            return None, None, None

        stream_name, n = strm.elements

        if not isinstance(n, Integer) or (n_int := n.value) < 0:
            evaluation.message("InputStream", "intpm", strm)
            return None, None, None

        stream = stream_manager.lookup_stream(n_int)
        if stream is None:
            evaluation.message("Read", "openx", strm)
            return SymbolFailed, None, None

        if stream.io is None:
            stream.__enter__()

        elif stream.io.closed:
            evaluation.message("Read", "openx", strm)
            return SymbolFailed, None, None

        stream_name_str = stream_name.to_python()
        return stream_name_str, n, stream

    except IOError as e:
        evaluation.message("Read", "noopen", str(e))
        return SymbolFailed, None, None


def read_list_from_types(read_types):
    """Return a Mathics List from a list of read_type names or a single read_type"""

    # Trun read_types into a list if it isn't already one.
    if read_types.has_form("List", None):
        read_types = read_types._elements
    else:
        read_types = (read_types,)

    # TODO: look for a better implementation handling "Hold[Expression]".
    #
    read_types = (
        (
            SymbolHoldExpression
            if (
                typ.get_head_name() == "System`Hold"
                and typ.elements[0].get_name() == "System`Expression"
            )
            else typ
        )
        for typ in read_types
    )

    return ListExpression(*read_types)


def read_check_options(options: dict, evaluation: Evaluation) -> Optional[dict]:
    # Options
    # TODO Proper error messages

    result = {}
    keys = list(options.keys())

    # AnchoredSearch
    if "System`AnchoredSearch" in keys:
        anchored_search = options["System`AnchoredSearch"].to_python(
            string_quotes=False
        )
        assert anchored_search in [True, False]
        result["AnchoredSearch"] = anchored_search

    # IgnoreCase
    if "System`IgnoreCase" in keys:
        ignore_case = options["System`IgnoreCase"].to_python(string_quotes=False)
        assert ignore_case in [True, False]
        result["IgnoreCase"] = ignore_case

    # WordSearch
    if "System`WordSearch" in keys:
        word_search = options["System`WordSearch"].to_python(string_quotes=False)
        assert word_search in [True, False]
        result["WordSearch"] = word_search

    # RecordSeparators
    if "System`RecordSeparators" in keys:
        record_separators = options["System`RecordSeparators"].to_python(
            string_quotes=False
        )
        assert isinstance(record_separators, list)
        result["RecordSeparators"] = record_separators

    # WordSeparators
    if "System`WordSeparators" in keys:
        word_separators = options["System`WordSeparators"].to_python(
            string_quotes=False
        )
        assert isinstance(word_separators, list)
        result["WordSeparators"] = word_separators

    # NullRecords
    if "System`NullRecords" in keys:
        null_records = options["System`NullRecords"].to_python(string_quotes=False)
        assert null_records in [True, False]
        result["NullRecords"] = null_records

    # NullWords
    if "System`NullWords" in keys:
        null_words = options["System`NullWords"].to_python()
        assert null_words in [True, False]
        result["NullWords"] = null_words

    # TokenWords
    if "System`TokenWords" in keys:
        token_words = options["System`TokenWords"].to_python(string_quotes=False)
        if not (isinstance(token_words, list) or isinstance(token_words, String)):
            evaluation.message("ReadList", "opstl", token_words)
            return None
        result["TokenWords"] = token_words

    return result


def read_get_separators(
    options, evaluation: Evaluation
) -> Optional[Tuple[dict, dict, dict]]:
    """Get record and word separators from apply "options"."""
    # Options
    # TODO Implement extra options
    py_options = read_check_options(options, evaluation)
    if py_options is None:
        return None
    # null_records = py_options['NullRecords']
    # null_words = py_options['NullWords']
    record_separators = py_options["RecordSeparators"]
    token_words = py_options.get("TokenWords", {})
    word_separators = py_options["WordSeparators"]

    return record_separators, token_words, word_separators


def read_from_stream(
    stream, word_separators: list, token_words: list, msgfn: Callable, accepted=None
):
    """
    This is a generator that returns "words" from stream deliminated by
    "word_separators" or "token_words".
    """
    while True:
        word = ""
        some_token_word_prefix = ""
        while True:
            try:
                tmp = stream.io.read(1)
            except UnicodeDecodeError:
                tmp = " "  # ignore
                msgfn("General", "ucdec")
            except EOFError:
                return SymbolEndOfFile

            if tmp == "":
                if word == "":
                    pos = stream.io.tell()
                    newchar = stream.io.read(1)
                    if pos == stream.io.tell():
                        raise EOFError
                    else:
                        if newchar:
                            word = newchar
                            continue
                        else:
                            yield word
                            continue
                yield word
                break

            if tmp in word_separators:
                if word == "":
                    continue
                if stream.io.seekable():
                    stream.io.seek(stream.io.tell() - 1)
                word += some_token_word_prefix
                some_token_word_prefix = ""
                yield word
                break

            if accepted is not None and tmp not in accepted:
                word += some_token_word_prefix
                some_token_word_prefix = ""
                yield word
                break

            some_token_word_prefix += tmp
            for token_word in token_words:
                if token_word == some_token_word_prefix:
                    if word:
                        yield [word, token_word]
                    else:
                        yield token_word
                    some_token_word_prefix = ""
                    break
            else:
                word += some_token_word_prefix
                some_token_word_prefix = ""
