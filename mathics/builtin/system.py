# -*- coding: utf-8 -*-

"""
Global System Information
"""

import _thread
import gc
import os
import platform
import subprocess
import sys

from pympler.asizeof import asizeof

from mathics import version_string
from mathics.core.atoms import Integer, Integer0, IntegerM1, Real, String
from mathics.core.attributes import A_CONSTANT
from mathics.core.builtin import Builtin, Predefined
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import SymbolNull
from mathics.core.systemsymbols import (
    SymbolFailed,
    SymbolNone,
    SymbolRule,
    SymbolSequence,
)
from mathics.version import __version__

try:
    import psutil
except ImportError:
    have_psutil = False
else:
    have_psutil = True

sort_order = "mathics.builtin.global-system-information"


class Breakpoint(Builtin):
    """<url>:Python breakpoint():https://docs.python.org/3/library/functions.html#breakpoint</url>

    <dl>
      <dt>'Breakpoint[]'
      <dd> Invoke a Python breakpoint.

      This can be used for debugging the Mathics3 implementation, but \
      if you are familiar with Python, it might assist in debugging a Mathics3 programs \
      as well.

      By default, the Python debugger ('pdb') is loaded. For loading other debuggers, \
      change the environment variable 'PYTHONBREAKPOINT'.
    </dl>


    Mathics3 code includes a breakpoint handler function, 'mathics.disabled_breakpoint' which \
    reports whether 'Breakpoint[]' was encountered in Mathics3, or 'breakpoint()' was encountered \
    in the Mathics3 source code. In contrast to 'pdb', 'trepan3k' and other handlers, this breakpoint \
    handler does not stop inside, it just reports.

    Here is how to use 'mathics.disabled_breakpoint':

    >> SetEnvironment["PYTHONBREAKPOINT" -> "mathics.disabled_breakpoint"];

    >> Breakpoint[]
    = Hit disabled breakpoint.
    = Breakpoint[]

    The environment variable 'PYTHONBREAKPOINT' can be changed at runtime to switch \
    'breakpoint()' and 'Breakpoint[]' behavior.
    """

    summary_text = "invoke Python breakpoint()"

    def eval(self, evaluation: Evaluation):
        "Breakpoint[]"
        breakpoint()


class CommandLine(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/\\$CommandLine.html</url>
    <dl>
    <dt>'\\$CommandLine'
      <dd>is a list of strings passed on the command line to launch the Mathics3 session.
    </dl>

    >> $CommandLine
     = {...}
    """

    name = "$CommandLine"
    summary_text = (
        "get the command line arguments passed when the current Mathics3 "
        "session was launched"
    )

    def evaluate(self, evaluation: Evaluation) -> Expression:
        return ListExpression(*(String(arg) for arg in sys.argv))


class Environment(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Environment.html</url>

    <dl>
      <dt>'Environment'[$var$]
      <dd>gives the value of an operating system environment variable.
    </dl>

    S> Environment["HOME"]
     = ...

    See also <url>
    :'GetEnvironment':
    /doc/reference-of-built-in-symbols/global-system-information/getenvironment/</url> and <url>
    :'SetEnvironment':
    /doc/reference-of-built-in-symbols/global-system-information/setenvironment/</url>.
    """

    summary_text = "list the system environment variables"

    def eval(self, var, evaluation: Evaluation):
        "Environment[var_String]"
        env_var = var.get_string_value()
        if env_var not in os.environ:
            return SymbolFailed
        else:
            return String(os.environ[env_var])


class GetEnvironment(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/GetEnvironment.html</url>

    <dl>
      <dt>'GetEnvironment'["$var$"]
      <dd>gives the setting corresponding to the variable "var" in the operating \
      system environment.

      <dt>'GetEnvironment'[{"$var_1$", "$var_2$", ...}]
      <dd>gives a list rules for each of the environment variables listed.

      <dt>'GetEnvironment[]'
      <dd>gives a list rules for all environment variables.
    </dl>

    On POSIX systems, the following gets the users HOME directory:
    S> GetEnvironment["HOME"]
    = ...

    We can get both the HOME directory and the user name in one go:
    S> GetEnvironment[{"HOME", "USER"}]
    = ...

    Arguments however must be strings:
    S> GetEnvironment[HOME]
    : HOME is not ALL or a string or a list of strings.
    = GetEnvironment[HOME]

    See also <url>
    :'Environment':
    /doc/reference-of-built-in-symbols/global-system-information/environment/</url> and <url>
    :'SetEnvironment':
    /doc/reference-of-built-in-symbols/global-system-information/setenvironment/</url>.
    """

    messages = {"name": "`1` is not ALL or a string or a list of strings."}
    summary_text = "retrieve the value of a system environment variable"

    def eval(self, var, evaluation: Evaluation):
        "GetEnvironment[var___]"
        if isinstance(var, String):
            env_var = var.value
            tup = (
                var,
                (
                    SymbolNone
                    if env_var not in os.environ
                    else String(os.environ[env_var])
                ),
            )

            return Expression(SymbolRule, *tup)

        if (
            isinstance(var, ListExpression)
            or hasattr(var, "head")
            and var.head == SymbolSequence
        ):
            if len(var.elements) == 0:
                rules = [
                    Expression(SymbolRule, String(name), String(value))
                    for name, value in os.environ.items()
                ]
                return ListExpression(*rules)
            else:
                rules = []
                for env_var in var.elements:
                    if not isinstance(env_var, String):
                        evaluation.message("GetEnvironment", "name", var)
                        return None
                    rules.append(
                        Expression(
                            SymbolRule,
                            env_var,
                            String(os.environ.get(env_var.value, "")),
                        )
                    )
                return ListExpression(*rules)
        else:
            evaluation.message("GetEnvironment", "name", var)


class Machine(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/\\$Machine.html</url>

    <dl>
    <dt>'\\$Machine'
        <dd>returns a string describing the type of computer system on which the \
            Mathics3 is being run.
    </dl>

    S> $Machine
     = ...
    """

    name = "$Machine"
    summary_text = "get the OS platform of the system running Mathics3"

    def evaluate(self, evaluation: Evaluation) -> String:
        return String(sys.platform)


class MachineName(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/MachineName.html</url>

    <dl>
      <dt>'\\$MachineName'
      <dd>is a string that gives the assigned name of the computer on which Mathics3 \
          is being run, if such a name is defined.
    </dl>

    S> $MachineName
     = ...
    """

    name = "$MachineName"
    summary_text = "get the name of computer that Mathics3 is running"

    def evaluate(self, evaluation: Evaluation) -> String:
        return String(platform.uname().node)


class MathicsVersion(Predefined):
    r"""
    ## <url>:mathics native:</url>

    <dl>
      <dt>'MathicsVersion'
      <dd>this string is the version of Mathics we are running.
    </dl>

    >> MathicsVersion
    = ...
    """

    summary_text = "get the version of the Mathics3 kernel"

    def evaluate(self, evaluation: Evaluation) -> String:
        return String(__version__)


class MaxLengthIntStringConversion(Predefined):
    """
    <url>:Python 3.11 Integer string conversion length limitation:
    https://docs.python.org/3.11/library/stdtypes.html#int-max-str-digits</url>
    <dl>
      <dt>'$MaxLengthIntStringConversion'
      <dd>A positive system integer that fixes the largest size of the string that \
          can appear when converting an 'Integer' value into a 'String'. When the \
          string value is too large, then the middle of the integer contains \
          an indication of the number of digits elided inside << >>.

          If '\\$MaxLengthIntStringConversion' is set to 0, there is no \
          bound. Aside from 0, 640 is the smallest value allowed.

          The initial value can be set via environment variable \
          'DEFAULT_MAX_STR_DIGITS'. If that is not set, \
          the default value is 7000.
    </dl>

    Although Mathics3 can represent integers of arbitrary size, when it formats \
    the value for display, there can be nonlinear behavior in printing the decimal string \
    or converting it to a 'String'.

    Python, in version 3.11 and up, puts a default limit on the size of \
    the number of digits allows when converting a large integer into \
    a string.

    Show the default value of '\\$MaxLengthIntStringConversion':
    >> $MaxLengthIntStringConversion
     = ...

    500! is a 1135-digit number:
    >> 500! //ToString//StringLength
     = ...

    We first set '\\$MaxLengthIntStringConversion' to the smallest value allowed, \
    so that we can see the truncation of digits in the middle:
    >> $MaxLengthIntStringConversion = 640
    ## Pyston 2.3.5 returns 0 while CPython returns 640
    ## Therefore output testing below is generic.
     = ...

    Note that setting '\\$MaxLengthIntStringConversion' has an effect only on Python 3.11 and later;
    Pyston 2.x however ignores this.

    Now when we print the string value of 500! and Pyston 2.x is not used, \
    the middle digits are removed:
    >> 500!
     = ...

    To see this easier, manipulate the result as 'String':

    >> bigFactorial = ToString[500!]; StringTake[bigFactorial, {310, 330}]
     = ...

    The <<501>> indicates that 501 digits have been omitted in the string conversion.

    Other than 0, an 'Integer' value less than 640 is not accepted:
    >> $MaxLengthIntStringConversion = 10
     : 10 is not 0 or an Integer value greater than 640.
     = ...
    """

    attributes = A_CONSTANT
    messages = {"inv": "`1` is not 0 or an Integer value greater than 640."}
    name = "$MaxLengthIntStringConversion"
    summary_text = (
        "get the maximum length for which an integer is converted to a String"
    )

    def evaluate(self, evaluation: Evaluation) -> Integer:
        try:
            return Integer(sys.get_int_max_str_digits())
        except AttributeError:
            return Integer0

    def eval_set(self, expr, evaluation):
        """Set[$MaxLengthIntStringConversion, expr_]"""
        if isinstance(expr, Integer):
            try:
                sys.set_int_max_str_digits(expr.value)
                return self.evaluate(evaluation)
            except AttributeError:
                if expr.value != 0 and expr.value < 640:
                    evaluation.message("$MaxLengthIntStringConversion", "inv", expr)
                return Integer0
            except ValueError:
                pass

        evaluation.message("$MaxLengthIntStringConversion", "inv", expr)
        return self.evaluate(evaluation)

    def eval_setdelayed(self, expr, evaluation: Evaluation):
        """SetDelayed[$MaxLengthIntStringConversion, expr_]"""
        return self.eval_set(expr)


class MemoryInUse(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/MemoryInUse.html</url>

    <dl>
      <dt>'MemoryInUse[]'
      <dd>Returns the amount of memory used by all of the definitions objects if we can determine that; -1 otherwise.
    </dl>

    >> MemoryInUse[]
     = ...
    """

    summary_text = "get the number of bytes of memory currently being used by Mathics3"

    def eval(self, evaluation: Evaluation) -> Integer:
        """MemoryInUse[]"""
        gc.collect()
        return Integer(asizeof(evaluation.definitions))


class Packages(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Packages.html</url>

    <dl>
      <dt>'\\$Packages'
      <dd>returns a list of the contexts corresponding to all packages which have \
          been loaded into Mathics.
    </dl>

    S> $Packages
    = {ImportExport`, XML`, Internal`, System`, Global`}
    """

    summary_text = "list the packages loaded in the current session"
    name = "$Packages"
    rules = {
        "$Packages": '{"ImportExport`",  "XML`","Internal`", "System`", "Global`"}'
    }


class ParentProcessID(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/$ParentProcessID.html</url>

    <dl>
      <dt>'\$ParentProcesID'
      <dd>gives the ID assigned to the process which invokes Mathics3 by the operating \
          system under which it is run.
    </dl>

    >> $ParentProcessID
     = ...

    """

    name = "$ParentProcessID"
    summary_text = "get process id of the process that invoked Mathics3"

    def evaluate(self, evaluation: Evaluation) -> Integer:
        return Integer(os.getppid())


class ProcessID(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/ProcessID.html</url>

    <dl>
      <dt>'\$ProcessID'
      <dd>gives the ID assigned to the Mathics3 process by the operating system under \
          which it is run.
    </dl>

    >> $ProcessID
     = ...
    """

    name = "$ProcessID"
    summary_text = "get process id of the Mathics process"

    def evaluate(self, evaluation: Evaluation) -> Integer:
        return Integer(os.getpid())


class ProcessorType(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ProcessorType.html</url>

    <dl>
      <dt>'\\$ProcessorType'
      <dd>gives a string giving the architecture of the processor on which \
          Mathics3 is being run.
    </dl>

    >> $ProcessorType
    = ...
    """

    name = "$ProcessorType"

    summary_text = "get the name of the architecture of the processor over which Mathics3 is running"

    def evaluate(self, evaluation):
        return String(platform.machine())


class PythonImplementation(Predefined):
    r"""
    ## <url>:PythonImplementation native symbol:</url>

    <dl>
    <dt>'\$PythonImplementation'
        <dd>gives a string indication the Python implementation used to run Mathics3.
    </dl>

    >> $PythonImplementation
    = ...
    """

    name = "$PythonImplementation"

    summary_text = "get the name of the Python implementation running Mathics3"

    def evaluate(self, evaluation: Evaluation):
        from mathics.system_info import python_implementation

        return String(python_implementation())


class Run(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Run.html</url>

    <dl>
      <dt>'Run'[$command$]
      <dd>runs command as an external operating system command, returning the exit \
         code returned from running the system command.
    </dl>

    X> Run["date"]
     = ...
    """

    summary_text = "run a system command"

    def eval(self, command, evaluation: Evaluation):
        "Run[command_String]"
        command_str = command.to_python()
        return Integer(subprocess.call(command_str, shell=True))


class ScriptCommandLine(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ScriptCommandLine.html</url>

    <dl>
      <dt>'\\$ScriptCommandLine'
      <dd>is a list of string arguments when running the kernel is script mode.
    </dl>

    >> $ScriptCommandLine
     = {...}
    """

    summary_text = "list of command line arguments"
    name = "$ScriptCommandLine"

    def evaluate(self, evaluation: Evaluation):
        try:
            dash_index = sys.argv.index("--")
        except ValueError:
            # not run in script mode
            return ListExpression()
        scriptname = "" if dash_index == 0 else sys.argv[dash_index - 1]
        params = [scriptname] + [s for s in sys.argv[dash_index + 1 :]]
        return to_mathics_list(*params, elements_conversion_fn=String)


class SessionID(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/SessionID.html</url>

    <dl>
       <dt>'\$SessionID'
       <dd>is a number which is unique to a particular \Mathics System session.
    </dl>

    X> $SessionID
     = ...
    """

    name = "$SessionID"
    summary_text = "get a unique session id"

    def evaluate(self, evaluation: Evaluation) -> Integer:
        # In theory, it is possible for two different sessions to have
        # the same id since threading ID's are recycled. Also in
        # theory, on different processes the thread numbers might be
        # the same.  In practice, however, this is unlikely.  What we
        # want here is something that is likely to be available on all
        # platforms and OS's including enscripten. I had considered
        # folding in the os.getpid() value, but this is not available
        # on the enscripten platform.
        return Integer(_thread.get_ident())


class SetEnvironment(Builtin):
    """
     <url>:WMA link:https://reference.wolfram.com/language/ref/SetEnvironment.html</url>

     <dl>
       <dt>'SetEnvironment'["$var$" -> "$value$"]
       <dd>sets the value of an operating system environment variable.

       <dt>'SetEnvironment'[{"$var$" -> "$value$", ...}]
       <dd>sets more than one environment variable.
     </dl>

     Set a single environment variable:
     S> SetEnvironment["FOO" -> "bar"]

     See that the environment variable has changed:
     S> GetEnvironment["FOO"]
      = FOO -> bar

     Set two environment variables:
     S> SetEnvironment[{"FOO" -> "baz", "A" -> "B"}]

     See that the environment variable has changed:
     S> GetEnvironment["FOO"]
      = FOO -> baz

     Environment values must be strings:

     S> SetEnvironment["FOO" -> 5]
      : 5 must be a string or None.
      = $Failed

     S> GetEnvironment["FOO"]
      = FOO -> baz

    If the environment name is not a string, the evaluation fails without a message.

     S> SetEnvironment[1 -> "bar"]
      = SetEnvironment[1 -> bar]

     See also <url>
     :'Environment':
     /doc/reference-of-built-in-symbols/global-system-information/environment/</url> and <url>
     :'GeEnvironment':
     /doc/reference-of-built-in-symbols/global-system-information/getenvironment/</url>.
    """

    messages = {"value": "`1` must be a string or None."}
    summary_text = "set system environment variable(s)"

    def eval(self, rule, evaluation):
        "SetEnvironment[rule_Rule]"
        env_var_name, env_var_value = rule.elements
        # WMA does not give an error message if env_var_name is not a String - weird.
        if not isinstance(env_var_name, String):
            return None

        if not (env_var_value is SymbolNone or isinstance(env_var_value, String)):
            evaluation.message("SetEnvironment", "value", env_var_value)
            return SymbolFailed

        os.environ[env_var_name.value] = (
            None if None is SymbolNone else env_var_value.value
        )
        return SymbolNull

    def eval_list(self, rules: Expression, evaluation: Evaluation):
        "SetEnvironment[{rules__}]"

        # All the rules must be of the form
        for rule in rules.elements:
            if not rule.has_form("System`Rule", 2):
                return None
            if not isinstance(rule.elements[0], String):
                return None

        for rule in rules.elements:
            self.eval(rule, evaluation)
        return SymbolNull

        return SymbolNull


class Share(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Share.html</url>

    <dl>
      <dt>'Share[]'
      <dd>release memory forcing Python to do garbage collection. If Python package \
          'psutil' installed is the amount of released memoryis returned. Otherwise \
          returns $0$. This function differs from WMA which tries to reduce the amount \
          of memory required to store definitions, by reducing duplicated definitions.
      <dt>'Share[Symbol]'
      <dd>Does the same thing as 'Share[]'; Note: this function differs from WMA which \
          tries to reduce the amount of memory required to store definitions associated \
          to $Symbol$.

    </dl>

    >> Share[]
     = ...
    """

    summary_text = "force Python garbage collection"

    def eval(self, evaluation: Evaluation) -> Integer:
        """Share[]"""
        # TODO: implement a routine that swap all the definitions,
        # collecting repeated symbols and expressions, and then
        # replace them by references.
        # Return the amount of memory recovered.
        if have_psutil:
            totalmem = psutil.virtual_memory().available
            gc.collect()
            return Integer(totalmem - psutil.virtual_memory().available)
        else:
            gc.collect()
            return Integer0

    def eval_with_symbol(self, symbol, evaluation: Evaluation) -> Integer:
        """Share[symbol_Symbol]"""
        # TODO: implement a routine that swap all the definitions,
        # collecting repeated symbols and expressions, and then
        # replace them by references.
        # Return the amount of memory recovered.
        if have_psutil:
            totalmem = psutil.virtual_memory().available
            gc.collect()
            return Integer(totalmem - psutil.virtual_memory().available)
        else:
            gc.collect()
            return Integer0


class SystemID(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/SystemID.html</url>

    <dl>
       <dt>'\$SystemID'
       <dd>is a short string that identifies the type of computer system on which the \Mathics is being run.
    </dl>

    X> $SystemID
     = linux
    """

    name = "$SystemID"
    summary_text = "get id for the type of computer system"

    def evaluate(self, evaluation: Evaluation) -> String:
        return String(sys.platform)


class SystemWordLength(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/SystemWordLength.html</url>

    <dl>
      <dt>'\$SystemWordLength'
      <dd>gives the effective number of bits in raw machine words on the computer \
          system where Mathics3 is running.
    </dl>

    X> $SystemWordLength
    = 64
    """

    name = "$SystemWordLength"
    summary_text = "get word length of computer system"

    def evaluate(self, evaluation: Evaluation) -> Integer:
        # https://docs.python.org/3/library/platform.html#module-platform
        # says it is more reliable to get bits using sys.maxsize
        # than platform.architecture()[0]
        size = 128
        while not sys.maxsize > 2**size:
            size >>= 1
        return Integer(size << 1)


class UserName(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/UserName.html</url>

    <dl>
      <dt>\$UserName
      <dd>returns the login name, according to the operative system, of the user that started the current
      \Mathics session.
    </dl>

    X> $UserName
     = ...
    """

    name = "$UserName"
    summary_text = "get login name of the user that invoked the current session"

    def evaluate(self, evaluation: Evaluation) -> String:
        try:
            user = os.getlogin()
        except Exception:
            import pwd

            user = pwd.getpwuid(os.getuid())[0]
        return String(user)


class Version(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Version.html</url>

    <dl>
      <dt>'$Version'
      <dd>returns a string with the current Mathics version and the versions of relevant libraries.
    </dl>

    >> $Version
     = Mathics3 ...
    """

    name = "$Version"
    summary_text = "get the current Mathics3 version"

    def evaluate(self, evaluation: Evaluation) -> String:
        return String(version_string.replace("\n", " "))


class VersionNumber(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/VersionNumber.html</url>

    <dl>
      <dt>'\$VersionNumber'
      <dd>is a real number which gives the current Wolfram Language version that \Mathics tries to be compatible with.
    </dl>

    >> $VersionNumber
    = ...
    """

    name = "$VersionNumber"
    value = 10.0
    summary_text = "get the version number of the current Mathics3 Kernel"

    def evaluate(self, evaluation: Evaluation) -> Real:
        # Make this be whatever the latest Mathematica release is,
        # assuming we are trying to be compatible with this.
        return Real(self.value)


if have_psutil:

    class SystemMemory(Predefined):
        """
        <url>:WMA link:https://reference.wolfram.com/language/ref/SystemMemory.html</url>

        <dl>
          <dt>'\\$SystemMemory'
          <dd>Returns the total amount of physical memory.
        </dl>

        >> $SystemMemory
         = ...
        """

        name = "$SystemMemory"
        summary_text = "get the total amount of physical memory in the system"

        def evaluate(self, evaluation: Evaluation) -> Integer:
            totalmem = psutil.virtual_memory().total
            return Integer(totalmem)

    class MemoryAvailable(Builtin):
        """
        <url>:WMA link:https://reference.wolfram.com/language/ref/MemoryAvailable.html</url>

        <dl>
          <dt>'MemoryAvailable'
          <dd>Returns the amount of the available physical memory.
        </dl>

        >> MemoryAvailable[]
         = ...

        The relationship between \\$SystemMemory, MemoryAvailable, and MemoryInUse:
        >> $SystemMemory > MemoryAvailable[] > MemoryInUse[]
         = True
        """

        summary_text = "get the available amount of physical memory in the system"

        def eval(self, evaluation: Evaluation) -> Integer:
            """MemoryAvailable[]"""
            totalmem = psutil.virtual_memory().available
            return Integer(totalmem)

else:

    class SystemMemory(Predefined):
        """
        <url>:WMA link:https://reference.wolfram.com/language/ref/SystemMemory.html</url>

        <dl>
          <dt>'$SystemMemory'
          <dd>Returns the total amount of physical memory when Python module "psutil" is installed.
          This system however doesn't have that installed, so -1 is returned instead.
        </dl>

        >> $SystemMemory
         = -1
        """

        summary_text = "the total amount of physical memory in the system"
        name = "$SystemMemory"

        def evaluate(self, evaluation: Evaluation) -> Integer:
            return IntegerM1

    class MemoryAvailable(Builtin):
        """
        <url>:WMA link:https://reference.wolfram.com/language/ref/MemoryAvailable.html</url>

        <dl>
          <dt>'MemoryAvailable'
          <dd>Returns the amount of the available physical when Python module "psutil" is installed.
          This system however doesn't have that installed, so -1 is returned instead.
        </dl>

        >> MemoryAvailable[]
         = -1
        """

        summary_text = "get the available amount of physical memory in the system"

        def eval(self, evaluation: Evaluation) -> Integer:
            """MemoryAvailable[]"""
            return IntegerM1
