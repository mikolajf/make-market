from make_market.dict_zip import dict_zip


def test_dict_zip_basic():
    dict1 = {"a": 1, "b": 2}
    dict2 = {"a": 3, "c": 4}
    result = dict_zip(dict1, dict2)
    expected = {"a": (1, 3), "b": (2, None), "c": (None, 4)}
    assert result == expected


def test_dict_zip_with_default():
    dict1 = {"a": 1, "b": 2}
    dict2 = {"a": 3, "c": 4}
    result = dict_zip(dict1, dict2, default=0)
    expected = {"a": (1, 3), "b": (2, 0), "c": (0, 4)}
    assert result == expected


def test_dict_zip_empty_dicts():
    dict1 = {}
    dict2 = {}
    result = dict_zip(dict1, dict2)
    expected = {}
    assert result == expected


def test_dict_zip_single_dict():
    dict1 = {"a": 1, "b": 2}
    result = dict_zip(dict1)
    expected = {"a": (1,), "b": (2,)}
    assert result == expected


def test_dict_zip_multiple_dicts():
    dict1 = {"a": 1, "b": 2}
    dict2 = {"a": 3, "c": 4}
    dict3 = {"a": 5, "b": 6, "d": 7}
    result = dict_zip(dict1, dict2, dict3)
    expected = {
        "a": (1, 3, 5),
        "b": (2, None, 6),
        "c": (None, 4, None),
        "d": (None, None, 7),
    }
    assert result == expected


def test_dict_zip_with_none_default():
    dict1 = {"a": 1, "b": 2}
    dict2 = {"a": 3, "c": 4}
    result = dict_zip(dict1, dict2, default=None)
    expected = {"a": (1, 3), "b": (2, None), "c": (None, 4)}
    assert result == expected
