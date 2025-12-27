This README concerns testing implemented in `test_plot_detail.py`,
which are primarily driven by test cases described in the `*.yaml`
files. These test cases aim to provide broad coverage of plotting
functions.

The test cases list in the `*.yaml` files are executed and then
two output files are created in `/tmp`:

* A `.txt` file contains a distilled outline-form version of the
  `Graphics*` expression produced by the plotting routine.  For
  testing stability numbers are only printed with limited precision.
  `NumericArray`s print only a sampling of the array for brevity.

* The `Graphics*` expression is converted to SVG and a distilled
  outline-form version is stored in a `*.svg.txt`. This is similarly
  printed with limited precision for testing stability.

Then the actual output is compared against a reference output stored
in `test_plot_detail_ref` using ordinary text line-by-line diff.  The
distilled outline form of the test files makes such comparison an
effective way to understand what has changed.

## Running the tests

The tests can be run in the usual way with pytest, either alone or as
part of the broader pytest suite:

    pytest -x test_plot_detail.py

During development testing I find pytest sometimes to be a bit noisy,
so you can run the tests more directly to get more focused output:

    python -m test.builtin.drawing.test_plot_detail

This will produce a diff between the actual and reference files,
stopping after the first error. You can also try this:

    python -m test.builtin.drawing.test_plot_detail --update

The `--update` flag causes it to copy any actual output files in
`/tmp` that differ to the reference directory `test_plot_detail_ref`.
This is useful for two purposes:

* When new test cases are added you can quickly generate the reference
  files using `--update`.

* In development mode when some code change has changed the output you
  can use the `--update` flag to update the reference files, and the
  use git tools to quickly examine the changes and decide whether to
  accept them by commiting, or not by reverting. Personally I like the
  diff view offered by GitHub Desktop for this purpose.

  
