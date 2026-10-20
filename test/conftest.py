# Code that gets run before pytest runs..
import gc


def pytest_sessionfinish(session, exitstatus):
    """Executes after all tests have completed.

    Disables cyclic GC right before pytest exits, preventing PyGC_Collect from
    walking Generation 2 during _Py_Finalize.
    """
    gc.disable()
