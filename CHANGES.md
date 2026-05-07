# CHANGES

## 10.0.1

April 18, 2026

Fix packaging to add some test YAML files.

Thanks, yet again, to @vic74p.

## 10.0.0

Some foundational work on overhauling plotting with NumPy vectors was started. Alas, work on it was not complete by release time, so this could not be finished. Expect a future release to have revamped graphics.

A major revision of Form handling and character encoding `$CharacterEncoding` was started with a focus on `TeXForm`, `MathMLForm`, and `OutputForm`.

_Notes:_

1.  There are numerous incompatible changes. Use with Mathics-scanner   10.0.0 or greater.
2.  We are in the process of renaming `Mathics` to `Mathics3`. You will notice a new Mathics3 logo in the documentation. `Mathics` was monolithic Python 2-ish code. Mathics3 has rewritten a number of major subcomponents and split off a number of subcomponents. There are still several that need to be revised or rewritten. The name change reflects this distinction between the two efforts, and emphasizes that `Mathics3` uses modern Python 3 idioms. While right now the repository name and import refer to `mathics`, several repositories that use the Mathics3 core, or that Mathics3 uses, have been renamed. In particular, `Mathics_Scanner` is now `Mathics3_Scanner`.

### New Builtins

1.  `$Language` variable
2.  `ArcBox` boxing function
3.  `Csch` function [PR  \#1768](https://github.com/Mathics3/mathics-core/pull/1768)
4.  `` JSON`Import`JSONImport ``
5.  `RasterBox` boxing function
6.  `Format`
7.  `FormBox`, and `RoundBox` boxing functions
8.  `ShowSpecialCharacters` option
9.  `ShowStringCharacters` option

### Enhancements

1.  Many Builtin functions now report argument-mismatch errors
2.  `Trig` option added to `Numerator` and `Denominator`
3.  `CharacterEncoding`, and `Path` options added to `Get`
4.  `PowerMod` and `Quotient` handle the 3-argument form, roots of exponents (`PowerMod`), lists of exponents, and numbers other than Integers.
5.  `N[integer, MachinePrecision]` added
6.  `PrintPrecision` for `N[integer]` matches WMA; so does the largest mantissa before converting to MachinePrecision Integer (for display) matches WMA.
7.  `BeginPackage` with `Needs` parameter added. This should allow more  packages to load properly
8.  `Expand`, and `Apart` work with relations
9.  [\#1596](https://github.com/Mathics3/mathics-core/issues/1481)   Improve `FullForm` compatibility

### Bugs Fixed

1.  [PR \#1755](https://github.com/Mathics3/mathics-core/pull/1775)  Ensure date formats have a year in them. This is needed for future Python versions.
2.  [PR \#1762](https://github.com/Mathics3/mathics-core/pull/1762) Fix Rayleigh expansion rules to only match half-integer orders. (Chenxin Zhong)
3.  [\#1741](https://github.com/Mathics3/mathics-core/issues/1741)  Implement `MachinePrecision` option for large numbers that fall outside of Python's built-in `float` mantissa
4.  [\#1740](https://github.com/Mathics3/mathics-core/issues/1740)  `N[3^200]` in formats as `PrecisionReal` instead of `MachinePrecision`
5.  [\#1723](https://github.com/Mathics3/mathics-core/issues/1723)  Plotting nested functions
6.  [\#1713](https://github.com/Mathics3/mathics-core/issues/1713) `?` *symbol* and `??` *symbol* should be parsed as `Information["symbol"]` and `Information["symbol"]`
7.  [\#1699](https://github.com/Mathics3/mathics-core/issues/1699) Character sequences used for the string representation of boxes should be treated as single characters in string character-wise manipulation operations.
8.  [\#1692](https://github.com/Mathics3/mathics-core/issues/1692) `Map` does not automatically map a function over `Association` values (Li-Xiang-Ideal)
9.  [\#1639](https://github.com/Mathics3/mathics-core/issues/1639) Map does not automatically map a function over Association values
10. [\#1622](https://github.com/Mathics3/mathics-core/issues/1622) Handling escape sequences inside string literals
11. [\#1519](https://github.com/Mathics3/mathics-core/issues/1519)  `Order` for Numerics, e.g. `Order[1.0, 1] == -1`, but is 0
12. [\#1492](https://github.com/Mathics3/mathics-core/issues/1492)   `UpSet` not giving a "Tag Integer is Protected." message
13. [\#1487](https://github.com/Mathics3/mathics-core/issues/1487) `FindMinimum`, `FindMaximum` do not give approximate results when   `$IterationLimit` has been exceeded and convergence fails
14. [\#1481](https://github.com/Mathics3/mathics-core/issues/1481)  \$TraceBuiltins=False does not work after more than one    \$TraceBuiltins=True use.
15. Reset `evaluation.iteration_count` on each new evaluation. This caused problems in long-running sessions, such as the Mathics3-django gallery examples.
16. `Binomial` attributes corrected

### Command-line Utilities

Command-line program `mathics` was renamed to `mathics3`; the old name will be available for a while. This apparently facilitates `uv` packaging.

Command-line program `mathics3-codeparser-parse` was added to show how expressions are parsed. This is roughly analogous to the `CodeParse` function of the `CodeParser` WMA package.

### Internals

- A major revision and reorganization was begun to improve Form
  handling, leading to the new modules `mathics.forms.format` and
  `mathics.forms.render`. Existing render functions from
  `mathics.format` has been moved under `mathics.form.render`. (mmatera) Corrections were made to variables `$PrintForms` and `$OutputForms`. (mmatera)
- Primitive datatype `NumericArray`, which is essentially a NumPy array,  was added to support vector operations, such as plotting. (Bruce Lucas) In support of this, the module `mathics.core.atoms` was split up.
- Internals for handling Graphics have been revised to be able to accept a more complete list.
- Parsing now uses more data from YAML tables instead of hard-coding values inside code.
- Revise representation for `Complex` Numbers; both the real and imaginary parts can now be arbitrary non-complex Real numbers. The precision, a derived value, is also saved.
- Numerous internal changes were made to improve performance.
- `mpmath` is used to store large integer mantissas in `N[x_Integer]`.
- Token names were changed to align better with the names reported in
  `` CodeParser`Tokenize ``. Note, however, Mathics3 parsing is a bit different from `` CodeParser`Parse ``.

### Package updates

1.  Python 3.14 supported. Support for Python 3.10 dropped; it may still work, but is not supported.
2.  Sympy 1.14 supported
3.  llvm 18+ now supported

### API incompatibility

- Front ends must now issue an explicit call to  `import_and_load_builtins()`. Previously, this was handled simply by
  `import` of `MathicsSession`. Loading modules loaded via `import` was unpredictable in how and when things got loaded. The change was made to address this and to be able to give more flexibility in loading.
- Token names have changed to align better with  ``CodeParser ' CodeTokenize. ``

### Documentation

Go over documentation for `PowerMod[]`, `Denominator[]`, `Numerator[]`, `Limit`, and `ColorData`, among other things.

### Documentation

Go over documentation for `PowerMod[]`, `Denominator[]`, `Numerator[]`, `Limit`, and `ColorData`, among other things.


## 9.0.0

Added support for Python 3.13. Dropped support for Python 3.8 and 3.9.

Note: There are incompatible changes. Use with Mathics-scanner 2.0.0 or greater.

You may notice a speedup in performance, especially graphics performance, in this version. There is a speedup due to removing conversions from Mathics3 to Python and vice versa for literal data, which happens a lot in plotting graphics. Also, Python 3.13 is a bit faster than previous versions. Previously, rendering via ``asymptote`` was slow. This is no longer the situation.

Preliminary work to track locations has started. This is useful in debugging and error reporting, and is controlled via Boolean System variable ``$TrackLocations``.

Boxing operators have been added. The full range of escape sequences is supported.  A limited form of boxing escape ``\*`` that handles a single Boxing function has been added.

A basic interrupt handler was added that loosely follows wolframscript's interrupt handler. Interrupt commands "abort", "exit", "continue", "debugger", "show", and "inspect" are available; "trace" will be added later.

``main.py`` has been moved to ``__main__.py`` following Python conventions for main routines. This makes ``python -m mathics`` work. GNU Readline history is enabled for ``mathics`` when it is available. It shares history files with ``mathicsscript``.

The priority for rule selection when there are several matching a function call has been revised and more closely follows WMA behavior.

Assignment statements, e.g. ``SetDelayed``, ``UpSetDelayed``, or ``DownSetDelayed`` have been revised to isolate left-hand-side references from conditions and element attributes. As a result, more of the code in WMA and Mathics3 packages work.

``$IterationLimit`` detects runaway rule expansion better.

Parameter count checking expanded to more Builtin functions.



New Builtins
------------

* ``$SessionID``
* ``$TrackLocations`` (not WMA)
* ``BinaryReadList[]`` (needed to support importing gzip files)
* ``Hypergeometric2F1``

By Aravindh Krishnamoorthy (needed for better Rubi support):

* ``Hypergeometric1F1[]``
* ``HypergeometricPFQ[]``
* ``MeijerG[]``
* ``HypergeometricU[]``


Documentation
-------------

Go over docs for ``Beta[]``, ``Gamma[]``, ``Product[]``, and infix operators with no meaning.
Expand ``Transpose[]`` documentation.


Enhancements
-------------

* Set-related code reworked for better WMA conformance. There is better WMA conformance in rule selection when several rules match.
* ``mathics`` CLI options are more like wolframscript
* The debugging interface has been improved. ``TraceEvaluation[]`` and ``TraceDebug[]`` filter and colorize output for Mathics3 constructs much better.
* Single-dash long options like ``-help``, ``-file`` are now accepted. Short option ``-f`` is associated with ``-file`` rather than ``--fullform``; ``-F`` is is now used for
   ``FullForm``. Option ``--read`` with alias ``-r`` is now ``-code`` and short option ``-c``.
* Boolean Options ``ShowRewrites`` and ``ShowEvaluation`` were added to ``TraceEvalation[]``. These are for either rewrite rules or evaluation expressions. Presumably, you don't want to filter both.
* We check argument counts on more Builtin Functions and give error messages (tags ``argb``, ``argx``, ``argr``, ``argrx``) for invalid parameter combinations.
* ``$TraceBuiltins`` output uses standard Mathics3 I/O mechanisms rather than Python's builtin ``print``. Therefore, it will be seen in more front-ends like Django or PyOxide.

Bugs Fixed
----------

* #1057 ``ListPlot[]`` error handling (and ``NestList[]``) needs going over
* #1213 ``Condition[]`` expressions as second element in ``RuleDelayed`` behaviour not compatible with WMA
* #1187 Add ``Hypergeometric2F1`` Builtin Function
* #1198 Blanks in ``Set`` operations are not properly handled in tag positions.
* #1245 Add "lpn" error message checking in _ListPlot
* #1383 Support for hypergeometric functions
* #1384 Option management tweaks
* #1388 In WMA, ``Pochhammer[0,-2]`` returns 1/2
* #1395 Match WMA for ``Gamma[1+x]`` and ``Product[...]``
* #1405 structure_cache in ``mathics.core.expression.structure`` is ``None`` but we try to set it in ``_is_neutral_symbol()``
* #1412 ``Transpose[]`` does not work on three-dimensional array
* #1425 `Erroneous Protected message in SetDelayed
* #1432 URL links with $ in them are getting messed up
* #1461 "noopen" errors sometimes return ``$Failed``
* #1465 Crash in running ``Trace[Sin[Log[2.5, 7]]]``
* #1473 Doctest for ``Quantity``, ``KnownUnitQ``, and others fail when the documentation is generated
* #1474 Document typo: "is a valid Association object" should be "is a valid Quantity object"
* #1476 ``$IterationLimit`` is not limiting evalation expansion

WMA Compatibility
-----------------

* Hypergeometric functions have been revised to conform better to WMA behavior by expanding hypergeometric results.
* ``$IterationLimit`` now defaults to 4096.
* ``mathics`` command-line conform better to ``wolframscript`` options.
* Rule selection of functions when multiple rules apply conforms to WMA more closely.
* LHS reference selection conforms to WMA more closely.


Incompatible changes
---------------------

Scanner API has changed. Options on ``mathics`` CLI have changed. See above for the changes.
Location of ``mathics`` in ``mathics.__main__``, the more usual location, rather than ``mathics.main``.

* Mathics scanner exceptions of class TranslateError are incompatible
with previous versions, and now store error parameters, "name", "tag", and
"args".
* The method ``get_sort_key()`` was replaced by two different properties:
  ``element_order``, for canonical ordering of expressions, and
  ``pattern_precedence``, used for ordering rules according to their precedence
  in the evaluation loop.
* In both cases, the part of the sort key related to properties of the
  expressions and patterns are now stored as a magic number instead of
  a tuple.

## 8.0.1

Feb 8, 2025

Some work was made on the Mathics3 Kernel to work in Python 3.13.
The maximum version of numpy was increased to < 2.3 to allow marimo to work.


Bugs
----

Correct for a mismatch between ListExpression and a tuple in ``DispatchAtom``.
This is needed for the PacletManager code to work better.


Compatibility
-------------

* When the result of an evaluation is ``Symbol`Null``, Mathics CLI  now does not show an ``Out[...]=`` line, following the behavior of
  the WMA CLI.
* Asymptote rendering of platonic solids added.


Internals
---------

Document tagging code handles TeX math mode more completely. Image tags in PDF properly.

Documentation
-------------

* Documentation has been gone over so that expressions are tagged in TeX. As a result, the user guide and reference manual render much nicer in the PDF and Django.
* More links have been added. References to The Digital Library of Mathematical Functions https://dlmf.nist.gov/ have been added where appropriate.
* Add mention of MathicsLive
* Platonic solid rendered properly in PDF

# 8.0.0

Jan 26, 2025

This release is to get out some of the major changes that have gone on already in advance of redoing Boxing and Formatting.

Code now supports the emscripten platform, so this code can be installed in pyodide using ``micropip.install``.

Operators are now controlled from a new operators YAML table from the ``mathics-scanner`` repository. A pass was made over the Mathics parser to handle box operators more properly. More work is needed here.

We started adding more debugging capabilities:

* ``Breakpoint[]``
* ``Stack[]``, and
* ``Trace[]``

And in the [Mathics3-Trepan](https://github.com/Mathics3/Mathics3-trepan) repository:

* ``DebugActivate[]``
* ``Debugger[]``, and
* ``TraceActivate[]``

Option ``--post-mortem`` was added, which goes into the [trepan3k debugger](https://pypi.org/project/trepan3k/) on an unrecoverable error. This option is available on other front ends.

This debugging code is very much alpha quality, but it greatly improves the ability to debug problems in loading existing packages
written from Mathematica. So packages ``BoolEval`` and ``CleanSlate`` were added to the repository.

Also, as a result of the improved ability to debug Mathics3, we now provide a version of Rubi 4.17 using git submodules. To use this, you will need a patched version of ``stopit``.  Aravindh Krishnamoorthy led the initial port of [Rubi](https://github.com/Mathics3/Mathics3-Rubi).

David A. Roberts worked on ensuring Mathics3 runs on pyodide and contributed a number of new Built-in Functions that are found in [The On-Line Encyclopedia of Integer Sequences (OEIS)](https://oeis.org/).


# New Builtins

* ``Between``
* ``Breakpoint`` - (not WMA; forces a Python ``breakpoint()``
* ``CheckAbort``
* ``FileNameDrop``
* ``FormatValues``
* ``ListStepPlot``
* ``MapApply``
* ``PythonCProfileEvaluation`` (not WMA; interface to Python cProfile)
* ``RealValuedNumberQ``
* ``SequenceForm``
* ``SetEnvironment``
* ``Stack``
* ``SyntaxQ``
* ``Trace``
* ``UnitStep``

By [@davidar](<https://github.com/davidar>):

* ``BellB``
* ``DivisorSigma``
* ``DivisorSum``
* ``EulerE``
* ``HypergeometricU``
* ``IntegerPart``
* ``IntegerPartitions``
* ``JacobiSymbol``
* ``KroneckerSymbol``
* ``LambertW``
* ``LinearRecurrence``
* ``LucasL``
* ``MersennePrimeExponent``
* ``MoebiusMu``
* ``NumberDigit``
* ``PolygonalNumber``
* ``PolyLog``
* ``PowersRepresentations``
* ``ReverseSort``
* ``RootSum``
* ``SeriesCoefficient``
* ``SquaresR``
* ``Subfactorial``

# Documentation


* Unicode operators appear in Django documentation. In the PDF, AMSLaTeX is used.
* Summaries of builtin functions have been improved and regularized

# ``mathics`` command line


Option ``--post-mortem`` was added, which goes into the [trepan3k debugger](https https://pypi.org/project/trepan3k/)_ on an
unrecoverable error. This option is available on other front-ends.

# WMA Compatibility

* ``GetEnvironment`` expanded to handle ``[]`` and ``{var1, var2,...}`` forms
* The system ``packages`` directory has been renamed ``Packages`` to conformance with WMA.
* ``$Path`` now includes a ``Packages`` directory under ``$HOME``.
* All of the 100 or so Unicode operators without a pre-defined meaning are now supported

Internals
---------

* More of the on-OO evaluation code that forms what might be an
  instruction evaluator has been moved out of the module
  ``mathics.builtins`` put in ``mathics.eval``. This includes code for plotting and making boxes.
* nested ``TimeConstraint[]`` works via external Python module ``stopit``.
* ``Pause[]`` is more interruptable
* More code has been linted, more type errors removed, and docstrings added/improved


Performance
-----------

* ``Blank*`` patterns without arguments are now singletons.

API incompatibility
-------------------

* ``Matcher`` now requires an additional ``evaluation`` parameter
* ``Romberg`` removed as an ``NIntegrate[]`` method. It is deprecated in SciPy and is to be removed by SciPy 1.15.
* The signature of the ``Definition.__init__`` now receives a single dict parameter instead of the several `*values` parameters.
* Rule positions in ``Definition.{get|set}_values`` now includes the word ``values``. For example ``pos="up"`` now is ``pos="upvalues"``.
* ``Definitions.get_ownvalue`` now returns a ``BaseElement`` instead of a ``BaseRule`` object.
* Patterns in ``eval_`` and ``format_`` methods of builtin classes
  parses patterns in docstrings of the form
  ``Symbol: Expr`` as ``Pattern[Symbol, Expr]``.
  To specify the associated format in ``format_`` methods, the
  docstring, the list of formats must be wrapped in parentheses, like
  ``(InputForm,): Definitions[...]`` instead of just ``InputForm: Definitions[...]``.
* Character and Operator information that has been gone over in the Mathics Scanner project. The information in JSON tables, the keys, and values have thus changed. Here, we read this information in and use it instead of previously hard-coded values.


Bugs
----

* Fix infinite recursion when formatting ``Sequence[...]``
* Parsing ``\(`` ... ``\)`` improved
* Fixed #1105, #1106, #1107, #1172 #1173, #1195, #1205, #1221, #1223, and #1228 among others

### Mathics3 Packages

* Added ``BoolEval``
* Added ``CleanSlate``
* ``Combinatorica`` moved to a separate repository and v.9 was renamed to 0.9.1.
    More code v0.9.1 works. v2.0 was renamed v2.0.1, and some code now works.
* ``Rubi`` version 4.17 (work in progress; algebraic integrations work)


### Mathics3 Modules

* Added preliminary [Mathics3 debugger](https://github.com/Mathics3/mathics3-trepan).

### Python Package Updates

* Python 3.12 is now supported
* SymPy 1.13 is now supported

## 7.0.0

Aug 9, 2024

Some work was done here in support of planned future improvements like lazy loading of builtin functions. A bit of effort was also spent to modernize Python code and style, add more type annotations, remove spelling errors, and use newer versions of important software like SymPy and Python itself.

# New Builtins

-   `$MaxLengthIntStringConversion`
-   `Elements`
-   `ComplexExpand` (thanks to vitrun)
-   `ConjugateTranspose`
-   `LeviCivitaTensor`
-   `RealAbs` and `RealSign`
-   `RealValuedNumberQ`

# Documentation

Many formatting issues with the PDF file have been addressed. In particular, the spacing of section numbers in the chapter and section table of contents has been increased. The margin space around builtin definitions has also been increased. Numerous spelling corrections to the document have been applied.

The code to run doctests and produce LaTeX documentation has been revised and refactored to allow incremental builtin update, and to DRY the code.

Section Head-Related Operations is a new section of \"Expression Structure\". The title of the PDF has changed from Mathics to Mathics3 and the introduction has been updated and revised.

## Compatibility

-   `*Plot` does not show messages during the evaluation.
-   `Range[]` now handles a negative `di` PR #951
-   Improved support for `DirectedInfinity` and `Indeterminate`.
-   `Graphics` and `Graphics3D`, including wrong primitives and
    directives, are shown with a pink background. In the Mathics-Django interface, a tooltip error message is also shown.
-   Improving support for `$CharacterEncoding`. Now it is possible to
    change it from inside the session.

Internals \-\--

-   `eval_abs` and `eval_sign` extracted from `Abs` and `Sign` and added to `mathics.eval.arithmetic`.
-   Maximum number of digits allowed in a string set to 7000 and can be adjusted using the environment variable `MATHICS_MAX_STR_DIGITS` on  Python versions that don't adjust automatically (like pyston).
-   Real number comparisons implemented are now in the internal implementation of `RealSign`.
-   For Python 3.11, the variable `$MaxLengthIntStringConversion`   controls the maximum size of the literal conversion between large integers and Strings.
-   Older style non-appearing and non-pedagogical doctests have been  converted to pytest
-   Built-in code is directed explicitly rather than implicitly. This facilitates the ability to lazy load builtins or \"autoload\" them via GNU Emacs autoload.
-   add mpmath lru cache
-   Some work was done to make it possible so that in the future, we can  speed up initial loading and reduce the initial memory footprint

## Bugs

-   `Definitions` is compatible with `pickle`.
-   Improved support for `Quantity` expressions, including conversions,  formatting, and arithmetic operations.
-   `Background` option for `Graphics` and `Graphics3D` is operative again.
-   Numeric comparisons against expressions involving `String`s; Issue #797)
-   `Switch[]` involving `Infinity`. Issue #956
-   `Outer[]` on `SparseArray`. Issue #939
-   `ArrayQ[]` detects `SparseArray` PR #947
-   `BoxExpressionError` exceptions handled. Issue PR #970
-   `Derivative` evaluation of `True`, `False`, and `List[]` corrected.  PR #971, #973
-   `Combinatorica` package fixes. PR #974
-   `Exit[]` not working. PR #998
nn-   `BaseForm` is now listed in `$OutputForms`

# API

We now require an explicit call to a new function`import_and_load_builtins()`. Previously, loading was implicit and
indeterminate as to when this occurred, as it was based on the import order.

We need this so that we can support in the future lazy loading of builtin modules.

# Package updates

1.  Python 3.11 is now supported
2.  Sympy 1.12 is now supported

## 6.0.2 to 6.0.4


Small fixes noticed by users and packagers, such as OpenSUSE Tumbleweed

## 6.0.1

Release to get Pillow 9.2 dependency added for Python 3.7+

Note that future releases in the 6.1 or 7.0 range will drop support for Python 3.6.

Some Pattern-matching code has been gone over to add type annotations and to start documenting its behavior and characteristics. Function
attributes are now examined and stored at the time of Pattern-object creation rather than at evaluation time. This better matches WMA behavior, which pulls out the attribute this even earlier than this.  These changes reduce doctest runtime by about 7% under Pyston.

Combinatorica version upgraded from 0.9 (circa 1992) to 0.91 (circa 1995), which more closely matches the published book.

Random Builtin function documentation has been gone over to conform to the current documentation style.

## 6.0.0

A fair bit of code refactoring has gone on so that we might be able to scale the code, get it to be more performant, and more in line with other interpreters. There is greater use of Symbols as opposed to strings.

The builtin Functions have been organized into groups akin to what is found in WMA. This is not just for documentation purposes, but it better modularizes the code and keeps the modules smaller while suggesting where functions below as we scale.

Image Routines have been gone over and fixed. Basically, we use Pillow imaging routines, as opposed to home-grown image code.

A number of Built-in functions that were implemented were not accessible for various reasons.

Mathics3 Modules are better integrated into the documentation. Existing Mathics3 modules `pymathics.graph` and `pymathics.natlang` have had a major overhaul, although more is needed. And will continue after the 6.0.0 release

We have gradually been rolling in more Python type annotations and current Python practices such as using `isort`, `black`, and `flake8`.

Evaluation methods of built-in functions start `eval_`, not `apply_`.

### API

1.  New function `mathics.system_info.python_implementation()` shows the Python Implementation, e.g., CPython, PyPy, Pyston, that is running Python. This is included in the information  `mathics.system_info.mathics_system__system_info()` returns and is  used in `$PythonImplementation`
2.  A list of optional software can be found in `mathics.optional_software`. Versions of that software are included in `mathics.version_info`.

#### Package update

*  SymPy 1.11.1 accepted
*  Numpy 1.24.0 accepted

#### New Builtins

* `$BoxForms`
* `$OutputForms`
* `$PrintForms`
* `$PythonImplementation`
* `Accuracy`
* `ClebschGordan`
* `Curl` (2-D and 3-D vector forms only)
* `DiscretePlot`
* `Kurtosis`
* `ListLogPlot`
* `LogPlot`
* `$MaxMachineNumber`
* `$MinMachineNumber`
* `NumberLinePlot`
* `PauliMatrix`
* `Remove`
* `SetOptions`
* `SixJSymbol`
* `Skewness`
* `ThreeJSymbol`

### Documentation

1.  All Builtins have links to WMA pages.
2.  "Accuracy and Precision" section added to the Tutorial portion.
3.  "Attribute Definitions" section reinstated.
4.  "Expression Structure" split out as a guide section (was "Structure of Expressions").
5.  "Exponential Functional" split out from "Trigonometry Functions"
6.  "Functional Programming" section split out.
7.  "Image Manipulation" has been split off from Graphics and Drawing and turned into a guide section.
8.  Image examples now appear in the LaTeX and, therefore, the PDF doc
9.  "Logic and Boolean Algebra" section reinstated.
10. "Forms of Input and Output" is its own guide section.
11. More URL links to Wiki pages added; more internal cross-links added.
12. "Units and Quantities" section reinstated.
13. The Mathics3 Modules are now included in LaTeX and therefore the PDF doc.

### Internals

* `boxes_to_` methods are now optional for `BoxElement` subclasses. Most of the code is now moved to the `mathics.format` submodule and implemented in a more scalable way.
* `from_mpmath` conversion supports a new parameter `acc` to set the accuracy of the number.
* `mathics.builtin.inout` was split into several modules (`inout`, `messages`, `layout`, `makeboxes`) in order to improve the documentation.
* `mathics.eval` was created to have code that might be put in an instruction interpreter. The opcodes-like functions start `eval_`, other functions are helper functions for those.
* Operator name to Unicode or ASCII comes from Mathics scanner character tables.
* Builtin instance methods that start `eval` are considered rule matching and function application; the use of the name `apply`is deprecated when `eval` is intended.
* Modularize and improve the way in which `Builtin` classes are selected to have an associated `Definition`.
* `_SetOperator.assign_elementary` was renamed `_SetOperator.assign`. All the special cases are not handled by the    `_SetOperator.special_cases` dict.
* `isort` runs over all Python files. More type annotations and docstrings on functions added.
* Caching on immutable atoms like, `String`, `Integer`, `Real`, etc. was improved; the `__hash__()` function was sped up. There is a small speedup overall from this at the expense of increased memory.
* More type annotations added to functions, especially builtin  functions
* Numerical constants used throughout the code were renamed using caps, according to Python's convention.

### Bugs

* ``0`` with a given precision (like in ```0`3```) is now parsed as ``0``, an integer number.
* Reading certain GIFs now works again
* ``Random[]`` works now.
* ``RandomSample`` with one list argument now returns a random ordering of the list items. Previously, it would return just one item.
* Origin placement corrected on ``ListPlot`` and ``LinePlot``.
* Fix long-standing bugs in Image handling
* Some scikit image routines line ``EdgeDetect`` were getting omitted due to overly stringent PyPI requirements
* Units and Quantities were sometimes failing. Also, they were omitted from the documentation.
* Better handling of ``Infinite`` quantities.
* Improved ``Precision`` and ``Accuracy``compatibility with WMA. In particular, ``Precision[0.]`` and ``Accuracy[0.]``
* Accuracy in numbers using the notation ``` n.nnn``acc ```  now is properly handled.
* numeric precision in mpmath was not reset after operations that changed these. This cause huges slowdowns after an operation that sets the mpmath precision high. This was the source of several-minute slowdowns in testing.
* GIF87a (```MadTeaParty.gif`` or ExampleData) image loading fixed
* Replace the non-free Leena image with a freely distributable image. Issue #728

### PyPI Package requirements

Mathics3 aims for a richer set of functionality.

Therefore, NumPy and Pillow (9.10 or later) are required Python packages, where they had been optional before. In truth, probably running Mathics without one or both probably did not work well if it worked at all; we had not been testing setups that did not have NumPy.

### Enhancements

* Vector restriction on `Norm[]` removed. "Frobinius" p-form allowed.
* Better handling of comparisons with finite precision numbers.
* Improved implementation for `Precision`.
* Infix operators, like `->` render with their Unicode symbol when `$CharacterEncoding` is not "ASCII".
*`Grid` compatibility with WMA was improved. Now it supports a non-uniform list of lists and lists with general elements.
* Support for BigEndian Big TIFF

## 5.0.2

August 6, 2022


Get in `requirements-cython.txt`` into tarball. Issue #483

New Symbols
-----------

1. ``Undefined``


## 5.0.1

August 6, 2022

Mostly a release to fix a Python packaging problem.

## Internals


1. ``format`` and ``do_format`` methods were removed from the interface of
   ``BaseElement``, becoming non-member functions.
1. The class ``BoxElement`` was introduced as a base for boxing elements.

## New Builtin

1. 'Inverse Gudermannian'.

Documentation
-------------

Hyperbolic functions were split off form trigonometry and exponential functions. More URL links were added.

Bugs Fixed
----------

1. Creating a complex number from Infinity no longer crashes and returns 'I * Infinity'

## 5.0.0

July 31, 2022

This release starts to address some of the performance problems and
terminology confusion that goes back to the very beginning. As a result,
this release is not API compatible with prior releases.

In conjunction with the performance improvement in this release, we
start refactoring some of the core classes and modules to start to get
this to look and act more like other interpreters, and to follow more
current Python practice.

More work will continue in subsequent releases.

# New Builtins

1.  Euler\'s `Beta` function.
2.  `Bernoulli`.
3.  `CatalanNumber` (Integer arguments only).
4.  `CompositeQ`.
5.  `Diagonal`. Issue \#115.
6.  `Divisible`.
7.  `EllipticE`
8.  `EllipticF`
9.  `EllipticK`
10. `EllipticPi`
11. `EulerPhi`
12. `$Echo`. Issue \#42.
13. `FindRoot` was improved to support numerical derivatives, Issue #67, as well as the use of scipy libraries when available.
14. `FindRoot` (for the `newton` method) partially supports
    `EvaluationMonitor` and `StepMonitor` options.
15. `FindMinimum` and `FindMaximum` now have a minimal implementation
    for 1D problems and the use of scipy libraries when they are available.
16. `LogGamma`.
17. `ModularInverse`.
18. `NumericFunction`.
19. `Projection`.
20. Partial support for Graphics option `Opacity`.
21. `SeriesData` operations were improved.
22. `TraceEvaluation[]` shows expression name calls and return values of
    it argument.
    -   Pass option `ShowTimeBySteps`, to show the accumulated time before
        each step
    -   The variable `$TraceEvalution`, when set True, will show all
        expression evaluations.
23. `TraditionalForm`

# Enhancements

1.  `D` acts over `Integrate` and `NIntegrate`. Issue \#130.
2.  `SameQ` (`===`) handles chaining, e.g. `a == b == c` or
    `SameQ[a, b, c]`.
3.  `Simplify` handles expressions of the form `Simplify[0^a]`, Issue #167.
4.  `Simplify` and `FullSimplify` support optional parameters
    `Assumptions` and `ComplexityFunction`.
5.  `UnsameQ` (`=!=`) handles chaining, e.g. `a =!= b =!= c` or
    `UnsameQ[a, b, c]`.
6.  Assignments to usage messages associated with `Symbols` are allowed
    as it is in WMA. With this and other changes, Combinatorica 2.0
    works as written.
7.  `Share[]` performs an explicit call to the Python garbage collection
    and returns the amount of memory free.
8.  Improve the compatibility of `TeXForm` and `MathMLForm` outputs with
    WMA. MathML tags around numbers appear as \"\<mn\>\" tags instead of
    \"\<mtext\>\", except in the case of `InputForm` expressions. In
    TeXForm: some quotes around strings have been removed to conform to
    WMA. It is not clear whether this is the correct behavior.
9.  Allow `scipy` and `skimage` to be optional. In particular: revise
    `Nintegrate[]` to use `Method="Internal"` when scipy isn\'t
    available.
10. Pyston up to versions from 2.2 to 2.3.4 are supported as are PyPy
    versions from 3.7-7.3.9.0 up 3.9-7.3.9. However, those Python
    interpreters may have limitations and limitations on the packages that
    they support.
11. Improved support for `Series` Issue \#46.
12. `Cylinder` rendering is implemented in Asymptote.

# Documentation

1.  \"Testing Expressions\" section added.
2.  \"Representation of Numbers\" section added.
3.  \"Descriptive Statistics\" section added and \"Moments\" folded into
    that.
4.  Many More URL references. `<url>` now supports link text.
5. Reference Chapter and Sections are now in alphabetical order
6.  Two-column mode was removed in most sections, so the printed PDF
    looks nicer.
7.  Printed Error message output in test examples is in typewriter font
    and doesn't drop inter-word spaces.

# Internals

1.  Inexplicably, what the rest of the world calls a \"nodes\" in a tree
    or in WMA \"elements\" in a tree had been called a \"leaves\". We
    now use the proper term \"element\".
2.  Lots of predefined `Symbol`s have been added. Many appear in the
    module `mathics.core.systemsymbols`.
3.  Attributes are now stored in a bitset instead of a tuple of strings.
    This speeds up attributes read and RAM usage.
4.  `Symbol.is_numeric` and `Expression.is_numeric` now use the
    attribute `Definition.is_numeric` to determine the returned value.
5.  `NIntegrate` internal algorithms and interfaces to `scipy` were
    moved to `mathics.algorithm.integrators` and
    `mathics.builtin.scipy_utils.integrators` respectively.
6.  `N[Integrate[...]]` now is evaluated as `NIntegrate[...]`
7.  Definitions for symbols `CurrentContext` and `ContextPath[]` are
    mirrored in the `mathics.core.definitions.Definitions` object for
    faster access.
8.  `FullForm[List[...]]` is shown as `{...}` according to the WL
    standard.
9.  `Expression.is_numeric()` accepts an `Evaluation` object as a
    parameter; the definitions attribute of that is used.
10. `SameQ` first checks the type, then the `id`, and then the names in
    symbols.
11. In `mathics.builtin.patterns.PatternTest`, if the condition is one
    of the most used tests (`NumberQ`, `NumericQ`, `StringQ`, etc), the
    `match` method is overwritten to specialized versions that avoid
    function calls.
12. `mathics.core.patterns.AtomPattern` specializes in the comparison
    depending on the `Atom` type.
13. To speed up development, you can set `NO_CYTHON` to skip Cythonizing
    Python modules. If you are using Pyston or PyPy, Cythonization slows
    things down.
14. `any` and`all` calls were unrolled as loops in Cythonized modules:
    this avoids the overhead of a function call, replacing it by a (C)
    for loop, which is faster.
15. A bug was fixed relating to the order in which
    `mathics.core.definitions` stores the rules
16. `InstanceableBuiltin` -\> `BuiltinElement`
17. `BoxConstruction` -\> `BoxExpression`
18. the method `Element.is_true()` was removed in favor of
    `is SymbolTrue`
19. `N[_,_,Method->method]` was reworked. Issue #137.
20. The methods `boxes_to_*` were moved to `BoxExpression`.
21. remove `flatten_*` from the `Atom` interface.
22. `Definition` has a new property `is_numeric`.

## Speed improvements:

1.  Creating two `Symbol` objects with the same name will give the same
    object. This avoids unnecessary string comparisons and calls to
    `ensure_context`.
2.  Attributes are now stored in a bitset instead of a tuple of strings.
3.  The `Definitions` object has two properties: `current_context` and
    `context_path`. This speeds up the lookup of symbol names. These
    properties store their values in the corresponding symbols in the
    `builtin` definitions.
4.  `eval_N` was added to speed up the then often-used built-in function
    `N`.
5.  `Expression` evaluation was gone over and improved. properties on
    the collection, which can speed up evaluation, such as whether an
    expression is fully evaluated, is ordered, or is flat are collected.
6.  `List` evaluation is customized. There is a new `ListExpression`
    class that has a more streamlined `evaluate()` method. More of this
    kind of thing will follow
7.  `BaseExpression.get_head` avoids building a symbol, saving two
    function calls.

## Package update

1.  SymPy 1.10.1

# Compatibility

1.  `ScriptCommandLine` now returns, as the first element, the name of
    the script file (when available), for compatibility with WMA. Issue #132.
2.  `Expression.numerify` improved in a way to obtain a behavior closer
    to WMA.

3. `NumericQ` lhs expressions are now handled as a special case in assignment. For example `NumericQ[a]=True` tells the interpreter that `a` must be considered

4. a numeric quantity, so `NumericQ[Sin[a]]` evaluates to `True`.

# Bugs

1.  `First`, `Rest`, and `Last` now handle invalid arguments.
2.  `Set*`: fixed.  Issue #128.
3.  `SameQ`: comparison with MachinePrecision only needs to be exact
    within the last bit. Issue #148.
4.  Fix a bug in `Simplify` that produced expressions of the form
    `ConditionalExpression[_,{True}]`.
5.  Fix bug in `Clear` and `ClearAll` (Issue #194).
6.  Fix base 10 formatting for infix `Times`. Issue #266.
7.  Partial fix of `FillSimplify`
8.  Streams used in MathicsOpen are now freed, and their file descriptors are now released. Issue #326.
9.  Some temporary files that were created are now removed from the
    filesystem. Issue #309.
10. There were a number of small changes/fixes involving `NIntegrate`
    and its Method options. `Nintegrate` tests have been expanded.
11. Fix a bug in handling arguments of pythonized expressions, that are
    produced by `Compile` when the llvmlite compiler fails.
12. `N` now handles arbitrary precision numbers when the number of
    digits is not specified.
13. [N\[Indeterminate\]]{.title-ref} now produces
    [Indeterminate]{.title-ref} instead a
    [PrecisionReal(nan)]{.title-ref}.
14. Fix crash in `NestWhile` when supplying `All` as the fourth
    argument.
15. Fix the comparison between `Image` and other expressions.
16. Fix an issue that prevented that [Collect]{.title-ref} from handling polynomials properly on expressions (Issue #285).
17. Fix a bug in formatting expressions of the form `(-1)^a` without the
    parentheses (Issue #332).
18. Fix a bug in the order in which
    `mathics.core.definitions` stores the rules.
19. Numeric overflows now do not affect the full evaluation, but instead
    just the element that produces it.
20. Compatibility with the way expressions are ordered more closely
    follows WMA: Now expressions with fewer elements come first (Issue
    #458).
21. The order of the context name resolution (and `$ContextPath`) was
    switched; `"System` comes before `"Global`.

# Incompatible changes

The following changes were motivated by a need to speed up the
interpreter.

1. `Expression` arguments differ. The first parameter has to be a `Symbol` while the remaining arguments have to be some sort of `BaseElement` rather than something that can be converted to an element.

2   Properties for the collection of elements can be specified when they
    are known. To get the old behavior, use `to_expression`

3.  Expressions that are lists are a new kind of class,
    `ListExpression`. As with expressions, the constructor requires
    valid elements, not something convertible to an element. Use
    `to_mathics_list`

## 4.0.1

New builtins
------------

1. `Guidermannian`
1. `Cone`
1. `Tube`
1. `Normal` now have a basic support for `SeriesData`

Tensor functions:

1. `RotationTransform`
1. `ScalingTransform`
1. `ShearingTransform`
1. `TransformationFunction`
1. `TranslationTransform`

Spherical Bessel functions:

1. `SphericalBesselJ`
1. `SphericalBesselY`
1. `SphericalHankelH1`
1. `SphericalHankelH2`

Gamma functions:

1. `PolyGamma`
1. `Stieltjes`

Uniform Polyhedron
1. `Dodecahedron`
1. `Icosahedron`
1. `Octahedron`
1. `TetraHedron`
1. `UniformPolyedron`

Mathics-specific

1. `TraceBuiltin[]`, `$TraceBuiltins`, `ClearTrace[]`, `PrintTrace[]`

These collect builtin-function call counts and elapsed time in the routines.
`TraceBuiltin[expr]` collects information for just *expr*. Whereas
setting `$TraceBuiltins` to True will accumulate results of evaluations
`PrintTrace[]` dumps the statistics and `ClearTrace[]` clears the statistics data.

`mathics -T/--trace-builtin` is about the same as setting
`$TraceBuiltins = True` on entry and runs `PrintTrace[]` on exit.


Bugs Fixed
----------

1. Fix and document better behavior of `Quantile`
1. Improve Asymptote `BezierCurve` implementation
1. `Rationalize` gives symmetric results for +/- like MMA does. If the result is an integer, it stays that way.
1. stream processing was redone. `InputStream`, `OutputStream` and `StringToStream` should all open, close, and assign stream numbers now

## 4.0.0

August 31, 2021

The main thrust behind this API-breaking release is to be able to support a protocol for Graphics3D.

It new Graphics3D protocol is currently expressed in JSON. There is an
independent [threejs-based module](https://www.npmjs.com/package/@mathicsorg/mathics-threejs-backend)
to implement this. Tiago Cavalcante Trindade is responsible for this
code.

The other main API-breaking change is more decentralization of the
Mathics3 Documentation. A lot more work needs to go on here, and so
there will be one or two more API breaking releases. After this
release, the documentation code will be split off into its own git
repository.

Enhancements
------------

1. a Graphics3D protocol, mentioned above, has been started
1. `mathics.setting` have been gone over to simplify.
1. A rudimentary and crude SVG Density Plot was added. The prior method relied on mysterious secret handshakes in JSON between Mathics3 Core and Mathics Django. While the density plot output was nicer in Mathics Django, from an overall API perspective this was untenable. A future version may improve SVG handling of Density plots using elliptic density gratings in SVG. And/or we may define this in the JSON API.
1. SVG and Asymptote drawing now includes inline comments indicating which Box Structures are being implemented in code

Documentation
-------------

1. Document data used in producing PDFs and HTML-rendered documents is now stored in both the user space, where it can be extended, and in the package install space -- which is useful when there is no user-space data.
1. The documentation pipeline has been gone over. Turning the internal data into a LaTeX file is now a separate own program. See `mathics/doc/test/README.rst` for an overview of the dataflow needed to create a PDF.
1. Summary text for various built-in functions has been started. These  summaries are visible in Mathics3 Django when lists links are given in Chapters, Guide Sections, or Sections.
1. A Sections for Lists has been started and grouping for these have been added. So code and sections have moved around here.
1. Regexp detection of tests versus document text has been improved.
1. Documentation improved
1. The flakiness around showing sine graphs with filling on the axes or below has been addressed. We now warn when a version of Asymptote or Ghostscript is used that is likely to give a problem.

Bugs Fixed
----------

1. A small SVGTransform bug was fixed. Thanks to axelclk for spotting.
1. Elliptic arcs are now supported in Asymptote. There still is a bug however in calculating the bounding box when this happens.
1. A bug in image decoding introduced in 3.1.0 or so was fixed.
1. A bug SVG LineBoxes was fixed

Regressions
-----------

1. Some of the test output for builtins inside a guide sections is not automatically rendered
1. Density plot rendered in Mathics3 Django do not render as nice since we no longer use the secret protocol handshake hack. We may fix this in a future release
1. Some of the Asymptote graphs look different. Graphic3D mesh lines are not as prominent or don't appear. This is due to using a newer version of Asymptote, and we will address this in a future release.

## 3.1.0

August 3, 2021

New variables and builtins
--------------------------

1. `Arrow` for Graphics3D (preliminary)
1. `Cylinder` (preliminary)
1. `Factorial2` PR #1459 Issue #682.

Enhancements
------------

Large sections like the "Strings and Characters", "Integer Functions" and "Lists" sections
have been broken up into subsections. These more closely match
online WL "Guide" sections.  This is beneficial not just in the
documentation, but also for code organization. See PRs #1464, #1473.

A lot more work is needed here.

The Introduction section of the manual has been revised. Licensing and Copyright/left sections
have been reformatted for non-fixed-width displays. #1474

PolarPlot documentation was improved. #1475.

A getter/setter method for Mathics3 settings was added #1472.


Bugs Fixed
----------

1. Add `requirements-*.txt`to distribution files. `pip install Mathics3[dev]` should work now. PR #1461
1. Some `PointBox` bugs were fixed
1. Some `Arrow3DBox` and `Point3DBox` bugs were fixed PR #1463
1. Fix bug in `mathics` CLI when  `-script` and `-e` were combined PR #1455

-----------------


## 3.0.0

June 26, 2021

Overall there is a major refactoring underway of how formatting works
and its interaction with graphics.  More work will come in later releases.

Some of the improvements are visible not here but in the front-ends
mathicsscript and mathics-django. In mathicsscript, we can now show
SVG images (via matplotlib).  In Mathics3 Django, images and threejs
graphs are no longer embedded in MathML.

A lot of the improvements in this release were done or made possible with the help of
Tiago Cavalcante Trindade.

Enhancements
------------

It is now possible to get back SVG, and graphics that are not embedded in MathML.

The code is now Pyston 2.2 compatible. However `scipy` `lxml` are
not currently available on Pyston so there is a slight loss of
functionality. The code runs about 30% faster under Pyston 2.2. Note
that the code also works under PyPy 3.7.

Bugs Fixed
----------

1. Tick marks and the placement of numbers on charts have been corrected. PR #1437
1. Asymptote now respects the `PointSize` setting.
1. In graphs rendered in SVG, the `PointSize` has been made more closely match Mathematica.
1. Polygons rendered in Asymptote now respects the even/odd rule for filling areas.

Density Plots rendered in SVG broke with this release. They will be reinstated in the future.

Documentation
-------------

Go over settings file to ensure usage names are full sentences.

We have started to put more builtins in the sections or subsections
following the organization in Mathematics 5 or as found in the online
Wolfram Language Reference. As a result, long lists in previous topics
are a bit shorter and there are now more sections. This work was
started in 2.2.0.

More work is needed on formatting and showing this information, with
the additional breakout we now have subsections. More reorganization
and sectioning is needed.

These cleanups will happen in a future version.

Chapters without introductory text like `Structural Operations`, or `Tensors` have had descriptions added.

Sections that were empty have either been expanded or removed because
the underlying name was never a user-level built in, e.g. the various
internal Boxing functions like `DiskBox`, or `CompiledCodeBox`

Documentation specific builtins like `PolarPlot` or
`BernsteinBasis` have been added improved, and document examples
have been revised such as for `PieChart`, `Pi` and others.

The Mathics3 Gallery examples have been updated.

Some slight improvements were made to producing the PDF and more kinds
of non-ASCII symbols are tolerated. Expect more work on this in the future via tables from the [Mathics3 Scanner](https://pypi.org/project/Mathics-Scanner/1.2.1/) project.

Chapters are no longer in Roman Numerals.


Internal changes
----------------

1. `docpipline.py`  accepts the option `--chapters` or `-c` to narrow tests to a particular chapter
1. Format routines have been isolated into its own module. Currently, we have format routines for SVG, JSON and Asymptote. Expect more reorganization in the future.
1. Boxing routines have been isolated to its own module.
1. The entire code base has been run through the Python formatter [black](https://black.readthedocs.io/en/stable/).
1. More Python3 types to function signatures have been added.
1. More document tests that were not user-visible have been moved to unit tests, which run faster. More work is needed here.

## 2.2.0

May 5, 2021

Package update
--------------

1. SymPy 1.8

New variables and builtins
--------------------------

1. `Arg`
1. `CoefficientArrays` and `Collect` (#1174, #1194)
1. `Dispatch`
1. `FullSimplify`
1. `LetterNumber` #1298. The `alphabet` parameter supports only a minimal number of languages.
1. `MemoryAvailable`
1. `MemoryInUse`
1. `Nand` and `Nor` logical functions.
1. `Series`,  `O` and `SeriesData`
1. `StringReverse`
1. `$SystemMemory`
1. Add all of the named colors, e.g. `Brown` or `LighterMagenta`.



Enhancements
------------

1. a function `evaluate_predicate` allows for a basic predicate evaluation using `$Assumptions`.
1. `Attributes` accepts a string parameter.
1. `Cases` accepts Heads option. Issue #1302.
1. `ColorNegate` for colors is supported.
1. `D` and `Derivative` improvements.
1. `Expand` and `ExpandAll` now support a second parameter `patt` Issue #1301.
1. `Expand` and `ExpandAll` works with hyperbolic functions (`Sinh`, `Cosh`, `Tanh`, `Coth`).
1. `FileNames` returns a sorted list. Issue #1250.
1. `FindRoot` now accepts several optional parameters like `Method` and `MaxIterations`. See Issue #1235.
1. `FixedPoint` now supports the `SameTest` option.
1. `mathics` CLI now uses its own Mathics3 `settings.m` file
1. `Prepend` works with `DownValues` Issue #1251
1. `Prime` and `PrimePi` now accept a list parameter and have the `NumericFunction` attribute.
1. `Read` with `Hold[Expression]` now supported. (#1242)
1. `ReplaceRepeated` and `FixedPoint` now supports the `MaxIteration` option. See Issue #1260.
1. `Simplify` performs a more sophisticated set of simplifications.
1. `Simplify` accepts a second parameter that temporarily overwrites `$Assumptions`.
1. `StringTake` now accepts a form containing a list of strings and a specification. See Issue #1297.
1. `Table` [*expr*, *n*] is supported.
1. `ToExpression` handles multi-line string input.
1. `ToString` accepts an optional *form* parameter.
1. `ToExpression` handles multi-line string input.
1. `$VersionNumber` now set to 10.0 (was 6.0).
1. The implementation of Streams was redone.
1. Function `mathics.core.definitions.autoload_files` was added and exposed to allow front-ends to provide their own custom Mathics. settings.
1. String output in the `mathics` terminal has surrounding quotes to make it more visually distinct from unexpanded and symbol output. To disable this behavior use `--strict-wl-output`.


Bug fixes
---------

1. `SetTagDelayed` now does not evaluate the RHS before assignment.
1. `$InstallationDirectory` starts out `Unprotected`.
1. `FindRoot` now handles equations.
1. Malformed Patterns are detected and an error message is given for them.
1. Functions gone over to ensure the `Listable` and `NumericFunction` properties are correct.


Incompatible changes
1.-------------------

1. `System`$UseSansSerif` moved from core and is sent to front-ends using `Settings`$UseSansSerif`.


Internal changes
1.---------------

1. `docpipeline.py`  accepts the option `-d` to show how long it takes to parse, evaluate and compare each individual test. `-x` option (akin to `pytests -x` is a short-hand for stop on first error
1. Some builtin functions have been grouped together in a module underneath the top-level builtin directory.  As a result, in the documents you will list some builtins listed under an overarching category like `Specific Functions` or `Graphics, Drawing, and Images`. More work is expected in the future to improve document sectioning.
1. `System`$Notebooks` is removed from settings. It is in all of the front-ends now.


## 2.1.0



New builtins
------------

1. `ArcTanh`
1. `ByteArray`
1. `CreateFile`
1. `CreateTemporary`
1. `FileNames`
1. `NIntegrate`
1. `PartitionsP`
1. `$Notebooks`
1. `SparseArray`

Enhancements
------------

1. The Mathics3 version is checked for builtin modules at load time. A message is given when a builtin doesn't load.
1. Automatic detection for the best strategy to numeric evaluation of constants.
1. `FileNameJoin` now implements `OperatingSystem` option
1. Mathics3 functions are accepted by `Compile[]`. The return value or type will be `Compile[] and CompiledFunction[]`.  Every Mathics3 Expression can have a compiled form, which may be implemented as a Python function.
1. `Equal[]` now compares complex against other numbers properly.
1. Improvements in handling products with infinite factors: `0 Infinity`-> `Indeterminate`, and `expr Infinity`-> `DirectedInfinite[expr]`
1. `$Path` is now `Unprotected` by default
1. `Read[]` handles expressions better.
1. `StringSplit[]` now accepts a list in the first argument.
1. `SetDelayed[]` now accepts several conditions imposed both at LHS as well as RHS.
1. Axes for 2D Plots are now rendered for SVGs
1. `InsertBox` accepts an opaque parameter


Bug fixes
---------

`TeXForm[]` for integrals are now properly formatted.


Mathics3 Modules
----------------

1. Mathics3 modules now can run initialization code when are loaded.
1. The `builtins` list is not hard-linked to the library anymore. This simplifies the loading and reloading of pymathics modules.
1. Decoupling of BoxConstructors from the library. Now are defined at the level of the definition objects. This is useful for customizing the Graphics output if it is available.


Miscellanea
-----------

1. A pass was made to improve Microsoft Windows compatibility and testing Windows under MSYS.
1. Include numpy version in version string. Show in CLI
1. Small CLI tweaks `--colors=None` added to match mathicsscript.
1. In the `BaseExpression` and derived classes, the method `boxes_to_xml` now are called `boxes_to_mathml`.
1. In the `format` method of the class `Evaluation`,  the builtin `ToString` is called instead of  `boxes_to_text`
1. In order to control the final form of boxes from the user space in specific symbols and contexts.
1. `GraphicsBox` now have two methods:  `to_svg` and  `to_mathml`. The first produces SVG plain text while the second produces `<mglyph ...>` tags with base64 encoded SVGs.


What's to expect in a Future Release
------------------------------------

1. Improved `Equal` See [PR #1209](https://github.com/mathics/Mathics/pull/1209/)
1. Better Unicode support, especially for Mathics3 operators
1. Improved `D[]` and `Derivative[]` See [PR #1220](https://github.com/mathics/Mathics/pull/1220/)
1. Improved performance
1. `Collect[]` See [Issue #1194](https://github.com/mathics/Mathics/issues/1194).
1. `Series[]` See [Issue #1193](https://github.com/mathics/Mathics/issues/1193).


2.0.0
=====

Feb 14, 2021

To accommodate growth and increased use of pieces of Mathics3 inside other packages, parts of Mathics3 have been split off and moved to separate packages. In particular:

1. The Django front-end is now a PyPI installable package called [Mathics3-django](https://pypi.org/project/Mathics3-django).
1. Scanner routines, character translation tables to/from Unicode, and character properties are now [mathics-scanner](https://github.com/Mathics3/mathics-scanner).
1. Specific builtins involving heavy, non-standard routines were moved to pymathics modules [Mathics3-Module-networkx](https://github.com/Mathics3/Mathics3-Module-networkx), [Mathics3-Module-nltk](https://github.com/Mathics3/Mathics3-Module-nltk).

Incompatible changes:
---------------------

1. `-e` `--execute` is better suited for embedded use. It shows just evaluation output as text.
1. Docker scripts `dmathics`, `dmathicsscript` and `dmathicsserver` have been removed. They are part of the `docker-mathics` a separate PyPI package.

The bump in the major version number reflects major changes in this release. Another major release is planned soon, with more major changes.

See below for future work planned.

New builtins
------------

1. `AnglePath`,  `AnglePathFold`, `AngleVector`
1. `BoxData`, `TextData`, `InterpretationBox`, `StyleBox`, `TagBox`, `TemplateBox`, `ButtonBox`, `InterpretationBox`
1. `ContinuedFraction`
1. `ConvertCommonDumpRemoveLinearSyntax` and `System`ConvertersDump` context variables
1. `FirstCase`, `Lookup`, `Key`, `Lookup` and `Failure`
1. `Haversine`, `InverseHaversine`
1. `Insert` and `Delete`
1. `LerchPhi`
1. `MathicsVersion` (this is not in WL)
1. `NumberQ`
1. `PossibleZeroQ` PR #1100
1. `Run`
1. `Show`
1. `SympyObject`
1. `TimeRemaining` and `TimeConstrained`
1. `\[RadicalBox]`
1.  Improving support for options in the Plot module: `Axes`, `Filling`, `ImageSize`, `Joined`

New constants
-------------

Mathematical Constants is now its own module/section. Constants have been filled out. These constants have been added:

1. `Catalan`
1. `Degree`
1. `Glaisher`
1. `GoldenRatio`
1. `Khinchin`

Many of these and the existing constants are computable via mpmath, NumPy, or Sympy.

Settings through WL variables
-----------------------------

Certain aspects of the kernel configuration are now controlled by variables, defined in `/autoload/settings.m`.

1. `$GetTrace` (`False` by default).  Defines if when a WL module is load through `Get`, definitions will be traced (for debug).
1. `$PreferredBackendMethod` Set this do whether to use mpmath, NumPy or SymPy for numeric and symbolic constants and methods when there is a choice (`"sympy"` by default) (see #1124)

Enhancements
------------

1. Add `Method` option "mpmath" to compute `Eigenvalues` using mpmath (#1115).
1. Improve support for `OptionValue` and `OptionsPattern` (#1113)

Bug fixes
---------

Numerous bugs were fixed while working on Combinatorica V0.9 and CellsToTeX.

1. `Sum` involving numeric integer bounds involving Mathics3 functions fixed.
1. `Equal` `UnEqual` testing on Strings (#1128).

Document updates
----------------

1. Start a readthedocs [Developer Guide](https://mathics-development-guide.reandthedocs.io/en/latest/)_

Enhancements and bug fixes:
---------------------------

1. Fix evaluation timeouts
1. `Sum`'s lower and upper bounds can now be Mathics3 expressions

Miscellanea
-----------

1. Enlarge the set of `gries_schneider` tests
1. Improve the way builtins modules are loaded at initialization time (#1138).

Future
------

1. We are in the process of splitting out graphics renderers, notably for matplotlib. See [pymathics-matplotlib](https://github.com/Mathics3/pymathics-matplotlib).
1. Work is also being done on asymptote. See [PR #1145](https://github.com/mathics/Mathics/pull/1145).
1. Makeboxes is being decoupled from a renderer. See [PR #1140](https://github.com/mathics/Mathics/pull/1140).
1. Inline SVG will be supported (right now SVG is binary).
1. Better support integrating Unicode in output (such as for Rule arrows) is in the works. These properties will be in the scanner package.
1. A method option ("mpmath", "sympy", or "numpy") will be added to the `N[]`. See [PR #1144](https://github.com/mathics/Mathics/pull/1144>).


# 1.1.1

This may be the last update before some major refactoring and interface changes occur.

In a future 2.0.0 release, Django will no longer be bundled here. See [Mathics3-django](https://github.com/Mathics3/mathics-django) for the unbundled replacement.

Some changes were made to support network graph [Mathics3-Module-networkx](https://github.com/Mathics3/pymathics-graph), a new graph package bundled separately, and to support the ability for front-ends to handle rendering on their own. Note that currently this doesn't integrate well into the Django interface, although it works well in `mathicsscript`.

Package updates
---------------

1. SymPy 1.7.1

Mathics3 Packages added:

1. `DiscreteMath`CombinatoricaV0.9` (preferred) and `DiscreteMath`CombinatoricaV0.6`.

Both of these correspond to Steven Skiena's *older* book: *Implementing Discrete Mathematics: Combinatorics and Graph Theory*.

If you have a package that you would like included in the distribution, and it works with Mathics, please contact us.

Rubi may appear in a future release, possibly in a year or so. Any help to make this happen sooner is appreciated.

New builtins
------------

1. `StirlingS1`, `StirlingS2` (not all WL variations handled)
1. `MapAt` (not all WL variations handled)
1. `PythonForm`, `SympyForm`: not in WL. Expect more and better translations later as Mathics3 modules.
1. `Throw` and `Catch`
1. `With`
1. `FileNameTake`

Enhancements and bug fixes
--------------------------

1. Workaround for `Compile` so it accepts functions ##1026
1. Add `Trace` option to `Get`. `Get["fn", Trace->True]` will show lines as they are read
1. Convert to/from Boolean types properly in `from_python`, `to_python`. Previously they were 0 and 1
1. Extend `DeleteCases` to accept a levelspec parameter
1. Set `Evaluation#exc_result` to capture `Aborted`, `Timeout`, `Overflow1`, etc.
1. `ImageData` changed to get bits {0,1}, not booleans as previously
1. Add tokenizer symbols for `<->` and `->` and the Unicode versions of those
1. Small corrections to `Needs`, e.g check if already loaded, correct a typo, etc.
1. `System`$InputFileName` is now set inside `Needs` and `Get`
1. Install shell scripts `dmathicserver`, `dmathicsscript`, and `dmathics` to simplify running docker
1. Adjust `$InputFileName` inside `Get` and `Needs`
1. Support for `All` as a `Part` specification
1. Fix `BeginPackage`
1. Improving support for `OptionValue`. Now it supports list of Options
1. Adding support in `from_python()` to convert dictionaries in list of rules
1. Fix `OptionsPattern` associated symbols

----

## 1.1.0

So we can get onto PyPI, the PyPI install name has changed from Mathics to Mathics3.

Enhancements and bug fixes
--------------------------

1. Add Symbolic Comparisons. PR #1000
1. Support for externally PyPI-packagable builtin modules - PyMathics
1. `SetDirectory` fixes. PR #994
1. Catch ``PatternError` Exceptions
1. Fix formatting of `..` and `...` (`RepeatAll`)
1. Tokenization of `\.` without a following space (`ReplaceAll`). Issue #992.
1. Support for assignments to named ``Pattern``
1. Improve support for ``Names`. PR #1003
1. Add a `MathicsSession` class to simplify running Mathics3 from Python. PR #1001
1. Improve support for ``Protect`` and ``Unprotect`` list of symbols and regular expressions. PR #1003

----

## 1.1.0 rc1

Package updates
---------------

All major packages that Mathics3 needs have been updated for more recent
releases. Specifically these include:

1. Python: Python 3.6-3.9 are now supported
1. Cython >= 0.15.1
1. Django 3.1.x
1. mpmath >= 1.1.0
1. SymPy 1.6.2

New features (50+ builtins)
---------------------------

1. `Association`, `AssociationQ`, `FirstPostion`, `LeafCount`
1. `Association`, `AssociationQ`, `Keys`, `Values` #705
1. `BarChart[]`, `PieChart`, `Histogram`, `DensityPlot` #499
1. `BooleanQ`, `DigitQ` and `LetterQ`
1. `CharacterEncoding` option for `Import[]`
1. `Coefficient[]`, `Coefficient[x * y, z, 0]`, `Coefficient*[]`
1. `DiscreteLimit` #922
1. `Environment`
1. File read operations from URLs
1. `FirstPostions`, `Integers`, `PrePendTo[]`
1. `GetEnvironment` # 938
1. `Integers`, `PrependTo` and `ContainsOnly`
1. `Import` support for WL packages
1. `IterationLimit`
1. `LoadModule`
1. `MantissaExponent[]`, `FractionalPart[]`, `CubeRoot[]`
1. `PolynomialQ[]`, `MinimalPolynomial[]`
1. `Quit[]`, `Exit[]` #523, #814,
1. `RealDigits` #891, #691, `Interrupt`, `Unique`
1. `RemoveDiacritics[]`, `Transliterate[]` #617
1. `Root` #806
1. `Sign[]`, `Exponent`, `Divisors`, `QuotientRemainder`, `FactorTermsList`
1. Speedups by avoiding inner classes, #616
1. `StringRiffle[]`, `StringFreeQ[]`, `StringContainsQ[]`, `StringInsert`
1. `SubsetQ` and `Delete[]` #688, #784,
1. `Subsets` #685
1. `SystemTimeZone` and correct `TimeZone` #924
1. `System\`Byteordering` and `System\`Environment` #859
1. `$UseSansSerif` #908
1. `randchoice` option for `NoNumPyRandomEnv` #820
1. Support for `MATHICS_MAX_RECURSION_DEPTH`
1. Option `--full-form` (`-F`) on `mathics` to parsed `FullForm` of input expressions

Enhancements and bug fixes
--------------------------

1. speed up leading-blank patterns #625, #933
1. support for iteration over Sequence objects in `Table`, `Sum`, and `Product`
1. fixes for option handling
1. fixes for `Manipulate[x,{x,{a,b}}]`
1. fixes rule -> rule case for `Nearest`
1. fixes and enhancements to `WordCloud`
1. added `StringTrim[]`
1. fixes `URLFetch` options
1. fixes `XMLGetString` and parse error
1. fixes `LanguageIdentify`
1. fixes 2 <= base <= 36 in number parsing
1. improved error messages
1. fixes `Check`, `Interrupt`, and `Unique` #696
1. fixes `Eigenvalues`, `Eigenvectors` #804
1. fixes `Solve` #806
1. proper sympolic expantion for `Re` and `Im`
1. fixes a bug in the evaluation of `SympyPrime` #827
1. clean up `ColorData`
1. fixes Unicode characters in TeX document
1. update Django gallery examples
1. fixes `Sum` and `Product` #869, #873
1. warn when using options not supported by a Builtin #898, #645

Mathematica tracking changes
----------------------------

1. renamed `FetchURL` to `URLFetch` (according to the WL standard)
1. renamed `SymbolLookup` to `Lookup`

Performance improvements
------------------------

1. Speed up pattern matching for large lists
1. Quadratic speed improvement in pattern matching. #619 and see the graph comparisons there
1. In-memory sessions #623

Other changes
-------------

1. bump `RecursionLimit`
1. blacken (format) a number of Python files and remove blanks at the end of lines
1. Adding several CI tests
1. Remove various deprecation warnings
1. Change `#!` from `python` to `python3`
1. Update docs

Backward incompatibilities
--------------------------

1. Support for Python 3.5 and earlier, and in particular Python 2.7, was dropped.
1. The `graphs` module (for Graphs) has been pulled until Mathics3 supports  pymathics and graphics using `networkx` better. It will reappear as a pymathics module.
1. The `natlang` (for Natural Language processing) has also been pulled.  The problem here, too, is that the pymathics mechanism needs a small amount of work to make it scalable, and in 1.0 these were hard-coded. Also, both this module and `graphs` pulled in some potentially hard-to-satisfy non-Python dependencies such as matplotlib, or NLP libraries, and word lists. All of this made installation of Mathics3 harder, and the import of these libraries,   `natlang` in particular, took some time. All of these point to having these live in their repositories and get imported lazily on demand.


-----

## 1.0 (October 2016)

New features
------------

1. `LinearModelFit` #592
1. `EasterSunday` #590
1. `DSolve` for PDE #589
1. `LogisticSigmoid` #588
1. `CentralMoment`, `Skewness`, `Kurtosis` #583
1. New web interface #574
1. `Image` support and image processing functions #571, #541, #497, #493, #482
1. `StringCases`, `Shortest`, `Longest` string match/replace #570
1. `Quantime` and `Quartiles` #567
1. `Pick` #563
1. `ByteCount` #560
1. `Nearest` #559
1. `Count` #558
1. `RegularPolygon` #556
1. Improved date parsing #555
1. `Permutations` #552
1. LLVM compilation of simple expressions #548
1. `NumberForm` #534, #530, #455
1. Basic scripting with mathicsscript
1. Arcs for `Disk` and `Circle` #498, #526
1. Download from URL #525
1. `$CommandLine` #524
1. `Background` option for `Graphics` #522
1. `Style` #521, #471, #468
1. Abbreviated string patterns #518
1. `Return` #515
1. Better messages #514
1. Undo and redo functionality in web interface #511
1. `Covariance` and `Correlation` #506
1. `ToLowerCase`, `ToUpperCase`, `LowerCaseQ`, `UpperCaseQ` #505
1. `StringRepeat` #504
1. `TextRecognise` #500
1. Axis numbers to integers when possible #495
1. `PointSize` #494
1. `FilledCurve`, `BezierCurve`, `BezierFunction` #485
1. `PadLeft`, `PadRight` #484
1. `Manipulate` #483, #379, #366
1. `Replace` #478
1. String operator versions #476
1. Improvements to `Piecewise` #475
1. Derivation typo #474
1. Natural language processing functions #472
1. `Arrow`, `Arrowheads` #470
1. Optional modules with requires attribute #465
1. `MachinePrecision` #463
1. `Catenate` #454
1. `Quotient` #456
1. Disable spellcheck on query fields #453
1. `MapThread` #452
1. `Scan` and `Return` #451
1. `On` and `Off` #450
1. `$MachineEpsilon` and `$MachinePrecision` #449
1. `ExpandAll` #447
1. `Position` #445
1. `StringPosition` #444
1. `AppendTo`, `DeleteCases`, `TrueQ`,  `ValueQ` #443
1. `Indeterminate` #439
1. More integral functions #437
1. `ExpIntegralEi` and `ExpIntegralE` #435
1. `Variance` and `StandardDeviation` #424
1. Legacy `Random` function #422
1. Improved gamma functions #419
1. New recursive descent parser #416
1. `TakeSmallest` and related #412
1. `Boole` #411
1. `Median`, `RankedMin`, `RankedMax` #410
1. `HammingDistance` #409
1. `JaccardDissimilarity` and others #407
1. `EuclideanDistance` and related #405
1. Magic methods for `Expression` #404
1. `Reverse` #403
1. `RotateLeft` and `RotateRight` #402
1. `ColorDistance`, `ColorConvert` #400
1. Predefine and document `$Aborted` and `$Failed` #399
1. `IntegerString`, `FromDigits`, and more #397
1. `EditDistance` and `DamerauLevenshteinDistance` #394
1. `QRDecomposition` #393
1. `RandomChoice` and `RandomSample` #488
1. `Hash` #387
1. Graphics boxes for colors #386
1. `Except` #353
1. Document many things #341
1. `StringExpression` #339
1. Legacy file functions #338

Bug fixes
---------

1. Nested `Module` #591, #584
1. Python2 import bug #565
1. XML import #554
1. `\[Minus]` parsing bug #550
1. `Cases` evaluation bug #531
1. `Take` edge cases #519
1. `PlotSize` bug #512
1. Firefox nodeValue warning #496
1. Django database permissions #489
1. `FromDigits` missing message #479
1. Numerification upon result only #477
1. Saving and loading notebooks #473
1. `Rationalise` #460
1. `Optional` and `Pattern` precedence values #459
1. Fix `Sum[i / Log[i], {i, 1, Infinity}]` #442
1. Add `\[Pi]`, `\[Degree]`, `\[Infinity]` and `\[I]` to parser #441
1. Fix loss of precision bugs #440
1. Many minor bugs from fuzzing #436
1. `Positive`/`Negative` do not numerify arguments #430 fixes #380
1. Chains of approximate identities #429
1. Logical expressions behave inconsistently/incorrectly #420 fixes #260
1. Fix `Take[_Symbol, ___]` #396
1. Avoid slots in rule handling #375 fixes #373
1. `Gather`, `GatherBy`, `Tally`, `Union`, `Intersect`, `IntersectingQ`, `DisjointQ`, `SortBy` and `BinarySearch` #373
1. Symbol string comparison bug #371
1. Fix `Begin`/`BeginPackage` leaking user-visible symbols #352
1. Fix `TableForm` and `Dimensions` with an empty list #343
1. Trailing slash bug #337
1. `Global` system bug #336
1. `Null` comparison bug #371
1. `CompoundExpression` and `Out[n]` assignment bug #335 fixes #331
1. Load unevaluated cells #332

Performance improvements
------------------------

1. Large expression formatting with `$OutputSizeLimit` #581
1. Faster terminal output #579
1. Faster `walk_paths` #578
1. Faster flatten for `Sequence` symbols #577
1. Compilation for plotting #576
1. `Sequence` optimisations #568
1. Improvements to `GatherBy` #566
1. Optimised `Expression` creation #536
1. `Expression` caching #535
1. `Definitions` caching #507
1. Optimised `Position`, `Cases`, `DeleteCases` #503
1. Optimised `StringSplit` #502
1. Optimised `$RecursionLimit` #501
1. Optimised insert_rule #464
1. Optimised `IntegerLength` #462
1. Optimised `BaseExpression` creation #458
1. No reevaluation of evaluated values #391
1. Shortcut rule lookup #389
1. 15% performance boost by preventing some rule lookups #384
1. 25% performance boost using same over `__eq__`
1. n log n algorithm for `Complement` and `DeleteDuplicates` #373
1. Avoid computing `x^y` in `PowerMod[x, y, m]` #342


-----

0.9 (March 2016)
================

New features
------------

1. Improve syntax error messages #329
1. `SVD`, `LeastSquares`, `PseudoInverse` #258, #321
1. Python 2.7, 3.2-3.5 via six support #317
1. Improvements to `Riffle` #313
1. Tweaks to `PolarPlot` #305
1. `StringTake` #285
1. `Norm` #268 #270
1. `Total`, `Accumulate`, `FoldList`, `Fold` #264, #252
1. `Flatten` #253 #269
1. `Which` with symbolic arguments #250
1. `Min`/`Max` with symbolic arguments # 249

Dependency updates
------------------

1. Upgrade to ply 3.8 (issue #246)
1. Drop interrupting cow #317
1. Add six (already required by Django) #317

Bug fixes
---------

1. Span issues with negative indices #196 fixed by #263 #325
1. SVG export bug fixed by #324
1. Django runserver threading issue #158 fixed by #323
1. asymptote bug building docs #297 fixed by #317
1. Simplify issue #254 fixed by #322
1. `ParametricPlot` bug fixed by #320
1. `DensityPlot` SVG regression in the web interface
1. Main function for server.py #288, #289 fixed by #298
1. ply table regeneration #294 fixed by #295
1. Print bar issue #290 fixed by #293
1. Quit[] index error #292 partially fixed by #307
1. Quit definition fixed by #286
1. Conjugate issue #272 fixed by #281

-----------

## 0.8 (late May 2015)

New features
------------

1. Improvements to 3D Plotting, see #238
1. Enable MathJax menu, see #236
1. Improvements to documentation

Dependency updates
------------------

1. Upgrade to SymPy 0.7.6
1. Upgrade to ply3.6 (new parsetab format, see #246)
1. Upgrade to mpmath 0.19

Bug fixes
---------

1. `IntegerDigits[0]`

-----------

## 0.7 (Dec 2014)

New features
------------

1. Readline tab completion
1. Automatic database initialisation
1. Support for wildcards in `Clear` and `ClearAll`
1. Add `Conjugate`
1. More tests and documentation for `Sequence`
1. Context support


Bugs Fixed
----------

1. Fix unevaluated index handling (issue #217)
1. Fix `Solve` treating one solution equal to 1 as a tautology (issue #208)
1. Fix temporary symbols appearing in the result when taking derivatives with respect to `t` (issue #184)
1. Typo in save worksheet help text (issue #199)
1. Fix mathicsserver wildcard address binding
1. Fix `Dot` acting on matrices in MatrixForm (issue #145)
1. Fix Sum behaviour when using range to generate index values (issue #149)
1. Fix behaviour of plot with unevaluated arguments (issue #150)
1. Fix zero-width space between factors in MathJax output (issue #45)
1. Fix `{{2*a, 0},{0,0}}//MatrixForm` crashing in the web interface (issue #182)

--------------

## 0.6 (late October 2013)

New features
------------

1. `ElementData` using data from Wikipedia
1. Add `Switch`
1. Add `DSolve` and `RSolve`
1. More Timing functions `AbsoluteTiming`, `TimeUsed`, `SessionTime`, `Pause`
1. Date functions `DateList`, `DateString`, `DateDifference`, etc.
1. Parser rewritten using lex/yacc (PLY)
1. Unicode character support
1. `PolarPlot`
1. IPython style (coloured) input
1. `VectorAnalysis` Package
1. More special functions (Bessel functions and orthogonal polynomials)
1. More NumberTheory functions
1. `Import`, `Export`, `Get`, `Needs` and other IO related functions
1. PyPy compatibility
1. Add benchmarks (`mathics/benchmark.py`)
1. `BaseForm`
1. `DeleteDuplicates`
1. Depth, Operate Through, and other Structure-related functions
1. Changes to `MatrixForm` and `TableForm` printing
1. Use interrupting COW to limit evaluation time
1. Character Code functions

Bugs Fixed
----------

1. Fix divide-by-zero with zero-length plot range
1. Fix mathicsserver exception on startup with Django 1.6 (issues #194, #205, #209)

-------

## 0.5 (August 2012)

1. Compatibility with Sage 5, SymPy 0.7, Cython 0.15, Django 1.2
1. 3D graphics and plots using WebGL in the browser and Asymptote in TeX output
1. Plot: adaptive sampling
1. MathJax 2.0 and line breaking
1. New symbols: `Graphics3D` etc., `Plot3D`, `ListPlot`, `ListLinePlot`, `ParametricPlot`, `Prime`, `Names`, `$Version`
1. Fixed issues: 1, 4, 6, 8-21, 23-27
1. Lots of minor fixes and improvements
1. Number of built-in symbols: 386

-------

## 0.4

Compatibility with Sage 4.0 and other latest libraries

-------


## 0.3 (beta only)

Resolved several issues

-------


## 0.1 (alpha only)

Initial version
