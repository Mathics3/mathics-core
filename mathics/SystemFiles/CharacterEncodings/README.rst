This directory contains information about how to map Mathics3's characters for a particular ``$CharacterEncoding`` name.
``$CharacterEncoding`` values are often taken from a Python's CodePage name, like ``ISO8559-10`` or ``CP396``. Files in this directory helps to extend these codepages to other customized encodings.

The base name of the file (with the ``.wl`` extension stripped off) is
the `code page <https://en.wikipedia.org/wiki/Code_page>`_ name.

Available codepages are listed evaluating the symbol ``$SystemCharacterEncodings``. The list contains the WL names of Python standard codepages, plus codepages defined by the files in this directory.

Each of these files are WL files containing a list of two items, the size of the
mapping, ("7bit", "8bit" or "16bit"), and list mappings character mappings where they differ from the default mapping that Mathics3 uses.

For example the file ``Unicode.wl`` contains::

   {"16Bit", {}}

Unicode uses the 16-bit variable length mappings and there are exceptions we need to record.

Similarly for ASCII (a 7-bit encoding) the file ``ASCII.wl`` contains::

  {"7Bit", {}}

Klingon is an easy encoding to describe. It is an 8-bit encoding. In
part, it remaps the ASCII letters to their Klingon Unicode value::

  {"8Bit",
     {{65, "\:F8D0"},
      {66, "\:F8D1"}, ...


Some other ASCII symbols, like ``'`, ``*``, ``(`` or ``^`` are remapped as well.

The second element on each entry corresponds to the Unicode internal representation of a character, and the first entry is the numerical code associated to the charcode of that character in the encoding defined by the file. In some cases, the second entry can be also a number, corresponding to the Unicode code, or `None`. In the later case, the character is identified with ``0x0xF200 + charcode``.
In some encodings, it can appear a third element, which can only take the value ``False``. We speculate that this value is related to the "non-invertibility" of the character map. In any case, it seems to be a deprecated feature in WMA >=10.0, and it does not have any observable effect.

Character encoding files are loaded on the fly when they a required. This happends for instance when we set the ``$CharacterEncoding`` variable, or when we use the character encoding in a ``ToString``, ``FromCharacterCode``/``ToCharacterCode`` evaluation, or in file operations. If the encoding is successfully loaded, then a Python codec is created from the data in the definition file. Notice however that most of the available character encodings are loaded directly by translating to their Python codec names. Character encoding files are used just for those encodings that do not have a direct translation.

Notice also that currently, only 7-Bit and 8-Bit custom encodings are supported.16-Bit codepages in WMA mostly coincides with their builtin Python encodings, so by now we rely on them.
