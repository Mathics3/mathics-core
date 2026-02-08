import inspect
from typing import Callable

from mathics.core.element import BoxElementMixin

# key is str: (to_xxx name, value) is formatter function to call
format2fn: dict = {}


def encode_mathml(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace('"', "&quot;").replace(" ", "&nbsp;")
    text = text.replace("\n", '<mspace linebreak="newline" />')
    return text


def add_conversion_fn(cls, module_fn_name=None) -> None:
    """Add to `format2fn` a mapping from a conversion type and builtin-class
    to a conversion method.

    The conversion type is determined form the module name.
    For example, in module mathics.format.render.svg the conversion
    type is "svg".

    The conversion method is assumed to be a method in the caller's
    module, and is derived from lowercasing `cls`.

    For example function arrowbox in module mathics.format.render.svg would be
    the SVG conversion routine for class ArrowBox.

    We use frame introspection to get all of this done.
    """
    fr = inspect.currentframe()
    assert fr is not None
    fr = fr.f_back
    assert fr is not None
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


def box_to_format(box, format: str, **options) -> str:  # Maybe Union[str, bytearray]
    """
    Translates a box structure ``box`` to a file format ``format``.
    This is used only at the root Box of a boxed expression.
    """
    options["format_type"] = format
    return convert_box_to_format(box, **options)


def convert_box_to_format(box, **options) -> str:
    """
    Translates a box structure ``box`` to a file format ``format``.
    This is used at either non-root-level boxes or from the
    initial call from box_to_format.
    """
    return lookup_method(box, options["format_type"])(box, **options)


def convert_inner_box_field(box, field: str = "inner_box", **options):
    # Note: values set in `options` take precedence over `box_options`
    inner_box = getattr(box, field)
    child_options = (
        {**box.box_options, **options} if hasattr(box, "box_options") else options
    )
    return convert_box_to_format(inner_box, **child_options)


def lookup_method(self, format: str) -> Callable:
    """
    Find a conversion method for `format` in self's class method resolution order.
    """
    for cls in inspect.getmro(type(self)):
        format_fn = format2fn.get((format, cls), None)
        if format_fn is not None:
            # print(f"format function: {format_fn.__name__} for {type(self).__name__}")
            return format_fn

    box_to_method = getattr(self, f"to_{format}", None)
    if getattr(BoxElementMixin, f"to_{format}") is box_to_method:
        box_to_method = None
    if box_to_method:
        print("using", box_to_method)

        # The elements is not used anywhere.
        def ret_fn(box, elements=None, **opts):
            assert elements is None, "elements parameter is not used anymore."
            return box_to_method(**opts)

        return ret_fn

    error_msg = f"Can't find formatter {format} for {type(self).__name__} ({self})"
    raise RuntimeError(error_msg)
