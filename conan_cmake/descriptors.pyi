import typing as t
import typing_extensions as tex

R = t.TypeVar('R', covariant=True)
T = t.TypeVar('T')
U = t.TypeVar('U')
O = t.TypeVar('O', contravariant=True)


class Bindable(t.Generic[O, R], tex.Protocol):
    """A protocol for callables.

    The default protocol, :class:`t.Callable`, is missing the :func:`__get__`
    method.
    """

    __doc__: t.Optional[str]

    def __get__(self, obj: O, typ: t.Type[O]) -> t.Callable[..., R]:
        ...


class Descriptor(t.Generic[O, T], tex.Protocol):
    """The type of a descriptor."""

    @t.overload
    def __get__(self, obj: None, typ: t.Type[O] = None) -> Descriptor[O, T]:
        ...

    @t.overload
    def __get__(self, obj: O, typ: t.Type[O] = None) -> T:
        ...

    def __set__(self, obj: O, value: T) -> None:
        ...

    def __delete__(self, obj: O) -> None:
        ...


class MappedDescriptor(Descriptor[O, T]):
    ...


def fmap(
    function: t.Callable[[U], T],
    descriptor: Descriptor[O, U],
) -> Descriptor[O, T]:
    ...


class CachedPropertyDescriptor(Descriptor[O, T]):

    def __init__(self, fget: t.Callable[[O], T]):
        ...


cached_property = CachedPropertyDescriptor

ClassGetter = t.Callable[[t.Type[O]], T]


class ClassPropertyDescriptor(Descriptor[O, T]):

    def __init__(self, fget: ClassGetter):
        ...


def classproperty(fget: ClassGetter) -> ClassPropertyDescriptor:
    ...


class CachedClassPropertyDescriptor(Descriptor[O, T]):

    def __init__(self, fget: ClassGetter):
        ...


def cached_classproperty(fget: ClassGetter) -> CachedClassPropertyDescriptor:
    ...
