#!/bin/env python
"""
Convert a YAML file into a JSON file.
"""


import json
import sys

import yaml


def main():
    filename = sys.argv[1]
    name, ext = filename.split(".")
    assert ext.upper() == "YAML"
    with open(filename, "r") as strm:
        test_dict = yaml.safe_load(strm)
    with open(f"{name}.json", "w") as strm:
        json.dump(test_dict, strm)
    print("Done!")


if __name__ == "__main__":
    main()
