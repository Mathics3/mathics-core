import argparse

import test_plot_detail

parser = argparse.ArgumentParser(description="manage plot tests")
parser.add_argument(
    "--generate", action="store_true", help="generate test reference files"
)
parser.add_argument(
    "--check-docs", action="store_true", help="compare doc tests with docs"
)
args = parser.parse_args()


if args.generate:
    test_plot_detail.make_ref_files()

if args.check_docs:
    print("TBD")
