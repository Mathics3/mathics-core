"""
System File Directories
"""

from mathics.core.atoms import String
from mathics.core.attributes import A_NO_ATTRIBUTES
from mathics.core.builtin import Predefined
from mathics.core.evaluation import Evaluation
from mathics.eval.directories import INITIAL_DIR, SYS_ROOT_DIR, TMP_DIR
from mathics.settings import ROOT_DIR


class BaseDirectory_(Predefined):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/$BaseDirectory.html</url>

    <dl>
      <dt>'$BaseDirectory'
      <dd>returns the folder where user configurations are stored.
    </dl>

    >> $BaseDirectory
     = ...
    """

    name = "$BaseDirectory"
    summary_text = "path to the configuration directory"

    def evaluate(self, evaluation: Evaluation):
        return String(ROOT_DIR)


class InitialDirectory(Predefined):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/$InitialDirectory.html</url>

    <dl>
      <dt>'$InitialDirectory'
      <dd>returns the directory from which \\Mathics was started.
    </dl>

    >> $InitialDirectory
     = ...
    """

    name = "$InitialDirectory"
    summary_text = "initial directory when Mathics was started"

    def evaluate(self, evaluation: Evaluation):
        return String(INITIAL_DIR)


class InstallationDirectory(Predefined):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/InstallationDirectory.html</url>

    <dl>
      <dt>'$InstallationDirectory'
      <dd>returns the top-level directory in which \\Mathics was installed.
    </dl>

    >> $InstallationDirectory
     = ...
    """

    attributes = A_NO_ATTRIBUTES
    name = "$InstallationDirectory"
    summary_text = "Mathics installation directory"

    def evaluate(self, evaluation):
        global ROOT_DIR
        return String(ROOT_DIR)


class RootDirectory(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/$RootDirectory.html</url>

    <dl>
    <dt>'$RootDirectory'
      <dd>returns the system root directory.
    </dl>

    >> $RootDirectory
     = ...
    """

    name = "$RootDirectory"
    summary_text = "system root directory"

    def evaluate(self, evaluation):
        return String(SYS_ROOT_DIR)


class TemporaryDirectory(Predefined):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/$TemporaryDirectory.html</url>

    <dl>
    <dt>'$TemporaryDirectory'
      <dd>returns the directory used for temporary files.
    </dl>

    >> $TemporaryDirectory
     = ...
    """

    name = "$TemporaryDirectory"
    summary_text = "path to the temporary directory"

    def evaluate(self, evaluation):
        return String(TMP_DIR)
