"""Types and class property descriptors."""


class MappedDescriptor:
    """A descriptor that maps a function over another descriptor."""

    def __init__(self, descriptor, function):
        self.descriptor = descriptor
        self.function = function

    def __get__(self, obj, typ):
        return self.function(self.descriptor.__get__(obj, typ))


def fmap(function, descriptor):
    """Return a descriptor that maps a function over another descriptor."""
    return MappedDescriptor(descriptor, function)


# Because Conan makes it impossible to just import code from PyPI,
# and because it's such a small class,
# we implement our own ``cached_property`` descriptor.
class CachedPropertyDescriptor:
    """A caching version of :func:`property`."""

    def __init__(self, fget):
        self.__doc__ = fget.__doc__
        self.fget = fget

    def __get__(self, obj, typ=None):
        if obj is None:
            return self
        if typ is None:
            typ = type(obj)
        f = self.fget
        value = obj.__dict__[f.__name__] = f.__get__(obj, typ)()
        return value


cached_property = CachedPropertyDescriptor  # pylint: disable=invalid-name


class ClassPropertyDescriptor:
    """A descriptor for a class attribute.

    Compare with :func:`property`, which is for instance attributes.
    """

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, typ=None):
        if typ is None:
            typ = type(obj)
        return self.fget.__get__(obj, typ)()

    # Setting or deleting a class attribute does not delegate to a descriptor.


def classproperty(fget):
    return ClassPropertyDescriptor(classmethod(fget))


classproperty.__doc__ = ClassPropertyDescriptor.__doc__

_UNDEFINED = object()


class CachedClassPropertyDescriptor:
    """A caching descriptor for a class attribute.

    Compare with :class:`ClassPropertyDescriptor`, which does not cache.
    """

    def __init__(self, fget):
        self.fget = fget
        self.value = _UNDEFINED

    def __get__(self, obj, typ=None):
        if self.value is _UNDEFINED:
            if typ is None:
                typ = type(obj)
            self.value = self.fget.__get__(obj, typ)()
        return self.value


def cached_classproperty(fget):
    return CachedClassPropertyDescriptor(classmethod(fget))


cached_classproperty.__doc__ = CachedClassPropertyDescriptor.__doc__
