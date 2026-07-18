"""
Test mathics.repl
"""

from mathics.core.definitions import Definitions
from mathics.repl import TerminalShell


def fake_readline(prompt: str) -> str:
    return "Fake readline"


definitions = Definitions(add_builtin=False, extension_modules=tuple())
definitions.set_line_no(1)

shell = TerminalShell(
    definitions,
    "NoColor",
    want_readline=False,
    want_completion=False,
    autoload=False,
)


def test_in_prompt():
    shell.read_line = fake_readline
    assert shell.in_prompt == "In[1]:= ", "We should start out with In[1]:="
    shell.feed()
    assert (
        shell.in_prompt == "        "
    ), "Multiline prompt should be blanks of the length of 'In[1]:= '"
    definitions.set_line_no(9)
    shell.multiline_input = False
    assert (
        shell.in_prompt == "In[9]:= "
    ), "Setting line number to the last length-one digit"
    shell.feed()
    assert (
        shell.in_prompt == "        "
    ), "Multiline prompt should be blanks of the length of 'In[9]:= '"
    definitions.set_line_no(10)
    shell.multiline_input = False
    shell.feed()
    assert (
        shell.in_prompt == "         "
    ), "Multiline prompt should be blanks of the length of 'In[10]:= '"
