# pylint: disable=missing-docstring,no-self-argument,no-self-use

from conan_cmake.descriptors import classproperty, cached_classproperty


def test_cached_classproperty():
    times_called = 0

    class Base:

        @cached_classproperty
        def attrs(cls):
            nonlocal times_called
            times_called += 1
            return {'name': 'project_name'}

        @classproperty
        def name(cls):
            return cls.attrs['name']

    assert times_called == 0
    assert Base.name == 'project_name'
    assert times_called == 1
    assert Base.name == 'project_name'
    assert times_called == 1


def test_lazy_classproperty():

    class Base:
        default_name = 'default_name1'

        @classproperty
        def name(cls):
            return cls.default_name

    class Derived(Base):
        default_name = 'default_name2'

    assert Base.default_name == 'default_name1'
    assert Derived.default_name == 'default_name2'


def test_overridden_classproperty():

    class Base:

        @cached_classproperty
        def attrs(cls):
            return {'name': 'default_name'}

        @classproperty
        def name(cls):
            return cls.attrs['name']

    class Derived(Base):

        @cached_classproperty
        def attrs(cls):
            return {'name': 'overridden_name'}

    assert Base.name == 'default_name'
    assert Derived.name == 'overridden_name'


def test_conan_pattern():

    class Base:

        @cached_classproperty
        def source_dir(cls):
            return 'base'

        @cached_classproperty
        def attrs(cls):
            return {'name': cls.source_dir + '/project_name'}

        @classproperty
        def name(cls):
            return cls.attrs['name']

    class Derived(Base):
        source_dir = 'derived'

    assert Derived.name == 'derived/project_name'
