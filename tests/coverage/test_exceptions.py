from __future__ import annotations

from gault.exceptions import PipelineError, Unprocessable
from gault.models import Schema


def test_unprocessable_message():
    class Foo(Schema, collection="test_unprocessable"):
        pass

    err = Unprocessable(model=Foo, reason="invalid data")
    assert str(err) == "Unprocessable Foo ; invalid data"


def test_pipeline_error_message():
    err = PipelineError.__new__(PipelineError)
    err.pipeline = None  # type: ignore[assignment]
    err.reason = "bad stage"
    err.__post_init__()
    assert str(err) == "Pipeline error ; bad stage"
