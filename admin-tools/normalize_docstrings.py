#!/usr/bin/env python


"""
This program ensures a consistent indentation <dd>, and <dt> inside <dl> in docstrings.
"""

import filecmp
import os
import re
import sys


def rewrite_dl_tags(filename: str) -> int:
    """
    Look for <dl>, <dd>, and <dt> tags and rewrite them
    using a consistent set of indentation.
    0 is returned there was no error.
    """
    new_lines = []
    with open(filename, "r") as f_in:
        for line in f_in.readlines():
            line = re.sub(r"^[ ]*[<]dl[>]", r"    <dl>", line)
            line = re.sub(r"^[ ]*[<]/dl[>]", r"    </dl>", line)
            line = re.sub(r"^[ ]*[<]dt[>]", r"      <dt>", line)
            line = re.sub(r"^[ ]*[<]dd[>]", r"      <dd>", line)
            new_lines.append(line)

    rewritten_file = filename + ".rewritten"
    with open(rewritten_file, "w") as f_out:
        for line in new_lines:
            f_out.write(line)
        if filecmp.cmp(rewritten_file, filename):
            print(f"No change; removing temporary {rewritten_file}")
        else:
            backup_file = filename + "~"
            print(f"File changed, backing up {filename} to {backup_file}")
            os.rename(filename, backup_file)
            os.rename(rewritten_file, filename)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        print("usage:")
        print(f"  {__file__} [Mathics-module-containing-builtins]")
        quit(-1)
    filename = sys.argv[1]
    print(f"Checking <dl>, <dd>, and <dt> indentation on {filename}.")
    quit(rewrite_dl_tags(filename))
