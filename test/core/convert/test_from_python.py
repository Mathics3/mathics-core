from mathics.core.atoms import ByteArray
from mathics.core.convert.python import from_python


def test_from_python():
    assert isinstance(
        from_python(b"abc"), ByteArray
    ), "Python bytes() converts to a Mathics3 ByteArray"
    assert isinstance(
        from_python(bytearray([1, 2, 3])), ByteArray
    ), "Python bytearray converts to a Mathics3 ByteArray"
    # Many other tests are imagined to come...
