"""Small, generic data structures and algorithms.

We keep them here to declutter other modules.
"""

import functools
import typing as t

_StringLike = t.Union[str, bytes]


def named(name):
    """Change the name of something (via a decorator)."""

    def decorator(obj):
        obj.__name__ = name
        return obj

    return decorator


def one_or_more(value: t.Union[_StringLike, t.Iterable[_StringLike]]
               ) -> t.Iterable[_StringLike]:
    """Return a list of values from one or more values."""
    return (
        [value] if isinstance(value, str) or isinstance(value, bytes) else value
    )


def zero_or_more(value: t.Union[None, _StringLike, t.Iterable[_StringLike]]
                ) -> t.Iterable[_StringLike]:
    """Return a list of values from zero or more values."""
    return [] if value is None else one_or_more(value)


def logging(f):

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        xs = map(str, args)
        ys = (f'{key}={value}' for key, value in kwargs.items())
        print(f'{f.__name__}({", ".join([*xs, *ys])})...')
        try:
            value = f(*args, **kwargs)
        except Exception as cause:
            print(f'! {cause}')
            raise
        print(f'=> {value}')
        return value

    return decorated


class Object:
    """An object that takes keyword attributes in its constructor."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
