#!/usr/bin/env python


"""
This program ensures the indentation inside docstrings.
"""

import re
import sys
import os
import shutil


def process_file(filename: str) -> int:
    new_lines = []
    with open(filename, "r") as f_in:
        for line in f_in.readlines():
            line = re.sub(r"^[ ]*[<]dl[>]", r"    <dl>", line)
            line = re.sub(r"^[ ]*[<]/dl[>]", r"    </dl>", line)
            line = re.sub(r"^[ ]*[<]dt[>]", r"      <dt>", line)
            line = re.sub(r"^[ ]*[<]dd[>]", r"      <dd>", line)
            new_lines.append(line)

    # backup the file
    shutil.copyfile(filename, filename + "~")
    with open(filename, "w") as f_out:
        for line in new_lines:
            f_out.write(line)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("This tool applies basic rules to normalize the format of docstrings")
        print("usage:")
        print("clean_docstring  [filename]")
        exit(-1)
    filename = sys.argv[1]
    print(f"normalizing {filename}. Backup in {filename}~")
    process_file(filename)
