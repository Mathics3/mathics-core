import os.path as osp
import glob
import importlib


__py_files__ = [
    osp.basename(f[0:-3])
    for f in glob.glob(osp.join(osp.dirname(__file__), "[a-z]*.py"))
]

for module_name in __py_files__:
    try:
        importlib.import_module(f"mathics.format.{module_name}")
    except Exception as e:
        print(e)
        print(f"    Not able to load {module_name}. Check your installation.")
        print(f"    mathics.format loads from {__file__[:-11]}")
        exit(-1)
