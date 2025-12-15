from strata import Field, Model, Path
from strata.accumulators import (
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


class MyModel(Model, collection="my-coll"):
    id: Field[int]


def test_add_to_set(subtests):
    with subtests.test():
        acc = AddToSet("$var")
        assert acc.compile() == {"$addToSet": "$var"}

    with subtests.test():
        acc = AddToSet(Path("foo.bar"))
        assert acc.compile() == {"$addToSet": "$foo.bar"}

    with subtests.test():
        acc = AddToSet(MyModel.id)
        assert acc.compile() == {"$addToSet": "$id"}


def test_avg(subtests):
    with subtests.test():
        acc = Avg("$var")
        assert acc.compile() == {"$avg": "$var"}

    with subtests.test():
        acc = Avg(Path("foo.bar"))
        assert acc.compile() == {"$avg": "$foo.bar"}

    with subtests.test():
        acc = Avg(MyModel.id)
        assert acc.compile() == {"$avg": "$id"}


def test_bottom(subtests):
    with subtests.test():
        acc = Bottom(sort_by={"score": 1}, output="$var")
        assert acc.compile() == {"$bottom": {"sortBy": {"score": 1}, "output": "$var"}}

    with subtests.test():
        acc = Bottom(sort_by={"score": 1}, output=Path("foo.bar"))
        assert acc.compile() == {
            "$bottom": {"sortBy": {"score": 1}, "output": "$foo.bar"}
        }

    with subtests.test():
        acc = Bottom(sort_by={"score": 1}, output=MyModel.id)
        assert acc.compile() == {"$bottom": {"sortBy": {"score": 1}, "output": "$id"}}


def test_bottom_n(subtests):
    with subtests.test():
        acc = BottomN(n=3, sort_by={"score": 1}, output="$var")
        assert acc.compile() == {
            "$bottomN": {"n": 3, "sortBy": {"score": 1}, "output": "$var"}
        }

    with subtests.test():
        acc = BottomN(n=5, sort_by={"score": 1}, output=Path("foo.bar"))
        assert acc.compile() == {
            "$bottomN": {"n": 5, "sortBy": {"score": 1}, "output": "$foo.bar"}
        }

    with subtests.test():
        acc = BottomN(n=10, sort_by={"score": 1}, output=MyModel.id)
        assert acc.compile() == {
            "$bottomN": {"n": 10, "sortBy": {"score": 1}, "output": "$id"}
        }


def test_count(subtests):
    with subtests.test():
        acc = Count()
        assert acc.compile() == {"$count": {}}


def test_first(subtests):
    with subtests.test():
        acc = First("$var")
        assert acc.compile() == {"$first": "$var"}

    with subtests.test():
        acc = First(Path("foo.bar"))
        assert acc.compile() == {"$first": "$foo.bar"}

    with subtests.test():
        acc = First(MyModel.id)
        assert acc.compile() == {"$first": "$id"}


def test_first_n(subtests):
    with subtests.test():
        acc = FirstN(value="$var", n=3)
        assert acc.compile() == {"$firstN": {"input": "$var", "n": 3}}

    with subtests.test():
        acc = FirstN(value=Path("foo.bar"), n=5)
        assert acc.compile() == {"$firstN": {"input": "$foo.bar", "n": 5}}

    with subtests.test():
        acc = FirstN(value=MyModel.id, n=10)
        assert acc.compile() == {"$firstN": {"input": "$id", "n": 10}}


def test_last(subtests):
    with subtests.test():
        acc = Last("$var")
        assert acc.compile() == {"$last": "$var"}

    with subtests.test():
        acc = Last(Path("foo.bar"))
        assert acc.compile() == {"$last": "$foo.bar"}

    with subtests.test():
        acc = Last(MyModel.id)
        assert acc.compile() == {"$last": "$id"}


def test_last_n(subtests):
    with subtests.test():
        acc = LastN(value="$var", n=3)
        assert acc.compile() == {"$lastN": {"input": "$var", "n": 3}}

    with subtests.test():
        acc = LastN(value=Path("foo.bar"), n=5)
        assert acc.compile() == {"$lastN": {"input": "$foo.bar", "n": 5}}

    with subtests.test():
        acc = LastN(value=MyModel.id, n=10)
        assert acc.compile() == {"$lastN": {"input": "$id", "n": 10}}


def test_max(subtests):
    with subtests.test():
        acc = Max("$var")
        assert acc.compile() == {"$max": "$var"}

    with subtests.test():
        acc = Max(Path("foo.bar"))
        assert acc.compile() == {"$max": "$foo.bar"}

    with subtests.test():
        acc = Max(MyModel.id)
        assert acc.compile() == {"$max": "$id"}


def test_max_n(subtests):
    with subtests.test():
        acc = MaxN(value="$var", n=3)
        assert acc.compile() == {"$maxN": {"input": "$var", "n": 3}}

    with subtests.test():
        acc = MaxN(value=Path("foo.bar"), n=5)
        assert acc.compile() == {"$maxN": {"input": "$foo.bar", "n": 5}}

    with subtests.test():
        acc = MaxN(value=MyModel.id, n=10)
        assert acc.compile() == {"$maxN": {"input": "$id", "n": 10}}


def test_median(subtests):
    with subtests.test():
        acc = Median("$var")
        assert acc.compile() == {"$median": {"input": "$var", "method": "approximate"}}

    with subtests.test():
        acc = Median(Path("foo.bar"))
        assert acc.compile() == {
            "$median": {"input": "$foo.bar", "method": "approximate"}
        }

    with subtests.test():
        acc = Median(MyModel.id)
        assert acc.compile() == {"$median": {"input": "$id", "method": "approximate"}}


def test_merge_objects(subtests):
    with subtests.test():
        acc = MergeObjects("$var")
        assert acc.compile() == {"$mergeObjects": "$var"}

    with subtests.test():
        acc = MergeObjects(Path("foo.bar"))
        assert acc.compile() == {"$mergeObjects": "$foo.bar"}

    with subtests.test():
        acc = MergeObjects(MyModel.id)
        assert acc.compile() == {"$mergeObjects": "$id"}


def test_min(subtests):
    with subtests.test():
        acc = Min("$var")
        assert acc.compile() == {"$min": "$var"}

    with subtests.test():
        acc = Min(Path("foo.bar"))
        assert acc.compile() == {"$min": "$foo.bar"}

    with subtests.test():
        acc = Min(MyModel.id)
        assert acc.compile() == {"$min": "$id"}


def test_min_n(subtests):
    with subtests.test():
        acc = MinN(value="$var", n=3)
        assert acc.compile() == {"$minN": {"input": "$var", "n": 3}}

    with subtests.test():
        acc = MinN(value=Path("foo.bar"), n=5)
        assert acc.compile() == {"$minN": {"input": "$foo.bar", "n": 5}}

    with subtests.test():
        acc = MinN(value=MyModel.id, n=10)
        assert acc.compile() == {"$minN": {"input": "$id", "n": 10}}


def test_percentile(subtests):
    with subtests.test():
        acc = Percentile(input="$var", p=[0.5, 0.75, 0.9])
        assert acc.compile() == {
            "$percentile": {
                "input": "$var",
                "p": [0.5, 0.75, 0.9],
                "method": "approximate",
            }
        }

    with subtests.test():
        acc = Percentile(input=Path("foo.bar"), p=[0.95])
        assert acc.compile() == {
            "$percentile": {"input": "$foo.bar", "p": [0.95], "method": "approximate"}
        }

    with subtests.test():
        acc = Percentile(input=MyModel.id, p=[0.5])
        assert acc.compile() == {
            "$percentile": {"input": "$id", "p": [0.5], "method": "approximate"}
        }


def test_push(subtests):
    with subtests.test():
        acc = Push("$var")
        assert acc.compile() == {"$push": "$var"}

    with subtests.test():
        acc = Push(Path("foo.bar"))
        assert acc.compile() == {"$push": "$foo.bar"}

    with subtests.test():
        acc = Push(MyModel.id)
        assert acc.compile() == {"$push": "$id"}


def test_std_dev_pop(subtests):
    with subtests.test():
        acc = StdDevPop(value="$var", p=None)
        assert acc.compile() == {"$stdDevPop": "$var"}

    with subtests.test():
        acc = StdDevPop(value=Path("foo.bar"), p=None)
        assert acc.compile() == {"$stdDevPop": "$foo.bar"}

    with subtests.test():
        acc = StdDevPop(value=MyModel.id, p=None)
        assert acc.compile() == {"$stdDevPop": "$id"}


def test_std_dev_samp(subtests):
    with subtests.test():
        acc = StdDevSamp(value="$var", p=None)
        assert acc.compile() == {"$stdDevSamp": "$var"}

    with subtests.test():
        acc = StdDevSamp(value=Path("foo.bar"), p=None)
        assert acc.compile() == {"$stdDevSamp": "$foo.bar"}

    with subtests.test():
        acc = StdDevSamp(value=MyModel.id, p=None)
        assert acc.compile() == {"$stdDevSamp": "$id"}


def test_sum(subtests):
    with subtests.test():
        acc = Sum("$var")
        assert acc.compile() == {"$sum": "$var"}

    with subtests.test():
        acc = Sum(Path("foo.bar"))
        assert acc.compile() == {"$sum": "$foo.bar"}

    with subtests.test():
        acc = Sum(MyModel.id)
        assert acc.compile() == {"$sum": "$id"}


def test_top(subtests):
    with subtests.test():
        acc = Top(sort_by={"score": -1}, output="$var")
        assert acc.compile() == {"$top": {"sortBy": {"score": -1}, "output": "$var"}}

    with subtests.test():
        acc = Top(sort_by={"score": -1}, output=Path("foo.bar"))
        assert acc.compile() == {
            "$top": {"sortBy": {"score": -1}, "output": "$foo.bar"}
        }

    with subtests.test():
        acc = Top(sort_by={"score": -1}, output=MyModel.id)
        assert acc.compile() == {"$top": {"sortBy": {"score": -1}, "output": "$id"}}


def test_top_n(subtests):
    with subtests.test():
        acc = TopN(n=3, sort_by={"score": -1}, output="$var")
        assert acc.compile() == {
            "$topN": {"n": 3, "sortBy": {"score": -1}, "output": "$var"}
        }

    with subtests.test():
        acc = TopN(n=5, sort_by={"score": -1}, output=Path("foo.bar"))
        assert acc.compile() == {
            "$topN": {"n": 5, "sortBy": {"score": -1}, "output": "$foo.bar"}
        }

    with subtests.test():
        acc = TopN(n=10, sort_by={"score": -1}, output=MyModel.id)
        assert acc.compile() == {
            "$topN": {"n": 10, "sortBy": {"score": -1}, "output": "$id"}
        }
