"""
User File Directories
"""

import os

from mathics.core.atoms import String
from mathics.core.attributes import A_NO_ATTRIBUTES
from mathics.core.builtin import Predefined
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.streams import HOME_DIR, PATH_VAR


class Path(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Path.html</url>

    <dl>
      <dt>'$Path'
      <dd>returns the list of directories to search when looking for a file.
    </dl>

    >> $Path
     = ...
    """

    attributes = A_NO_ATTRIBUTES
    name = "$Path"
    summary_text = "list directories where files are searched"

    def evaluate(self, evaluation: Evaluation):
        return to_mathics_list(*PATH_VAR, elements_conversion_fn=String)


class HomeDirectory(Predefined):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/HomeDirectory.html</url>

    <dl>
      <dt>'$HomeDirectory'
      <dd>returns the users HOME directory.
    </dl>

    >> $HomeDirectory
     = ...
    """

    name = "$HomeDirectory"
    summary_text = "user home directory"

    def evaluate(self, evaluation: Evaluation):
        return String(HOME_DIR)


class UserBaseDirectory(Predefined):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/UserBaseDirectory.html</url>

    <dl>
    <dt>'$UserBaseDirectory'
      <dd>returns the folder where user configurations are stored.
    </dl>

    >> $UserBaseDirectory
     = ...
    """

    name = "$UserBaseDirectory"
    summary_text = "get directory where user configurations are stored"

    def evaluate(self, evaluation: Evaluation):
        return String(HOME_DIR + os.sep + ".mathics")


# TODO: $UserDocumentsDirectory, $WolfromDocumentsDirectory
