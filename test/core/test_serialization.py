import io
import pickle

from mathics.session import MathicsSession


def test_session_serialization():
    """Check that a session, with Definitions and Rules can be serialized properly,
    that is, that they can be dumped and loaded.
    """

    original_session = MathicsSession()
    original_session.evaluate("x = 4")
    original_session.evaluate("r = y -> 3")

    pickle_buffer = io.BytesIO()
    pickle.dump(original_session, pickle_buffer)
    pickle_buffer.seek(0)
    restored_session = pickle.load(pickle_buffer)
    result = restored_session.evaluate("ToString[x]").value
    assert result == "4", "Assign[] did not dump and restore properly"
    result = restored_session.evaluate("x + y /. r")
    assert (
        result.to_python() == 7
    ), "Rule[] and Assign[] did not dump and restore properly"
