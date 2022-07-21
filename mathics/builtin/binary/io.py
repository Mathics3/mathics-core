# -*- coding: utf-8 -*-
"""
Binary Reading and Writing
"""

import math
import mpmath
import struct
import sympy

from itertools import chain

from mathics.builtin.base import Builtin
from mathics.core.atoms import Complex, Integer, MachineReal, Real, String
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.expression import Expression

from mathics.core.systemsymbols import (
    SymbolDirectedInfinity,
    SymbolIndeterminate,
)

from mathics.core.number import dps
from mathics.core.read import SymbolEndOfFile
from mathics.core.streams import stream_manager
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolComplex

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
            return Expression(SymbolDirectedInfinity, Integer((-1) ** (real < 0)))
        else:
            return Real(real)

    @staticmethod
    def _IEEE_cmplx(real, imag):
        if math.isnan(real) or math.isnan(imag):
            return SymbolIndeterminate
        elif math.isinf(real) or math.isinf(imag):
            if math.isinf(real) and math.isinf(imag):
                return SymbolIndeterminate
            return Expression(
                SymbolDirectedInfinity,
                to_expression(
                    SymbolComplex,
                    (-1) ** (real < 0) if math.isinf(real) else 0,
                    (-1) ** (imag < 0) if math.isinf(imag) else 0,
                ),
            )
        else:
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
                return Expression(SymbolDirectedInfinity, Integer((-1) ** signbit))
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

            return from_mpmath(result, dps(112))

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
    <dl>
    <dt>'BinaryRead[$stream$]'
      <dd>reads one byte from the stream as an integer from 0 to 255.
    <dt>'BinaryRead[$stream$, $type$]'
      <dd>reads one object of specified type from the stream.
    <dt>'BinaryRead[$stream$, {$type1$, $type2$, ...}]'
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

    ## Write as Bytes then Read
    #> WbR[bytes_, form_] := Module[{stream, res}, stream = OpenWrite[BinaryFormat -> True]; BinaryWrite[stream, bytes]; stream = OpenRead[Close[stream], BinaryFormat -> True]; res = BinaryRead[stream, form]; DeleteFile[Close[stream]]; res]

    ## Byte
    #> WbR[{149, 2, 177, 132}, {"Byte", "Byte", "Byte", "Byte"}]
     = {149, 2, 177, 132}
    #> (# == WbR[#, Table["Byte", {50}]]) & [RandomInteger[{0, 255}, 50]]
     = True

    ## Character8
    #> WbR[{97, 98, 99}, {"Character8", "Character8", "Character8"}]
     = {a, b, c}
    #> WbR[{34, 60, 39}, {"Character8", "Character8", "Character8"}]
     = {", <, '}

    ## Character16
    #> WbR[{97, 0, 98, 0, 99, 0}, {"Character16", "Character16", "Character16"}]
     = {a, b, c}
    #> ToCharacterCode[WbR[{50, 154, 182, 236}, {"Character16", "Character16"}]]
     = {{39474}, {60598}}
    ## #> WbR[ {91, 146, 206, 54}, {"Character16", "Character16"}]
    ##  = {\\:925b, \\:36ce}

    ## Complex64
    #> WbR[{80, 201, 77, 239, 201, 177, 76, 79}, "Complex64"] // InputForm
     = -6.368779889243691*^28 + 3.434203392*^9*I
    #> % // Precision
     = MachinePrecision
    #> WbR[{158, 2, 185, 232, 18, 237, 0, 102}, "Complex64"] // InputForm
     = -6.989488623351118*^24 + 1.522090212973691*^23*I
    #> WbR[{195, 142, 38, 160, 238, 252, 85, 188}, "Complex64"] // InputForm
     = -1.4107982814807285*^-19 - 0.013060791417956352*I

    ## Complex128
    #> WbR[{15,114,1,163,234,98,40,15,214,127,116,15,48,57,208,180},"Complex128"] // InputForm
     = 1.1983977035653814*^-235 - 2.6465639149433955*^-54*I
    #> WbR[{148,119,12,126,47,94,220,91,42,69,29,68,147,11,62,233},"Complex128"] // InputForm
     = 3.2217026714156333*^134 - 8.98364297498066*^198*I
    #> % // Precision
     = MachinePrecision
    #> WbR[{15,42,80,125,157,4,38,97, 0,0,0,0,0,0,240,255}, "Complex128"]
      = -I Infinity
    #> WbR[{15,42,80,125,157,4,38,97, 0,0,0,0,0,0,240,127}, "Complex128"]
      = I Infinity
    #> WbR[{15,42,80,125,157,4,38,97, 1,0,0,0,0,0,240,255}, "Complex128"]
     = Indeterminate
    #> WbR[{0,0,0,0,0,0,240,127, 15,42,80,125,157,4,38,97}, "Complex128"]
     = Infinity
    #> WbR[{0,0,0,0,0,0,240,255, 15,42,80,125,157,4,38,97}, "Complex128"]
     = -Infinity
    #> WbR[{1,0,0,0,0,0,240,255, 15,42,80,125,157,4,38,97}, "Complex128"]
     = Indeterminate
    #> WbR[{0,0,0,0,0,0,240,127, 0,0,0,0,0,0,240,127}, "Complex128"]
     = Indeterminate
    #> WbR[{0,0,0,0,0,0,240,127, 0,0,0,0,0,0,240,255}, "Complex128"]
     = Indeterminate

    ## Complex256
    ## TODO

    ## Integer8
    #> WbR[{149, 2, 177, 132}, {"Integer8", "Integer8", "Integer8", "Integer8"}]
     = {-107, 2, -79, -124}
    #> WbR[{127, 128, 0, 255}, {"Integer8", "Integer8", "Integer8", "Integer8"}]
     = {127, -128, 0, -1}

    ## Integer16
    #> WbR[{149, 2, 177, 132, 112, 24}, {"Integer16", "Integer16", "Integer16"}]
     = {661, -31567, 6256}
    #> WbR[{0, 0, 255, 0, 255, 255, 128, 127, 128, 128}, Table["Integer16", {5}]]
     = {0, 255, -1, 32640, -32640}

    ## Integer24
    #> WbR[{152, 173, 160, 188, 207, 154}, {"Integer24", "Integer24"}]
     = {-6247016, -6631492}
    #> WbR[{145, 173, 231, 49, 90, 30}, {"Integer24", "Integer24"}]
     = {-1593967, 1989169}

    ## Integer32
    #> WbR[{209, 99, 23, 218, 143, 187, 236, 241}, {"Integer32", "Integer32"}]
     = {-636001327, -236143729}
    #> WbR[{15, 31, 173, 120, 245, 100, 18, 188}, {"Integer32", "Integer32"}]
     = {2024611599, -1139645195}

    ## Integer64
    #> WbR[{211, 18, 152, 2, 235, 102, 82, 16}, "Integer64"]
     = 1176115612243989203
    #> WbR[{37, 217, 208, 88, 14, 241, 170, 137}, "Integer64"]
     = -8526737900550694619

    ## Integer128
    #> WbR[{140,32,24,199,10,169,248,117,123,184,75,76,34,206,49,105}, "Integer128"]
     = 139827542997232652313568968616424513676
    #> WbR[{101,57,184,108,43,214,186,120,153,51,132,225,56,165,209,77}, "Integer128"]
     = 103439096823027953602112616165136677221
    #> WbR[{113,100,125,144,211,83,140,24,206,11,198,118,222,152,23,219}, "Integer128"]
     = -49058912464625098822365387707690163087

    ## Real32
    #> WbR[{81, 72, 250, 79, 52, 227, 104, 90}, {"Real32", "Real32"}] // InputForm
     = {8.398086656*^9, 1.6388001768669184*^16}
    #> WbR[{251, 22, 221, 117, 165, 245, 18, 75}, {"Real32", "Real32"}] // InputForm
     = {5.605291528399748*^32, 9.631141*^6}
    #> WbR[{126, 82, 143, 43}, "Real32"] // InputForm
     = 1.0183657302847982*^-12
    #> % // Precision
     = MachinePrecision
    #> WbR[{0, 0, 128, 127}, "Real32"]
     = Infinity
    #> WbR[{0, 0, 128, 255}, "Real32"]
     = -Infinity
    #> WbR[{1, 0, 128, 255}, "Real32"]
     = Indeterminate
    #> WbR[{1, 0, 128, 127}, "Real32"]
     = Indeterminate

    ## Real64
    #> WbR[{45, 243, 20, 87, 129, 185, 53, 239}, "Real64"] // InputForm
     = -5.146466194262116*^227
    #> WbR[{192, 60, 162, 67, 122, 71, 74, 196}, "Real64"] // InputForm
     = -9.695316988087658*^20
    #> WbR[{15, 42, 80, 125, 157, 4, 38, 97}, "Real64"] // InputForm
     = 9.67355569763742*^159
    #> % // Precision
     = MachinePrecision
    #> WbR[{0, 0, 0, 0, 0, 0, 240, 127}, "Real64"]
     = Infinity
    #> WbR[{0, 0, 0, 0, 0, 0, 240, 255}, "Real64"]
     = -Infinity
    #> WbR[{1, 0, 0, 0, 0, 0, 240, 127}, "Real64"]
     = Indeterminate
    #> WbR[{1, 0, 0, 0, 0, 0, 240, 255}, "Real64"]
     = Indeterminate

    ## Real128
    ## 0x0000
    #> WbR[{0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0}, "Real128"]
     = 0.×10^-4965
    #> WbR[{0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,128}, "Real128"]
     = 0.×10^-4965
    ## 0x0001 - 0x7FFE
    #> WbR[{0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,255,63}, "Real128"]
     = 1.00000000000000000000000000000000
    #> WbR[{0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,255,191}, "Real128"]
     = -1.00000000000000000000000000000000
    #> WbR[{135, 62, 233, 137, 22, 208, 233, 210, 133, 82, 251, 92, 220, 216, 255, 63}, "Real128"]
     = 1.84711247573661489653389674493896
    #> WbR[{135, 62, 233, 137, 22, 208, 233, 210, 133, 82, 251, 92, 220, 216, 207, 72}, "Real128"]
     = 2.45563355727491021879689747166252×10^679
    #> WbR[{74, 95, 30, 234, 116, 130, 1, 84, 20, 133, 245, 221, 113, 110, 219, 212}, "Real128"]
     = -4.52840681592341879518366539335138×10^1607
    #> % // Precision
     = 33.
    ## 0x7FFF
    #> WbR[{0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,255,127}, "Real128"]
     = Infinity
    #> WbR[{0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,255,255}, "Real128"]
     = -Infinity
    #> WbR[{1,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,255,127}, "Real128"]
     = Indeterminate
    #> WbR[{1,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,255,255}, "Real128"]
     = Indeterminate

    ## TerminatedString
    #> WbR[{97, 98, 99, 0}, "TerminatedString"]
     = abc
    #> WbR[{49, 50, 51, 0, 52, 53, 54, 0, 55, 56, 57}, Table["TerminatedString", {3}]]
     = {123, 456, EndOfFile}
    #> WbR[{0}, "TerminatedString"] // InputForm
     = ""

    ## UnsignedInteger8
    #> WbR[{96, 94, 141, 162, 141}, Table["UnsignedInteger8", {5}]]
     = {96, 94, 141, 162, 141}
    #> (#==WbR[#,Table["UnsignedInteger8",{50}]])&[RandomInteger[{0, 255}, 50]]
     = True

    ## UnsignedInteger16
    #> WbR[{54, 71, 106, 185, 147, 38, 5, 231}, Table["UnsignedInteger16", {4}]]
     = {18230, 47466, 9875, 59141}
    #> WbR[{0, 0, 128, 128, 255, 255}, Table["UnsignedInteger16", {3}]]
     = {0, 32896, 65535}

    ## UnsignedInteger24
    #> WbR[{78, 35, 226, 225, 84, 236}, Table["UnsignedInteger24", {2}]]
     = {14820174, 15488225}
    #> WbR[{165, 2, 82, 239, 88, 59}, Table["UnsignedInteger24", {2}]]
     = {5374629, 3889391}

    ## UnsignedInteger32
    #> WbR[{213,143,98,112,141,183,203,247}, Table["UnsignedInteger32", {2}]]
     = {1885507541, 4157323149}
    #> WbR[{148,135,230,22,136,141,234,99}, Table["UnsignedInteger32", {2}]]
     = {384206740, 1676316040}

    ## UnsignedInteger64
    #> WbR[{95, 5, 33, 229, 29, 62, 63, 98}, "UnsignedInteger64"]
     = 7079445437368829279
    #> WbR[{134, 9, 161, 91, 93, 195, 173, 74}, "UnsignedInteger64"]
     = 5381171935514265990

    ## UnsignedInteger128
    #> WbR[{108,78,217,150,88,126,152,101,231,134,176,140,118,81,183,220}, "UnsignedInteger128"]
     = 293382001665435747348222619884289871468
    #> WbR[{53,83,116,79,81,100,60,126,202,52,241,48,5,113,92,190}, "UnsignedInteger128"]
     = 253033302833692126095975097811212718901

    ## EndOfFile
    #> WbR[{148}, {"Integer32", "Integer32","Integer32"}]
     = {EndOfFile, EndOfFile, EndOfFile}
    """

    summary_text = "read an object of the specified type"
    readers = _BinaryFormat.get_readers()

    messages = {
        "format": "`1` is not a recognized binary format.",
        "openw": "`1` is open for output.",
        "bfmt": "The stream `1` has been opened with BinaryFormat -> False and cannot be used with binary data.",
    }

    def apply_empty(self, name, n, evaluation):
        "BinaryRead[InputStream[name_, n_Integer]]"
        return self.apply(name, n, None, evaluation)

    def apply(self, name, n, typ, evaluation):
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
    <dl>
      <dt>'BinaryWrite[$channel$, $b$]'
      <dd>writes a single byte given as an integer from 0 to 255.

      <dt>'BinaryWrite[$channel$, {b1, b2, ...}]'
      <dd>writes a sequence of byte.

      <dt>'BinaryWrite[$channel$, "string"]'
      <dd>writes the raw characters in a string.

      <dt>'BinaryWrite[$channel$, $x$, $type$]'
      <dd>writes $x$ as the specified type.

      <dt>'BinaryWrite[$channel$, {$x1$, $x2$, ...}, $type$]'
      <dd>writes a sequence of objects as the specified type.

      <dt>'BinaryWrite[$channel$, {$x1$, $x2$, ...}, {$type1$, $type2$, ...}]'
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

    ## Write then Read as Bytes
    #> WRb[bytes_, form_] := Module[{stream, res={}, byte}, stream = OpenWrite[BinaryFormat -> True]; BinaryWrite[stream, bytes, form]; stream = OpenRead[Close[stream], BinaryFormat -> True]; While[Not[SameQ[byte = BinaryRead[stream], EndOfFile]], res = Join[res, {byte}];]; DeleteFile[Close[stream]]; res]

    ## Byte
    #> WRb[{149, 2, 177, 132}, {"Byte", "Byte", "Byte", "Byte"}]
     = {149, 2, 177, 132}
    #> WRb[{149, 2, 177, 132}, {"Byte", "Byte", "Byte", "Byte"}]
     = {149, 2, 177, 132}
    #> (# == WRb[#, Table["Byte", {50}]]) & [RandomInteger[{0, 255}, 50]]
     = True

    ## Character8
    #> WRb[{"a", "b", "c"}, {"Character8", "Character8", "Character8"}]
     = {97, 98, 99}
    #> WRb[{34, 60, 39}, {"Character8", "Character8", "Character8"}]
     = {51, 52, 54, 48, 51, 57}
    #> WRb[{"ab", "c", "d"}, {"Character8", "Character8", "Character8", "Character8"}]
     = {97, 98, 99, 100}

    ## Character16
    ## TODO

    ## Complex64
    #> WRb[-6.36877988924*^28 + 3.434203392*^9 I, "Complex64"]
     = {80, 201, 77, 239, 201, 177, 76, 79}
    #> WRb[-6.98948862335*^24 + 1.52209021297*^23 I, "Complex64"]
     = {158, 2, 185, 232, 18, 237, 0, 102}
    #> WRb[-1.41079828148*^-19 - 0.013060791418 I, "Complex64"]
     = {195, 142, 38, 160, 238, 252, 85, 188}
    #> WRb[{5, -2054}, "Complex64"]
     = {0, 0, 160, 64, 0, 0, 0, 0, 0, 96, 0, 197, 0, 0, 0, 0}
    #> WRb[Infinity, "Complex64"]
     = {0, 0, 128, 127, 0, 0, 0, 0}
    #> WRb[-Infinity, "Complex64"]
     = {0, 0, 128, 255, 0, 0, 0, 0}
    #> WRb[DirectedInfinity[1 + I], "Complex64"]
     = {0, 0, 128, 127, 0, 0, 128, 127}
    #> WRb[DirectedInfinity[I], "Complex64"]
     = {0, 0, 0, 0, 0, 0, 128, 127}
    ## FIXME (different convention to MMA)
    #> WRb[Indeterminate, "Complex64"]
     = {0, 0, 192, 127, 0, 0, 192, 127}

    ## Complex128
    #> WRb[1.19839770357*^-235 - 2.64656391494*^-54 I,"Complex128"]
     = {102, 217, 1, 163, 234, 98, 40, 15, 243, 104, 116, 15, 48, 57, 208, 180}
    #> WRb[3.22170267142*^134 - 8.98364297498*^198 I,"Complex128"]
     = {219, 161, 12, 126, 47, 94, 220, 91, 189, 66, 29, 68, 147, 11, 62, 233}
    #> WRb[-Infinity, "Complex128"]
     = {0, 0, 0, 0, 0, 0, 240, 255, 0, 0, 0, 0, 0, 0, 0, 0}
    #> WRb[DirectedInfinity[1 - I], "Complex128"]
     = {0, 0, 0, 0, 0, 0, 240, 127, 0, 0, 0, 0, 0, 0, 240, 255}
    #> WRb[DirectedInfinity[I], "Complex128"]
     = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 240, 127}
    ## FIXME (different convention to MMA)
    #> WRb[Indeterminate, "Complex128"]
     = {0, 0, 0, 0, 0, 0, 248, 127, 0, 0, 0, 0, 0, 0, 248, 127}

    ## Complex256
    ## TODO

    ## Integer8
    #> WRb[{5, 2, 11, -4}, {"Integer8", "Integer8", "Integer8", "Integer8"}]
     = {5, 2, 11, 252}
    #> WRb[{127, -128, 0}, {"Integer8", "Integer8", "Integer8"}]
     = {127, 128, 0}

    ## Integer16
    #> WRb[{661, -31567, 6256}, {"Integer16", "Integer16", "Integer16"}]
     = {149, 2, 177, 132, 112, 24}
    #> WRb[{0, 255, -1, 32640, -32640}, Table["Integer16", {5}]]
     = {0, 0, 255, 0, 255, 255, 128, 127, 128, 128}

    ## Integer24
    #> WRb[{-6247016, -6631492}, {"Integer24", "Integer24"}]
     = {152, 173, 160, 188, 207, 154}
    #> WRb[{-1593967, 1989169}, {"Integer24", "Integer24"}]
     = {145, 173, 231, 49, 90, 30}

    ## Integer32
    #> WRb[{-636001327, -236143729}, {"Integer32", "Integer32"}]
     = {209, 99, 23, 218, 143, 187, 236, 241}
    #> WRb[{2024611599, -1139645195}, {"Integer32", "Integer32"}]
     = {15, 31, 173, 120, 245, 100, 18, 188}

    ## Integer64
    #> WRb[{1176115612243989203}, "Integer64"]
     = {211, 18, 152, 2, 235, 102, 82, 16}
    #> WRb[{-8526737900550694619}, "Integer64"]
     = {37, 217, 208, 88, 14, 241, 170, 137}

    ## Integer128
    #> WRb[139827542997232652313568968616424513676, "Integer128"]
     = {140, 32, 24, 199, 10, 169, 248, 117, 123, 184, 75, 76, 34, 206, 49, 105}
    #> WRb[103439096823027953602112616165136677221, "Integer128"]
     = {101, 57, 184, 108, 43, 214, 186, 120, 153, 51, 132, 225, 56, 165, 209, 77}
    #> WRb[-49058912464625098822365387707690163087, "Integer128"]
     = {113, 100, 125, 144, 211, 83, 140, 24, 206, 11, 198, 118, 222, 152, 23, 219}

    ## Real32
    #> WRb[{8.398086656*^9, 1.63880017681*^16}, {"Real32", "Real32"}]
     = {81, 72, 250, 79, 52, 227, 104, 90}
    #> WRb[{5.6052915284*^32, 9.631141*^6}, {"Real32", "Real32"}]
     = {251, 22, 221, 117, 165, 245, 18, 75}
    #> WRb[Infinity, "Real32"]
     = {0, 0, 128, 127}
    #> WRb[-Infinity, "Real32"]
     = {0, 0, 128, 255}
    ## FIXME (different convention to MMA)
    #> WRb[Indeterminate, "Real32"]
     = {0, 0, 192, 127}

    ## Real64
    #> WRb[-5.14646619426*^227, "Real64"]
     = {91, 233, 20, 87, 129, 185, 53, 239}
    #> WRb[-9.69531698809*^20, "Real64"]
     = {187, 67, 162, 67, 122, 71, 74, 196}
    #> WRb[9.67355569764*^159, "Real64"]
     = {132, 48, 80, 125, 157, 4, 38, 97}
    #> WRb[Infinity, "Real64"]
     = {0, 0, 0, 0, 0, 0, 240, 127}
    #> WRb[-Infinity, "Real64"]
     = {0, 0, 0, 0, 0, 0, 240, 255}
    ## FIXME (different convention to MMA)
    #> WRb[Indeterminate, "Real64"]
     = {0, 0, 0, 0, 0, 0, 248, 127}

    ## Real128
    ## TODO

    ## TerminatedString
    #> WRb["abc", "TerminatedString"]
     = {97, 98, 99, 0}
    #> WRb[{"123", "456"}, {"TerminatedString", "TerminatedString", "TerminatedString"}]
     = {49, 50, 51, 0, 52, 53, 54, 0}
    #> WRb["", "TerminatedString"]
    = {0}

    ## UnsignedInteger8
    #> WRb[{96, 94, 141, 162, 141}, Table["UnsignedInteger8", {5}]]
     = {96, 94, 141, 162, 141}
    #> (#==WRb[#,Table["UnsignedInteger8",{50}]])&[RandomInteger[{0, 255}, 50]]
     = True

    ## UnsignedInteger16
    #> WRb[{18230, 47466, 9875, 59141}, Table["UnsignedInteger16", {4}]]
     = {54, 71, 106, 185, 147, 38, 5, 231}
    #> WRb[{0, 32896, 65535}, Table["UnsignedInteger16", {3}]]
     = {0, 0, 128, 128, 255, 255}

    ## UnsignedInteger24
    #> WRb[{14820174, 15488225}, Table["UnsignedInteger24", {2}]]
     = {78, 35, 226, 225, 84, 236}
    #> WRb[{5374629, 3889391}, Table["UnsignedInteger24", {2}]]
     = {165, 2, 82, 239, 88, 59}

    ## UnsignedInteger32
    #> WRb[{1885507541, 4157323149}, Table["UnsignedInteger32", {2}]]
     = {213, 143, 98, 112, 141, 183, 203, 247}
    #> WRb[{384206740, 1676316040}, Table["UnsignedInteger32", {2}]]
     = {148, 135, 230, 22, 136, 141, 234, 99}
    """

    summary_text = "write an object of the specified type"
    messages = {
        "writex": "`1`.",
    }

    writers = _BinaryFormat.get_writers()

    def apply_notype(self, name, n, b, evaluation):
        "BinaryWrite[OutputStream[name_, n_], b_]"
        return self.apply(name, n, b, None, evaluation)

    def apply(self, name, n, b, typ, evaluation):
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
        while i < len(pyb):
            x = pyb[i]
            # Types are "repeated as many times as necessary"
            t = types[i % len(types)]

            # Coerce x
            if t == "TerminatedString":
                x = x.get_string_value() + "\x00"
            elif t.startswith("Real"):
                if isinstance(x, Real):
                    x = x.to_python()
                elif x.has_form("DirectedInfinity", 1):
                    if x.elements[0].get_int_value() == 1:
                        x = float("+inf")
                    elif x.elements[0].get_int_value() == -1:
                        x = float("-inf")
                    else:
                        x = None
                elif isinstance(x, Symbol) and x.get_name() == "System`Indeterminate":
                    x = float("nan")
                else:
                    x = None
                assert x is None or isinstance(x, float)
            elif t.startswith("Complex"):
                if isinstance(x, (Complex, Real, Integer)):
                    x = x.to_python()
                elif x.has_form("DirectedInfinity", 1):
                    x = x.elements[0].to_python(n_evaluation=evaluation)

                    # x*float('+inf') creates nan if x.real or x.imag are zero
                    x = complex(
                        x.real * float("+inf") if x.real != 0 else 0,
                        x.imag * float("+inf") if x.imag != 0 else 0,
                    )
                elif isinstance(x, Symbol) and x.get_name() == "System`Indeterminate":
                    x = complex(float("nan"), float("nan"))
                else:
                    x = None
            elif t.startswith("Character"):
                if isinstance(x, Integer):
                    x = [String(char) for char in str(x.get_int_value())]
                    pyb = list(chain(pyb[:i], x, pyb[i + 1 :]))
                    x = pyb[i]
                if isinstance(x, String) and len(x.get_string_value()) > 1:
                    x = [String(char) for char in x.get_string_value()]
                    pyb = list(chain(pyb[:i], x, pyb[i + 1 :]))
                    x = pyb[i]
                x = x.get_string_value()
            elif t == "Byte" and isinstance(x, String):
                if len(x.get_string_value()) > 1:
                    x = [String(char) for char in x.get_string_value()]
                    pyb = list(chain(pyb[:i], x, pyb[i + 1 :]))
                    x = pyb[i]
                x = ord(x.get_string_value())
            else:
                x = x.get_int_value()

            if x is None:
                return evaluation.message(SymbolBinaryWrite, "nocoerce", b)

            try:
                self.writers[t](stream.io, x)
            except struct.error:
                return evaluation.message(SymbolBinaryWrite, "nocoerce", b)
            i += 1

        try:
            stream.io.flush()
        except IOError as err:
            evaluation.message(SymbolBinaryWrite, "writex", err.strerror)
        return channel


# TODO: BinaryReadList, BinaryWrite, BinaryReadList
