import pytest

from strata.expressions import SortArray


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SortArray("$input", "sorter")
        result = op.compile_expression(context=context)
        assert result == {"$sortArray": {"input": "$input", "sortBy": {"sorter": 1}}}
