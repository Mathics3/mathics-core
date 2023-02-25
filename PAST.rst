While ``FUTURE.rst`` gives our current roadmap, this file ``PAST.rst``
looks the other way for what we have accomplished when compared to what _was_ planned in ``FUTURE.rst``

While this is also listed in ``CHANGES.rst``, here we extract that to
make it easier to see the bigger picture without the details that are
in ``CHANGES.rst``.

Progress from 2022
==================

A fair bit of code refactoring has gone on so that we might be able to
scale the code, get it to be more performant, and more in line with
other interpreters. There is Greater use of Symbols as opposed to strings.

The buitin Functions have been organized into grouping akind to what is found in WMA.
This is not just for documentation purposes, but it better modularizes the code and keep
the modules smaller while suggesting where functions below as we scale.

Image Routines have been gone over.

A number of Built-in functions that were implemented were not accessible for various reasons.

Mathics3 Modules are better integrated into the documentation.
Existing Mathics3 modules ``pymathics.graph`` and ``pymathics.natlang`` have
had a major overhaul, although more is needed. And will continue after th 6.0.0 release

We have gradually been rolling in more Python type annotations and
current Python practices such as using ``isort``, ``black`` and ``flake8``.


Boxing and Formatting
---------------------

While some work on formatting is done has been made and the change in API reflects a little of this.
However a lot more work needs to be done.

Excecution Performance
----------------------

This has improved a slight bit, but not because it has been a focus, but
rather because in going over the code organization, we are doing this
less dumb, e.g. using Symbols more where symbols are intended. Or
fixing bugs like resetting mpmath numeric precision on operations that
need to chnage it temporarily.

Simpler Things
--------------

A number of items here remain, but should not be thought as independent items, but instead part of
"Forms, Boxing and Formatting".

"Making StandardOutput of polynomials match WMA" is really are Forms, Boxing and Formatting issue;
"Working on Jupyter integrations" is also very dependant this.

So the next major refactor will be on Forms, Boxing and Formatting.
