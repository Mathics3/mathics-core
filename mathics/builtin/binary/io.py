# -*- coding: utf-8 -*-
"""
Binary Reading and Writing
"""

import math
import struct
from itertools import chain

import mpmath
import sympy

from mathics.core.atoms import Complex, Integer, MachineReal, Real, String
from mathics.core.builtin import Builtin
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.expression import Expression
from mathics.core.expression_predefined import (
    MATHICS3_I_INFINITY,
    MATHICS3_I_NEG_INFINITY,
    MATHICS3_INFINITY,
    MATHICS3_NEG_INFINITY,
)
from mathics.core.streams import stream_manager
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolIndeterminate
from mathics.eval.files_io.read import SymbolEndOfFile
from mathics.eval.nevaluator import eval_N

SymbolBinaryWrite = Symbol("BinaryWrite")


class _BinaryFormat:
    """
    Container for BinaryRead readers and BinaryWrite writers
    """

    @staticmethod
    def _IEEE_real(real):
        if math.isnan(real):
            return SymbolIndeterminate
        elif math.isinf(real):
            return MATHICS3_NEG_INFINITY if real < 0 else MATHICS3_INFINITY
        else:
            return Real(real)

    @staticmethod
    def _IEEE_cmplx(real, imag):
        if math.isnan(real) or math.isnan(imag):
            return SymbolIndeterminate
        if math.isinf(real):
            if math.isinf(imag):
                return SymbolIndeterminate
            return MATHICS3_NEG_INFINITY if real < 0 else MATHICS3_INFINITY
        if math.isinf(imag):
            return MATHICS3_I_NEG_INFINITY if imag < 0 else MATHICS3_I_INFINITY
        return Complex(MachineReal(real), MachineReal(imag))

    @classmethod
    def get_readers(cls):
        readers = {}
        for funcname in dir(cls):
            if funcname.startswith("_") and funcname.endswith("_reader"):
                readers[funcname[1:-7]] = getattr(cls, funcname)
        return readers

    @classmethod
    def get_writers(cls):
        writers = {}
        for funcname in dir(cls):
            if funcname.startswith("_") and funcname.endswith("_writer"):
                writers[funcname[1:-7]] = getattr(cls, funcname)
        return writers

    # Reader Functions

    @staticmethod
    def _Byte_reader(s):
        "8-bit unsigned integer"
        return Integer(*struct.unpack("B", s.read(1)))

    @staticmethod
    def _Character8_reader(s):
        "8-bit character"
        return String(struct.unpack("c", s.read(1))[0].decode("ascii"))

    @staticmethod
    def _Character16_reader(s):
        "16-bit character"
        return String(chr(*struct.unpack("H", s.read(2))))

    @staticmethod
    def _Complex64_reader(s):
        "IEEE single-precision complex number"
        return _BinaryFormat._IEEE_cmplx(*struct.unpack("ff", s.read(8)))

    @staticmethod
    def _Complex128_reader(s):
        "IEEE double-precision complex number"
        return _BinaryFormat._IEEE_cmplx(*struct.unpack("dd", s.read(16)))

    def _Complex256_reader(self, s):
        "IEEE quad-precision complex number"
        return Complex(self._Real128_reader(s), self._Real128_reader(s))

    @staticmethod
    def _Integer8_reader(s):
        "8-bit signed integer"
        return Integer(*struct.unpack("b", s.read(1)))

    @staticmethod
    def _Integer16_reader(s):
        "16-bit signed integer"
        return Integer(*struct.unpack("h", s.read(2)))

    @staticmethod
    def _Integer24_reader(s):
        "24-bit signed integer"
        b = s.read(3)
        return Integer(struct.unpack("<i", b"\x00" + b)[0] >> 8)

    @staticmethod
    def _Integer32_reader(s):
        "32-bit signed integer"
        return Integer(*struct.unpack("i", s.read(4)))

    @staticmethod
    def _Integer64_reader(s):
        "64-bit signed integer"
        return Integer(*struct.unpack("q", s.read(8)))

    @staticmethod
    def _Integer128_reader(s):
        "128-bit signed integer"
        a, b = struct.unpack("Qq", s.read(16))
        return Integer((b << 64) + a)

    @staticmethod
    def _Real32_reader(s):
        "IEEE single-precision real number"
        return _BinaryFormat._IEEE_real(*struct.unpack("f", s.read(4)))

    @staticmethod
    def _Real64_reader(s):
        "IEEE double-precision real number"
        return _BinaryFormat._IEEE_real(*struct.unpack("d", s.read(8)))

    @staticmethod
    def _Real128_reader(s):
        "IEEE quad-precision real number"
        # Workaround quad missing from struct
        # correctness is not guaranteed
        b = s.read(16)
        sig, sexp = b[:14], b[14:]

        # Sign / Exponent
        (sexp,) = struct.unpack("H", sexp)
        signbit = sexp // 0x8000
        expbits = sexp % 0x8000

        # Signifand
        try:
            fracbits = int.from_bytes(sig, byteorder="little")
        except AttributeError:  # Py2
            fracbits = int(sig[::-1].encode("hex"), 16)

        if expbits == 0x0000 and fracbits == 0:
            return Real(sympy.Float(0, 4965))
        elif expbits == 0x7FFF:
            if fracbits == 0:
                return MATHICS3_NEG_INFINITY if signbit else MATHICS3_INFINITY
            else:
                return SymbolIndeterminate

        with mpmath.workprec(112):
            core = mpmath.fdiv(fracbits, 2**112)
            if expbits == 0x000:
                assert fracbits != 0
                exp = -16382
                core = mpmath.fmul((-1) ** signbit, core)
            else:
                assert 0x0001 <= expbits <= 0x7FFE
                exp = expbits - 16383
                core = mpmath.fmul((-1) ** signbit, mpmath.fadd(1, core))

            if exp >= 0:
                result = mpmath.fmul(core, 2**exp)
            else:
                result = mpmath.fdiv(core, 2**-exp)

            return from_mpmath(result, precision=112)

    @staticmethod
    def _TerminatedString_reader(s):
        "null-terminated string of 8-bit characters"
        b = s.read(1)
        contents = b""
        while b != b"\x00":
            if b == b"":
                raise struct.error
            contents += b
            b = s.read(1)
        return String(contents.decode("ascii"))

    @staticmethod
    def _UnsignedInteger8_reader(s):
        "8-bit unsigned integer"
        return Integer(*struct.unpack("B", s.read(1)))

    @staticmethod
    def _UnsignedInteger16_reader(s):
        "16-bit unsigned integer"
        return Integer(*struct.unpack("H", s.read(2)))

    @staticmethod
    def _UnsignedInteger24_reader(s):
        "24-bit unsigned integer"
        return Integer(*struct.unpack("I", s.read(3) + b"\0"))

    @staticmethod
    def _UnsignedInteger32_reader(s):
        "32-bit unsigned integer"
        return Integer(*struct.unpack("I", s.read(4)))

    @staticmethod
    def _UnsignedInteger64_reader(s):
        "64-bit unsigned integer"
        return Integer(*struct.unpack("Q", s.read(8)))

    @staticmethod
    def _UnsignedInteger128_reader(s):
        "128-bit unsigned integer"
        a, b = struct.unpack("QQ", s.read(16))
        return Integer((b << 64) + a)

    # Writer Functions

    @staticmethod
    def _Byte_writer(s, x):
        "8-bit unsigned integer"
        s.write(struct.pack("B", x))

    @staticmethod
    def _Character8_writer(s, x):
        "8-bit character"
        s.write(struct.pack("c", x.encode("ascii")))

    # TODO
    # @staticmethod
    # def _Character16_writer(s, x):
    #     "16-bit character"
    #     pass

    @staticmethod
    def _Complex64_writer(s, x):
        "IEEE single-precision complex number"
        s.write(struct.pack("ff", x.real, x.imag))
        # return _BinaryFormat._IEEE_cmplx(*struct.unpack('ff', s.read(8)))

    @staticmethod
    def _Complex128_writer(s, x):
        "IEEE double-precision complex number"
        s.write(struct.pack("dd", x.real, x.imag))

    # TODO
    # @staticmethod
    # def _Complex256_writer(s, x):
    #     "IEEE quad-precision complex number"
    #     pass

    @staticmethod
    def _Integer8_writer(s, x):
        "8-bit signed integer"
        s.write(struct.pack("b", x))

    @staticmethod
    def _Integer16_writer(s, x):
        "16-bit signed integer"
        s.write(struct.pack("h", x))

    @staticmethod
    def _Integer24_writer(s, x):
        "24-bit signed integer"
        s.write(struct.pack("i", x << 8)[1:])

    @staticmethod
    def _Integer32_writer(s, x):
        "32-bit signed integer"
        s.write(struct.pack("i", x))

    @staticmethod
    def _Integer64_writer(s, x):
        "64-bit signed integer"
        s.write(struct.pack("q", x))

    @staticmethod
    def _Integer128_writer(s, x):
        "128-bit signed integer"
        a, b = x & 0xFFFFFFFFFFFFFFFF, x >> 64
        s.write(struct.pack("Qq", a, b))

    @staticmethod
    def _Real32_writer(s, x):
        "IEEE single-precision real number"
        s.write(struct.pack("f", x))

    @staticmethod
    def _Real64_writer(s, x):
        "IEEE double-precision real number"
        s.write(struct.pack("d", x))

    # TODO
    # @staticmethod
    # def _Real128_writer(s, x):
    #     "IEEE quad-precision real number"
    #     pass

    @staticmethod
    def _TerminatedString_writer(s, x):
        "null-terminated string of 8-bit characters"
        s.write(x.encode("utf-8"))

    @staticmethod
    def _UnsignedInteger8_writer(s, x):
        "8-bit unsigned integer"
        s.write(struct.pack("B", x))

    @staticmethod
    def _UnsignedInteger16_writer(s, x):
        "16-bit unsigned integer"
        s.write(struct.pack("H", x))

    @staticmethod
    def _UnsignedInteger24_writer(s, x):
        "24-bit unsigned integer"
        s.write(struct.pack("I", x << 8)[1:])

    @staticmethod
    def _UnsignedInteger32_writer(s, x):
        "32-bit unsigned integer"
        s.write(struct.pack("I", x))

    @staticmethod
    def _UnsignedInteger64_writer(s, x):
        "64-bit unsigned integer"
        s.write(struct.pack("Q", x))

    @staticmethod
    def _UnsignedInteger128_writer(s, x):
        "128-bit unsigned integer"
        a, b = x & 0xFFFFFFFFFFFFFFFF, x >> 64
        s.write(struct.pack("QQ", a, b))


class BinaryRead(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/BinaryRead.html</url>

    <dl>
      <dt>'BinaryRead'[$stream$]
      <dd>reads one byte from the stream as an integer from 0 to 255.

      <dt>'BinaryRead'[$stream$, $type$]
      <dd>reads one object of specified type from the stream.

      <dt>'BinaryRead'[$stream$, {$type_1$, $type_2$, ...}]
      <dd>reads a sequence of objects of specified types.
    </dl>

    >> strm = OpenWrite[BinaryFormat -> True]
     = OutputStream[...]
    >> BinaryWrite[strm, {97, 98, 99}]
     = OutputStream[...]
    >> Close[strm];
    >> strm = OpenRead[%, BinaryFormat -> True]
     = InputStream[...]
    >> BinaryRead[strm, {"Character8", "Character8", "Character8"}]
     = {a, b, c}
    >> DeleteFile[Close[strm]];
    """

    summary_text = "read an object of the specified type"
    readers = _BinaryFormat.get_readers()

    messages = {
        "format": "`1` is not a recognized binary format.",
        "openw": "`1` is open for output.",
        "bfmt": "The stream `1` has been opened with BinaryFormat -> False and cannot be used with binary data.",
    }

    def eval_empty(self, name, n, evaluation):
        "BinaryRead[InputStream[name_, n_Integer]]"
        return self.eval(name, n, None, evaluation)

    def eval(self, name, n, typ, evaluation):
        "BinaryRead[InputStream[name_, n_Integer], typ_]"

        channel = to_expression("InputStream", name, n)

        # Check typ
        if typ is None:
            expr = to_expression("BinaryRead", channel)
            typ = String("Byte")
        else:
            expr = to_expression("BinaryRead", channel, typ)

        # Check channel
        stream = stream_manager.lookup_stream(n.value)

        if stream is None or stream.io.closed:
            evaluation.message("General", "openx", name)
            return expr

        if stream.mode not in ["rb"]:
            evaluation.message("BinaryRead", "bfmt", channel)
            return expr

        if typ.has_form("List", None):
            types = typ.elements
        else:
            types = [typ]

        types = [t.get_string_value() for t in types]
        if not all(t in self.readers for t in types):
            evaluation.message("BinaryRead", "format", typ)
            return expr

        # Read from stream
        result = []
        for t in types:
            try:
                result.append(self.readers[t](stream.io))
            except struct.error:
                result.append(SymbolEndOfFile)

        if typ.has_form("List", None):
            return to_mathics_list(*result)
        else:
            if len(result) == 1:
                return result[0]


class BinaryWrite(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/BinaryWrite.html</url>

    <dl>
      <dt>'BinaryWrite'[$channel$, $b$]
      <dd>writes a single byte given as an integer from 0 to 255.

      <dt>'BinaryWrite'[$channel$, {b1, b2, ...}]
      <dd>writes a sequence of byte.

      <dt>'BinaryWrite'[$channel$, "string"]
      <dd>writes the raw characters in a string.

      <dt>'BinaryWrite'[$channel$, $x$, $type$]
      <dd>writes $x$ as the specified type.

      <dt>'BinaryWrite'[$channel$, {$x_1$, $x_2$, ...}, $type$]
      <dd>writes a sequence of objects as the specified type.

      <dt>'BinaryWrite'[$channel$, {$x_1$, $x_2$, ...}, {$type_1$, $type_2$, ...}]
      <dd>writes a sequence of objects using a sequence of specified types.
    </dl>

    >> strm = OpenWrite[BinaryFormat -> True]
     = OutputStream[...]
    >> BinaryWrite[strm, {39, 4, 122}]
     = OutputStream[...]
    >> Close[strm];
    >> strm = OpenRead[%, BinaryFormat -> True]
     = InputStream[...]
    >> BinaryRead[strm]
     = 39
    >> BinaryRead[strm, "Byte"]
     = 4
    >> BinaryRead[strm, "Character8"]
     = z
    >> DeleteFile[Close[strm]];

    Write a String
    >> strm = OpenWrite[BinaryFormat -> True]
     = OutputStream[...]
    >> BinaryWrite[strm, "abc123"]
     = OutputStream[...]
    >> pathname = Close[%]
     = ...

    Read as Bytes
    >> strm = OpenRead[%, BinaryFormat -> True]
     = InputStream[...]
    >> BinaryRead[strm, {"Character8", "Character8", "Character8", "Character8", "Character8", "Character8", "Character8"}]
     = {a, b, c, 1, 2, 3, EndOfFile}
    >> pathname = Close[strm]
     = ...

    Read as Characters
    >> strm = OpenRead[%, BinaryFormat -> True]
     = InputStream[...]
    >> BinaryRead[strm, {"Byte", "Byte", "Byte", "Byte", "Byte", "Byte", "Byte"}]
     = {97, 98, 99, 49, 50, 51, EndOfFile}
    >> DeleteFile[Close[strm]];

    Write Type
    >> strm = OpenWrite[BinaryFormat -> True]
     = OutputStream[...]
    >> BinaryWrite[strm, 97, "Byte"]
     = OutputStream[...]
    >> BinaryWrite[strm, {97, 98, 99}, {"Byte", "Byte", "Byte"}]
     = OutputStream[...]
    >> DeleteFile[Close[%]];
    """

    summary_text = "write an object of the specified type"
    messages = {
        "writex": "`1`.",
    }

    writers = _BinaryFormat.get_writers()

    def eval_notype(self, name, n, b, evaluation):
        "BinaryWrite[OutputStream[name_, n_], b_]"
        return self.eval(name, n, b, None, evaluation)

    def eval(self, name, n, b, typ, evaluation):
        "BinaryWrite[OutputStream[name_, n_], b_, typ_]"

        channel = to_expression("OutputStream", name, n)

        # Check Empty Type
        if typ is None:
            expr = Expression(SymbolBinaryWrite, channel, b)
            typ = to_expression("List")
        else:
            expr = Expression(SymbolBinaryWrite, channel, b, typ)

        # Check channel
        stream = stream_manager.lookup_stream(n.get_int_value())

        if stream is None or stream.io.closed:
            evaluation.message("General", "openx", name)
            return expr

        if stream.mode not in ["wb", "ab"]:
            evaluation.message(SymbolBinaryWrite, "openr", channel)
            return expr

        # Check b
        if b.has_form("List", None):
            pyb = b.elements
        else:
            pyb = [b]

        # Check Type
        if typ.has_form("List", None):
            types = typ.elements
        else:
            types = [typ]

        if len(types) == 0:  # Default type is "Bytes"
            types = [String("Byte")]

        types = [t.get_string_value() for t in types]
        if not all(t in self.writers for t in types):
            evaluation.message("BinaryRead", "format", typ)
            return expr

        # Write to stream
        i = 0
        # TODO: please, modularize me.
        while i < len(pyb):
            x = pyb[i]
            # Types are "repeated as many times as necessary"
            t = types[i % len(types)]

            # Coerce x
            if t == "TerminatedString":
                x_py = x.get_string_value() + "\x00"
            elif t.startswith("Real"):
                if isinstance(x, Real):
                    x_py = x.to_python()
                elif x.has_form("DirectedInfinity", 1):
                    if x.elements[0].get_int_value() == 1:
                        x_py = float("+inf")
                    elif x.elements[0].get_int_value() == -1:
                        x_py = float("-inf")
                    else:
                        x_py = None
                elif x is SymbolIndeterminate:
                    x_py = float("nan")
                else:
                    x_py = None
                assert x_py is None or isinstance(x_py, float)
            elif t.startswith("Complex"):
                if isinstance(x, (Complex, Real, Integer)):
                    x_py = x.to_python()
                elif x.has_form("DirectedInfinity", 1):
                    x_py = eval_N(x.elements[0], evaluation).to_python()

                    # x*float('+inf') creates nan if x.real or x.imag are zero
                    x_py = complex(
                        x_py.real * float("+inf") if x_py.real != 0 else 0,
                        x_py.imag * float("+inf") if x_py.imag != 0 else 0,
                    )
                elif x is SymbolIndeterminate:
                    x_py = complex(float("nan"), float("nan"))
                else:
                    x_py = None
            elif t.startswith("Character"):
                if isinstance(x, Integer):
                    x_list = [String(char) for char in str(x.get_int_value())]
                    pyb = list(chain(pyb[:i], x_list, pyb[i + 1 :]))
                    x = pyb[i]
                    assert isinstance(x, String)
                if isinstance(x, String) and len(x.value) > 1:
                    x_list = [String(char) for char in x.value]
                    pyb = list(chain(pyb[:i], x_list, pyb[i + 1 :]))
                    x = pyb[i]
                    assert isinstance(x, String)
                    x_py = x.value
                else:
                    # Not sure what happens here...
                    # TODO: Check...
                    x_py = x.get_string_value()
            elif t == "Byte" and isinstance(x, String):
                if len(x.value) > 1:
                    x_list = [String(char) for char in x.value]
                    pyb = list(chain(pyb[:i], x_list, pyb[i + 1 :]))
                    x = pyb[i]
                assert isinstance(x, String)
                x_py = ord(x.value)
            else:
                x_py = x.get_int_value()

            if x_py is None:
                evaluation.message(SymbolBinaryWrite, "nocoerce", b)
                return

            try:
                self.writers[t](stream.io, x_py)
            except struct.error:
                evaluation.message(SymbolBinaryWrite, "nocoerce", b)
                return
            i += 1

        try:
            stream.io.flush()
        except IOError as err:
            evaluation.message(SymbolBinaryWrite, "writex", err.strerror)
        return channel


# TODO: BinaryReadList, BinaryWrite, BinaryReadList
