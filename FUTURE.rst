*One can always dream...*

.. contents::

The following 2023 road map that appears the 6.0.0 hasn't gone through enough discussion. This provisional.
Check the github repository for updates.


2023 Roadmap
============


When the release settles, "Forms, Boxing, And "Formatting" is the next
large refactor slated.  Having this will allow us to supporting Jupyter or other front
ends. And it is something that is most visibly wrong in Mathics3 output.

See ``PAST.rst`` for how the 2023 Roadmap compares to the 2022 Roadmap.

Forms, Boxing and Formatting
----------------------------

This remains the biggest holdover item from 2022, and seems easily doable.
It hinders interaction with Jupyter or other front ends.

Right now "Form" (a high-level specification of how to format) and
"format" (a low level specification of how output is encoded) are sometimes muddied.

For example, TeXForm may be a "Form", but output encoded for AMS-LaTeX is done by a *formatter*.
So AMS-LaTeX rendering and other kinds of rendering should be split into its own rendering for formatter module.
Currently we have asymptote, and svg "format" modules.

Back to high-level again, Boxing is something that can be written in Mathics3, and doing this at
least initially ensures that we have design that fits more naturally
into the Wolfram Language philosophy.


Performance
-----------

While this is probably more of an overall concern, for now, big refactoring needed here, such as
going over pattern matching, will get done after Forms, Boxing and Formatting .

Forms, Boxing and Formatting will however contain one improvement that
should speed up our performance: separating M-Expression evaluation from
Box "evaluations).

We expect there will be other little opportunities here and there as we have seen in the past.


More Custom kinds of (compound) Expressions
+++++++++++++++++++++++++++++++++++++++++++

We scratched the surface here with ListExpression. Associations and Python/Sympy/numpy literals can be customized with an aim towards reducing conversions from and to M-expressions.
A number of compound expressions, especially those which involve literals are more efficiently represented in some other way. For example,
representing a Mathics3 Association as a Python ordered dictionary, a Mathics3 List as a Python list or tuple, or as a numpy array.


Further Code Reorganization in Core and Eval
--------------------------------------------

Core object like ``BaseElement`` and possibly ``Symbol``, (and
probably others) are too "fat": they have too many custom methods that
are not applicable for most of the subclasses support.  It is likely
another pass will be made over this.

We have started moving "eval" code out of the "eval" methods and into its own module.

Mathics3 Module Enhancement
---------------------------

While we have put in quite a bit of effort to get these to be 6.0.0 compliant. There is still more work to do, and there are numerous bugs there.
Refactoring code to generate Graphs in ``pymathics.graph`` might happen. Porting the ``pymathics.graph`` code to use NetworkX 3.0 would be nice;
``pymathics.natlang`` could also use a look over in terms of the libraries we are using.

Python upgrades
---------------

After Mathics3 Version 6.0.0, Python 3.6 will be dropped and possibly 3.7. Changes are needed to support 3.11 so we will be focusing on 3.8 to 3.11.

We have gradually been using a more modern Python programming style
and idioms: more type annotation, use of ``isort`` (order Python
imports), ``black`` (code formatting), and ``flake8`` (Python lint
checking).


Deferred
--------

As mentioned before, pattern-matching revision is for later. `This
discussion
<https://github.com/Mathics3/mathics-core/discussions/800>`_ is a
placeholder for this discussion.

Overhauling the documentation to use something better supported and
more mainstream like sphinx is deferred. This would really be nice to
have, but it will require a bit of effort and detracts from all of the other work that is needed.

We will probably try this out in a limited basis in one of the Mathics3 modules.

Speaking of Mathics3 Modules, there are probably various scoping/context issues that Mathics3 modules make more apparent.
This will is deferred for now.

Way down the line, is converting to a more sequence-based interpreter which is needed for JIT'ing and better Compilation support.

Likewise, speeding up startup time via saving and loading an image is something that is more of a long-term goal.

Things in this section can change, depending on the help we can get.


Miscellaneous
-------------

No doubt there will be numerous bug fixes, and builtin-function additions especially now that we have a better framework to support this kind of growth.
Some of the smaller deferred issues refactorings may get addressed.

As always, where and how fast things grow here depends on help available.


2022 Roadmap
=============

Code reorganization and Refactoring
-----------------------------------

This has been the biggest impediment to doing just about anything else.

Boxing and Formatting
+++++++++++++++++++++

We will isolate and make more scalable how boxing and top-level formatting is done. This will happen right after release 5.0.0

API Expansion
+++++++++++++

We have an API for graphics3d which is largely used for many Graphics 3D objects like spheres and regular polyhedra. However, this needs to get expanded for Plotting.

An API for JSON 2D plotting is needed too.

Execution Performance
----------------------

While we have made a start on this in 5.0, much more is needed.

We have only gone over the top-level evaluation for compound expressions.
The following evaluation phases need to be gone over and revised:

* pattern-matching and rewrite rules
* apply steps

With respect to top-level evaluation, we have only scratched the surface of what can be done with evaluation specialization. We currently have a kind of specialization for Lists. Possibly the same is needed for Associations.

This work will continue after the 5.0.0 release. We expect plotting will be faster by the next release or major release.

Being able to run existing WMA packages
----------------------------------------

Sadly, Mathics cannot run most of the open-source WMA packages.

In particular we would like to see the following run:

* Rubi
* KnotTheory

This is a longer-term goal.

Documentation System
--------------------

The current home-grown documentation should be replaced with Sphynx and autodoc.

Compilation
-----------

Compilation is a rather unsophisticated process by trying to speed up Python code using llvmlite. The gains here will always be small compared the kinds of gains a compiler can get. However in order to even be able to contemplate writing a compiler (let alone say a JIT compiler), the code base needs to be made to work more like a traditional interpreter. Some work will be needed just to be able or create a sequence of instructions to run.

Right now the interpreter is strictly a tree interpreter.

Simpler Things
---------------

There have been a number of things that have been deferred:

* Using unicode symbols in output
* Making StandardOutput of polynomials match WMA
* Finish reorganizing Builtin Functions so that the structure matches is more logical
* Adding more Graphics Primitives
* Working on Jupyter integrations

In some cases like the first two items these are easy, and more important things have prevented doing this. In some cases like the last two, there are more foundational work that should be done first.


2021 Roadmap
=============


Graphics3D
----------

With 4.0.0, we have started defining a Graphics3D protocol.  It is
currently expressed in JSON. There is an independent `threejs-based
module
<https://www.npmjs.com/package/@mathicsorg/mathics-threejs-backend>`_
to implement this. Tiago Cavalcante Trindade is responsible for this
code and for modernizing our JavaScript, and it use in threejs.

We expect a lot more to come. For example UniformPolyhedra is too new
to have been able to make this release.

We also need to define a protocol and implementation for 2D Graphics.


Boxing, Formatting, Forms
-------------------------

While we have started to segregate boxing (bounding-box layout) and
formatting (translation to a conventional rendering format or
language), a lot more work needs to be done.

Also, a lot more Forms should be defined. And those that exist, like
TeXForm, and StandardForm, could use improvement.

This area is still a big mess.

Jupyter and other Front Ends
----------------------------

Although we had planned to move forward on this previously, it now
appears that we should nail down some of the above better, before
undertaking. Jupyter uses a wire protocol, and we still have
work to do in defining the interfaces mentioned above.

That said, this is still on the horizon.

Interest has also been expressed in WebGL, and Flask front ends. But
these too will require use to have better protocols defined and in
place.


Documentation
-------------

Sometime around release 4.0.0, all of the code related to producing
documentation in LaTeX and in Mathics Django, and running doctests
will be split off and put into its own git repository.

I've spent a lot of time banging on this to try to get to to be be
less fragile, more modular, more intelligible, but it still needs a
*lot* more work and still is very fragile.

Also there is much to do on the editor side of things in terms of
reorganizing sections (which also implies reorganizing the builtin
module structure, since those are tightly bound together).

We still need to convert this into Sphinx-based, with its doctest.  We
also need to be able to extract information in sphinx/RsT format
rather than its home-brew markup language which is sort of XML like.

Performance
-----------

This is one area where we know a lot about what *kinds* of things need
to be done, but have barely scratched the surface here.

The current implementation is pretty bare bones.

We have problems with recursion, memory consumption, loading time, and
overall speed in computation.

Support for External Packages
-----------------------------

I would have liked to have seen this going earlier. However right now
Mathics is still at too primitive a level for any serious package to
be run on it. This will change at some point though.

Support for Mathematica Language Levels
---------------------------------------

This is something that I think would be extremely useful and is
straightforward to do someone has used Mathematica over the years
knows it well. I think most of this could be supported in Mathics code
itself and loaded as packages. Any takers?
