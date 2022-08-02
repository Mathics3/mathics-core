# -*- coding: utf-8 -*-

"""
Operations on Strings
"""

import hashlib
import re
import zlib


from mathics.algorithm.parts import python_seq, convert_seq


from mathics.builtin.atomic.strings import (
    _StringFind,
    _evaluate_match,
    _parallel_match,
    mathics_split,
    to_regex,
)
from mathics.builtin.box.inout import _BoxedString

from mathics.builtin.base import (
    BinaryOperator,
    Builtin,
)

from mathics.core.atoms import (
    ByteArrayAtom,
    Integer,
    Integer1,
    String,
)
from mathics.core.attributes import (
    flat,
    listable,
    one_identity,
    protected,
    read_protected,
)
from mathics.core.convert.python import from_python
from mathics.core.expression import Expression, string_list
from mathics.core.formatter import format_element
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    Symbol,
    SymbolFalse,
    SymbolList,
    SymbolTrue,
)
from mathics.core.systemsymbols import (
    SymbolAll,
    SymbolByteArray,
    SymbolDirectedInfinity,
    SymbolFullForm,
    SymbolOutputForm,
)


SymbolStringInsert = Symbol("StringInsert")
SymbolStringJoin = Symbol("StringJoin")
SymbolStringPosition = Symbol("StringPosition")
SymbolStringRiffle = Symbol("StringRiffle")
SymbolStringSplit = Symbol("StringSplit")


class _ZLibHash:  # make zlib hashes behave as if they were from hashlib
    def __init__(self, fn):
        self._bytes = b""
        self._fn = fn

    def update(self, bytes):
        self._bytes += bytes

    def hexdigest(self):
        return format(self._fn(self._bytes), "x")


class Hash(Builtin):
    """
    <dl>
      <dt>'Hash[$expr$]'
      <dd>returns an integer hash for the given $expr$.

      <dt>'Hash[$expr$, $type$]'
      <dd>returns an integer hash of the specified $type$ for the given $expr$.
      <dd>The types supported are "MD5", "Adler32", "CRC32", "SHA", "SHA224", "SHA256", "SHA384", and "SHA512".

      <dt>'Hash[$expr$, $type$, $format$]'
      <dd>Returns the hash in the specified format.
    </dl>

    > Hash["The Adventures of Huckleberry Finn"]
    = 213425047836523694663619736686226550816

    > Hash["The Adventures of Huckleberry Finn", "SHA256"]
    = 95092649594590384288057183408609254918934351811669818342876362244564858646638

    > Hash[1/3]
    = 56073172797010645108327809727054836008

    > Hash[{a, b, {c, {d, e, f}}}]
    = 135682164776235407777080772547528225284

    > Hash[SomeHead[3.1415]]
    = 58042316473471877315442015469706095084

    >> Hash[{a, b, c}, "xyzstr"]
     = Hash[{a, b, c}, xyzstr, Integer]
    """

    attributes = protected | read_protected

    rules = {
        "Hash[expr_]": 'Hash[expr, "MD5", "Integer"]',
        "Hash[expr_, type_String]": 'Hash[expr, type, "Integer"]',
    }

    summary_text = "compute hash codes for a string"

    # FIXME md2
    _supported_hashes = {
        "Adler32": lambda: _ZLibHash(zlib.adler32),
        "CRC32": lambda: _ZLibHash(zlib.crc32),
        "MD5": hashlib.md5,
        "SHA": hashlib.sha1,
        "SHA224": hashlib.sha224,
        "SHA256": hashlib.sha256,
        "SHA384": hashlib.sha384,
        "SHA512": hashlib.sha512,
    }

    @staticmethod
    def compute(user_hash, py_hashtype, py_format):
        hash_func = Hash._supported_hashes.get(py_hashtype)
        if hash_func is None:  # unknown hash function?
            return  # in order to return original Expression
        h = hash_func()
        user_hash(h.update)
        res = h.hexdigest()
        if py_format in ("HexString", "HexStringLittleEndian"):
            return String(res)
        res = int(res, 16)
        if py_format == "DecimalString":
            return String(str(res))
        elif py_format == "ByteArray":
            return Expression(SymbolByteArray, ByteArrayAtom(res))
        return Integer(res)

    def apply(self, expr, hashtype, outformat, evaluation):
        "Hash[expr_, hashtype_String, outformat_String]"
        return Hash.compute(
            expr.user_hash, hashtype.get_string_value(), outformat.get_string_value()
        )


class StringDrop(Builtin):
    """
    <dl>
      <dt>'StringDrop["$string$", $n$]'
      <dd>gives $string$ with the first $n$ characters dropped.

      <dt>'StringDrop["$string$", -$n$]'
      <dd>gives $string$ with the last $n$ characters dropped.

      <dt>'StringDrop["$string$", {$n$}]'
      <dd>gives $string$ with the $n$th character dropped.

      <dt>'StringDrop["$string$", {$m$, $n$}]'
      <dd>gives $string$ with the characters $m$ through $n$ dropped.
    </dl>

    >> StringDrop["abcde", 2]
    = cde
    >> StringDrop["abcde", -2]
    = abc
    >> StringDrop["abcde", {2}]
    = acde
    >> StringDrop["abcde", {2,3}]
    = ade
    >> StringDrop["abcd",{3,2}]
    = abcd
    >> StringDrop["abcd",0]
    = abcd
    """

    messages = {
        "strse": "String expected at position 1.",
        "mseqs": "Integer or list of two Integers are expected at position 2.",
        "drop": 'Cannot drop positions `1` through `2` in "`3`".',
    }

    summary_text = "drop a part of a string"

    def apply_with_n(self, string, n, evaluation):
        "StringDrop[string_,n_Integer]"
        if not isinstance(string, (String, _BoxedString)):
            return evaluation.message("StringDrop", "strse")
        if isinstance(n, Integer):
            pos = n.value
            if pos > len(string.get_string_value()):
                return evaluation.message("StringDrop", "drop", 1, pos, string)
            if pos < -len(string.get_string_value()):
                return evaluation.message("StringDrop", "drop", pos, -1, string)
            if pos > 0:
                return String(string.get_string_value()[pos:])
            if pos < 0:
                return String(string.get_string_value()[:(pos)])
            if pos == 0:
                return string
        return evaluation.message("StringDrop", "mseqs")

    def apply_with_ni_nf(self, string, ni, nf, evaluation):
        "StringDrop[string_,{ni_Integer,nf_Integer}]"
        if not isinstance(string, (String, _BoxedString)):
            return evaluation.message("StringDrop", "strse", string)

        if ni.value == 0 or nf.value == 0:
            return evaluation.message("StringDrop", "drop", ni, nf)
        fullstring = string.get_string_value()
        lenfullstring = len(fullstring)
        posi = ni.value
        if posi < 0:
            posi = lenfullstring + posi + 1
        posf = nf.value
        if posf < 0:
            posf = lenfullstring + posf + 1
        if posf > lenfullstring or posi > lenfullstring or posf <= 0 or posi <= 0:
            # positions out or range
            return evaluation.message("StringDrop", "drop", ni, nf, fullstring)
        if posf < posi:
            return string  # this is what actually mma does
        return String(fullstring[: (posi - 1)] + fullstring[posf:])

    def apply_with_ni(self, string, ni, evaluation):
        "StringDrop[string_,{ni_Integer}]"
        if not isinstance(string, (String, _BoxedString)):
            return evaluation.message("StringDrop", "strse", string)
        if ni.value == 0:
            return evaluation.message("StringDrop", "drop", ni, ni)
        fullstring = string.get_string_value()
        lenfullstring = len(fullstring)
        posi = ni.value
        if posi < 0:
            posi = lenfullstring + posi + 1
        if posi > lenfullstring or posi <= 0:
            return evaluation.message("StringDrop", "drop", ni, ni, fullstring)
        return String(fullstring[: (posi - 1)] + fullstring[posi:])

    def apply(self, string, something, evaluation):
        "StringDrop[string_,something___]"
        if not isinstance(string, (String, _BoxedString)):
            return evaluation.message("StringDrop", "strse")
        return evaluation.message("StringDrop", "mseqs")


class StringInsert(Builtin):
    """
    <dl>
      <dt>'StringInsert["$string$", "$snew$", $n$]'
      <dd>yields a string with $snew$ inserted starting at position $n$ in $string$.

      <dt>'StringInsert["$string$", "$snew$", -$n$]'
      <dd>inserts a at position $n$ from the end of "$string$".

      <dt>'StringInsert["$string$", "$snew$", {$n_1$, $n_2$, ...}]'
      <dd>inserts a copy of $snew$ at each position $n_i$ in $string$;
        the $n_i$ are taken before any insertion is done.

      <dt>'StringInsert[{$s_1$, $s_2$, ...}, "$snew$", $n$]'
      <dd>gives the list of results for each of the $s_i$.
    </dl>

    >> StringInsert["noting", "h", 4]
     = nothing

    #> StringInsert["abcdefghijklm", "X", 15]
     : Cannot insert at position 15 in abcdefghijklm.
     = StringInsert[abcdefghijklm, X, 15]

    #> StringInsert[abcdefghijklm, "X", 4]
     : String or list of strings expected at position 1 in StringInsert[abcdefghijklm, X, 4].
     = StringInsert[abcdefghijklm, X, 4]

    #> StringInsert["abcdefghijklm", X, 4]
     : String expected at position 2 in StringInsert[abcdefghijklm, X, 4].
     = StringInsert[abcdefghijklm, X, 4]

    #> StringInsert["abcdefghijklm", "X", a]
     : Position specification a in StringInsert[abcdefghijklm, X, a] is not a machine-sized integer or a list of machine-sized integers.
     = StringInsert[abcdefghijklm, X, a]

    #> StringInsert["abcdefghijklm", "X", 0]
     : Cannot insert at position 0 in abcdefghijklm.
     =  StringInsert[abcdefghijklm, X, 0]

    >> StringInsert["note", "d", -1]
     = noted

    >> StringInsert["here", "t", -5]
     = there

    #> StringInsert["abcdefghijklm", "X", -15]
     : Cannot insert at position -15 in abcdefghijklm.
     = StringInsert[abcdefghijklm, X, -15]

    >> StringInsert["adac", "he", {1, 5}]
     = headache

    #> StringInsert["abcdefghijklm", "X", {1, -1, 14, -14}]
     = XXabcdefghijklmXX

    #> StringInsert["abcdefghijklm", "X", {1, 0}]
     : Cannot insert at position 0 in abcdefghijklm.
     = StringInsert[abcdefghijklm, X, {1, 0}]

    #> StringInsert["", "X", {1}]
     = X

    #> StringInsert["", "X", {1, -1}]
     = XX

    #> StringInsert["", "", {1}]
     = #<--#

    #> StringInsert["", "X", {1, 2}]
     : Cannot insert at position 2 in .
     = StringInsert[, X, {1, 2}]

    #> StringInsert["abcdefghijklm", "", {1, 2, 3, 4 ,5, -6}]
     = abcdefghijklm

    #> StringInsert["abcdefghijklm", "X", {}]
     = abcdefghijklm

    >> StringInsert[{"something", "sometimes"}, " ", 5]
     = {some thing, some times}

    #> StringInsert[{"abcdefghijklm", "Mathics"}, "X", 13]
     : Cannot insert at position 13 in Mathics.
     = {abcdefghijklXm, StringInsert[Mathics, X, 13]}

    #> StringInsert[{"", ""}, "", {1, 1, 1, 1}]
     = {, }

    #> StringInsert[{"abcdefghijklm", "Mathics"}, "X", {0, 2}]
     : Cannot insert at position 0 in abcdefghijklm.
     : Cannot insert at position 0 in Mathics.
     = {StringInsert[abcdefghijklm, X, {0, 2}], StringInsert[Mathics, X, {0, 2}]}

    #> StringInsert[{"abcdefghijklm", Mathics}, "X", {1, 2}]
     : String or list of strings expected at position 1 in StringInsert[{abcdefghijklm, Mathics}, X, {1, 2}].
     = StringInsert[{abcdefghijklm, Mathics}, X, {1, 2}]

    #> StringInsert[{"", "Mathics"}, "X", {1, 1, -1}]
     = {XXX, XXMathicsX}

    >> StringInsert["1234567890123456", ".", Range[-16, -4, 3]]
     = 1.234.567.890.123.456"""

    messages = {
        "strse": "String or list of strings expected at position `1` in `2`.",
        "string": "String expected at position `1` in `2`.",
        "ins": "Cannot insert at position `1` in `2`.",
        "psl": "Position specification `1` in `2` is not a machine-sized integer or a list of machine-sized integers.",
    }

    summary_text = "insert a string in a given position"

    def _insert(self, str, add, lpos, evaluation):
        for pos in lpos:
            if abs(pos) < 1 or abs(pos) > len(str) + 1:
                str_string = String(str)
                add_string = String(add)
                lpos_element = Integer(lpos[0]) if len(lpos) == 1 else from_python(lpos)
                evaluation.message("StringInsert", "ins", Integer(pos), str_string)
                return evaluation.format_output(
                    Expression(
                        SymbolStringInsert,
                        str_string,
                        add_string,
                        lpos_element,
                    )
                )

        # Create new list of position which are rearranged
        pos_limit = len(str) + 2
        listpos = [p if p > 0 else pos_limit + p for p in lpos]
        listpos.sort()

        result = ""
        start = 0
        for pos in listpos:
            stop = pos - 1
            result += str[start:stop] + add
            start = stop
        else:
            result += str[start : len(str)]

        return result

    def apply(self, strsource, strnew, pos, evaluation):
        "StringInsert[strsource_, strnew_, pos_]"

        exp = Expression(SymbolStringInsert, strsource, strnew, pos)

        py_strnew = strnew.get_string_value()
        if py_strnew is None:
            return evaluation.message("StringInsert", "string", Integer(2), exp)

        # Check and create list of position
        listpos = []
        if pos.has_form("List", None):
            elements = pos.get_elements()
            if not elements:
                return strsource
            else:
                for i, posi in enumerate(elements):
                    py_posi = posi.get_int_value()
                    if py_posi is None:
                        return evaluation.message("StringInsert", "psl", pos, exp)
                    listpos.append(py_posi)
        else:
            py_pos = pos.get_int_value()
            if py_pos is None:
                return evaluation.message("StringInsert", "psl", pos, exp)
            listpos.append(py_pos)

        # Check and perform the insertion
        if strsource.has_form("List", None):
            py_strsource = [sub.get_string_value() for sub in strsource.elements]
            if any(sub is None for sub in py_strsource):
                return evaluation.message("StringInsert", "strse", Integer1, exp)
            return ListExpression(
                *[
                    String(self._insert(s, py_strnew, listpos, evaluation))
                    for s in py_strsource
                ]
            )
        else:
            py_strsource = strsource.get_string_value()
            if py_strsource is None:
                return evaluation.message("StringInsert", "strse", Integer1, exp)
            return String(self._insert(py_strsource, py_strnew, listpos, evaluation))


class StringJoin(BinaryOperator):
    """
    <dl>
    <dt>'StringJoin["$s1$", "$s2$", ...]'
        <dd>returns the concatenation of the strings $s1$, $s2$,  .
    </dl>

    >> StringJoin["a", "b", "c"]
     = abc
    >> "a" <> "b" <> "c" // InputForm
     = "abc"

    'StringJoin' flattens lists out:
    >> StringJoin[{"a", "b"}] // InputForm
     = "ab"
    >> Print[StringJoin[{"Hello", " ", {"world"}}, "!"]]
     | Hello world!
    """

    attributes = flat | one_identity | protected
    operator = "<>"
    precedence = 600
    summary_text = "join strings together"

    def apply(self, items, evaluation):
        "StringJoin[items___]"
        result = ""
        if hasattr(items, "flatten_with_respect_to_head"):
            items = items.flatten_with_respect_to_head(SymbolList)
        if items.get_head_name() == "System`List":
            items = items.elements
        else:
            items = items.get_sequence()
        for item in items:
            if not isinstance(item, (String, _BoxedString)):
                evaluation.message("StringJoin", "string")
                return
            result += item.value
        return String(result)


class StringLength(Builtin):
    """
    <dl>
      <dt>'StringLength["$string$"]'
      <dd>gives the length of $string$.
    </dl>

    >> StringLength["abc"]
     = 3
    'StringLength' is listable:
    >> StringLength[{"a", "bc"}]
     = {1, 2}

    >> StringLength[x]
     : String expected.
     = StringLength[x]
    """

    attributes = listable | protected

    summary_text = "length of a string (in Unicode characters)"

    def apply(self, str, evaluation):
        "StringLength[str_]"
        if not isinstance(str, (String, _BoxedString)):
            evaluation.message("StringLength", "string")
            return
        return Integer(len(str.value))


class StringPosition(Builtin):
    """
    <dl>
    <dt>'StringPosition["$string$", $patt$]'
      <dd>gives a list of starting and ending positions where $patt$ matches "$string$".
    <dt>'StringPosition["$string$", $patt$, $n$]'
      <dd>returns the first $n$ matches only.
    <dt>'StringPosition["$string$", {$patt1$, $patt2$, ...}, $n$]'
      <dd>matches multiple patterns.
    <dt>'StringPosition[{$s1$, $s2$, ...}, $patt$]'
      <dd>returns a list of matches for multiple strings.
    </dl>

    >> StringPosition["123ABCxyABCzzzABCABC", "ABC"]
     = {{4, 6}, {9, 11}, {15, 17}, {18, 20}}

    >> StringPosition["123ABCxyABCzzzABCABC", "ABC", 2]
     = {{4, 6}, {9, 11}}

    'StringPosition' can be useful for searching through text.
    >> data = Import["ExampleData/EinsteinSzilLetter.txt"];
    >> StringPosition[data, "uranium"]
     = {{299, 305}, {870, 876}, {1538, 1544}, {1671, 1677}, {2300, 2306}, {2784, 2790}, {3093, 3099}}

    #> StringPosition["123ABCxyABCzzzABCABC", "ABC", -1]
     : Non-negative integer or Infinity expected at position 3 in StringPosition[123ABCxyABCzzzABCABC, ABC, -1].
     = StringPosition[123ABCxyABCzzzABCABC, ABC, -1]

    ## Overlaps
    #> StringPosition["1231221312112332", RegularExpression["[12]+"]]
     = {{1, 2}, {2, 2}, {4, 7}, {5, 7}, {6, 7}, {7, 7}, {9, 13}, {10, 13}, {11, 13}, {12, 13}, {13, 13}, {16, 16}}
    #> StringPosition["1231221312112332", RegularExpression["[12]+"], Overlaps -> False]
     = {{1, 2}, {4, 7}, {9, 13}, {16, 16}}
    #> StringPosition["1231221312112332", RegularExpression["[12]+"], Overlaps -> x]
     = {{1, 2}, {4, 7}, {9, 13}, {16, 16}}
    #> StringPosition["1231221312112332", RegularExpression["[12]+"], Overlaps -> All]
     : Overlaps -> All option is not currently implemented in Mathics.
     = {{1, 2}, {2, 2}, {4, 7}, {5, 7}, {6, 7}, {7, 7}, {9, 13}, {10, 13}, {11, 13}, {12, 13}, {13, 13}, {16, 16}}

    #> StringPosition["21211121122", {"121", "11"}]
     = {{2, 4}, {4, 5}, {5, 6}, {6, 8}, {8, 9}}
    #> StringPosition["21211121122", {"121", "11"}, Overlaps -> False]
     = {{2, 4}, {5, 6}, {8, 9}}

    #> StringPosition[{"abc", "abcda"}, "a"]
     = {{{1, 1}}, {{1, 1}, {5, 5}}}

    #> StringPosition[{"abc"}, "a", Infinity]
     = {{{1, 1}}}

    #> StringPosition["abc"]["123AabcDEabc"]
     = {{5, 7}, {10, 12}}
    """

    messages = {
        "strse": "String or list of strings expected at position `1` in `2`.",
        "overall": "Overlaps -> All option is not currently implemented in Mathics.",
        "innf": "Non-negative integer or Infinity expected at position `2` in `1`.",
    }

    options = {
        "IgnoreCase": "False",
        "MetaCharacters": "None",
        "Overlaps": "True",
    }

    rules = {
        "StringPosition[patt_][s_]": "StringPosition[s, patt]",
    }

    summary_text = "range of positions where substrings match a pattern"

    def apply(self, string, patt, evaluation, options):
        "StringPosition[string_, patt_, OptionsPattern[StringPosition]]"
        return self.apply_n(
            string,
            patt,
            Expression(SymbolDirectedInfinity, Integer1),
            evaluation,
            options,
        )

    def apply_n(self, string, patt, n, evaluation, options):
        "StringPosition[string_, patt_, n:(_Integer|DirectedInfinity[1]), OptionsPattern[StringPosition]]"
        expr = Expression(SymbolStringPosition, string, patt, n)

        # check n
        if n.has_form("DirectedInfinity", 1):
            py_n = float("inf")
        else:
            py_n = n.get_int_value()
            if py_n is None or py_n < 0:
                return evaluation.message("StringPosition", "innf", expr, Integer(3))

        # check options
        if options["System`Overlaps"] is SymbolTrue:
            overlap = True
        elif options["System`Overlaps"] is SymbolFalse:
            overlap = False
        elif options["System`Overlaps"] is SymbolAll:
            # TODO
            evaluation.message("StringPosition", "overall")
            overlap = True
        else:
            overlap = False  # unknown options are teated as False

        # convert patterns
        if patt.has_form("List", None):
            patts = patt.get_elements()
        else:
            patts = [patt]
        re_patts = []
        for p in patts:
            py_p = to_regex(p, evaluation)
            if py_p is None:
                return evaluation.message("StringExpression", "invld", p, patt)
            re_patts.append(py_p)
        compiled_patts = [re.compile(re_patt) for re_patt in re_patts]

        # string or list of strings
        if string.has_form("List", None):
            py_strings = [s.get_string_value() for s in string.elements]
            if None in py_strings:
                return
            results = [
                self.do_apply(py_string, compiled_patts, py_n, overlap)
                for py_string in py_strings
            ]
            return ListExpression(*results)
        else:
            py_string = string.get_string_value()
            if py_string is None:
                return
            return self.do_apply(py_string, compiled_patts, py_n, overlap)

    @staticmethod
    def do_apply(py_string, compiled_patts, py_n, overlap):
        result = []
        start = 0
        while start < len(py_string):
            found_match = False
            for compiled_patt in compiled_patts:
                m = compiled_patt.match(py_string, start)
                if m is None:
                    continue
                found_match = True
                result.append([m.start() + 1, m.end()])  # 0 to 1 based indexing
                if len(result) == py_n:
                    return from_python(result)
                if not overlap:
                    start = m.end()
            if overlap or not found_match:
                start += 1
        return from_python(result)


class StringReplace(_StringFind):
    """
    <dl>
    <dt>'StringReplace["$string$", "$a$"->"$b$"]'
        <dd>replaces each occurrence of $old$ with $new$ in $string$.
    <dt>'StringReplace["$string$", {"$s1$"->"$sp1$", "$s2$"->"$sp2$"}]'
        <dd>performs multiple replacements of each $si$ by the
        corresponding $spi$ in $string$.
    <dt>'StringReplace["$string$", $srules$, $n$]'
        <dd>only performs the first $n$ replacements.
    <dt>'StringReplace[{"$string1$", "$string2$", ...}, $srules$]'
        <dd>performs the replacements specified by $srules$ on a list
        of strings.
    </dl>

    StringReplace replaces all occurrences of one substring with another:
    >> StringReplace["xyxyxyyyxxxyyxy", "xy" -> "A"]
     = AAAyyxxAyA

    Multiple replacements can be supplied:
    >> StringReplace["xyzwxyzwxxyzxyzw", {"xyz" -> "A", "w" -> "BCD"}]
     = ABCDABCDxAABCD

    Only replace the first 2 occurences:
    >> StringReplace["xyxyxyyyxxxyyxy", "xy" -> "A", 2]
     = AAxyyyxxxyyxy

    Also works for multiple rules:
    >> StringReplace["abba", {"a" -> "A", "b" -> "B"}, 2]
     = ABba

    StringReplace acts on lists of strings too:
    >> StringReplace[{"xyxyxxy", "yxyxyxxxyyxy"}, "xy" -> "A"]
     = {AAxA, yAAxxAyA}

    #> StringReplace["abcabc", "a" -> "b", Infinity]
     = bbcbbc
    #> StringReplace[x, "a" -> "b"]
     : String or list of strings expected at position 1 in StringReplace[x, a -> b].
     = StringReplace[x, a -> b]
    #> StringReplace["xyzwxyzwaxyzxyzw", x]
     : x is not a valid string replacement rule.
     = StringReplace[xyzwxyzwaxyzxyzw, x]
    #> StringReplace["xyzwxyzwaxyzxyzw", x -> y]
     : Element x is not a valid string or pattern element in x.
     = StringReplace[xyzwxyzwaxyzxyzw, x -> y]
    #> StringReplace["abcabc", "a" -> "b", -1]
     : Non-negative integer or Infinity expected at position 3 in StringReplace[abcabc, a -> b, -1].
     = StringReplace[abcabc, a -> b, -1]
    #> StringReplace["abc", "b" -> 4]
     : String expected.
     = a <> 4 <> c

    #> StringReplace["01101100010", "01" .. -> "x"]
     = x1x100x0

    #> StringReplace["abc abcb abdc", "ab" ~~ _ -> "X"]
     = X Xb Xc

    #> StringReplace["abc abcd abcd",  WordBoundary ~~ "abc" ~~ WordBoundary -> "XX"]
     = XX abcd abcd

    #> StringReplace["abcd acbd", RegularExpression["[ab]"] -> "XX"]
     = XXXXcd XXcXXd

    #> StringReplace["abcd acbd", RegularExpression["[ab]"] ~~ _ -> "YY"]
     = YYcd YYYY

    #> StringReplace["abcdabcdaabcabcd", {"abc" -> "Y", "d" -> "XXX"}]
     = YXXXYXXXaYYXXX


    #> StringReplace["  Have a nice day.  ", (StartOfString ~~ Whitespace) | (Whitespace ~~ EndOfString) -> ""] // FullForm
     = "Have a nice day."

    #> StringReplace["xyXY", "xy" -> "01"]
     = 01XY
    #> StringReplace["xyXY", "xy" -> "01", IgnoreCase -> True]
     = 0101

    StringReplace also can be used as an operator:
    >> StringReplace["y" -> "ies"]["city"]
     = cities
    """

    # TODO Special Characters
    """
    #> StringReplace["product: A \\[CirclePlus] B" , "\\[CirclePlus]" -> "x"]
     = A x B
    """

    rules = {
        "StringReplace[rule_][string_]": "StringReplace[string, rule]",
    }

    summary_text = "apply replace rules to substrings"

    def _find(self, py_stri, py_rules, py_n, flags, evaluation):
        def cases():
            k = 0
            for match, form in _parallel_match(py_stri, py_rules, flags, py_n):
                start, end = match.span()
                if start > k:
                    yield String(py_stri[k:start])
                yield _evaluate_match(form, match, evaluation)
                k = end
            if k < len(py_stri):
                yield String(py_stri[k:])

        return Expression(SymbolStringJoin, *list(cases()))

    def apply(self, string, rule, n, evaluation, options):
        "%(name)s[string_, rule_, OptionsPattern[%(name)s], n_:System`Private`Null]"
        # this pattern is a slight hack to get around missing Shortest/Longest.
        return self._apply(string, rule, n, evaluation, options, False)


class StringReverse(Builtin):
    """
    <dl>
      <dt>'StringReverse["$string$"]'
      <dd>reverses the order of the characters in "string".
      </dl>

      >> StringReverse["live"]
       = evil
    """

    attributes = listable | protected
    summary_text = "reverses the order of the characters in a string"

    def apply(self, string, evaluation):
        "StringReverse[string_String]"
        return String(string.get_string_value()[::-1])


class StringRiffle(Builtin):
    """
    <dl>
    <dt>'StringRiffle[{s1, s2, s3, ...}]'
      <dd>returns a new string by concatenating all the $si$, with spaces inserted between them.
    <dt>'StringRiffle[list, sep]'
      <dd>inserts the separator $sep$ between all elements in $list$.
    <dt>'StringRiffle[list, {"left", "sep", "right"}]'
      <dd>use $left$ and $right$ as delimiters after concatenation.

    ## These 2 forms are not currently implemented
    ## <dt>'StringRiffle[{{s11, s12, ...}, {s21, s22, ...}, ...}]'
    ##   <dd>returns a new string by concatenating the $sij$, and inserting spaces at the lowest level and newlines at the higher level.
    ## <dt>'StringRiffle[list, sep1, sep2, ...]'
    ##   <dd>inserts separator $sepi$ between elements of list at level i.
    </dl>

    >> StringRiffle[{"a", "b", "c", "d", "e"}]
     = a b c d e

    #> StringRiffle[{a, b, c, "d", e, "f"}]
     = a b c d e f

    ## 1st is not a list
    #> StringRiffle["abcdef"]
     : List expected at position 1 in StringRiffle[abcdef].
     : StringRiffle called with 1 argument; 2 or more arguments are expected.
     = StringRiffle[abcdef]

    #> StringRiffle[{"", "", ""}] // FullForm
     = "  "

    ## This form is not supported
    #> StringRiffle[{{"a", "b"}, {"c", "d"}}]
     : Sublist form in position 1 is is not implemented yet.
     = StringRiffle[{{a, b}, {c, d}}]

    >> StringRiffle[{"a", "b", "c", "d", "e"}, ", "]
     = a, b, c, d, e

    #> StringRiffle[{"a", "b", "c", "d", "e"}, sep]
     : String expected at position 2 in StringRiffle[{a, b, c, d, e}, sep].
     = StringRiffle[{a, b, c, d, e}, sep]

    >> StringRiffle[{"a", "b", "c", "d", "e"}, {"(", " ", ")"}]
     = (a b c d e)

    #> StringRiffle[{"a", "b", "c", "d", "e"}, {" ", ")"}]
     : String expected at position 2 in StringRiffle[{a, b, c, d, e}, { , )}].
     = StringRiffle[{a, b, c, d, e}, { , )}]
    #> StringRiffle[{"a", "b", "c", "d", "e"}, {left, " ", "."}]
     : String expected at position 2 in StringRiffle[{a, b, c, d, e}, {left,  , .}].
     = StringRiffle[{a, b, c, d, e}, {left,  , .}]

    ## This form is not supported
    #> StringRiffle[{"a", "b", "c"}, "+", "-"]
    ## Mathematica result: a+b+c, but we are not support multiple separators
     :  Multiple separators form is not implemented yet.
     = StringRiffle[{a, b, c}, +, -]
    """

    attributes = protected | read_protected

    messages = {
        "list": "List expected at position `1` in `2`.",
        "argmu": "StringRiffle called with 1 argument; 2 or more arguments are expected.",
        "argm": "StringRiffle called with 0 arguments; 2 or more arguments are expected.",
        "string": "String expected at position `1` in `2`.",
        "sublist": "Sublist form in position 1 is is not implemented yet.",
        "mulsep": "Multiple separators form is not implemented yet.",
    }

    summary_text = "assemble a string from a list, inserting delimiters"

    def apply(self, liststr, seps, evaluation):
        "StringRiffle[liststr_, seps___]"
        separators = seps.get_sequence()
        exp = (
            Expression(SymbolStringRiffle, liststr, seps)
            if separators
            else Expression(SymbolStringRiffle, liststr)
        )

        # Validate separators
        if len(separators) > 1:
            return evaluation.message("StringRiffle", "mulsep")
        elif len(separators) == 1:
            if separators[0].has_form("List", None):
                if len(separators[0].elements) != 3 or any(
                    not isinstance(s, (String, _BoxedString))
                    for s in separators[0].elements
                ):
                    return evaluation.message("StringRiffle", "string", Integer(2), exp)
            elif not isinstance(separators[0], (String, _BoxedString)):
                return evaluation.message("StringRiffle", "string", Integer(2), exp)

        # Validate list of string
        if not liststr.has_form("List", None):
            evaluation.message("StringRiffle", "list", Integer1, exp)
            return evaluation.message("StringRiffle", "argmu", exp)
        elif any(element.has_form("List", None) for element in liststr.elements):
            return evaluation.message("StringRiffle", "sublist")

        # Determine the separation token
        left, right = "", ""
        if len(separators) == 0:
            sep = " "
        else:
            if separators[0].has_form("List", None):
                left = separators[0].elements[0].value
                sep = separators[0].elements[1].value
                right = separators[0].elements[2].value
            else:
                sep = separators[0].get_string_value()

        # Getting all together
        result = left
        for i in range(len(liststr.elements)):
            text = format_element(
                liststr.elements[i], evaluation, SymbolOutputForm
            ).boxes_to_text(evaluation=evaluation)
            if i == len(liststr.elements) - 1:
                result += text + right
            else:
                result += text + sep

        return String(result)


class StringSplit(Builtin):
    """
    <dl>
      <dt>'StringSplit[$s$]'
      <dd>splits the string $s$ at whitespace, discarding the whitespace and returning a list of strings.

      <dt>'StringSplit[$s$, $pattern$]'
      <dd>splits $s$ into substrings separated by delimiters matching the string expression $pattern$.

      <dt>'StringSplit[$s$, {$p_1$, $p_2$, ...}]'
      <dd>splits $s$ at any of the $p_i$ patterns.

      <dt>'StringSplit[{$s_1$, $s_2$, ...}, {$d_1$, $d_2$, ...}]'
      <dd>returns a list with the result of applying the function to each element.
    </dl>


    >> StringSplit["abc,123", ","]
     = {abc, 123}

    By default any number of whitespace characters are used to at a delimiter:
    >> StringSplit["  abc    123  "]
     = {abc, 123}

    However if you want instead to use only a <i>single</i> character for each delimiter, use 'WhiteSpaceCharacter':
    >> StringSplit["  abc    123  ", WhitespaceCharacter]
     = {, , abc, , , , 123, , }

    >> StringSplit["abc,123.456", {",", "."}]
     = {abc, 123, 456}

    >> StringSplit["a  b    c", RegularExpression[" +"]]
     = {a, b, c}

    >> StringSplit[{"a  b", "c  d"}, RegularExpression[" +"]]
     = {{a, b}, {c, d}}

    >> StringSplit["x", "x"]
     = {}

    #> StringSplit[x]
     : String or list of strings expected at position 1 in StringSplit[x].
     = StringSplit[x, Whitespace]

    #> StringSplit["x", x]
     : Element x is not a valid string or pattern element in x.
     = StringSplit[x, x]

    Split using a delmiter that has nonzero list of 12's
    >> StringSplit["12312123", "12"..]
     = {3, 3}

    """

    messages = {
        "strse": "String or list of strings expected at position `1` in `2`.",
        "pysplit": "As of Python 3.5 re.split does not handle empty pattern matches.",
    }

    options = {
        "IgnoreCase": "False",
        "MetaCharacters": "None",
    }

    rules = {
        "StringSplit[s_]": "StringSplit[s, Whitespace]",
    }

    summary_text = "split strings at whitespace, or at a pattern"

    def apply(self, string, patt, evaluation, options):
        "StringSplit[string_, patt_, OptionsPattern[%(name)s]]"

        if string.get_head_name() == "System`List":
            elements = [
                self.apply(s, patt, evaluation, options) for s in string.elements
            ]
            return ListExpression(*elements)

        py_string = string.get_string_value()

        if py_string is None:
            return evaluation.message(
                "StringSplit", "strse", Integer1, Expression(SymbolStringSplit, string)
            )

        if patt.has_form("List", None):
            patts = patt.get_elements()
        else:
            patts = [patt]
        re_patts = []
        for p in patts:
            py_p = to_regex(p, evaluation)
            if py_p is None:
                return evaluation.message("StringExpression", "invld", p, patt)
            re_patts.append(py_p)

        flags = re.MULTILINE
        if options["System`IgnoreCase"] is SymbolTrue:
            flags = flags | re.IGNORECASE

        result = [py_string]
        for re_patt in re_patts:
            result = [t for s in result for t in mathics_split(re_patt, s, flags=flags)]

        return string_list(
            SymbolList,
            [
                String(x)
                for x in result
                # Remove the empty matches only if we aren't splitting by
                # whitespace because Python's RegEx matches " " as ""
                if x != "" or patts[0].to_python() in ("", "System`WhitespaceCharacter")
            ],
            evaluation,
        )


class StringTake(Builtin):
    """
    <dl>
      <dt>'StringTake["$string$", $n$]'
      <dd>gives the first $n$ characters in $string$.

      <dt>'StringTake["$string$", -$n$]'
      <dd>gives the last $n$ characters in $string$.

      <dt>'StringTake["$string$", {$n$}]'
      <dd>gives the $n$th character in $string$.

      <dt>'StringTake["$string$", {$m$, $n$}]'
      <dd>gives characters $m$ through $n$ in $string$.

      <dt>'StringTake["$string$", {$m$, $n$, $s$}]'
      <dd>gives characters $m$ through $n$ in steps of $s$.

      <dt>'StringTake[{$s1$, $s2$, ...} $spec$}]'
      <dd>gives the list of results for each of the $si$.
    </dl>

    >> StringTake["abcde", 2]
     = ab
    >> StringTake["abcde", 0]
     = #<--#
    >> StringTake["abcde", -2]
     = de
    >> StringTake["abcde", {2}]
     = b
    >> StringTake["abcd", {2,3}]
     = bc
    >> StringTake["abcdefgh", {1, 5, 2}]
     = ace

    Take the last 2 characters from several strings:
    >> StringTake[{"abcdef", "stuv", "xyzw"}, -2]
     = {ef, uv, zw}

    StringTake also supports standard sequence specifications
    >> StringTake["abcdef", All]
     = abcdef

    #> StringTake["abcd", 0] // InputForm
    = ""
    #> StringTake["abcd", {3, 2}] // InputForm
    = ""
    #> StringTake["", {1, 0}] // InputForm
    = ""

    #> StringTake["abc", {0, 0}]
    : Cannot take positions 0 through 0 in "abc".
    = StringTake[abc, {0, 0}]

    #> StringTake[{2, 4},2]
     : String or list of strings expected at position 1.
     = StringTake[{2, 4}, 2]

    #> StringTake["kkkl",Graphics[{}]]
     : Integer or a list of sequence specifications expected at position 2.
     = StringTake[kkkl, -Graphics-]
    """

    messages = {
        "strse": "String or list of strings expected at position 1.",
        # FIXME: mseqs should be: Sequence specification (+n, -n, {+n}, {-n}, {m, n}, or {m, n, s}) or a list
        # of sequence specifications expected at position 2 in
        "mseqs": "Integer or a list of sequence specifications expected at position 2.",
        "take": 'Cannot take positions `1` through `2` in "`3`".',
    }

    summary_text = "sub-string from a range of positions"

    def apply(self, string, seqspec, evaluation):
        "StringTake[string_String, seqspec_]"
        result = string.get_string_value()
        if result is None:
            return evaluation.message("StringTake", "strse")

        if isinstance(seqspec, Integer):
            pos = seqspec.get_int_value()
            if pos >= 0:
                seq = (1, pos, 1)
            else:
                seq = (pos, None, 1)
        else:
            seq = convert_seq(seqspec)

        if seq is None:
            return evaluation.message("StringTake", "mseqs")

        start, stop, step = seq
        py_slice = python_seq(start, stop, step, len(result))

        if py_slice is None:
            return evaluation.message("StringTake", "take", start, stop, string)

        return String(result[py_slice])

    def apply_strings(self, strings, spec, evaluation):
        "StringTake[strings__, spec_]"
        result_list = []
        for string in strings.elements:
            result = self.apply(string, spec, evaluation)
            if result is None:
                return None
            result_list.append(result)
        return ListExpression(*result_list)


class StringTrim(Builtin):
    """
    <dl>
      <dt>'StringTrim[$s$]'
      <dd>returns a version of $s$ with whitespace removed from start and end.
    </dl>

    >> StringJoin["a", StringTrim["  \\tb\\n "], "c"]
     = abc

    >> StringTrim["ababaxababyaabab", RegularExpression["(ab)+"]]
     = axababya
    """

    summary_text = "trim whitespace etc. from strings"

    def apply(self, s, evaluation):
        "StringTrim[s_String]"
        return String(s.get_string_value().strip(" \t\n"))

    def apply_pattern(self, s, patt, expression, evaluation):
        "StringTrim[s_String, patt_]"
        text = s.get_string_value()
        if not text:
            return s

        py_patt = to_regex(patt, evaluation)
        if py_patt is None:
            return evaluation.message("StringExpression", "invld", patt, expression)

        if not py_patt.startswith(r"\A"):
            left_patt = r"\A" + py_patt
        else:
            left_patt = py_patt

        if not py_patt.endswith(r"\Z"):
            right_patt = py_patt + r"\Z"
        else:
            right_patt = py_patt

        m = re.search(left_patt, text)
        left = m.end(0) if m else 0

        m = re.search(right_patt, text)
        right = m.start(0) if m else len(text)

        return String(text[left:right])
