from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Any, Callable, Union, Optional
    _K = Optional[Callable[[Any], str]]
    _L = tuple[str, _K]
    _T = Union[str, _L]


def pick(model: 'Any', *args: '_T', **kwargs: '_T') -> 'dict[str, Any]':
    """A function to conviently pick the attributes of any object, where nested
    Ex: pick(x, ('weight_class', WeightClass.__str__),
                          ('division', AgeDivision.__str__), name='board_definition__name')
    """
    def gen(key: '_T') -> 'tuple[str, _T]':
        if isinstance(key, str):
            return (key, key)
        return (key[0], (key[0], key[1]))

    genned = [gen(a) for a in args]
    (keys := kwargs.copy()).update(genned)

    def get_val(key: '_T'):
        if isinstance(key, tuple):
            lookup = key[0]
            func = key[1]
        else:
            lookup = key
            func = None

        obj = model
        for field in lookup.split('__'):
            obj = getattr(obj, field)

        return func(obj) if callable(func) else obj

    return {k: get_val(v) for k, v in keys.items()}
