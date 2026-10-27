# Code that gets run before pytest runs..
import gc


def pytest_sessionfinish(session, exitstatus):
    """Executes after all tests have completed.

    Freeze objects right before pytest exits. This prevents PyGC_Collect from
    walking Generation 2 objects during _Py_Finalize.
    """
    gc.freeze()
