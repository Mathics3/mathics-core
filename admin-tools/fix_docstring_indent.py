"""
This routine cleans most of the typical issues in docstring format and indentation.
"""


import os

import mathics.builtin

root = mathics.builtin.__file__[:-12]


def fix_docstring(filename):
    with open(filename, "r") as f:
        lines = f.readlines()

    modified = False
    file_newlines = []
    inclass = False
    in_docstring = False
    curr_indent = -3
    for linenumber, line in enumerate(lines):
        if line.startswith("class"):
            inclass = True
            file_newlines.append(line)
            continue
        if inclass and not in_docstring and line.strip().count('"""') > 0:
            in_docstring = True
            file_newlines.append(line)
            continue
        if in_docstring:
            if line.strip().count('"""') > 0:
                file_newlines.append(line)
                in_docstring = False
                inclass = False
                continue
            if line.count("<dl>"):
                curr_indent = line.index("<dl>")
                file_newlines.append(line)
                continue
            if line.count("</dl>"):
                assert curr_indent != -3, (
                    "Invalid docstring in "
                    + filename
                    + ":"
                    + str(linenumber)
                    + ". Abort."
                )
                if curr_indent != line.index("</dl>"):
                    modified = True
                    line = curr_indent * " " + line.strip() + "\n"
                file_newlines.append(line)
                curr_indent = -3
                continue
            if line.count("<dd>"):
                assert curr_indent != -3, (
                    "Invalid docstring in "
                    + filename
                    + ":"
                    + str(linenumber)
                    + ". Abort."
                )
                if line.index("<dd>") - curr_indent != 2:
                    modified = True
                    line = (2 + curr_indent) * " " + line.strip() + "\n"
                file_newlines.append(line)
                continue
            if line.count("<dt>"):
                assert curr_indent != -3, (
                    "Invalid docstring in "
                    + filename
                    + ":"
                    + str(linenumber)
                    + ". Abort."
                )
                if file_newlines[-1].strip().startswith("<dd>"):
                    modified = True
                    file_newlines.append("\n")
                if line.index("<dt>") - curr_indent != 2:
                    modified = True
                    line = (2 + curr_indent) * " " + line.strip() + "\n"
                file_newlines.append(line)
                continue
            if (
                curr_indent != -3
                and line.count("<dt>") == 0
                and line.count("<dd>") == 0
                and (
                    file_newlines[-1].count("<dt>") != 0
                    or file_newlines[-1].count("<dd>") != 0
                )
            ):
                modified = True
                print(
                    "joining lines",
                    [
                        file_newlines[-1],
                        "\n",
                        line,
                    ],
                )
                file_newlines[-1] = file_newlines[-1][:-1] + " " + line.strip() + "\n"
                continue
        # Otherwise
        file_newlines.append(line)

    if not modified:
        return

    with open(filename + "_modified", "w") as f:
        for line in lines:
            f.write(line)
    with open(filename, "w") as f:
        for line in file_newlines:
            f.write(line)

    print("file", filename, " changed")


if __name__ == "__main__":
    for root, dirs, files in os.walk(root):
        for filename in files:
            if filename.endswith(".py"):
                fix_docstring(os.path.join(root, filename))
