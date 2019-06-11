"""Types and class property descriptors."""

import typing as t

import typing_extensions as tex

R = t.TypeVar('R', covariant=True)
T = t.TypeVar('T')


class Bindable(t.Generic[R], tex.Protocol):
    """A protocol for callables.

    The default protocol, :class:`t.Callable`, is missing the :func:`__get__`
    method.
    """

    def __get__(self, obj: object, typ: type) -> t.Callable[..., R]:
        ...


class Descriptor(t.Generic[T], tex.Protocol):
    """The type of a descriptor."""

    def __get__(self, obj: object, typ: type = None) -> T:
        ...

    def __set__(self, obj: object, value: T) -> None:
        ...

    def __delete__(self, obj: object) -> None:
        ...


ClassGetter = Bindable[T]  # pylint: disable=invalid-name


class ClassPropertyDescriptor(Descriptor[T]):
    """A descriptor for a class attribute.

    Compare with :func:`property`, which is for instance attributes.
    """

    def __init__(self, fget: ClassGetter):
        self.fget = fget

    def __get__(self, obj: object, typ: type = None) -> T:
        if typ is None:
            typ = type(obj)
        return self.fget.__get__(obj, typ)()

    # Setting or deleting a class attribute does not delegate to a descriptor.


def classproperty(fget) -> ClassPropertyDescriptor:
    return ClassPropertyDescriptor(classmethod(fget))


classproperty.__doc__ = ClassPropertyDescriptor.__doc__

_UNDEFINED: t.Any = object()


class CachedClassPropertyDescriptor(Descriptor[T]):
    """A caching descriptor for a class attribute.

    Compare with :class:`ClassPropertyDescriptor`, which does not cache.
    """

    def __init__(self, fget: ClassGetter):
        self.fget = fget
        self.value: T = _UNDEFINED

    def __get__(self, obj: object, typ: type = None) -> T:
        if self.value is _UNDEFINED:
            if typ is None:
                typ = type(obj)
            self.value = self.fget.__get__(obj, typ)()
        return self.value


def cached_classproperty(fget) -> CachedClassPropertyDescriptor:
    return CachedClassPropertyDescriptor(classmethod(fget))


cached_classproperty.__doc__ = CachedClassPropertyDescriptor.__doc__
