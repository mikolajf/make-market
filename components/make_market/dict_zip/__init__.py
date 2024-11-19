from collections.abc import MutableMapping
from itertools import chain
from typing import TypeVar

KT = TypeVar("KT")  # dict keys
VT = TypeVar("VT")  # dict values
DT = TypeVar("DT")  # dict default


def dict_zip(
    *dicts: MutableMapping[KT, VT], default: DT = None
) -> dict[KT, tuple[VT | DT, ...]]:
    """
    Zips multiple dictionaries into a single dictionary, combining values from each dictionary into tuples.

    Args:
        *dicts (MutableMapping[KT, VT]): Variable number of dictionaries to be zipped.
        default (DT, optional): Default value to use if a key is missing in any of the dictionaries. Defaults to None.

    Returns:
        dict[KT, tuple[VT | DT, ...]]: A dictionary where each key is present in at least one of the input dictionaries,
        and the value is a tuple containing values from each dictionary (or the default value if the key is missing).

    """
    output_dict = {}

    # iterating over all available keys (present in at least one dict)
    for key in set(chain(*dicts)):
        # getting value given key from each dictionary,
        # if missing, we use to "default" argument, e.g. None
        output_dict[key] = tuple(d.get(key, default) for d in dicts)

    return output_dict
