"""A generic Conan recipe for CMake projects."""

import importlib.util
import os
from pathlib import Path
import subprocess as sp
import tempfile
import typing as t

from conans import CMake, ConanFile  # type: ignore

from autorecipes.descriptors import cached_property, classproperty


class CMakeAttributes:
    """A descriptor that lazily loads attributes from the CMake configuration."""

    def __init__(self):
        self.attrs = None

    def __get__(
        self,
        obj: object,
        typ: t.Type[ConanFile] = None,
    ) -> t.Mapping[str, t.Any]:
        if self.attrs is None:
            source_dir = Path(os.getcwd())
            # TODO: Try to cache the ``step1_dir`` within the ``source_dir``.
            # Configure the project in one directory,
            # then configure our "project" in a separate directory.
            with tempfile.TemporaryDirectory() as step1_dir:
                # TODO: Skip if no ``conanfile.txt``?
                sp.run(
                    [
                        'conan',
                        'install',
                        source_dir / 'conanfile.txt',
                    ],
                    cwd=step1_dir
                )
                # It would save us some time if the CMake CLI could configure
                # without generating.
                sp.run(
                    [
                        'cmake',
                        '-DCMAKE_TOOLCHAIN_FILE=conan_paths.cmake',
                        source_dir,
                    ],
                    cwd=step1_dir,
                )

                with tempfile.TemporaryDirectory() as step2_dir:
                    # ``pkg_resources`` doesn't work through
                    # ``python_requires``, so we must use a hack.
                    data_dir = Path(__file__) / '..' / 'data'
                    data_dir = data_dir.resolve(strict=False)
                    sp.run(
                        [
                            'cmake',
                            f'-DSTEP1_DIR={step1_dir}',
                            data_dir / 'configure',
                        ],
                        cwd=step2_dir,
                    )

                    spec = importlib.util.spec_from_file_location( # type: ignore
                        'attributes', f'{step2_dir}/attributes.py'
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)  # type: ignore
                    self.attrs = module
        return self.attrs

    def __matmul__(self, key):
        """Create a descriptor that lazily returns one attribute."""

        @classproperty
        def f(cls):
            # We are assuming that the :class:`CMakeAttributes` descriptor
            # will be named ``attrs``.
            return getattr(cls.attrs, key)  # type: ignore

        f.__name__ = key
        return f


class CMakeConanFile(ConanFile):
    """A base class for Conan recipes for CMake projects."""

    attrs = CMakeAttributes()

    name = attrs @ 'name'
    version = attrs @ 'version'
    description = attrs @ 'description'
    homepage = attrs @ 'homepage'
    url = attrs @ 'url'
    license = attrs @ 'license'
    author = attrs @ 'author'

    # Because the recipe depends on the sources, we must export the sources.
    exports = '*'
    # Do not copy the sources to the build directory.
    # This reflects the recommended CMake workflow for an out-of-source build.
    # In exchange, we promise not to touch the sources because they will be
    # shared by all configurations (settings + options).
    no_copy_source = True

    # TODO: ConanAttributes like requires, build_requires, generators
    # Is there a facility in ``conans`` for parsing ``conanfile.txt``?
    # For now, just hard code.
    generators = 'cmake_find_package', 'cmake_paths'
    build_requires = ['doctest/2.3.1@bincrafters/stable']

    scm = {
        'type': 'git',
        'url': 'auto',
        'revision': 'auto',
    }

    settings = 'arch', 'os', 'compiler', 'build_type'
    options = {'shared': [True, False]}
    default_options = {'shared': False}

    @cached_property
    def cmake(self) -> CMake:  # pylint: disable=missing-docstring
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        self.cmake.build()  # pylint: disable=no-member

    def package(self):
        self.cmake.install()  # pylint: disable=no-member

    def package_info(self):
        # TODO: dependency options from ``conanfile.txt``.
        # TODO
        pass
