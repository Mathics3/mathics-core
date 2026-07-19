This directory contains information about how to map Mathics3's characters for a particular ``$CharacterEncoding`` name.
``$CharacterEncoding`` values are often taken from a CodePage name, like ``ISO8559-10`` or ``CP396``.

Right now this directory is not used. In the future however it might be used to better match WMA behavior.

The base name of the file (with the ``.wl`` extension stripped off) is
the `code page <https://en.wikipedia.org/wiki/Code_page>`_ name.

The content of the file contains a list of two items, the size of the
mapping, ("7bit", "8bit" or "16bit"), and list mappings character mappings where they differ
from the default mapping that Mathics3 uses.

For example the file ``Unicode.wl`` contains::

   {"16Bit", {}}

Unicode uses the 16-bit mappings and there are exceptions we need to record.

Similarly for ASCII (a 7-bit encoding) the file ``ASCII.wl`` contains::

  {"7Bit", {}}

Klingon is an easy encoding to describe. It is an 8-bit encoding. In
part, it remaps the ASCII letters to their Klingon Unicode value::

  {"8Bit",
     {{65, "\:F8D0"},
      {66, "\:F8D1"}, ...


Some other ASCII symbols, like ``'`, ``*``, ``(`` or ``^`` are remapped as well.
