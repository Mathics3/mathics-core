	.. contents::

CHANGES
=======

6.0.3 and 6.0.4
-----

Correct type annotation in ``mathics.session.MathicsSession`` See `Issue #934 <https://github.com/Mathics3/mathics-core/issues/934>`_.

6.0.2
-----

Change testing to facilitate openSUSE Tumbleweed distribution which uses Sympy 1.12. See `Issue #881 <https://github.com/Mathics3/mathics-core/issues/881>`_.

Package update
..............

#. SymPy 1.12 accepted

6.0.1
-----

Release to get Pillow 9.2 dependency added for Python 3.7+

Some Pattern-matching code gone over to add type annotations and to start
documenting its behavior and characteristics. Function
attributes are now examined and stored at the time of Pattern-object creation
rather than at evaluation time. This better matches WMA behavior which pulls
out attribute this even earlier than this.  These changes speed up
doctest running time by about 7% under Pyston.

Combinatorica version upgraded from 0.9 (circa 1992) to 0.91 (circa 1995) which closer matches the published book.

Random builtin documentation gone over to conform to current documentation style.

6.0.0
-----

A fair bit of code refactoring has gone on so that we might be able to
scale the code, get it to be more performant, and more in line with
other interpreters. There is Greater use of Symbols as opposed to strings.

The builtin Functions have been organized into grouping akin to what is found in WMA.
This is not just for documentation purposes, but it better modularizes the code and keep
the modules smaller while suggesting where functions below as we scale.

Image Routines have been gone over and fixed. Basically we use Pillow
imaging routines and as opposed to home-grown image code.

A number of Built-in functions that were implemented were not accessible for various reasons.

Mathics3 Modules are better integrated into the documentation.
Existing Mathics3 modules ``pymathics.graph`` and ``pymathics.natlang`` have
had a major overhaul, although more is needed. And will continue after the 6.0.0 release

We have gradually been rolling in more Python type annotations and
current Python practices such as using ``isort``, ``black`` and ``flake8``.

Evaluation methods of built-in functions start ``eval_`` not ``apply_``.


API
+++

#. New function ``mathics.system_info.python_implementation()`` shows the Python Implementation, e.g. CPython, PyPy, Pyston that is running Python. This is included in the information ``mathics.system_info.mathics_system__system_info()`` returns and is used in ``$PythonImplementation``
#. A list of optional software can be found in ``mathics.optional_software``. Versions of that software are included in ``mathics.version_info``.


Package update
..............

#. SymPy 1.11.1 accepted
#. Numpy 1.24.0 accepted


New Builtins
+++++++++++

#. ``$BoxForms``
#. ``$OutputForms``
#. ``$PrintForms``
#. ``$PythonImplementation``
#. ``Accuracy``
#. ``ClebschGordan``
#. ``Curl`` (2-D and 3-D vector forms only)
#. ``DiscretePlot``
#. ``Kurtosis``
#. ``ListLogPlot``
#. ``LogPlot``
#. ``$MaxMachineNumber``
#. ``$MinMachineNumber``
#. ``NumberLinePlot``
#. ``PauliMatrix``
#. ``Remove``
#. ``SetOptions``
#. ``SixJSymbol``
#. ``Skewness``
#. ``ThreeJSymbol``


Documentation
+++++++++++++

#. All Builtins have links to WMA pages.
#. "Accuracy and Precision" section added to the Tutorial portion.
#. "Attribute Definitions" section reinstated.
#. "Expression Structure" split out as a guide section (was "Structure of Expressions").
#. "Exponential Functional" split out from "Trigonometry Functions"
#. "Functional Programming" section split out.
#. "Image Manipulation" has been split off from Graphics and Drawing and turned into a guide section.
#. Image examples now appear in the LaTeX and therfore the PDF doc
#. "Logic and Boolean Algebra" section reinstated.
#. "Forms of Input and Output" is its own guide section.
#. More URL links to Wiki pages added; more internal cross links added.
#. "Units and Quantities" section reinstated.
#. The Mathics3 Modules are now included in LaTeX and therefore the PDF doc.

Internals
+++++++++

#. ``boxes_to_`` methods are now optional for ``BoxElement`` subclasses. Most of the code is now moved to the ``mathics.format`` submodule, and implemented in a more scalable way.
#. ``from_mpmath`` conversion supports a new parameter ``acc`` to set the accuracy of the number.
#. ``mathics.builtin.inout`` was split in several modules (``inout``, ``messages``, ``layout``, ``makeboxes``) in order to improve the documentation.
#. ``mathics.eval`` was create to have code that might be put in an instruction interpreter. The opcodes-like functions start ``eval_``, other functions are helper functions for those.
#. Operator name to Unicode or ASCII comes from Mathics scanner character tables.
#. Builtin instance methods that start ``eval`` are considered rule matching and function application; the use of the name ``apply``is deprecated, when ``eval`` is intended.
#. Modularize and improve the way in which ``Builtin`` classes are selected to have an associated ``Definition``.
#. ``_SetOperator.assign_elementary`` was renamed as ``_SetOperator.assign``. All the special cases are not handled by the ``_SetOperator.special_cases`` dict.
#. ``isort`` run over all Python files. More type annotations and docstrings on functions added.
#. caching on immutable atoms like, ``String``, ``Integer``, ``Real``, etc. was improved; the ``__hash__()`` function was sped up. There is a small speedup overall from this at the expense of increased memory.
#. more type annotations added to functions, especially builtin functions
#. Numerical constants used along the code was renamed using caps, according to the Python's convention.

Bugs
++++

# ``0`` with a given precision (like in ```0`3```) is now parsed as ``0``, an integer number.
# Reading certain GIFs now work again
#. ``Random[]`` works now.
#. ``RandomSample`` with one list argument now returns a random ordering of the list items. Previously it would return just one item.
#. Origin placement corrected on ``ListPlot`` and ``LinePlot``.
#. Fix long-standing bugs in Image handling
#. Some scikit image routines line ``EdgeDetect`` were getting omitted due to overly stringent PyPI requirements
#. Units and Quantities were sometimes failing. Also they were omitted from documentation.
#. Better handling of ``Infinite`` quantities.
#. Improved ``Precision`` and ``Accuracy``compatibility with WMA. In particular, ``Precision[0.]`` and ``Accuracy[0.]``
#. Accuracy in numbers using the notation ``` n.nnn``acc ```  now is properly handled.
#. numeric precision in mpmath was not reset after operations that changed these. This cause huges slowdowns after an operation that set the mpmath precison high. This was the source of several-minute slowdowns in testing.
#. GIF87a (```MadTeaParty.gif`` or ExampleData) image loading fixed
#. Replace non-free Leena image with a a freely distributable image. Issue #728


PyPI Package requirements
+++++++++++++++++++++++++

Mathics3 aims at a more richer set of functionality.

Therefore NumPy and Pillow (9.10 or later) are required Python
packages where they had been optional before.  In truth, probably
running Mathics without one or both probably did not work well if it
worked at all; we had not been testing setups that did not have NumPy.

Enhancements
++++++++++++

#. Vector restriction on ``Norm[]`` removed. "Frobinius" p-form allowed.
#. Better handling of comparisons with finite precision numbers.
#. Improved implementation for  ``Precision``.
#. Infix operators, like ``->`` render with their Unicode symbol when ``$CharacterEncoding`` is not "ASCII".
#. ``Grid`` compatibility with WMA was improved.  Now it supports non-uniform list of lists and lists with general elements.
#. Support for BigEndian Big TIFF



5.0.2
-----

Get in `requirements-cython.txt`` into tarball. Issue #483

New Symbols
+++++++++++

#. ``Undefined``



5.0.1
-----

Mostly a release to fix a Python packaging problem.

Internals
+++++++++


#. ``format`` and ``do_format`` methods were removed from the interface of
   ``BaseElement``, becoming non-member functions.
#. The class ``BoxElement`` was introduced as a base for boxing elements.

New Builtin
+++++++++++
#. 'Inverse Gudermannian'.

Documentation
+++++++++++++

Hyperbolic functions were split off form trigonometry and exponential functions. More URL links were added.

Bugs
++++

#. Creating a complex number from Infinity no longer crashes and returns 'I * Infinity'

5.0.0
------


This release starts to address some of the performance problems and terminology confusion that goes back to the very beginning.
As a result, this release is not API compatible with prior releases.

In conjunction with the performance improvement in this release, we start refactoring some of the core classes and modules to start to get this to look and act more like other interpreters, and to follow more current Python practice.

More work will continue in subsequent releases.

New Builtins
++++++++++++
#. Euler's ``Beta`` function.
#. ``Bernoulli``.
#. ``CatalanNumber`` (Integer arguments only).
#. ``CompositeQ``.
#. ``Diagonal``. Issue #115.
#. ``Divisible``.
#. ``EllipticE``
#. ``EllipticF``
#. ``EllipticK``
#. ``EllipticPi``
#. ``EulerPhi``
#. ``$Echo``. Issue #42.
#. ``FindRoot`` was improved for supporting numerical derivatives Issue #67, as well as the use of scipy libraries when are available.
#. ``FindRoot`` (for the ``newton`` method) partially supports ``EvaluationMonitor`` and ``StepMonitor`` options.
#. ``FindMinimum`` and ``FindMaximum`` now have a minimal implementation for 1D problems and the use of scipy libraries when are available.
#. ``LogGamma``.
#. ``ModularInverse``.
#. ``NumericFunction``.
#. ``Projection``.
#. Partial support for Graphics option ``Opacity``.
#. ``SeriesData`` operations was improved.
#. ``TraceEvaluation[]`` shows expression name calls and return values of it argument.
   -  Pass option ``ShowTimeBySteps``, to show accumulated time before each step
   - The variable ``$TraceEvalution`` when set True will show all expression evaluations.
#. ``TraditionalForm``


Enhancements
++++++++++++

#. ``D`` acts over ``Integrate`` and  ``NIntegrate``. Issue #130.
#. ``SameQ`` (``===``) handles chaining, e.g. ``a == b == c`` or ``SameQ[a, b, c]``.
#. ``Simplify`` handles expressions of the form ``Simplify[0^a]`` Issue #167.
#. ``Simplify`` and ``FullSimplify`` support optional parameters ``Assumptions`` and ``ComplexityFunction``.
#. ``UnsameQ`` (``=!=``) handles chaining, e.g. ``a =!= b =!= c`` or ``UnsameQ[a, b, c]``.
#. Assignments to usage messages associated with ``Symbols`` is allowed as it is in WMA. With this and other changes, Combinatorica 2.0 works as written.
#. ``Share[]`` performs an explicit call to the Python garbage collection and returns the amount of memory free.
#. Improve the compatibility of ``TeXForm`` and ``MathMLForm`` outputs with WMA. MathML tags around numbers appear as "<mn>" tags instead of "<mtext>", except in the case of ``InputForm`` expressions. In TeXForm some quotes around strings have been removed to conform to WMA. It is not clear whether this is the correct behavior.
#. Allow ``scipy`` and ``skimage`` to be optional. In particular: revise ``Nintegrate[]`` to use ``Method="Internal"`` when scipy isn't available.
#. Pyston up to versions from 2.2 to 2.3.4 are supported as are PyPy versions from 3.7-7.3.9.0 up 3.9-7.3.9. However those Python interpreters may have limitations and limitations on packages that they support.
#. Improved support for ``Series`` Issue #46.
#. ``Cylinder`` rendering is implemented in Asymptote.


Documentation
+++++++++++++

#. "Testing Expressions" section added.
#. "Representation of Numbers" section added.
#. "Descriptive Statistics" section added and "Moments" folded into that.
#. Many More URL references. ``<url>`` now supports link text.
#. Reference Chapter and Sections are now in alphabetical order
#. Two-column mode was removed in most sections so the printed PDF looks nicer.
#. Printed Error message output in test examples is in typewriter font and doesn't drop inter-word spaces.

Internals
+++++++++

#. Inexplicably, what the rest of the world calls a "nodes" in a tree or or in WMA "elements" in a tree had been called a "leaves". We now use the proper term "element".
#. Lots of predefined ``Symbol``s have been added. Many appear in the module ``mathics.core.systemsymbols``.
#. Attributes are now stored in a bitset instead of a tuple of string. This speeds up attributes read, and RAM usage, .
#. ``Symbol.is_numeric`` and  ``Expression.is_numeric`` now uses the attribute ``Definition.is_numeric`` to determine the returned value.
#. ``NIntegrate`` internal algorithms and interfaces to ``scipy`` were moved to ``mathics.algorithm.integrators`` and ``mathics.builtin.scipy_utils.integrators`` respectively.
#. ``N[Integrate[...]]`` now is evaluated as ``NIntegrate[...]``
#. Definitions for symbols ``CurrentContext`` and ``ContextPath[]`` are mirrored in the ``mathics.core.definitions.Definitions`` object for faster access.
#. ``FullForm[List[...]]`` is shown as ``{...}`` according to the WL standard.
#. ``Expression.is_numeric()`` accepts an ``Evaluation`` object as a parameter;  the definitions attribute of that is used.
#. ``SameQ`` first checks the type, then the ``id``, and then names in symbols.
#. In ``mathics.builtin.patterns.PatternTest``, if the condition is one of the most used tests (``NumberQ``, ``NumericQ``, ``StringQ``, etc) the ``match`` method is overwritten to specialized versions that avoid function calls.
#. ``mathics.core.patterns.AtomPattern`` specializes the comparison depending of the ``Atom`` type.
#. To speed up development, you can set ``NO_CYTHON`` to skip Cythonizing Python modules. If you are using Pyston or PyPy, Cythonization slows things down.
#. ``any`` and``all`` calls were unrolled as loops in Cythonized modules: this avoids the overhead of a function call replacing it by a (C) for loop, which is faster.
#. A bug was fixed relating to the order in which ``mathics.core.definitions`` stores the rules
#. ``InstanceableBuiltin`` -> ``BuiltinElement``
#. ``BoxConstruction`` -> ``BoxExpression``
#. the method ``Element.is_true()`` was removed in favor of ``is SymbolTrue``
#. ``N[_,_,Method->method]`` was reworked. Issue #137.
#. The methods  ``boxes_to_*`` were moved to ``BoxExpression``.
#. remove ``flatten_*`` from the ``Atom`` interface.
#. ``Definition`` has a new property ``is_numeric``.

Speed improvements:
...................

#. Creating two ``Symbol`` objects with the same name will give the same object. This avoids unnecessary string comparisons, and calls to ``ensure_context``.
#. Attributes are now stored in a bitset instead of a tuple of strings.
#. The ``Definitions`` object has two properties: ``current_contex`` and ``context_path``. This speeds up the lookup of symbols names.  These properties store their values into the corresponding symbols in the ``builtin`` definitions.
#. ``eval_N`` was add to speed up the then often-used built-in function ``N``.
#. ``Expression`` evaluation was gone over and improved. properties on the collection which can speed up evaluation, such as whether an expression is fully evaluated, is ordered, or is flat are collected.
#. ``List`` evaluation is customized. There is a new ``ListExpression`` class which has a more streamlined ``evaluate()`` method. More of this kind of thing will follow
#. ``BaseExpression.get_head`` avoids building a symbol saving two function calls.


Package update
..............

#. SymPy 1.10.1

Compatibility
+++++++++++++

#. ``ScriptCommandLine`` now returns, as the first element, the name of the script file (when available), for compatibility with WMA. Issue #132.
#. ``Expression.numerify`` improved in a way to obtain a behavior closer to WMA.
#. ``NumericQ`` lhs expressions are now handled as a special case in assignment. For example ``NumericQ[a]=True`` tells the interpreter that ``a`` must be considered
  a numeric quantity, so ``NumericQ[Sin[a]]`` evaluates to ``True``.

Bugs
++++

#. ``First``, ``Rest`` and  ``Last`` now handle invalid arguments.
#.  ``Set*``: fixed issue #128.
#.  ``SameQ``: comparison with MachinePrecision only needs to be exact within the last bit Issue #148.
#. Fix a bug in ``Simplify`` that produced expressions of the form ``ConditionalExpression[_,{True}]``.
#. Fix bug in ``Clear``  and ``ClearAll`` (#194).
#. Fix base 10 formatting for infix ``Times``. Issue #266.
#. Partial fix of ``FillSimplify``
#. Streams used in MathicsOpen are now freed and their file descriptors now released. Issue #326.
#. Some temporary files that were created are now removed from the filesystem. Issue #309.
#. There were a number of small changes/fixes involving ``NIntegrate`` and its Method options. ``Nintegrate`` tests have been expanded.
#. Fix a bug in handling arguments of pythonized expressions, that are produced by ``Compile`` when the llvmlite compiler fails.
#. ``N`` now handles arbitrary precision numbers when the number of digits is not specified.
#. `N[Indeterminate]` now produces `Indeterminate` instead a `PrecisionReal(nan)`.
#. Fix crash in ``NestWhile`` when supplying ``All`` as the fourth argument.
#. Fix the comparison between ``Image`` and other expressions.
#. Fix an issue that prevented that `Collect` handles properly polynomials on expressions (issue #285).
#. Fix a bug in formatting expressions of the form ``(-1)^a`` without the parenthesis (issue #332).
#. Fix a but in failure in the order in which ``mathics.core.definitions`` stores the rules.
#. Numeric overflows now do not affect the full evaluation, but instead just the element which produce it.
#. Compatibility with the way expressions are ordered more closely follows WMA: Now expressions with fewer elements come first (issue #458).
#. The order of the context name resolution (and ``$ContextPath``) was switched; ``"System`` comes before ``"Global``.

Incompatible changes
+++++++++++++++++++++

The following changes were motivated by a need to speed up the interpreter.

#. ``Expression`` arguments differ. The first parameter has to be a ``Symbol`` while the remaining arguments have to be some sort of ``BaseElement`` rather than something that can be converted to an element.
  Properties for the collection of elements can be specified when they are known. To get the old behavior, use ``to_expression``
#. Expressions which are lists are a new kind of class, ``ListExpression``. As with expressions, the constructor requires valid elements, not something convertible to an element. Use ``to_mathics_list``


-----------------


4.0.1
-----

New builtins
++++++++++++

#. ``Guidermannian``
#. ``Cone``
#. ``Tube``
#. ``Normal`` now have a basic support for ``SeriesData``

Tensor functions:

#. ``RotationTransform``
#. ``ScalingTransform``
#. ``ShearingTransform``
#. ``TransformationFunction``
#. ``TranslationTransform``

Spherical Bessel functions:

#. ``SphericalBesselJ``
#. ``SphericalBesselY``
#. ``SphericalHankelH1``
#. ``SphericalHankelH2``

Gamma functions:

#. ``PolyGamma``
#. ``Stieltjes``

Uniform Polyhedron
#. ``Dodecahedron``
#. ``Icosahedron``
#. ``Octahedron``
#. ``TetraHedron``
#. ``UniformPolyedron``

Mathics-specific

#. ``TraceBuiltin[]``, ``$TraceBuiltins``, ``ClearTrace[]``, ``PrintTrace[]``

These collect builtin-function call counts and elapsed time in the routines.
``TraceBuiltin[expr]`` collects information for just *expr*. Whereas
setting ``$TraceBuiltins`` to True will accumulate results of evaluations
``PrintTrace[]`` dumps the statistics and ``ClearTrace[]`` clears the statistics data.

``mathics -T/--trace-builtin`` is about the same as setting
``$TraceBuiltins = True`` on entry and runs ``PrintTrace[]`` on exit.


Bugs
++++

#. Fix and document better behavior of ``Quantile``
#. Improve Asymptote ``BezierCurve``implementation
#. ``Rationalize`` gives symmetric results for +/- like MMA does. If
  the result is an integer, it stays that way.
#. stream processing was redone. ``InputStream``, ``OutputStream`` and
  ``StringToStream`` should all open, close, and assign stream numbers now

4.0.0
#.----

The main thrust behind this API-breaking release is to be able to
support a protocol for Graphics3D.

It new Graphics3D protocol is currently expressed in JSON. There is an
independent `threejs-based module
<https://www.npmjs.com/package/@mathicsorg/mathics-threejs-backend>`_
to implement this. Tiago Cavalcante Trindade is responsible for this
code.

The other main API-breaking change is more decentralization of the
Mathics Documentation. A lot more work needs to go on here, and so
there will be one or two more API breaking releases. After this
release, the documentation code will be split off into its own git
repository.

Enhancements
++++++++++++

#. a Graphics3D protocol, mentioned above, has been started
#. ``mathics.setting`` have been gone over to simplify.
#. A rudimentary and crude SVG Density Plot was added. The prior method
  relied on mysterious secret handshakes in JSON between Mathics Core
  and Mathics Django. While the density plot output was nicer in
  Mathics Django, from an overall API perspective this was untenable. A
  future version may improve SVG handling of Density plots using
  elliptic density gratings in SVG. And/or we may define this in the
  JSON API.
#. SVG and Asymptote drawing now includes inline comments indicating
  which Box Structures are being implemented in code

Documentation
.............

#. Document data used in producing PDFs and HTML-rendered documents is now stored
  in both the user space, where it can be extended, and in the package install
  space -- which is useful when there is no user-space data.
#. The documentation pipeline has been gone over. Turning the internal data
  into a LaTeX file is now a separate own program. See ``mathics/doc/test/README.rst``
  for an overview of the dataflow needed to create a PDF.
#. Summary text for various built-in functions has been started. These
  summaries are visible in Mathics Django when lists links are given
  in Chapters, Guide Sections, or Sections.
#. A Sections for Lists has been started and grouping for these
  have been added. So code and sections have moved around here.
#. Regexp detection of tests versus document text has been improved.
#. Documentation improved
#. The flakiness around showing sine graphs with filling on the axes or below has
  been addressed. We now warn when a version of Asymptote or Ghostscript is used
  that is likely to give a problem.

Bugs
++++

#. A small SVGTransform bug was fixed. Thanks to axelclk for spotting.
#. Elliptic arcs are now supported in Asymptote. There still is a bug however
  in calculating the bounding box when this happens.
#. A bug in image decoding introduced in 3.1.0 or so was fixed.
#. A bug SVG LineBoxes was fixed

Regressions
+++++++++++

#. Some of the test output for builtins inside a guide sections is not automatically rendered
#. Density plot rendered in Mathics Django do not render as nice since we no longer
  use the secret protocol handshake hack. We may fix this in a future release
#. Some of the Asymptote graphs look different. Graphic3D mesh lines are not as
  prominent or don't appear. This is due to using a newer version of Asymptote, and
  we will address this in a future release.

-----------------

3.1.0
----

New variables and builtins
++++++++++++++++++++++++++

#. ``Arrow`` for Graphics3D (preliminary)
#. ``Cylinder`` (preliminary)
#. ``Factorial2`` PR #1459 Issue #682.

Enhancements
++++++++++++

Large sections like the "Strings and Characters", "Integer Functions" and "Lists" sections
have been broken up into subsections. These more closely match
online WL "Guide" sections.  This is beneficial not just in the
documentation, but also for code organization. See PRs #1464, #1473.

A lot more work is needed here.

The Introduction section of the manual has been revised. Licensing and Copyright/left sections
have been reformatted for non-fixed-width displays. #1474

PolarPlot documentation was improved. #1475.

A getter/setter method for Mathics settings was added #1472.


Bugs
++++

#. Add ``requirements-*.txt``to distribution files. ``pip install Mathics3[dev]`` should work now. PR #1461
#. Some ``PointBox`` bugs were fixed
#. Some ``Arrow3DBox`` and ``Point3DBox`` bugs were fixed PR #1463
#. Fix bug in ``mathics`` CLI when  ``-script`` and ``-e`` were combined PR #1455

-----------------


3.0.0
----

Overall there is a major refactoring underway of how formatting works
and its interaction with graphics.  More work will come in later releases.

Some of the improvements are visible not here but in the front-ends
mathicsscript and mathics-django. In mathicsscript, we can now show
SVG images (via matplotlib).  In Mathics Django, images and threejs
graphs are no longer embedded in MathML.

A lot of the improvements in this release were done or made possible with the help of
Tiago Cavalcante Trindade.

Enhancements
++++++++++++

It is now possible to get back SVG, and graphics that are not embedded in MathML.

The code is now Pyston 2.2 compatible. However ``scipy`` ``lxml`` are
not currently available on Pyston so there is a slight loss of
functionality. The code runs about 30% faster under Pyston 2.2. Note
that the code also works under PyPy 3.7.

Bugs
++++

#. Tick marks and the placement of numbers on charts have been corrected. PR #1437
#. Asymptote now respects the ``PointSize`` setting.
#. In graphs rendered in SVG, the ``PointSize`` has been made more closely match Mathematica.
#. Polygons rendered in Asymptote now respects the even/odd rule for filling areas.

Density Plots rendered in SVG broke with this release. They will be reinstated in the future.

Documentation
+++++++++++++

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

Chapters without introductory text like ``Structural Operations``, or ``Tensors`` have had descriptions added.

Sections that were empty have either been expanded or removed because
the underlying name was never a user-level built in, e.g. the various
internal Boxing functions like ``DiskBox``, or ``CompiledCodeBox``

Documentation specific builtins like ``PolarPlot`` or
``BernsteinBasis`` have been added improved, and document examples
have been revised such as for ``PieChart``, ``Pi`` and others.

The Mathics Gallery examples have been updated.

Some slight improvements were made to producing the PDF and more kinds
of non-ASCII symbols are tolerated. Expect more work on this in the
future via tables from the `Mathics Scanner <https://pypi.org/project/Mathics-Scanner/1.2.1/>`_ project.

Chapters are no longer in Roman Numerals.


Internal changes
++++++++++++++++

#. ``docpipline.py``  accepts the option ``--chapters`` or ``-c`` to narrow tests to a particular chapter
#. Format routines have been isolated into its own module. Currently we have format routines for SVG, JSON and
  Asymptote. Expect more reorganization in the future.
#. Boxing routines have been isolated to its own module.
#. The entire code base has been run through the Python formatter `black <https://black.readthedocs.io/en/stable/>`_.
#. More Python3 types to function signatures have been added.
#. More document tests that were not user-visible have been moved to
  unit tests which run faster. More work is needed here.

-----------------

2.2.0
----

Package update
++++++++++++++

#. SymPy 1.8

New variables and builtins
++++++++++++++++++++++++++

#. ``Arg``
#. ``CoefficientArrays`` and ``Collect`` (#1174, #1194)
#. ``Dispatch``
#. ``FullSimplify``
#. ``LetterNumber`` #1298. The ``alphabet`` parameter supports only a minimal number of languages.
#. ``MemoryAvailable``
#. ``MemoryInUse``
#. ``Nand`` and ``Nor`` logical functions.
#. ``Series``,  ``O`` and ``SeriesData``
#. ``StringReverse``
#. ``$SystemMemory``
#. Add all of the named colors, e.g. ``Brown`` or ``LighterMagenta``.



Enhancements
++++++++++++

#. a function `evaluate_predicate` allows for a basic predicate evaluation using `$Assumptions`.
#. ``Attributes`` accepts a string parameter.
#. ``Cases`` accepts Heads option. Issue #1302.
#. ``ColorNegate`` for colors is supported.
#. ``D`` and ``Derivative`` improvements.
#. ``Expand`` and ``ExpandAll`` now support a second parameter ``patt`` Issue #1301.
#. ``Expand`` and ``ExpandAll`` works with hyperbolic functions (`Sinh`, `Cosh`, `Tanh`, `Coth`).
#. ``FileNames`` returns a sorted list. Issue #1250.
#. ``FindRoot`` now accepts several optional parameters like ``Method`` and ``MaxIterations``. See Issue #1235.
#. ``FixedPoint`` now supports the ``SameTest`` option.
#. ``mathics`` CLI now uses its own Mathics ``settings.m`` file
#. ``Prepend`` works with ``DownValues`` Issue #1251
#. ``Prime`` and ``PrimePi`` now accept a list parameter and have the ``NumericFunction`` attribute.
#. ``Read`` with ``Hold[Expression]`` now supported. (#1242)
#. ``ReplaceRepeated`` and ``FixedPoint`` now supports the ``MaxIteration`` option. See Issue #1260.
#. ``Simplify`` performs a more sophisticated set of simplifications.
#. ``Simplify`` accepts a second parameter that temporarily overwrites ``$Assumptions``.
#. ``StringTake`` now accepts form containing a list of strings and specification. See Issue #1297.
#. ``Table`` [*expr*, *n*] is supported.
#. ``ToExpression`` handles multi-line string input.
#. ``ToString`` accepts an optional *form* parameter.
#. ``ToExpression`` handles multi-line string input.
#. ``$VersionNumber`` now set to 10.0 (was 6.0).
#. The implementation of Streams was redone.
#. Function ``mathics.core.definitions.autoload_files`` was added and
  exposed to allow front-ends to provide their own custom Mathics.
  settings.
#. String output in the ``mathics`` terminal has surrounding quotes to make it more visually distinct from unexpanded and symbol output.
  To disable this behavior use ``--strict-wl-output``.


Bug fixes
+++++++++

#. ``SetTagDelayed`` now does not evaluate the RHS before assignment.
#. ``$InstallationDirectory`` starts out ``Unprotected``.
#. ``FindRoot`` now handles equations.
#. Malformed Patterns are detected and an error message is given for them.
#. Functions gone over to ensure the ``Listable`` and ``NumericFunction`` properties are correct.


Incompatible changes
#.-------------------

#. ``System`$UseSansSerif`` moved from core and is sent front-ends using ``Settings`$UseSansSerif``.


Internal changes
#.---------------

#. ``docpipeline.py``  accepts the option ``-d`` to show how long it takes to parse, evaluate and compare each individual test.
  ``-x`` option (akin to ``pytests -x`` is a short-hand for stop on first error
#. Some builtin functions have been grouped together in a module
  underneath the top-level builtin directory.  As a result, in the
  documents you will list some builtins listed under an overarching
  category like ``Specific Functions`` or ``Graphics, Drawing, and
  Images``. More work is expected in the future to improve document sectioning.
#. ``System`$Notebooks`` is removed from settings. It is in all of the front-ends now.

------

2.1.0
----

New builtins
++++++++++++

#. ``ArcTanh``
#. ``ByteArray``
#. ``CreateFile``
#. ``CreateTemporary``
#. ``FileNames``
#. ``NIntegrate``
#. ``PartitionsP``
#. ``$Notebooks``
#. ``SparseArray``

Enhancements
++++++++++++

#. The Mathics version is checked for builtin modules at load time. A message is given when a builtin doesn't load.
#. Automatic detection for the best strategy to numeric evaluation of constants.
#. ``FileNameJoin`` now implements ``OperatingSystem`` option
#. Mathics functions are accepted by ``Compile[]``. The return value or
  type will be ``Compile[] and CompiledFunction[]``.  Every Mathics
  Expression can have a compiled form, which may be implemented as a
  Python function.
#. ``Equal[]`` now compares complex against other numbers properly.
#. Improvements in handling products with infinite factors: ``0 Infinity``-> ``Indeterminate``, and ``expr Infinity``-> ``DirectedInfinite[expr]``
#. ``$Path`` is now ``Unprotected`` by default
#. ``Read[]`` handles expressions better.
#. ``StringSplit[]`` now accepts a list in the first argument.
#. ``SetDelayed[]`` now accepts several conditions imposed both at LHS as well as RHS.
#. Axes for 2D Plots are now rendered for SVGs
#. ``InsertBox`` accepts an opaque parameter


Bug fixes
+++++++++

``TeXForm[]`` for integrals are now properly formatted.


Pymathics Modules
+++++++++++++++++

#. Pymathics modules now can run initialization code when are loaded.
#. The ``builtins`` list is not hard-linked to the library anymore. This simplifies
  the loading and reloading of pymathics modules.
#. Decoupling of BoxConstructors from the library. Now are defined at the
  level of the definition objects. This is useful for customizing the
  Graphics output if it is available.


Miscellanea
+++++++++++

#. A pass was made to improve Microsoft Windows compatibility and testing Windows under MSYS.
#. Include numpy version in version string. Show in CLI
#. Small CLI tweaks ``--colors=None`` added to match mathicsscript.
#. In the ``BaseExpression`` and derived classes, the method ``boxes_to_xml`` now are called ``boxes_to_mathml``.
#. In the ``format`` method of the class ``Evaluation``,  the builtin ``ToString`` is called instead of  ``boxes_to_text``
#. In order to control the final form of boxes from the user space in specific symbols and contexts.
#. ``GraphicsBox`` now have two methods:  ``to_svg`` and  ``to_mathml``. The first produces SVG plain text while the second produces ``<mglyph ...>`` tags with base64 encoded SVGs.


What's to expect in a Future Release
++++++++++++++++++++++++++++++++++++

#. Improved ``Equal`` See `PR #1209 <https://github.com/mathics/Mathics/pull/1209/>`_
#. Better Unicode support, especially for Mathics operators
#. Improved ``D[]`` and ``Derivative[]`` See `PR #1220 <https://github.com/mathics/Mathics/pull/1209/>`_.
#. Improved performance
#. ``Collect[]`` See `Issue #1194 <https://github.com/mathics/Mathics/issues/1194>`_.
#. ``Series[]`` See `Issue #1193 <https://github.com/mathics/Mathics/issues/1194>`_.

-----

2.0.0
----

To accommodate growth and increased use of pieces of Mathics inside other packages, parts of Mathics have been split off and moved to separate packages. In particular:

#. The Django front-end is now a PyPI installable package called `Mathics-Django <https://pypi.org/project/Mathics-Django/>`_.
#. Scanner routines, character translation tables to/from Unicode, and character properties are now `mathics-scanner https://github.com/Mathics3/mathics-scanner`_.
#. Specific builtins involving heavy, non-standard routines were moved to pymathics modules `pymathics-graph https://github.com/Mathics3/pymathics-graph`_, `pymathics-natlang https://github.com/Mathics3/pymathics-natlang`_.

Incompatible changes:
+++++++++++++++++++++

#. ``-e`` ``--execute`` is better suited for embedded use. It shows just evaluation output as text.
#. Docker scripts ``dmathics``, ``dmathicsscript`` and ``dmathicsserver`` have been removed. They are part of the ``docker-mathics`` a separate PyPI package.

The bump in the major version number reflects major changes in this release. Another major release is planned soon, with more major changes.

See below for future work planned.

New builtins
++++++++++++

#. ``AnglePath``,  ``AnglePathFold``, ``AngleVector``
#. ``BoxData``, ``TextData``, ``InterpretationBox``, ``StyleBox``, ``TagBox``, ``TemplateBox``, ``ButtonBox``, ``InterpretationBox``
#. ``ContinuedFraction``
#. ``ConvertCommonDumpRemoveLinearSyntax`` and ``System`ConvertersDump`` context variables
#. ``FirstCase``, ``Lookup``, ``Key``, ``Lookup`` and ``Failure``
#. ``Haversine``, ``InverseHaversine``
#. ``Insert`` and ``Delete``
#. ``LerchPhi``
#. ``MathicsVersion`` (this is not in WL)
#. ``NumberQ``
#. ``PossibleZeroQ`` PR #1100
#. ``Run``
#. ``Show``
#. ``SympyObject``
#. ``TimeRemaining`` and ``TimeConstrained``
#. ``\[RadicalBox]``
#.  Improving support for options in the Plot module: ``Axes``, ``Filling``, ``ImageSize``, ``Joined``

New constants
+++++++++++++

Mathematical Constants is now its own module/section. Constants have been filled out. These constants have been added:

#. ``Catalan``
#. ``Degree``
#. ``Glaisher``
#. ``GoldenRatio``
#. ``Khinchin``

Many of these and the existing constants are computable via mpmath, NumPy, or Sympy.

Settings through WL variables
+++++++++++++++++++++++++++++

Certain aspects of the kernel configuration are now controlled by variables, defined in ``/autoload/settings.m``.

#. ``$GetTrace`` (``False`` by default).  Defines if when a WL module is load through ``Get``, definitions will be traced (for debug).
#. ``$PreferredBackendMethod`` Set this do whether to use mpmath, NumPy or SymPy for numeric and symbolic constants and methods when there is a choice (``"sympy"`` by default) (see #1124)

Enhancements
++++++++++++

#. Add ``Method`` option "mpmath" to compute ``Eigenvalues`` using mpmath (#1115).
#. Improve support for ``OptionValue`` and ``OptionsPattern`` (#1113)

Bug fixes
+++++++++

Numerous bugs were fixed while working on Combinatorica V0.9 and CellsToTeX.

#. ``Sum`` involving numeric integer bounds involving Mathics functions fixed.
#. ``Equal`` ``UnEqual`` testing on Strings (#1128).

Document updates
++++++++++++++++

#. Start a readthedocs `Developer Guide <https://mathics-development-guide.reandthedocs.io/en/latest/>`_

Enhancements and bug fixes:
+++++++++++++++++++++++++++

#. Fix evaluation timeouts
#. ``Sum``'s lower and upper bounds can now be Mathics expressions

Miscellanea
+++++++++++

#. Enlarge the set of ``gries_schneider`` tests
#. Improve the way builtins modules are loaded at initialization time (#1138).

Future
++++++

#. We are in the process of splitting out graphics renderers, notably for matplotlib. See `pymathics-matplotlib <https://github.com/Mathics3/pymathics-matplotlib>`_.
#. Work is also being done on asymptote. See `PR #1145 <https://github.com/mathics/Mathics/pull/1145>`_.
#. Makeboxes is being decoupled from a renderer. See `PR #1140 <https://github.com/mathics/Mathics/pull/1140>`_.
#. Inline SVG will be supported (right now SVG is binary).
#. Better support integrating Unicode in output (such as for Rule arrows) is in the works. These properties will be in the scanner package.
#. A method option ("mpmath", "sympy", or "numpy") will be added to the ``N[]``. See `PR #1144 <https://github.com/mathics/Mathics/pull/1144>`_.


----

1.1.1
----

This may be the last update before some major refactoring and interface changing occurs.

In a future 2.0.0 release, Django will no longer be bundled here. See `mathics-django <https://github.com/Mathics3/mathics-django>` for the unbundled replacement.

Some changes were made to support `Pymathics Graph <https://github.com/Mathics3/pymathics-graph>`_, a new graph package bundled separately, and to support the ability for front-ends to handle rendering on their own. Note that currently this doesn't integrate well into the Django interface, although it works well in ``mathicsscript``.

Package updates
+++++++++++++++

#. SymPy 1.7.1

Mathics Packages added:

#. ``DiscreteMath`CombinatoricaV0.9`` (preferred) and
  ``DiscreteMath`CombinatoricaV0.6``.

Both of these correspond to Steven Skiena's *older* book: *Implementing Discrete Mathematics: Combinatorics and Graph Theory*.

If you have a package that you would like included in the distribution, and it works with Mathics, please contact us.

Rubi may appear in a future release, possibly in a year or so. Any help to make this happen sooner is appreciated.

New builtins
++++++++++++

#. ``StirlingS1``, ``StirlingS2`` (not all WL variations handled)
#. ``MapAt`` (not all WL variations handled)
#. ``PythonForm``, ``SympyForm``: not in WL.
  Will show a crude translation to SymPy or Python.
  Expect more and better translation later
#. ``Throw`` and ``Catch``
#. ``With``
#. ``FileNameTake``

Enhancements and bug fixes
++++++++++++++++++++++++++

#. Workaround for ``Compile`` so it accepts functions ##1026
#. Add ``Trace`` option to ``Get``. ``Get["fn", Trace->True]`` will show lines as they are read
#. Convert to/from Boolean types properly in ``from_python``, ``to_python``. Previously they were 0 and 1
#. Extend ``DeleteCases`` to accept a levelspec parameter
#. Set ``Evaluation#exc_result`` to capture ``Aborted``, ``Timeout``, ``Overflow1``, etc.
#. ``ImageData`` changed to get bits {0,1}, not booleans as previously
#. Add tokenizer symbols for ``<->`` and ``->`` and the Unicode versions of those
#. Small corrections to ``Needs``, e.g check if already loaded, correct a typo, etc.
#. ``System`$InputFileName`` is now set inside ``Needs`` and ``Get``
#. Install shell scripts ``dmathicserver``, ``dmathicsscript``, and ``dmathics`` to simplify running docker
#. Adjust ``$InputFileName`` inside ``Get`` and ``Needs``
#. Support for ``All`` as a ``Part`` specification
#. Fix ``BeginPackage``
#. Improving support for ``OptionValue``. Now it supports list of Options
#. Adding support in ``from_python()`` to convert dictionaries in list of rules
#. Fix ``OptionsPattern`` associated symbols

----

1.1.0
----

So we can get onto PyPI, the PyPI install name has changed from Mathics to Mathics3.

Enhancements and bug fixes
++++++++++++++++++++++++++

#. Add Symbolic Comparisons. PR #1000
#. Support for externally PyPI-packagable builtin modules - PyMathics
#. ``SetDirectory`` fixes. PR #994
#. Catch ```PatternError`` Exceptions
#. Fix formatting of ``..`` and ``...`` (``RepeatAll``)
#. Tokenization of ``\.`` without a following space (``ReplaceAll``). Issue #992.
#. Support for assignments to named ```Pattern```
#. Improve support for ```Names``. PR #1003
#. Add a ``MathicsSession`` class to simplify running Mathics from Python. PR #1001
#. Improve support for ```Protect``` and ```Unprotect``` list of symbols and regular expressions. PR #1003

----

1.1.0 rc1
--------

Package updates
+++++++++++++++

All major packages that Mathics needs have been updated for more recent
releases. Specifically these include:

#. Python: Python 3.6-3.9 are now supported
#. Cython >= 0.15.1
#. Django 3.1.x
#. mpmath >= 1.1.0
#. SymPy 1.6.2

New features (50+ builtins)
+++++++++++++++++++++++++++

#. ``Association``, ``AssociationQ``, ``FirstPostion``, ``LeafCount``
#. ``Association``, ``AssociationQ``, ``Keys``, ``Values`` #705
#. ``BarChart[]``, ``PieChart``, ``Histogram``, ``DensityPlot`` #499
#. ``BooleanQ``, ``DigitQ`` and ``LetterQ``
#. ``CharacterEncoding`` option for ``Import[]``
#. ``Coefficient[]``, ``Coefficient[x * y, z, 0]``, ``Coefficient*[]``
#. ``DiscreteLimit`` #922
#. ``Environment``
#. File read operations from URLs
#. ``FirstPostions``, ``Integers``, ``PrePendTo[]``
#. ``GetEnvironment`` # 938
#. ``Integers``, ``PrependTo`` and ``ContainsOnly``
#. ``Import`` support for WL packages
#. ``IterationLimit``
#. ``LoadModule``
#. ``MantissaExponent[]``, ``FractionalPart[]``, ``CubeRoot[]``
#. ``PolynomialQ[]``, ``MinimalPolynomial[]``
#. ``Quit[]``, ``Exit[]`` #523, #814,
#. ``RealDigits`` #891, #691, ``Interrupt``, ``Unique``
#. ``RemoveDiacritics[]``, ``Transliterate[]`` #617
#. ``Root`` #806
#. ``Sign[]``, ``Exponent``, ``Divisors``, ``QuotientRemainder``, ``FactorTermsList``
#. Speedups by avoiding inner classes, #616
#. ``StringRiffle[]``, ``StringFreeQ[]``, ``StringContainsQ[]``, ``StringInsert``
#. ``SubsetQ`` and ``Delete[]`` #688, #784,
#. ``Subsets`` #685
#. ``SystemTimeZone`` and correct ``TimeZone`` #924
#. ``System\`Byteordering`` and ``System\`Environemnt`` #859
#. ``$UseSansSerif`` #908
#. ``randchoice`` option for ``NoNumPyRandomEnv`` #820
#. Support for ``MATHICS_MAX_RECURSION_DEPTH``
#. Option ``--full-form`` (``-F``) on ``mathics`` to parsed ``FullForm`` of input expressions

Enhancements and bug fixes
++++++++++++++++++++++++++

#. speed up leading-blank patterns #625, #933
#. support for iteration over Sequence objects in ``Table``, ``Sum``, and ``Product``
#. fixes for option handling
#. fixes for ``Manipulate[x,{x,{a,b}}]``
#. fixes rule -> rule case for ``Nearest``
#. fixes and enhancements to ``WordCloud``
#. added ``StringTrim[]``
#. fixes ``URLFetch`` options
#. fixes ``XMLGetString`` and parse error
#. fixes ``LanguageIdentify``
#. fixes 2 <= base <= 36 in number parsing
#. improved error messages
#. fixes ``Check``, ``Interrupt``, and ``Unique`` #696
#. fixes ``Eigenvalues``, ``Eigenvectors`` #804
#. fixes ``Solve`` #806
#. proper sympolic expantion for ``Re`` and ``Im``
#. fixes a bug in the evaluation of ``SympyPrime`` #827
#. clean up ``ColorData``
#. fixes Unicode characters in TeX document
#. update Django gallery examples
#. fixes ``Sum`` and ``Product`` #869, #873
#. warn when using options not supported by a Builtin #898, #645

Mathematica tracking changes
++++++++++++++++++++++++++++

#. renamed ``FetchURL`` to ``URLFetch`` (according to the WL standard)
#. renamed ``SymbolLookup`` to ``Lookup``

Performance improvements
++++++++++++++++++++++++

#. Speed up pattern matching for large lists
#. Quadradtic speed improvement in pattern matching. #619 and see the graph comparisons there
#. In-memory sessions #623

Other changes
+++++++++++++

#. bump ``RecursionLimit``
#. blacken (format) a number of Python files and remove blanks at the end of lines
#. Adding several CI tests
#. Remove various deprecation warnings
#. Change shbang from ``python`` to ``python3``
#. Update docs

Backward incompatibilities
++++++++++++++++++++++++++

#. Support for Python 3.5 and earlier, and in particular Python 2.7,
  was dropped.
#. The ``graphs`` module (for Graphs) has been pulled until Mathics
  supports pymathics and graphics using networkx better. It will
  reappear as a pymathics module.
#. The ``natlang`` (for Natural Language processing) has also been
  pulled.  The problem here too is that the pymathics mechanism needs
  a small amount of work to make it scalable, and in 1.0 these were
  hard coded. Also, both this module and ``graphs`` pulled in some
  potentially hard-to-satisfy non-Python dependencies such as
  matplotlib, or NLP libraries, and word lists. All of this made
  installation of Mathics harder, and the import of these libraries,
  ``natlang`` in particular, took some time. All of this points to having
  these live in their own repositories and get imported on lazily on
  demand.


-----

1.0 (October 2016)
------------------

New features
++++++++++++

#. ``LinearModelFit`` #592
#. ``EasterSunday`` #590
#. ``DSolve`` for PDE #589
#. ``LogisticSigmoid`` #588
#. ``CentralMoment``, ``Skewness``, ``Kurtosis`` #583
#. New web interface #574
#. ``Image`` support and image processing functions #571, #541, #497, #493, #482
#. ``StringCases``, ``Shortest``, ``Longest`` string match/replace #570
#. ``Quantime`` and ``Quartiles`` #567
#. ``Pick`` #563
#. ``ByteCount`` #560
#. ``Nearest`` #559
#. ``Count`` #558
#. ``RegularPolygon`` #556
#. Improved date parsing #555
#. ``Permutations`` #552
#. LLVM compilation of simple expressions #548
#. ``NumberForm`` #534, #530, #455
#. Basic scripting with mathicsscript
#. Arcs for ``Disk`` and ``Circle`` #498, #526
#. Download from URL #525
#. ``$CommandLine`` #524
#. ``Background`` option for ``Graphics`` #522
#. ``Style`` #521, #471, #468
#. Abbreviated string patterns #518
#. ``Return`` #515
#. Better messages #514
#. Undo and redo functionality in web interface #511
#. ``Covariance`` and ``Correlation`` #506
#. ``ToLowerCase``, ``ToUpperCase``, ``LowerCaseQ``, ``UpperCaseQ`` #505
#. ``StringRepeat`` #504
#. ``TextRecognise`` #500
#. Axis numbers to integers when possible #495
#. ``PointSize`` #494
#. ``FilledCurve``, ``BezierCurve``, ``BezierFunction`` #485
#. ``PadLeft``, ``PadRight`` #484
#. ``Manipulate`` #483, #379, #366
#. ``Replace`` #478
#. String operator versions #476
#. Improvements to ``Piecewise`` #475
#. Derivation typo #474
#. Natural language processing functions #472
#. ``Arrow``, ``Arrowheads`` #470
#. Optional modules with requires attribute #465
#. ``MachinePrecision`` #463
#. ``Catenate`` #454
#. ``Quotient`` #456
#. Disable spellcheck on query fields #453
#. ``MapThread`` #452
#. ``Scan`` and ``Return`` #451
#. ``On`` and ``Off`` #450
#. ``$MachineEpsilon`` and ``$MachinePrecision`` #449
#. ``ExpandAll`` #447
#. ``Position`` #445
#. ``StringPosition`` #444
#. ``AppendTo``, ``DeleteCases``, ``TrueQ``,  ``ValueQ`` #443
#. ``Indeterminate`` #439
#. More integral functions #437
#. ``ExpIntegralEi`` and ``ExpIntegralE`` #435
#. ``Variance`` and ``StandardDeviation`` #424
#. Legacy ``Random`` function #422
#. Improved gamma functions #419
#. New recursive descent parser #416
#. ``TakeSmallest`` and related #412
#. ``Boole`` #411
#. ``Median``, ``RankedMin``, ``RankedMax`` #410
#. ``HammingDistance`` #409
#. ``JaccardDissimilarity`` and others #407
#. ``EuclideanDistance`` and related #405
#. Magic methods for ``Expression`` #404
#. ``Reverse`` #403
#. ``RotateLeft`` and ``RotateRight`` #402
#. ``ColorDistance``, ``ColorConvert`` #400
#. Predefine and document ``$Aborted`` and ``$Failed`` #399
#. ``IntegerString``, ``FromDigits``, and more #397
#. ``EditDistance`` and ``DamerauLevenshteinDistance`` #394
#. ``QRDecomposition`` #393
#. ``RandomChoice`` and ``RandomSample`` #488
#. ``Hash`` #387
#. Graphics boxes for colors #386
#. ``Except`` #353
#. Document many things #341
#. ``StringExpression`` #339
#. Legacy file functions #338

Bug fixes
+++++++++

#. Nested ``Module`` #591, #584
#. Python2 import bug #565
#. XML import #554
#. ``\[Minus]`` parsing bug #550
#. ``Cases`` evaluation bug #531
#. ``Take`` edge cases #519
#. ``PlotSize`` bug #512
#. Firefox nodeValue warning #496
#. Django database permissions #489
#. ``FromDigits`` missing message #479
#. Numerification upon result only #477
#. Saving and loading notebooks #473
#. ``Rationalise`` #460
#. ``Optional`` and ``Pattern`` precedence values #459
#. Fix ``Sum[i / Log[i], {i, 1, Infinity}]`` #442
#. Add ``\[Pi]``, ``\[Degree]``, ``\[Infinity]`` and ``\[I]`` to parser #441
#. Fix loss of precision bugs #440
#. Many minor bugs from fuzzing #436
#. ``Positive``/``Negative`` do not numerify arguments #430 fixes #380
#. Chains of approximate identities #429
#. Logical expressions behave inconsistently/incorrectly #420 fixes #260
#. Fix ``Take[_Symbol, ___]`` #396
#. Avoid slots in rule handling #375 fixes #373
#. ``Gather``, ``GatherBy``, ``Tally``, ``Union``, ``Intersect``, ``IntersectingQ``, ``DisjointQ``, ``SortBy`` and ``BinarySearch`` #373
#. Symbol string comparison bug #371
#. Fix ``Begin``/``BeginPackage`` leaking user-visible symbols #352
#. Fix ``TableForm`` and ``Dimensions`` with an empty list #343
#. Trailing slash bug #337
#. ``Global`` system bug #336
#. ``Null`` comparison bug #371
#. ``CompoundExpression`` and ``Out[n]`` assignment bug #335 fixes #331
#. Load unevaluated cells #332

Performance improvements
++++++++++++++++++++++++

#. Large expression formatting with ``$OutputSizeLimit`` #581
#. Faster terminal output #579
#. Faster ``walk_paths`` #578
#. Faster flatten for ``Sequence`` symbols #577
#. Compilation for plotting #576
#. ``Sequence`` optimisations #568
#. Improvements to ``GatherBy`` #566
#. Optimised ``Expression`` creation #536
#. ``Expression`` caching #535
#. ``Definitions`` caching #507
#. Optimised ``Position``, ``Cases``, ``DeleteCases`` #503
#. Optimised ``StringSplit`` #502
#. Optimised ``$RecursionLimit`` #501
#. Optimised insert_rule #464
#. Optimised ``IntegerLength`` #462
#. Optimised ``BaseExpression`` creation #458
#. No reevaluation of evaluated values #391
#. Shortcut rule lookup #389
#. 15% performance boost by preventing some rule lookups #384
#. 25% performance boost using same over ``__eq__``
#. n log n algorithm for ``Complement`` and ``DeleteDuplicates`` #373
#. Avoid computing ``x^y`` in ``PowerMod[x, y, m]`` #342


-----

0.9 (March 2016)
----------------

New features
++++++++++++

#. Improve syntax error messages #329
#. ``SVD``, ``LeastSquares``, ``PseudoInverse`` #258, #321
#. Python 2.7, 3.2-3.5 via six support #317
#. Improvements to ``Riffle`` #313
#. Tweaks to ``PolarPlot`` #305
#. ``StringTake`` #285
#. ``Norm`` #268 #270
#. ``Total``, ``Accumulate``, ``FoldList``, ``Fold`` #264, #252
#. ``Flatten`` #253 #269
#. ``Which`` with symbolic arguments #250
#. ``Min``/``Max`` with symbolic arguments # 249

Dependency updates
++++++++++++++++++

#. Upgrade to ply 3.8 (issue #246)
#. Drop interrupting cow #317
#. Add six (already required by Django) #317

Bug fixes
+++++++++

#. Span issues with negative indices #196 fixed by #263 #325
#. SVG export bug fixed by #324
#. Django runserver threading issue #158 fixed by #323
#. asymptote bug building docs #297 fixed by #317
#. Simplify issue #254 fixed by #322
#. ``ParametricPlot`` bug fixed by #320
#. ``DensityPlot`` SVG regression in the web interface
#. Main function for server.py #288, #289 fixed by #298
#. ply table regeneration #294 fixed by #295
#. Print bar issue #290 fixed by #293
#. Quit[] index error #292 partially fixed by #307
#. Quit definition fixed by #286
#. Conjugate issue #272 fixed by #281

-----------

0.8 (late May 2015)
-------------------

New features
+++++++++++++

#. Improvements to 3D Plotting, see #238
#. Enable MathJax menu, see #236
#. Improvements to documentation

Dependency updates
++++++++++++++++++

#. Upgrade to SymPy 0.7.6
#. Upgrade to ply3.6 (new parsetab format, see #246)
#. Upgrade to mpmath 0.19

Bug fixes
+++++++++

#. ``IntegerDigits[0]``

-----------

0.7 (Dec 2014)
--------------

New features
++++++++++++

#. Readline tab completion
#. Automatic database initialisation
#. Support for wildcards in ``Clear`` and ``ClearAll``
#. Add ``Conjugate``
#. More tests and documentation for ``Sequence``
#. Context support


Bugs fixed
++++++++++

#. Fix unevaluated index handling (issue #217)
#. Fix ``Solve`` treating one solution equal to 1 as a tautology (issue
  #208)
#. Fix temporary symbols appearing in the result when taking
  derivatives with respect to t (issue #184)
#. typo in save worksheet help text (issue #199)
#. Fix mathicsserver wildcard address binding
#. Fix ``Dot`` acting on matrices in MatrixForm (issue #145)
#. Fix Sum behaviour when using range to generate index values (issue #149)
#. Fix behaviour of plot with unevaluated arguments (issue #150)
#. Fix zero-width space between factors in MathJax output (issue #45)
#. Fix ``{{2*a, 0},{0,0}}//MatrixForm`` crashing in the web interface
  (issue #182)

--------------

0.6 (late October 2013)
------------------------

New features
++++++++++++

#. ``ElementData`` using data from Wikipedia
#. Add ``Switch``
#. Add ``DSolve`` and ``RSolve``
#. More Timing functions ``AbsoluteTiming``, ``TimeUsed``, ``SessionTime``, ``Pause``
#. Date functions ``DateList``, ``DateString``, ``DateDifference``, etc.
#. Parser rewritten using lex/yacc (PLY)
#. Unicode character support
#. ``PolarPlot``
#. IPython style (coloured) input
#. ``VectorAnalysis`` Package
#. More special functions (Bessel functions and othogonal polynomials)
#. More NumberTheory functions
#. ``Import``, ``Export``, ``Get``, ``Needs`` and other IO related functions
#. PyPy compatibility
#. Add benchmarks (``mathics/benchmark.py``)
#. ``BaseForm``
#. ``DeleteDuplicates``
#. Depth, Operate Through and other Structure related functions
#. Changes to ``MatrixForm`` and ``TableForm`` printing
#. Use interrupting COW to limit evaluation time
#. Character Code functions

Bugs fixed
++++++++++

#. Fix divide-by-zero with zero-length plot range
#. Fix mathicsserver exception on startup with Django 1.6 (issues #194, #205, #209)

-------

0.5 (August 2012)
-----------------

#. Compatibility with Sage 5, SymPy 0.7, Cython 0.15, Django 1.2
#. 3D graphics and plots using WebGL in the browser and Asymptote in TeX output
#. Plot: adaptive sampling
#. MathJax 2.0 and line breaking
#. New symbols: ``Graphics3D`` etc., ``Plot3D``, ``ListPlot``,
  ``ListLinePlot``, ``ParametricPlot``, ``Prime``, ``Names``, ``$Version``
#. Fixed issues: 1, 4, 6, 8-21, 23-27
#. Lots of minor fixes and improvements
#. Number of built-in symbols: 386

-------

0.4
---

Compatibility to Sage 4.0 and other latest libraries

-------


0.3 (beta only)
--------------

Resolved several issues

-------


0.1 (alpha only)
--------------

Initial version
