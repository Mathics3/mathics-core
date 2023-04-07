"""
Expression Sizes and Signatures
"""
import hashlib
import platform
import zlib

from mathics.builtin.base import Builtin
from mathics.core.atoms import ByteArrayAtom, Integer, String
from mathics.core.attributes import A_PROTECTED, A_READ_PROTECTED
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolByteArray
from mathics.eval.parts import walk_levels

if platform.python_implementation() == "PyPy":
    bytecount_support = False
else:
    from mathics.builtin.pympler.asizeof import asizeof as count_bytes

    bytecount_support = True

# This tells documentation how to sort this module
sort_order = "mathics.builtin.exp_structure.exp_sizes_and"


class _ZLibHash:  # make zlib hashes behave as if they were from hashlib
    def __init__(self, fn):
        self._bytes = b""
        self._fn = fn

    def update(self, bytes):
        self._bytes += bytes

    def hexdigest(self):
        return format(self._fn(self._bytes), "x")


class ByteCount(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ByteCount.html</url>

    <dl>
      <dt>'ByteCount[$expr$]'
      <dd>gives the internal memory space used by $expr$, in bytes.
    </dl>

    The results may heavily depend on the Python implementation in use.
    """

    summary_text = "amount of memory used by expr, in bytes"

    def eval(self, expression, evaluation: Evaluation):
        "ByteCount[expression_]"
        if not bytecount_support:
            evaluation.message("ByteCount", "pypy")
        else:
            return Integer(count_bytes(expression))


class Hash(Builtin):
    """
    <url>:Hash function:https://en.wikipedia.org/wiki/Hash_function</url> \
    (<url>:WMA link:https://reference.wolfram.com/language/ref/Hash.html</url>)

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

    attributes = A_PROTECTED | A_READ_PROTECTED

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

    def eval(self, expr, hashtype: String, outformat: String, evaluation: Evaluation):
        "Hash[expr_, hashtype_String, outformat_String]"
        return Hash.compute(expr.user_hash, hashtype.value, outformat.value)


class LeafCount(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/LeafCount.html</url>

    <dl>
      <dt>'LeafCount[$expr$]'
      <dd>returns the total number of indivisible subexpressions in $expr$.
    </dl>

    >> LeafCount[1 + x + y^a]
     = 6

    >> LeafCount[f[x, y]]
     = 3

    >> LeafCount[{1 / 3, 1 + I}]
     = 7

    >> LeafCount[Sqrt[2]]
     = 5

    >> LeafCount[100!]
     = 1

    #> LeafCount[f[a, b][x, y]]
     = 5

    #> NestList[# /. s[x_][y_][z_] -> x[z][y[z]] &, s[s][s][s[s]][s][s], 4];
    #> LeafCount /@ %
     = {7, 8, 8, 11, 11}

    #> LeafCount[1 / 3, 1 + I]
     : LeafCount called with 2 arguments; 1 argument is expected.
     = LeafCount[1 / 3, 1 + I]
    """

    messages = {
        "argx": "LeafCount called with `1` arguments; 1 argument is expected.",
    }
    summary_text = "the total number of atomic subexpressions"

    def eval(self, expr, evaluation: Evaluation):
        "LeafCount[expr___]"

        from mathics.core.atoms import Complex, Rational

        elements = []

        def callback(level):
            if isinstance(level, Rational):
                elements.extend(
                    [level.get_head(), level.numerator(), level.denominator()]
                )
            elif isinstance(level, Complex):
                elements.extend([level.get_head(), level.real, level.imag])
            else:
                elements.append(level)
            return level

        expr = expr.get_sequence()
        if len(expr) != 1:
            evaluation.message("LeafCount", "argx", Integer(len(expr)))
            return

        walk_levels(expr[0], start=-1, stop=-1, heads=True, callback=callback)
        return Integer(len(elements))
