import pytest

from strata.compilers import compile_expression
from strata.expressions import Var


@pytest.fixture(name="context")
def get_context():
    return {}


@pytest.fixture(name="var")
def get_var():
    return Var("my_var")


def test_compile(context):
    var = Var("my_var")
    assert var.compile_field(context=context) == "my_var"
    assert var.compile_expression(context=context) == "$$my_var"


def test_sort(context):
    var = Var("my_var")
    assert var.asc() == (var, 1)
    assert var.desc() == (var, -1)
    assert var.by_score("my_name") == (var, {"$meta": "my_name"})


def test_abs(var, context):
    expression = var.abs()
    result = compile_expression(expression, context=context)
    assert result == {"$abs": "$$my_var"}


def test_acos(var, context):
    expression = var.acos()
    result = compile_expression(expression, context=context)
    assert result == {"$acos": "$$my_var"}


def test_acosh(var, context):
    expression = var.acosh()
    result = compile_expression(expression, context=context)
    assert result == {"$acosh": "$$my_var"}


def test_add(var, context):
    expression = var.add(42)
    result = compile_expression(expression, context=context)
    assert result == {"$add": ["$$my_var", 42]}


def test_all_elements_true(var, context):
    expression = var.all_elements_true()
    result = compile_expression(expression, context=context)
    assert result == {"$allElementsTrue": ["$$my_var"]}


def test_any_elements_true(var, context):
    expression = var.any_elements_true()
    result = compile_expression(expression, context=context)
    assert result == {"$anyElementsTrue": ["$$my_var"]}


def test_asin(var, context):
    expression = var.asin()
    result = compile_expression(expression, context=context)
    assert result == {"$asin": "$$my_var"}


def test_asinh(var, context):
    expression = var.asinh()
    result = compile_expression(expression, context=context)
    assert result == {"$asinh": "$$my_var"}


def test_atan(var, context):
    expression = var.atan()
    result = compile_expression(expression, context=context)
    assert result == {"$atan": "$$my_var"}


def test_atan2(var, context):
    expression = var.atan2(42)
    result = compile_expression(expression, context=context)
    assert result == {"$atan2": ["$$my_var", 42]}


def test_atanh(var, context):
    expression = var.atanh()
    result = compile_expression(expression, context=context)
    assert result == {"$atanh": "$$my_var"}


def test_binary_size(var, context):
    expression = var.binary_size()
    result = compile_expression(expression, context=context)
    assert result == {"$binarySize": "$$my_var"}


def test_bit_and(var, context):
    expression = var.bit_and(42)
    result = compile_expression(expression, context=context)
    assert result == {
        "$bitAnd": ["$$my_var", 42],
    }


def test_bit_not(var, context):
    expression = var.bit_not()
    result = compile_expression(expression, context=context)
    assert result == {
        "$bitNot": "$$my_var",
    }


def test_bit_or(var, context):
    expression = var.bit_or(42)
    result = compile_expression(expression, context=context)
    assert result == {
        "$bitOr": ["$$my_var", 42],
    }


def test_bit_xor(var, context):
    expression = var.bit_xor(42)
    result = compile_expression(expression, context=context)
    assert result == {"$bitXor": ["$$my_var", 42]}


def test_bson_size(var, context):
    expression = var.bson_size()
    result = compile_expression(expression, context=context)
    assert result == {
        "$bsonSize": "$$my_var",
    }


def test_ceil(var, context):
    expression = var.ceil()
    result = compile_expression(expression, context=context)
    assert result == {"$ceil": "$$my_var"}


def test_cmp(var, context):
    expression = var.cmp("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$cmp": ["$$my_var", "$other"],
    }


def test_concat(var, context):
    expression = var.concat("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$concat": ["$$my_var", "$other"],
    }


def test_cos(var, context):
    expression = var.cos()
    result = compile_expression(expression, context=context)
    assert result == {"$cos": "$$my_var"}


def test_cosh(var, context):
    expression = var.cosh()
    result = compile_expression(expression, context=context)
    assert result == {"$cosh": "$$my_var"}


def test_date_add(var, context):
    expression = var.date_add(unit="seconds", amount=3)
    result = compile_expression(expression, context=context)
    assert result == {
        "$dateAdd": {
            "amount": 3,
            "startDate": "$$my_var",
            "unit": "seconds",
        }
    }


def test_date_diff(var, context):
    expression = var.date_diff("$other", unit="seconds")
    result = compile_expression(expression, context=context)
    assert result == {
        "$dateDiff": {
            "endDate": "$other",
            "startDate": "$$my_var",
            "unit": "seconds",
        }
    }


def test_date_from_string(var, context):
    expression = var.date_from_string()
    result = compile_expression(expression, context=context)
    assert result == {
        "$dateFromString": {
            "dateString": "$$my_var",
        }
    }


def test_date_subtract(var, context):
    expression = var.date_subtract(unit="seconds", amount=3)
    result = compile_expression(expression, context=context)
    assert result == {
        "$dateSubtract": {
            "amount": 3,
            "startDate": "$$my_var",
            "unit": "seconds",
        }
    }


def test_date_to_parts(var, context):
    expression = var.date_to_parts()
    result = compile_expression(expression, context=context)
    assert result == {
        "$dateToParts": {
            "date": "$$my_var",
        }
    }


def test_date_to_string(var, context):
    expression = var.date_to_string()
    result = compile_expression(expression, context=context)
    assert result == {
        "$dateToString": {
            "date": "$$my_var",
        }
    }


def test_date_trunc(var, context):
    expression = var.date_trunc(unit="second")
    result = compile_expression(expression, context=context)
    assert result == {
        "$dateTrunc": {
            "date": "$$my_var",
            "unit": "second",
        }
    }


def test_day_of_month(var, context):
    expression = var.day_of_month()
    result = compile_expression(expression, context=context)
    assert result == {"$dayOfMonth": {"date": "$$my_var"}}


def test_day_of_week(var, context):
    expression = var.day_of_week()
    result = compile_expression(expression, context=context)
    assert result == {
        "$dayOfWeek": {
            "date": "$$my_var",
        }
    }


def test_day_of_year(var, context):
    expression = var.day_of_year()
    result = compile_expression(expression, context=context)
    assert result == {
        "$dayOfYear": {
            "date": "$$my_var",
        },
    }


def test_degrees_to_radians(var, context):
    expression = var.degrees_to_radians()
    result = compile_expression(expression, context=context)
    assert result == {
        "$degreesToRadians": "$$my_var",
    }


def test_exp(var, context):
    expression = var.exp()
    result = compile_expression(expression, context=context)
    assert result == {
        "$exp": "$$my_var",
    }


def test_filter(var, context):
    expression = var.filter("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$filter": {
            "cond": "$other",
            "input": "$$my_var",
        }
    }


def test_floor(var, context):
    expression = var.floor()
    result = compile_expression(expression, context=context)
    assert result == {
        "$floor": "$$my_var",
    }


def test_get_field(var, context):
    expression = var.get_field("subfield")
    result = compile_expression(expression, context=context)
    assert result == {
        "$getField": {
            "field": "subfield",
            "input": "$$my_var",
        }
    }


def test_gt(var, context):
    expression = var.gt(42)
    result = compile_expression(expression, context=context)
    assert result == {
        "$gt": ["$$my_var", 42],
    }


def test_gte(var, context):
    expression = var.gte(42)
    result = compile_expression(expression, context=context)
    assert result == {
        "$gte": ["$$my_var", 42],
    }


def test_hour(var, context):
    expression = var.hour()
    result = compile_expression(expression, context=context)
    assert result == {
        "$hour": {
            "date": "$$my_var",
        }
    }


def test_in(var, context):
    expression = var.in_("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$ifNull": ["$$my_var", "$other"],
    }


def test_index_of_array(var, context):
    expression = var.index_of_array("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$indexOfArray": ["$$my_var", "$other"],
    }


def test_index_of_bytes(var, context):
    expression = var.index_of_bytes("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$indexOfBytes": ["$$my_var", "$other"],
    }


def test_index_of_cp(var, context):
    expression = var.index_of_cp("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$indexOfCP": ["$$my_var", "$other"],
    }


def test_is_array(var, context):
    expression = var.is_array()
    result = compile_expression(expression, context=context)
    assert result == {
        "$isArray": ["$$my_var"],
    }


def test_is_number(var, context):
    expression = var.is_number()
    result = compile_expression(expression, context=context)
    assert result == {
        "$isNumber": "$$my_var",
    }


def test_iso_day_of_week(var, context):
    expression = var.iso_day_of_week()
    result = compile_expression(expression, context=context)
    assert result == {
        "$isoDayOfWeek": {
            "date": "$$my_var",
        },
    }


def test_iso_week_year(var, context):
    expression = var.iso_week_year()
    result = compile_expression(expression, context=context)
    assert result == {
        "$isoWeekYear": {
            "date": "$$my_var",
        },
    }


def test_ln(var, context):
    expression = var.ln()
    result = compile_expression(expression, context=context)
    assert result == {
        "$ln": "$$my_var",
    }


def test_log(var, context):
    expression = var.log(10)
    result = compile_expression(expression, context=context)
    assert result == {
        "$log": ["$$my_var", 10],
    }


def test_log10(var, context):
    expression = var.log10()
    result = compile_expression(expression, context=context)
    assert result == {
        "$log10": "$$my_var",
    }


def test_ltrim(var, context):
    expression = var.ltrim(chars="xyz")
    result = compile_expression(expression, context=context)
    assert result == {
        "$ltrim": {
            "chars": "xyz",
            "input": "$$my_var",
        }
    }


def test_trim(var, context):
    expression = var.trim(chars="xyz")
    result = compile_expression(expression, context=context)
    assert result == {
        "$trim": {
            "chars": "xyz",
            "input": "$$my_var",
        }
    }


def test_rtrim(var, context):
    expression = var.rtrim(chars="xyz")
    result = compile_expression(expression, context=context)
    assert result == {
        "$rtrim": {
            "chars": "xyz",
            "input": "$$my_var",
        }
    }


def test_lt(var, context):
    expression = var.lt(42)
    result = compile_expression(expression, context=context)
    assert result == {
        "$lt": ["$$my_var", 42],
    }


def test_lte(var, context):
    expression = var.lte(42)
    result = compile_expression(expression, context=context)
    assert result == {
        "$lte": ["$$my_var", 42],
    }


def test_map(var, context):
    expression = var.map("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$map": {
            "in": "$other",
            "input": "$$my_var",
        }
    }


def test_max_n(var, context):
    expression = var.max_n(42)
    result = compile_expression(expression, context=context)
    assert result == {
        "$maxN": {
            "input": "$$my_var",
            "n": 42,
        },
    }


def test_min_n(var, context):
    expression = var.min_n(42)
    result = compile_expression(expression, context=context)
    assert result == {
        "$minN": {
            "input": "$$my_var",
            "n": 42,
        },
    }


def test_millisecond(var, context):
    expression = var.millisecond()
    result = compile_expression(expression, context=context)
    assert result == {
        "$millisecond": {
            "date": "$$my_var",
        }
    }


def test_minute(var, context):
    expression = var.minute()
    result = compile_expression(expression, context=context)
    assert result == {
        "$minute": {
            "date": "$$my_var",
        }
    }


def test_month(var, context):
    expression = var.month()
    result = compile_expression(expression, context=context)
    assert result == {
        "$month": {
            "date": "$$my_var",
        }
    }


def test_year(var, context):
    expression = var.year()
    result = compile_expression(expression, context=context)
    assert result == {
        "$year": {
            "date": "$$my_var",
        }
    }


def test_mod(var, context):
    expression = var.mod(42)
    result = compile_expression(expression, context=context)
    assert result == {
        "$mod": ["$$my_var", 42],
    }


def test_multiply(var, context):
    expression = var.multiply(42)
    result = compile_expression(expression, context=context)
    assert result == {
        "$multiply": ["$$my_var", 42],
    }


def test_ne(var, context):
    expression = var.ne("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$ne": ["$$my_var", "$other"],
    }


def test_not(var, context):
    expression = var.not_()
    result = compile_expression(expression, context=context)
    assert result == {
        "$not": ["$$my_var"],
    }


def test_object_to_array(var, context):
    expression = var.object_to_array()
    result = compile_expression(expression, context=context)
    assert result == {
        "$objectToArray": "$$my_var",
    }


def test_pow(var, context):
    expression = var.pow(42)
    result = compile_expression(expression, context=context)
    assert result == {
        "$pow": ["$$my_var", 42],
    }


def test_radians_to_degrees(var, context):
    expression = var.radians_to_degrees()
    result = compile_expression(expression, context=context)
    assert result == {
        "$radiansToDegrees": "$$my_var",
    }


def test_reduce(var, context):
    expression = var.reduce("$other", initial_value="$initial")
    result = compile_expression(expression, context=context)
    assert result == {
        "$reduce": {
            "in": "$other",
            "initialValue": "$initial",
            "input": "$$my_var",
        }
    }


def test_regex_find(var, context):
    expression = var.regex_find("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$regexFind": {
            "input": "$$my_var",
            "regex": "$other",
        }
    }


def test_regex_find_all(var, context):
    expression = var.regex_find_all("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$regexFindAll": {
            "input": "$$my_var",
            "regex": "$other",
        }
    }


def test_regex_match(var, context):
    expression = var.regex_match("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$regexMatch": {
            "input": "$$my_var",
            "regex": "$other",
        }
    }


def test_replace_one(var, context):
    expression = var.replace_one("$other", replacement="$replacement")
    result = compile_expression(expression, context=context)
    assert result == {
        "$replaceOne": {
            "find": "$other",
            "input": "$$my_var",
            "replacement": "$replacement",
        }
    }


def test_replace_all(var, context):
    expression = var.replace_all("$other", replacement="$replacement")
    result = compile_expression(expression, context=context)
    assert result == {
        "$replaceAll": {
            "find": "$other",
            "input": "$$my_var",
            "replacement": "$replacement",
        }
    }


def test_reverse_array(var, context):
    expression = var.reverse_array()
    result = compile_expression(expression, context=context)
    assert result == {
        "$reverseArray": "$$my_var",
    }


def test_round(var, context):
    expression = var.round(42)
    result = compile_expression(expression, context=context)
    assert result == {
        "$round": [
            "$$my_var",
            42,
        ]
    }


def test_sample_rate(var, context):
    expression = var.sample_rate()
    result = compile_expression(expression, context=context)
    assert result == {
        "$sampleRate": "$$my_var",
    }


def test_second(var, context):
    expression = var.second()
    result = compile_expression(expression, context=context)
    assert result == {
        "$second": {
            "date": "$$my_var",
        },
    }


def test_set_difference(var, context):
    expression = var.set_difference("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$setDifference": ["$$my_var", "$other"],
    }


def test_set_equals(var, context):
    expression = var.set_equals("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$setEquals": ["$$my_var", "$other"],
    }


def test_set_intersection(var, context):
    expression = var.set_intersection("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$setIntersection": ["$$my_var", "$other"],
    }


def test_set_is_subset(var, context):
    expression = var.set_is_subset("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$setIsSubset": ["$$my_var", "$other"],
    }


def test_set_union(var, context):
    expression = var.set_union("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$setUnion": ["$$my_var", "$other"],
    }


def test_set_field(var, context):
    expression = var.set_field(field="$field", value="$value")
    result = compile_expression(expression, context=context)
    assert result == {
        "$setField": {
            "field": "$field",
            "input": "$$my_var",
            "value": "$value",
        }
    }


def test_sigmoid(var, context):
    expression = var.sigmoid()
    result = compile_expression(expression, context=context)
    assert result == {
        "$sigmoid": {
            "input": "$$my_var",
        }
    }


def test_size(var, context):
    expression = var.size()
    result = compile_expression(expression, context=context)
    assert result == {
        "$size": "$$my_var",
    }


def test_sin(var, context):
    expression = var.sin()
    result = compile_expression(expression, context=context)
    assert result == {
        "$sin": "$$my_var",
    }


def test_h(var, context):
    expression = var.sinh()
    result = compile_expression(expression, context=context)
    assert result == {
        "$sinh": "$$my_var",
    }


def test_tan(var, context):
    expression = var.tan()
    result = compile_expression(expression, context=context)
    assert result == {
        "$tan": "$$my_var",
    }


def test_tanh(var, context):
    expression = var.tanh()
    result = compile_expression(expression, context=context)
    assert result == {
        "$tanh": "$$my_var",
    }


def test_sort_array(var, context):
    expression = var.sort_array("-name")
    result = compile_expression(expression, context=context)
    assert result == {
        "$sortArray": {
            "input": "$$my_var",
            "sortBy": {"name": -1},
        }
    }


def test_split(var, context):
    expression = var.split("delim")
    result = compile_expression(expression, context=context)
    assert result == {
        "$split": ["$$my_var", "delim"],
    }


def test_sqrt(var, context):
    expression = var.sqrt()
    result = compile_expression(expression, context=context)
    assert result == {
        "$sqrt": "$$my_var",
    }


def test_str_case_cmp(var, context):
    expression = var.str_case_cmp("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$strcasecmp": ["$$my_var", "$other"],
    }


def test_str_len_bytes(var, context):
    expression = var.str_len_bytes()
    result = compile_expression(expression, context=context)
    assert result == {
        "$strLenBytes": "$$my_var",
    }


def test_str_len_cp(var, context):
    expression = var.str_len_cp()
    result = compile_expression(expression, context=context)
    assert result == {
        "$strLenCP": "$$my_var",
    }


def test_sub_str_bytes(var, context):
    expression = var.sub_str_bytes(0, 10)
    result = compile_expression(expression, context=context)
    assert result == {
        "$substrBytes": ["$$my_var", 0, 10],
    }


def test_to_bool(var, context):
    expression = var.to_bool()
    result = compile_expression(expression, context=context)
    assert result == {
        "$toBool": "$$my_var",
    }


def test_to_date(var, context):
    expression = var.to_date()
    result = compile_expression(expression, context=context)
    assert result == {
        "$toDate": "$$my_var",
    }


def test_to_decimal(var, context):
    expression = var.to_decimal()
    result = compile_expression(expression, context=context)
    assert result == {
        "$toDecimal": "$$my_var",
    }


def test_to_double(var, context):
    expression = var.to_double()
    result = compile_expression(expression, context=context)
    assert result == {
        "$toDouble": "$$my_var",
    }


def test_to_hashed_index_key(var, context):
    expression = var.to_hashed_index_key()
    result = compile_expression(expression, context=context)
    assert result == {
        "$toHashedIndexKey": "$$my_var",
    }


def test_to_int(var, context):
    expression = var.to_int()
    result = compile_expression(expression, context=context)
    assert result == {
        "$toInt": "$$my_var",
    }


def test_to_long(var, context):
    expression = var.to_long()
    result = compile_expression(expression, context=context)
    assert result == {
        "$toLong": "$$my_var",
    }


def test_to_object_id(var, context):
    expression = var.to_object_id()
    result = compile_expression(expression, context=context)
    assert result == {
        "$toObjectId": "$$my_var",
    }


def test_to_string(var, context):
    expression = var.to_string()
    result = compile_expression(expression, context=context)
    assert result == {
        "$toString": "$$my_var",
    }


def test_to_lower(var, context):
    expression = var.to_lower()
    result = compile_expression(expression, context=context)
    assert result == {
        "$toLower": "$$my_var",
    }


def test_to_upper(var, context):
    expression = var.to_upper()
    result = compile_expression(expression, context=context)
    assert result == {
        "$toUpper": "$$my_var",
    }


def test_to_uuid(var, context):
    expression = var.to_uuid()
    result = compile_expression(expression, context=context)
    assert result == {
        "$toUUID": "$$my_var",
    }


def test_ts_increment(var, context):
    expression = var.ts_increment()
    result = compile_expression(expression, context=context)
    assert result == {
        "$tsIncrement": "$$my_var",
    }


def test_ts_second(var, context):
    expression = var.ts_second()
    result = compile_expression(expression, context=context)
    assert result == {
        "$tsSecond": "$$my_var",
    }


def test_trunc(var, context):
    expression = var.trunc(42)
    result = compile_expression(expression, context=context)
    assert result == {
        "$trunc": ["$$my_var", 42],
    }


def test_type(var, context):
    expression = var.type()
    result = compile_expression(expression, context=context)
    assert result == {
        "$type": "$$my_var",
    }


def test_type(var, context):
    expression = var.type()
    result = compile_expression(expression, context=context)
    assert result == {
        "$type": "$$my_var",
    }


def test_unset_field(var, context):
    expression = var.unset_field("my_field")
    result = compile_expression(expression, context=context)
    assert result == {
        "$unsetField": {
            "field": "my_field",
            "input": "$$my_var",
        }
    }


def test_zip(var, context):
    expression = var.zip("$other")
    result = compile_expression(expression, context=context)
    assert result == {
        "$zip": {
            "inputs": ["$$my_var", "$other"],
        }
    }


def test_week(var, context):
    expression = var.week()
    result = compile_expression(expression, context=context)
    assert result == {
        "$week": {
            "date": "$$my_var",
        }
    }
