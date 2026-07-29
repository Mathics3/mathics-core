"""
WL File Format

WL and Mathics3 importer
"""

from mathics.core.builtin import Builtin, String
from mathics.core.evaluation import Evaluation
from mathics.eval.fileformats.wlformat import eval_WLImport


class ImportWL(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/format/WL.html</url>

    <dl>
      <dt>'WLDump`ImportWL[$path$]'
      <dd>Read $path$ as a Wolfram package and 'Get' it.
    </dl>

    This command is hooked into the 'Import' command via \
    'SystemFiles/Formats/WL/Import.wl'.

    When running this command directly, a list of rules is returned:

    >> WLDump`ImportWL["ExampleData/HelloWorld.wl"]
     = {Get ⇾ Hello, World!, Script ⇾ Hello, World!}

    The left-hand side is a element name that can be provided to 'Import', \
    and the right-hand side is the value associated with that element. Here it \
    represents the last evaluation value when evaluating the contents of the file.

    When an 'Import' is done and the file mentioned is a Mathics3 or a \
    Wolfram-Language file, this command is run underneath selecting value of the \
    "Get" element:

    >> Import["ExampleData/HelloWorld.wl"]
     = Hello, World!

    All of this is the same as just running a simple 'Get':
    >> << "ExampleData/HelloWorld.wl"
     = Hello, World!

    In sum, the built-in provides the glue to the 'Import' accees mechanism for 'Get'.
    """

    context = "WLDump`"
    summary_text = "import WL file"

    def eval(self, path: String, evaluation: Evaluation):
        "WLDump`ImportWL[path_String]"
        return eval_WLImport(path, evaluation)
