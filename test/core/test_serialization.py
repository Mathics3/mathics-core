import io
import pickle

from mathics.session import MathicsSession


def test_session_serialization():
    """
    Check that a session (and its Definitions object)
    be properly serialized.
    """

    original_session = MathicsSession()
    original_session.evaluate("x=4")

    pickle_buffer = io.BytesIO()
    pickle.dump(original_session, pickle_buffer)
    pickle_buffer.seek(0)
    restored_session = pickle.load(pickle_buffer)
    result = restored_session.evaluate("ToString[x]").value
    assert result == "4"
