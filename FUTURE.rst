*One can always dream...*

.. contents::

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

Complation is a rather unsophisticated process by trying to speed up Python code using llvmlite. The gains here will always be small compared the kinds of gains a compiler can get. However in order to even be able to contemplate writing a compiler (let alone say a JIT compiler), the code base needs to be made to work more like a traditional interpreter. Some work will be needed just to be able or create a sequence of instructions to run.

Right now the interpreter is strictly a tree interperter.

Simpiler Things
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
