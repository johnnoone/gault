from __future__ import annotations

from gault.sorting import normalize_token


def test_normalize_token_with_falsy_input(context):
    result = list(normalize_token(None, context=context))
    assert result == []
