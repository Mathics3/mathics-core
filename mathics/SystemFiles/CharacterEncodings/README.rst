This directory contains information about how to map Mathics3's characters for a particular ``$CharacterEncoding`` name.
``$CharacterEncoding`` values are often taken from a Python's CodePage name, like ``ISO8559-10`` or ``CP396``. Files in this directory helps to extend these codepages to other customized encodings.

The base name of the file (with the ``.wl`` extension stripped off) is
the `code page <https://en.wikipedia.org/wiki/Code_page>`_ name.

Available codepages are listed by evaluating the symbol ``$SystemCharacterEncodings``. The list contains the WL names of Python standard codepages, plus codepages defined by the files in this directory, with the extension (``.wl``) stripped. Notice that the list includes all the files in this folder, independently of whether the content is a valid encoding description. When an encoding is requested (for instance, in a ``ToString`` evaluation, or in a file-handling operation), the encoding name is first translated into a Python codec name. If the codec name is not available, then ``.wl`` encoding files in this folder are tried to be loaded using a ``Get`` evaluation. If the evaluation succeeds and the result is a ``List`` expression with the proper format, the elements of the list are interpreted, and a new Python codec is registered. 


A valid WL encoding definition consists of a ``List`` expression with two items: the size of the
mapping, ("7bit", "8bit" or "16bit"), and a ``List`` of entries specifying pairs of code/Unicode character for each character that differ from the default mapping that Mathics3 uses.

For example the file ``Unicode.wl`` contains::

   {"16Bit", {}}

Unicode uses the 16-bit variable-length mappings, and as it coincides exactly with the default encoding, the entries list is empty.

Similarly, for ASCII (a 7-bit encoding) the file ``ASCII.wl`` contains:

  {"7Bit", {}}

Klingon is an easy non-trivial encoding to describe. It is an 8-bit encoding. In
part, it remaps the ASCII letters to their Klingon Unicode value::

  {"8Bit",
     {{65, "\:F8D0"},
      {66, "\:F8D1"}, ...

Some other ASCII symbols, like ``'`, ``*``, ``(`` or ``^`` are remapped as well. 

The second element on each entry corresponds to the Unicode internal representation of a character, and the first entry is the numerical code associated to the charcode of that character in the encoding defined by the file. In some cases, the second entry can also be a number, corresponding to the Unicode code, or `None`. In the latter case, the character is identified with ``0x0xF200 + charcode``.
In some encodings, a third element can appear, which can only take the value ``False``. We speculate that this value is related to the "non-invertibility" of the character map. In any case, it seems to be a deprecated feature in WMA >=10.0, and it does not have any observable effect.

Character encoding files are loaded on the fly when they are required. This happens, for instance, when we set the ``$CharacterEncoding`` variable, or when we use the character encoding in a ``ToString``, ``FromCharacterCode``/``ToCharacterCode`` evaluation, or in file operations. If the encoding is successfully loaded, then a Python codec is created from the data in the definition file. Notice however that most of the available character encodings are loaded directly by translating to their Python codec names. Character encoding files are used just for those encodings that do not have a direct translation.

Notice also that currently, only 7-Bit and 8-Bit custom encodings are supported.16-Bit codepages in WMA mostly coincide with their built-in Python encodings, so by now we rely on them.

Let's consider a use example for one of these custom encodings: let's consider the string ``s="-Good bye Martok -\:f8df\:f8d0\:f8de\:f8d9\:f8d0\:f8f1"``. 
Encoding and decoding the string using the ``"Klingon"``  
``FromCharacterCode[ToCharacterCode[s, "Klingon"], "Klingon"]`` produces both in WMA and Mathics3 the same output ``"-\:f8d5ood bye \:f8daartok -\:f8df\:f8d0\:f8de\:f8d9\:f8d0\:f8f1"``. 

On the other hand, if we write it into a file using the ``"Klingon"`` encoding,
``
f=OpenWrite["/tmp/test.txt",CharacterEncoding->"Klingon"]; Write[f, s]; Close[f];
``
and then we open it back, 
``
f=OpenRead["/tmp/test.txt",CharacterEncoding->"Klingon"]; sr=Read[f, "String"]; Close[f];sr
``
what we get into the ``sr`` variable is ``"-\:f8d5ood bye \:f8daartok -\:f8df\:f8d0\:f8de\:f8d9\:f8d0\:f8f1"``: Klingon characters go back to Klingon characters, but also capital (Latin) letters are converted into their corresponding Klingon characters. Notice that this behavior is different from what we get in WMA: in that interpreter, encoding is taken into account for writing files, but not for reading them, so in WMA we would get ``"-Good bye Martok -KAPLA!"`` which looks inconsistent with the behavior of ``FromCharacterCode``/``ToCharacterCode``. 






