"""A generic Conan recipe for CMake projects."""

import importlib.util
import os
from pathlib import Path
import subprocess as sp
import typing as t

from conans import ConanFile  # type: ignore

from conan_cmake.descriptors import classproperty


class CMakeAttributes:
    """A descriptor that lazily loads attributes from the CMake configuration."""

    def __init__(self):
        self.attrs = None

    def __get__(self, obj: object, typ: type = None) -> t.Mapping[str, t.Any]:
        if self.attrs is None:
            # We are assuming the source directory attribute will be named
            # ``source_dir``.
            source_dir = typ.source_dir  # type: ignore
            build_dir = source_dir / '.conan_cmake'
            build_dir.mkdirs(exist_ok=True)
            sp.run(['conan', 'install', source_dir], cwd=build_dir)
            sp.run(
                [
                    'cmake',
                    '-DCMAKE_TOOLCHAIN_FILE=conan_paths.cmake',
                    source_dir,
                ],
                cwd=build_dir
            )

            spec = importlib.util.spec_from_file_location(
                'conan_attrs', build_dir / 'conan_attrs.py'
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore
            self.attrs = module
        return self.attrs

    def __getitem__(self, key):
        """Create a descriptor that lazily returns one attribute."""

        @classproperty
        def f(cls):
            # We are assuming that the :class:`CMakeAttributes` descriptor
            # will be named ``attrs``.
            return cls.attrs[key]  # type: ignore

        f.__name__ = key
        return f


class CMakeConanFile(ConanFile):
    """A base class for Conan recipes for CMake projects."""

    @classproperty
    def source_dir(cls):  # pylint: disable=no-self-argument,no-self-use
        return Path(os.getcwd())

    attrs = CMakeAttributes()

    name = attrs['name']
    version = attrs['version']
    description = attrs['description']
    homepage = attrs['homepage']
    url = attrs['url']

    exports = '*'
    settings = 'arch', 'os', 'compiler', 'build_type'
    options = {'shared': [True, False]}
    default_options = {'shared': False}
