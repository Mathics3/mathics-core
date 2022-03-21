import pytest


from mathics import __file__ as mathics_initfile_path
import glob
import importlib
import pkgutil
import os.path as osp
from mathics.version import __version__  # noqa used in loading to check consistency.


from mathics.builtin.base import Builtin

mathics_path = mathics_initfile_path[:-12]
mathics_builtins_path = mathics_path + "/builtins"

CHECK_GRAMMAR = True


if CHECK_GRAMMAR:
    try:
        import language_tool_python

        language_tool = language_tool_python.LanguageToolPublicAPI("en-US")
    except Exception:
        language_tool = None
        assert False, "language-tool-python not available"

module_subdirs = (
    "arithfns",
    "atomic",
    "assignments",
    "box",
    "colors",
    "distance",
    "drawing",
    "files_io",
    "intfns",
    "list",
    "moments",
    "numbers",
    "specialfns",
    "string",
    "fileformats",
)

print("directory:", mathics_builtins_path)
__py_files__ = [
    osp.basename(f[0:-3])
    for f in glob.glob(osp.join(mathics_builtins_path, "[a-z]*.py"))
]


def is_builtin(var):
    if var == Builtin:
        return True
    if hasattr(var, "__bases__"):
        return any(is_builtin(base) for base in var.__bases__)
    return False


def import_module(module_name: str):
    print("importing module ", module_name)
    try:
        module = importlib.import_module("mathics.builtin." + module_name)
    except Exception as e:
        print(e)
        return None

    modules[module_name] = module


# exclude_files = set(("codetables", "base"))
module_names = [f for f in __py_files__]


for subdir in module_subdirs:
    import_name = f"mathics.builtin.{subdir}"
    builtin_module = importlib.import_module(import_name)
    for importer, modname, ispkg in pkgutil.iter_modules(builtin_module.__path__):
        module_names.append(f"{subdir}.{modname}")


modules = dict()
for module_name in module_names:
    import_module(module_name)


@pytest.mark.parametrize(
    ("module_name",),
    [(module_name,) for module_name in modules],
)
def test_summary_text_available(module_name):
    """
    Checks that each Builtin has its summary_text property.
    """

    module = modules[module_name]
    vars = dir(module)
    for name in vars:
        var = getattr(module, name)
        if (
            hasattr(var, "__module__")
            and var.__module__.startswith("mathics.builtin.")
            and var.__module__ != "mathics.builtin.base"
            and is_builtin(var)
            and not name.startswith("_")
            and var.__module__ == module.__name__
        ):  # nopep8
            instance = var(expression=False)
            if isinstance(instance, Builtin):
                print(name, instance)
                if not hasattr(instance, "summary_text"):
                    continue

                assert hasattr(instance, "summary_text"), (
                    f"{var.__name__} in {module_name} "
                    "does not have a summary_text property"
                )
                if language_tool and CHECK_GRAMMAR:
                    s = "The expression " + instance.summary_text.strip()
                    matches = language_tool.check(s)
                    if matches:
                        assert False, [
                            (m.sentence, m.replacements, m.message) for m in matches
                        ]
