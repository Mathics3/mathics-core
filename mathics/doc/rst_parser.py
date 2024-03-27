"""
Minimal parser for ReStructuredText

This module provides a compatibility support for RsT syntax
in the Mathics documentation system.

We cannot use an standard library like docutils or sphinx since
by now, the documentation is written in a Mathics-specific syntax,
and for a while, both syntaxes will have to coexist.

"""

import re

RST_BLOCK_RE = re.compile(r"^\.\.\s+(.*)\n((?:^[ ]+.*\n|^\n)+)", re.MULTILINE)
RST_URL_RE = re.compile(r"`(?P<label>.*?)\<(?P<url>.*?)\>`_(?P<under>_?)")


PROCESS_RST_BLOCK = {}


def indent_level(line_str: str) -> int:
    """
    Compute the number of blank spaces at the left
    of a string.
    """
    line_lstrip = line_str.lstrip()
    if line_lstrip == "":
        return 80
    return len(line_str) - len(line_lstrip)


def normalize_indent(text: str, omit_first_line: bool = True) -> str:
    """
    Normalize the indentation level of the text.
    Usually, the docstring has an indentation equal
    to the code where its belongs.
    For processing the documentation, it is useful
    to normalize the indentation level.

    Usually, in a docstring, the first line has a different
    indentation level just because the "indentation" lays before the quotes.
    `omit_first_line` controls if that line must be taken into account to compute
    the indentation reference.

    """
    lines = text.splitlines()
    if len(lines) > 1:
        # First, look for the minimal level
        # of indentation.
        lines_ = lines[1:] if omit_first_line else lines

        # 80 is a safe upper limit in standard docstrings,
        # because the line shouldn't have more characters.
        block_indent_level = min(min(indent_level(line) for line in lines_), 80)
        if block_indent_level == 80:
            block_indent_level = 0

        # Now, remove the extra indent.
        if block_indent_level:
            if omit_first_line:
                return (
                    lines[0]
                    + "\n"
                    + "\n".join(
                        line[block_indent_level:] if line else "" for line in lines_
                    )
                )
            return "\n".join(
                line[block_indent_level:] if line else "" for line in lines_
            )
    return text


def process_image_block(head: str, block: str) -> str:
    """ """
    src = head.split("::")[1]
    lines = block.splitlines()
    keys = f" src='{src}'"
    for line in lines:
        try:
            _, key, val = line.strip().split(":")
        except ValueError:
            continue
        keys += f""" {key}='{val.strip()}'"""
    return f"""<imgpng {keys}>"""


PROCESS_RST_BLOCK["image"] = process_image_block


def process_code_block(head: str, block: str) -> str:
    """
    Process a block of code
    """
    if block.strip() == "":
        return None

    try:
        lang = head.split("::")[1].strip()
    except ValueError:
        lang = ""

    if lang.lower() == "python":
        lines = block.splitlines()
        if len(lines) == 1:
            return f"""<python>{lines[0]}</python>"""
        code = normalize_indent(block, False)
        return f"""<python>\n{code}</python>"""
    if lang.lower() == "mathics":
        indentation = 7 * " "
        lines = [
            indentation + line.lstrip() if idx else line.lstrip()
            for idx, line in enumerate(block.splitlines())
        ]
        code = "    >> " + "\n".join(lines)
        return code
    return None


PROCESS_RST_BLOCK["code"] = process_code_block


# TODO: Check if it wouldn't be better to go in the opposite direction,
# to have a ReStructured markdown compliant syntax everywhere.
def rst_to_native(text):
    """
    convert a RsT syntax to the Mathics XML
    native documentation syntax
    """

    def repl_url(match):
        label = strip(match.group(1))
        url = strip(match.group(2))
        private = "_" == match.group(3)
        if label == "" and private:
            return f"<url>{url}</url>"
        return f"<url>:{label}:{url}</url>"

    text = RST_URL_RE.sub(repl_url, text)

    def repl_block(match):
        head = match.group(1)
        block = match.group(2)
        lines = block.splitlines()
        block_type = head.split(" ")[0].split("::")[0].strip()
        last_line = lines[-1]
        if last_line and last_line[0] != " ":
            lines = lines[:-1]
            block = "\n".join(lines)
        else:
            last_line = ""

        result = PROCESS_RST_BLOCK.get(block_type, None)(head, block)
        if result is None:
            return
        return result + "\n" + last_line

    text = RST_BLOCK_RE.sub(repl_block, text)

    return text
