"""Tests for the bundled DiscreteMath`RSolve` package."""

import pytest

from mathics.core.symbols import SymbolNull, SymbolTrue
from mathics.session import MathicsSession


@pytest.mark.parametrize("loader", ["Get", "Needs"])
def test_rsolve_load(loader):
    session = MathicsSession()

    assert session.evaluate(f'{loader}["DiscreteMath`RSolve`"]') is SymbolNull
    assert session.evaluate('MemberQ[$Packages, "DiscreteMath`RSolve`"]') is SymbolTrue
    assert (
        session.evaluate(
            "!FreeQ[DownValues[DiscreteMath`RSolve`Private`iSeriesTerm], HypergeometricPFQ]"
        )
        is SymbolTrue
    )
