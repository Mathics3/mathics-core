# -*- coding: utf-8 -*-

"""
Global System Information
"""

sort_order = "mathics.builtin.global-system-information"

import gc
import os
import platform
import sys
import subprocess

from mathics import version_string
from mathics.builtin.base import Builtin, Predefined
from mathics.core.atoms import (
    Integer,
    Integer0,
    IntegerM1,
    Real,
    String,
)
from mathics.core.convert.expression import to_mathics_list
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.systemsymbols import (
    SymbolFailed,
    SymbolRule,
)
from mathics.version import __version__

try:
    import psutil
except:
    have_psutil = False
else:
    have_psutil = True


class Aborted(Predefined):
    """
    <dl>
    <dt>'$Aborted'
        <dd>is returned by a calculation that has been aborted.
    </dl>
    """

    summary_text = "return value for aborted evaluations"
    name = "$Aborted"


class CommandLine(Predefined):
    """
    <dl>
    <dt>'$CommandLine'
      <dd>is a list of strings passed on the command line to launch the Mathics session.
    </dl>
    >> $CommandLine
     = {...}
    """

    summary_text = "the command line arguments passed when the current Mathics session was launched"
    name = "$CommandLine"

    def evaluate(self, evaluation) -> Expression:
        return ListExpression(*(String(arg) for arg in sys.argv))


class Environment(Builtin):
    """
    <dl>
      <dt>'Environment[$var$]'
      <dd>gives the value of an operating system environment variable.
    </dl>
    X> Environment["HOME"]
     = ...
    """

    summary_text = "list the system environment variables"

    def apply(self, var, evaluation):
        "Environment[var_String]"
        env_var = var.get_string_value()
        if env_var not in os.environ:
            return SymbolFailed
        else:
            return String(os.environ[env_var])


class Failed(Predefined):
    """
    <dl>
    <dt>'$Failed'
        <dd>is returned by some functions in the event of an error.
    </dl>

    #> Get["nonexistent_file.m"]
     : Cannot open nonexistent_file.m.
     = $Failed
    """

    summary_text = "retrieved result for failed evaluations"
    name = "$Failed"


class GetEnvironment(Builtin):
    """
    <dl>
    <dt>'GetEnvironment["$var$"]'
        <dd>gives the setting corresponding to the variable "var" in the operating system environment.
    </dl>

    X> GetEnvironment["HOME"]
    = ...
    """

    summary_text = "retrieve the value of a system environment variable"

    def apply(self, var, evaluation):
        "GetEnvironment[var___]"
        if isinstance(var, String):
            env_var = var.get_string_value()
            tup = (
                env_var,
                "System`None"
                if env_var not in os.environ
                else String(os.environ[env_var]),
            )

            return Expression(SymbolRule, *tup)

        env_vars = var.get_sequence()
        if len(env_vars) == 0:
            rules = [
                Expression(SymbolRule, name, value)
                for name, value in os.environ.items()
            ]
            return ListExpression(*rules)


class Machine(Predefined):
    """
    <dl>
    <dt>'$Machine'
        <dd>returns a string describing the type of computer system on which the Mathics is being run.
    </dl>
    X> $Machine
     = linux
    """

    summary_text = "the type of computer system over whith Mathics is running"
    name = "$Machine"

    def evaluate(self, evaluation) -> String:
        return String(sys.platform)


class MachineName(Predefined):
    """
    <dl>
      <dt>'$MachineName'
      <dd>is a string that gives the assigned name of the computer on which Mathics is being run, if such a name is defined.
    </dl>
    X> $MachineName
     = buster
    """

    summary_text = "the name of computer over whith Mathics is running"
    name = "$MachineName"

    def evaluate(self, evaluation) -> String:
        return String(platform.uname().node)


class MathicsVersion(Predefined):
    r"""
    <dl>
      <dt>'MathicsVersion'
      <dd>this string is the version of Mathics we are running.
    </dl>

    >> MathicsVersion
    = ...
    """
    summary_text = "the version of the mathics core"

    def evaluate(self, evaluation) -> String:
        return String(__version__)


class Packages(Predefined):
    """
    <dl>
      <dt>'$Packages'
      <dd>returns a list of the contexts corresponding to all packages which have been loaded into Mathics.
    </dl>

    X> $Packages
    = {ImportExport`,XML`,Internal`,System`,Global`}
    #> MemberQ[$Packages, "System`"]
    = True
    """

    summary_text = "list the packages loaded in the current session"
    name = "$Packages"
    rules = {
        "$Packages": '{"ImportExport`",  "XML`","Internal`", "System`", "Global`"}'
    }


class ParentProcessID(Predefined):
    r"""
    <dl>
      <dt>'$ParentProcesID'
      <dd>gives the ID assigned to the process which invokes the \Mathics by the operating system under which it is run.
    </dl>

    >> $ParentProcessID
     = ...

    #> Head[$ParentProcessID] == Integer
     = True
    """
    summary_text = "id of the process that invoked Mathics"
    name = "$ParentProcessID"

    def evaluate(self, evaluation) -> Integer:
        return Integer(os.getppid())


class ProcessID(Predefined):
    r"""
    <dl>
      <dt>'$ProcessID'
      <dd>gives the ID assigned to the \Mathics process by the operating system under which it is run.
    </dl>

    >> $ProcessID
     = ...

    #> Head[$ProcessID] == Integer
     = True
    """
    summary_text = "id of the Mathics process"
    name = "$ProcessID"

    def evaluate(self, evaluation) -> Integer:
        return Integer(os.getpid())


class ProcessorType(Predefined):
    r"""
    <dl>
    <dt>'$ProcessorType'
        <dd>gives a string giving the architecture of the processor on which the \Mathics is being run.
    </dl>
    X> $ProcessorType
    = x86_64
    """
    summary_text = (
        "name of the architecture of the processor over which Mathics is running"
    )
    name = "$ProcessorType"

    def evaluate(self, evaluation):
        return String(platform.machine())


class ScriptCommandLine(Predefined):
    """
    <dl>
      <dt>'$ScriptCommandLine'
      <dd>is a list of string arguments when running the kernel is script mode.
    </dl>
    >> $ScriptCommandLine
     = {...}
    """

    summary_text = "list of command line arguments"
    name = "$ScriptCommandLine"

    def evaluate(self, evaluation):
        try:
            dash_index = sys.argv.index("--")
        except ValueError:
            # not run in script mode
            return ListExpression()
        scriptname = "" if dash_index == 0 else sys.argv[dash_index - 1]
        parms = [scriptname] + [s for s in sys.argv[dash_index + 1 :]]
        return to_mathics_list(*parms, elements_conversion_fn=String)


class Run(Builtin):
    """
    <dl>
      <dt>'Run[$command$]'
      <dd>runs command as an external operating system command, returning the exit code obtained.
    </dl>
    X> Run["date"]
     = ...
    """

    summary_text = "run a system command"

    def apply(self, command, evaluation):
        "Run[command_String]"
        command_str = command.to_python()
        return Integer(subprocess.call(command_str, shell=True))


class SystemID(Predefined):
    r"""
    <dl>
       <dt>'$SystemID'
       <dd>is a short string that identifies the type of computer system on which the \Mathics is being run.
    </dl>
    X> $SystemID
     = linux
    """
    summary_text = "id for the type of computer system"
    name = "$SystemID"

    def evaluate(self, evaluation) -> String:
        return String(sys.platform)


class SystemWordLength(Predefined):
    r"""
    <dl>
      <dt>'$SystemWordLength'
      <dd>gives the effective number of bits in raw machine words on the computer system where \Mathics is running.
    </dl>
    X> $SystemWordLength
    = 64

    #> Head[$SystemWordLength] == Integer
     = True
    """
    summary_text = "word length of computer system"
    name = "$SystemWordLength"

    def evaluate(self, evaluation) -> Integer:
        # https://docs.python.org/3/library/platform.html#module-platform
        # says it is more reliable to get bits using sys.maxsize
        # than platform.architecture()[0]
        size = 128
        while not sys.maxsize > 2**size:
            size >>= 1
        return Integer(size << 1)


class UserName(Predefined):
    r"""
    <dl>
      <dt>$UserName
      <dd>returns the login name, according to the operative system, of the user that started the current
      \Mathics session.
    </dl>

    X> $UserName
     = ...
    """
    summary_text = "login name of the user that invoked the current session"
    name = "$UserName"

    def evaluate(self, evaluation) -> String:
        try:
            user = os.getlogin()
        except:
            import pwd

            user = pwd.getpwuid(os.getuid())[0]
        return String(user)


class Version(Predefined):
    """
    <dl>
      <dt>'$Version'
      <dd>returns a string with the current Mathics version and the versions of relevant libraries.
    </dl>

    >> $Version
     = Mathics ...
    """

    summary_text = "the current Mathics version"
    name = "$Version"

    def evaluate(self, evaluation) -> String:
        return String(version_string.replace("\n", " "))


class VersionNumber(Predefined):
    r"""
    <dl>
      <dt>'$VersionNumber'
      <dd>is a real number which gives the current Wolfram Language version that \Mathics tries to be compatible with.
    </dl>

    >> $VersionNumber
    = ...
    """
    summary_text = "the version number of the current Mathics core"
    name = "$VersionNumber"
    value = 10.0

    def evaluate(self, evaluation) -> Real:
        # Make this be whatever the latest Mathematica release is,
        # assuming we are trying to be compatible with this.
        return Real(self.value)


if have_psutil:

    class SystemMemory(Predefined):
        """
        <dl>
          <dt>'$SystemMemory'
          <dd>Returns the total amount of physical memory.
        </dl>

        >> $SystemMemory
         = ...
        """

        summary_text = "the total amount of physical memory in the system"
        name = "$SystemMemory"

        def evaluate(self, evaluation) -> Integer:
            totalmem = psutil.virtual_memory().total
            return Integer(totalmem)

    class MemoryAvailable(Builtin):
        """
        <dl>
          <dt>'MemoryAvailable'
          <dd>Returns the amount of the available physical memory.
        </dl>

        >> MemoryAvailable[]
         = ...

        The relationship between $SystemMemory, MemoryAvailable, and MemoryInUse:
        >> $SystemMemory > MemoryAvailable[] > MemoryInUse[]
         = True
        """

        summary_text = "the available amount of physical memory in the system"

        def apply(self, evaluation) -> Integer:
            """MemoryAvailable[]"""
            totalmem = psutil.virtual_memory().available
            return Integer(totalmem)

else:

    class SystemMemory(Predefined):
        """
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

        def evaluate(self, evaluation) -> Integer:
            return IntegerM1

    class MemoryAvailable(Builtin):
        """
        <dl>
          <dt>'MemoryAvailable'
          <dd>Returns the amount of the available physical when Python module "psutil" is installed.
          This system however doesn't have that installed, so -1 is returned instead.
        </dl>

        >> MemoryAvailable[]
         = -1
        """

        summary_text = "the available amount of physical memory in the system"

        def apply(self, evaluation) -> Integer:
            """MemoryAvailable[]"""
            return Integer(-1)


class MemoryInUse(Builtin):
    """
    <dl>
      <dt>'MemoryInUse[]'
      <dd>Returns the amount of memory used by all of the definitions objects if we can determine that; -1 otherwise.
    </dl>

    >> MemoryInUse[]
     = ...
    """

    summary_text = "number of bytes of memory currently being used by Mathics"

    def apply_0(self, evaluation) -> Integer:
        """MemoryInUse[]"""
        # Partially borrowed from https://code.activestate.com/recipes/577504/
        from itertools import chain
        from sys import getsizeof

        definitions = evaluation.definitions
        seen = set()
        try:
            default_size = getsizeof(0)
        except TypeError:
            return IntegerM1

        handlers = {
            tuple: iter,
            list: iter,
            dict: (lambda d: chain.from_iterable(d.items())),
            set: iter,
            frozenset: iter,
        }

        def sizeof(obj):
            if id(obj) in seen:
                return 0
            seen.add(id(obj))
            s = getsizeof(obj, default_size)
            for typ, handler in handlers.items():
                if isinstance(obj, typ):
                    s += sum(map(sizeof, handler(obj)))
                    break
            return s

        return Integer(sizeof(definitions))


class Share(Builtin):
    """
    <dl>
      <dt>'Share[]'
      <dd>release memory forcing Python to do garbage collection. If Python package is 'psutil' installed is the amount of released memoryis returned. Otherwise returns $0$. This function differs from WMA which tries to reduce the amount of memory required to store definitions, by reducing duplicated definitions.
      <dt>'Share[Symbol]'
      <dd>Does the same thing as 'Share[]'; Note: this function differs from WMA which tries to reduce the amount of memory required to store definitions associated to $Symbol$.

    </dl>

    >> Share[]
     = ...
    """

    summary_text = "force Python garbage collection"

    def apply(self, evaluation) -> Integer:
        """Share[]"""
        # TODO: implement a routine that swap all the definitions,
        # collecting repeated symbols and expressions, and then
        # remplace them by references.
        # Return the amount of memory recovered.
        if have_psutil:
            totalmem = psutil.virtual_memory().available
            gc.collect()
            return Integer(totalmem - psutil.virtual_memory().available)
        else:
            gc.collect()
            return Integer0

    def apply_with_symbol(self, symbol, evaluation) -> Integer:
        """Share[symbol_Symbol]"""
        # TODO: implement a routine that swap all the definitions,
        # collecting repeated symbols and expressions, and then
        # remplace them by references.
        # Return the amount of memory recovered.
        if have_psutil:
            totalmem = psutil.virtual_memory().available
            gc.collect()
            return Integer(totalmem - psutil.virtual_memory().available)
        else:
            gc.collect()
            return Integer0
