from gault import Attribute, Model
from gault.accumulators import (
    AddToSet,
    Avg,
    Bottom,
    BottomN,
    Count,
    First,
    FirstN,
    Last,
    LastN,
    Max,
    MaxN,
    Median,
    MergeObjects,
    Min,
    MinN,
    Percentile,
    Push,
    StdDevPop,
    StdDevSamp,
    Sum,
    Top,
    TopN,
)
from gault.predicates import Field


class MyModel(Model, collection="my-coll"):
    id: Attribute[int]


def test_add_to_set(subtests, context):
    with subtests.test():
        acc = AddToSet("$var")
        assert acc.compile(context=context) == {"$addToSet": "$var"}

    with subtests.test():
        acc = AddToSet(Field("foo.bar"))
        assert acc.compile(context=context) == {"$addToSet": "$foo.bar"}

    with subtests.test():
        acc = AddToSet(MyModel.id)
        assert acc.compile(context=context) == {"$addToSet": "$id"}


def test_avg(subtests, context):
    with subtests.test():
        acc = Avg("$var")
        assert acc.compile(context=context) == {"$avg": "$var"}

    with subtests.test():
        acc = Avg(Field("foo.bar"))
        assert acc.compile(context=context) == {"$avg": "$foo.bar"}

    with subtests.test():
        acc = Avg(MyModel.id)
        assert acc.compile(context=context) == {"$avg": "$id"}


def test_bottom(subtests, context):
    with subtests.test():
        acc = Bottom(sort_by={"score": 1}, output="$var")
        assert acc.compile(context=context) == {
            "$bottom": {"sortBy": {"score": 1}, "output": "$var"}
        }

    with subtests.test():
        acc = Bottom(sort_by={"score": 1}, output=Field("foo.bar"))
        assert acc.compile(context=context) == {
            "$bottom": {"sortBy": {"score": 1}, "output": "$foo.bar"}
        }

    with subtests.test():
        acc = Bottom(sort_by={"score": 1}, output=MyModel.id)
        assert acc.compile(context=context) == {
            "$bottom": {"sortBy": {"score": 1}, "output": "$id"}
        }


def test_bottom_n(subtests, context):
    with subtests.test():
        acc = BottomN(n=3, sort_by={"score": 1}, output="$var")
        assert acc.compile(context=context) == {
            "$bottomN": {"n": 3, "sortBy": {"score": 1}, "output": "$var"}
        }

    with subtests.test():
        acc = BottomN(n=5, sort_by={"score": 1}, output=Field("foo.bar"))
        assert acc.compile(context=context) == {
            "$bottomN": {"n": 5, "sortBy": {"score": 1}, "output": "$foo.bar"}
        }

    with subtests.test():
        acc = BottomN(n=10, sort_by={"score": 1}, output=MyModel.id)
        assert acc.compile(context=context) == {
            "$bottomN": {"n": 10, "sortBy": {"score": 1}, "output": "$id"}
        }


def test_count(subtests, context):
    with subtests.test():
        acc = Count()
        assert acc.compile(context=context) == {"$count": {}}


def test_first(subtests, context):
    with subtests.test():
        acc = First("$var")
        assert acc.compile(context=context) == {"$first": "$var"}

    with subtests.test():
        acc = First(Field("foo.bar"))
        assert acc.compile(context=context) == {"$first": "$foo.bar"}

    with subtests.test():
        acc = First(MyModel.id)
        assert acc.compile(context=context) == {"$first": "$id"}


def test_first_n(subtests, context):
    with subtests.test():
        acc = FirstN(value="$var", n=3)
        assert acc.compile(context=context) == {"$firstN": {"input": "$var", "n": 3}}

    with subtests.test():
        acc = FirstN(value=Field("foo.bar"), n=5)
        assert acc.compile(context=context) == {
            "$firstN": {"input": "$foo.bar", "n": 5}
        }

    with subtests.test():
        acc = FirstN(value=MyModel.id, n=10)
        assert acc.compile(context=context) == {"$firstN": {"input": "$id", "n": 10}}


def test_last(subtests, context):
    with subtests.test():
        acc = Last("$var")
        assert acc.compile(context=context) == {"$last": "$var"}

    with subtests.test():
        acc = Last(Field("foo.bar"))
        assert acc.compile(context=context) == {"$last": "$foo.bar"}

    with subtests.test():
        acc = Last(MyModel.id)
        assert acc.compile(context=context) == {"$last": "$id"}


def test_last_n(subtests, context):
    with subtests.test():
        acc = LastN(value="$var", n=3)
        assert acc.compile(context=context) == {"$lastN": {"input": "$var", "n": 3}}

    with subtests.test():
        acc = LastN(value=Field("foo.bar"), n=5)
        assert acc.compile(context=context) == {"$lastN": {"input": "$foo.bar", "n": 5}}

    with subtests.test():
        acc = LastN(value=MyModel.id, n=10)
        assert acc.compile(context=context) == {"$lastN": {"input": "$id", "n": 10}}


def test_max(subtests, context):
    with subtests.test():
        acc = Max("$var")
        assert acc.compile(context=context) == {"$max": "$var"}

    with subtests.test():
        acc = Max(Field("foo.bar"))
        assert acc.compile(context=context) == {"$max": "$foo.bar"}

    with subtests.test():
        acc = Max(MyModel.id)
        assert acc.compile(context=context) == {"$max": "$id"}


def test_max_n(subtests, context):
    with subtests.test():
        acc = MaxN(value="$var", n=3)
        assert acc.compile(context=context) == {"$maxN": {"input": "$var", "n": 3}}

    with subtests.test():
        acc = MaxN(value=Field("foo.bar"), n=5)
        assert acc.compile(context=context) == {"$maxN": {"input": "$foo.bar", "n": 5}}

    with subtests.test():
        acc = MaxN(value=MyModel.id, n=10)
        assert acc.compile(context=context) == {"$maxN": {"input": "$id", "n": 10}}


def test_median(subtests, context):
    with subtests.test():
        acc = Median("$var")
        assert acc.compile(context=context) == {
            "$median": {"input": "$var", "method": "approximate"}
        }

    with subtests.test():
        acc = Median(Field("foo.bar"))
        assert acc.compile(context=context) == {
            "$median": {"input": "$foo.bar", "method": "approximate"}
        }

    with subtests.test():
        acc = Median(MyModel.id)
        assert acc.compile(context=context) == {
            "$median": {"input": "$id", "method": "approximate"}
        }


def test_merge_objects(subtests, context):
    with subtests.test():
        acc = MergeObjects("$var")
        assert acc.compile(context=context) == {"$mergeObjects": "$var"}

    with subtests.test():
        acc = MergeObjects(Field("foo.bar"))
        assert acc.compile(context=context) == {"$mergeObjects": "$foo.bar"}

    with subtests.test():
        acc = MergeObjects(MyModel.id)
        assert acc.compile(context=context) == {"$mergeObjects": "$id"}


def test_min(subtests, context):
    with subtests.test():
        acc = Min("$var")
        assert acc.compile(context=context) == {"$min": "$var"}

    with subtests.test():
        acc = Min(Field("foo.bar"))
        assert acc.compile(context=context) == {"$min": "$foo.bar"}

    with subtests.test():
        acc = Min(MyModel.id)
        assert acc.compile(context=context) == {"$min": "$id"}


def test_min_n(subtests, context):
    with subtests.test():
        acc = MinN(value="$var", n=3)
        assert acc.compile(context=context) == {"$minN": {"input": "$var", "n": 3}}

    with subtests.test():
        acc = MinN(value=Field("foo.bar"), n=5)
        assert acc.compile(context=context) == {"$minN": {"input": "$foo.bar", "n": 5}}

    with subtests.test():
        acc = MinN(value=MyModel.id, n=10)
        assert acc.compile(context=context) == {"$minN": {"input": "$id", "n": 10}}


def test_percentile(subtests, context):
    with subtests.test():
        acc = Percentile(input="$var", p=[0.5, 0.75, 0.9])
        assert acc.compile(context=context) == {
            "$percentile": {
                "input": "$var",
                "p": [0.5, 0.75, 0.9],
                "method": "approximate",
            }
        }

    with subtests.test():
        acc = Percentile(input=Field("foo.bar"), p=[0.95])
        assert acc.compile(context=context) == {
            "$percentile": {"input": "$foo.bar", "p": [0.95], "method": "approximate"}
        }

    with subtests.test():
        acc = Percentile(input=MyModel.id, p=[0.5])
        assert acc.compile(context=context) == {
            "$percentile": {"input": "$id", "p": [0.5], "method": "approximate"}
        }


def test_push(subtests, context):
    with subtests.test():
        acc = Push("$var")
        assert acc.compile(context=context) == {"$push": "$var"}

    with subtests.test():
        acc = Push(Field("foo.bar"))
        assert acc.compile(context=context) == {"$push": "$foo.bar"}

    with subtests.test():
        acc = Push(MyModel.id)
        assert acc.compile(context=context) == {"$push": "$id"}


def test_std_dev_pop(subtests, context):
    with subtests.test():
        acc = StdDevPop(value="$var", p=None)
        assert acc.compile(context=context) == {"$stdDevPop": "$var"}

    with subtests.test():
        acc = StdDevPop(value=Field("foo.bar"), p=None)
        assert acc.compile(context=context) == {"$stdDevPop": "$foo.bar"}

    with subtests.test():
        acc = StdDevPop(value=MyModel.id, p=None)
        assert acc.compile(context=context) == {"$stdDevPop": "$id"}


def test_std_dev_samp(subtests, context):
    with subtests.test():
        acc = StdDevSamp(value="$var", p=None)
        assert acc.compile(context=context) == {"$stdDevSamp": "$var"}

    with subtests.test():
        acc = StdDevSamp(value=Field("foo.bar"), p=None)
        assert acc.compile(context=context) == {"$stdDevSamp": "$foo.bar"}

    with subtests.test():
        acc = StdDevSamp(value=MyModel.id, p=None)
        assert acc.compile(context=context) == {"$stdDevSamp": "$id"}


def test_sum(subtests, context):
    with subtests.test():
        acc = Sum("$var")
        assert acc.compile(context=context) == {"$sum": "$var"}

    with subtests.test():
        acc = Sum(Field("foo.bar"))
        assert acc.compile(context=context) == {"$sum": "$foo.bar"}

    with subtests.test():
        acc = Sum(MyModel.id)
        assert acc.compile(context=context) == {"$sum": "$id"}


def test_top(subtests, context):
    with subtests.test():
        acc = Top(sort_by={"score": -1}, output="$var")
        assert acc.compile(context=context) == {
            "$top": {"sortBy": {"score": -1}, "output": "$var"}
        }

    with subtests.test():
        acc = Top(sort_by={"score": -1}, output=Field("foo.bar"))
        assert acc.compile(context=context) == {
            "$top": {"sortBy": {"score": -1}, "output": "$foo.bar"}
        }

    with subtests.test():
        acc = Top(sort_by={"score": -1}, output=MyModel.id)
        assert acc.compile(context=context) == {
            "$top": {"sortBy": {"score": -1}, "output": "$id"}
        }


def test_top_n(subtests, context):
    with subtests.test():
        acc = TopN(n=3, sort_by={"score": -1}, output="$var")
        assert acc.compile(context=context) == {
            "$topN": {"n": 3, "sortBy": {"score": -1}, "output": "$var"}
        }

    with subtests.test():
        acc = TopN(n=5, sort_by={"score": -1}, output=Field("foo.bar"))
        assert acc.compile(context=context) == {
            "$topN": {"n": 5, "sortBy": {"score": -1}, "output": "$foo.bar"}
        }

    with subtests.test():
        acc = TopN(n=10, sort_by={"score": -1}, output=MyModel.id)
        assert acc.compile(context=context) == {
            "$topN": {"n": 10, "sortBy": {"score": -1}, "output": "$id"}
        }
