import inspect
from typing import Callable
import re

# key is str: (to_xxx name, value) is formatter function to call
format2fn: dict = {}


def encode_mathml(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace('"', "&quot;").replace(" ", "&nbsp;")
    text = text.replace("\n", '<mspace linebreak="newline" />')
    return text


TEX_REPLACE = {
    "{": r"\{",
    "}": r"\}",
    "_": r"\_",
    "$": r"\$",
    "%": r"\%",
    "#": r"\#",
    "&": r"\&",
    "\\": r"\backslash{}",
    "^": r"{}^{\wedge}",
    "~": r"\sim{}",
    "|": r"\vert{}",
}
TEX_TEXT_REPLACE = TEX_REPLACE.copy()
TEX_TEXT_REPLACE.update(
    {
        "<": r"$<$",
        ">": r"$>$",
        "~": r"$\sim$",
        "|": r"$\vert$",
        "\\": r"$\backslash$",
        "^": r"${}^{\wedge}$",
    }
)
TEX_REPLACE_RE = re.compile("([" + "".join([re.escape(c) for c in TEX_REPLACE]) + "])")


def encode_tex(text: str, in_text=False) -> str:
    def replace(match):
        c = match.group(1)
        repl = TEX_TEXT_REPLACE if in_text else TEX_REPLACE
        # return TEX_REPLACE[c]
        return repl.get(c, c)

    text = TEX_REPLACE_RE.sub(replace, text)
    text = text.replace("\n", "\\newline\n")
    return text


extra_operators = set(
    (
        ",",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
        "\u301a",
        "\u301b",
        "\u00d7",
        "\u2032",
        "\u2032\u2032",
        " ",
        "\u2062",
        "\u222b",
        "\u2146",
    )
)


def lookup_method(self, format: str, module_fn_name=None) -> Callable:
    """
    Find a conversion method for `format` in self's class method resolution order.
    """
    for cls in inspect.getmro(type(self)):
        format_fn = format2fn.get((format, cls), None)
        if format_fn is not None:
            # print(f"format function: {format_fn.__name__} for {type(self).__name__}")
            return format_fn
    raise RuntimeError(
        f"Can't find formatter {format_fn.__name__} for {type(self).__name__}"
    )


def add_conversion_fn(cls, module_fn_name=None) -> None:
    """Add to `format2fn` a mapping from a conversion type and builtin-class
    to a conversion method.

    The conversion type is determined form the module name.
    For example, in module mathics.format.svg the conversion
    type is "svg".

    The conversion method is assumed to be a method in the caller's
    module, and is derived from lowercasing `cls`.

    For example function arrowbox in module mathics.format.svg would be
    the SVG conversion routine for class ArrowBox.

    We use frame introspection to get all of this done.
    """
    fr = inspect.currentframe().f_back
    module_dict = fr.f_globals

    # The last part of the module name is expected to be the conversion routine.
    conversion_type = module_dict["__name__"].split(".")[-1]

    # Derive the conversion function from the passed-in class argument,
    # unless it is already set.
    if module_fn_name is None:
        module_fn_name = cls.__name__.lower()
    elif hasattr(module_fn_name, "__name__"):
        module_fn_name = module_fn_name.__name__

    # Finally register the mapping: (Builtin-class, conversion name) -> conversion_function.
    format2fn[(conversion_type, cls)] = module_dict[module_fn_name]
