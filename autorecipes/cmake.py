"""A generic Conan recipe for CMake projects."""

import importlib.util
import os
from pathlib import Path
import subprocess as sp
import tempfile
import typing as t

from conans import CMake, ConanFile  # type: ignore

from autorecipes.descriptors import (
    cached_classproperty,
    cached_property,
    classproperty,
)
from autorecipes.stdlib import Object, named, zero_or_more


def generate_conanfile_txt(requires, build_requires, generators) -> str:
    """Generate contents of a ``conanfile.txt``."""
    text = ''
    if requires:
        text += '[requires]\n'
        text += ''.join(f'{line}\n' for line in requires)
    if build_requires:
        text += '[build_requires]\n'
        text += ''.join(f'{line}\n' for line in build_requires)
    if text and generators:
        text += '[generators]'
        text += ''.join(f'{line}\n' for line in generators)
    return text


class CMakeListsTxtAttributes:
    """A descriptor that lazily loads attributes from the CMake configuration."""

    def __init__(self):
        self.module = None

    def __get__(
        self,
        obj: object,
        typ: t.Type[ConanFile] = None,
    ) -> t.Mapping[str, t.Any]:
        if typ is None:
            raise ValueError(f'expected class type: {typ}')
        if self.module is None:
            source_dir = Path(os.getcwd())
            # TODO: Try to cache the ``step1_dir`` within the ``source_dir``.
            # Configure the project in one directory,
            # then configure our "project" in a separate directory.
            with tempfile.TemporaryDirectory() as step1_dir:
                conanfile: t.Any = source_dir / 'conanfile.txt'
                # Generate a ``conanfile.txt`` if the requirements are given
                # in this recipe, to avoid (infinite) recursion.
                generators = zero_or_more(typ.generators)
                if not conanfile.exists():
                    text = generate_conanfile_txt(
                        zero_or_more(typ.requires),
                        zero_or_more(typ.build_requires),
                        generators,
                    )
                    if text:
                        conanfile = Path(step1_dir) / 'conanfile.txt'
                        conanfile.write_text(text)
                    else:
                        conanfile = None
                if conanfile is not None:
                    sp.run(['conan', 'install', conanfile], cwd=step1_dir)
                # It would save us some time if the CMake CLI could configure
                # without generating.
                toolchain_args = (
                    ['-DCMAKE_TOOLCHAIN_FILE=conan_paths.cmake']
                    if 'cmake_paths' in generators else []
                )
                sp.run(
                    [
                        'cmake',
                        *toolchain_args,
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
                    self.module = module
        return self.module

    def __matmul__(self, key):
        """Create a descriptor that lazily returns one attribute."""

        @classproperty
        @named(key)
        def f(cls):
            # We are assuming that the :class:`CMakeListsTxtAttributes`
            # descriptor will be named ``cmakeliststxt``.
            return getattr(cls.cmakeliststxt, key)  # type: ignore

        return f


_UNDEFINED = object()


class ConanFileTxtAttributes:
    """A descriptor that lazily loads attributes from ``conanfile.txt``."""

    def __init__(self):
        self.loader = _UNDEFINED

    def __get__(
        self,
        obj: object,
        typ: t.Type[ConanFile] = None,
    ) -> t.Mapping[str, t.Any]:
        if self.loader is _UNDEFINED:
            from conans.client.loader_txt import ConanFileTextLoader  # type: ignore
            try:
                with open('conanfile.txt', 'r') as f:
                    self.loader = ConanFileTextLoader(f.read())
            except FileNotFoundError:
                self.loader = Object(
                    build_requirements=[],
                    generators=[],
                    requirements=[],
                )
        return self.loader

    def __matmul__(self, key):

        @classproperty
        @named(key)
        def f(cls):
            # We are assuming that the :class:`ConanFileTxtAttributes`
            # descriptor will be named ``conanfiletxt``.
            return getattr(cls.conanfiletxt, key)

        return f


class CMakeConanFile(ConanFile):
    """A base class for Conan recipes for CMake projects."""

    cmakeliststxt = CMakeListsTxtAttributes()

    name = cmakeliststxt @ 'name'
    version = cmakeliststxt @ 'version'
    description = cmakeliststxt @ 'description'
    homepage = cmakeliststxt @ 'homepage'
    url = cmakeliststxt @ 'url'
    license = cmakeliststxt @ 'license'
    author = cmakeliststxt @ 'author'

    # Because the recipe depends on the sources, we must export the sources.
    @cached_classproperty
    def exports(cls):  # pylint: disable=no-self-argument,no-self-use
        return sp.check_output(['git', 'ls-files']).decode().strip().split()

    # Do not copy the sources to the build directory.
    # This reflects the recommended CMake workflow for an out-of-source build.
    # In exchange, we promise not to touch the sources because they will be
    # shared by all configurations (settings + options).
    no_copy_source = True

    conanfiletxt = ConanFileTxtAttributes()

    generators = conanfiletxt @ 'generators'
    requires = conanfiletxt @ 'requirements'
    build_requires = conanfiletxt @ 'build_requirements'

    git = {
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
        # TODO: Shouldn't :class:`CMake` be smart enough for this?
        toolchain_file = Path(self.build_folder) / 'conan_paths.cmake'
        if toolchain_file.is_file():
            print(f'adding CMAKE_TOOLCHAIN_FILE = {toolchain_file}')
            cmake.definitions['CMAKE_TOOLCHAIN_FILE'] = str(toolchain_file)
        cmake.configure()
        return cmake

    def build(self):
        self.cmake.build()  # pylint: disable=no-member

    def package(self):
        self.cmake.install()  # pylint: disable=no-member

    def package_info(self):
        source_dir = Path(__file__) / '..' / 'data' / 'install'
        source_dir = source_dir.resolve(strict=False)
        with tempfile.TemporaryDirectory() as build_dir:
            sp.run(
                [
                    'cmake',
                    f'-DCMAKE_BUILD_TYPE={self.settings.build_type}',
                    f'-DCMAKE_PREFIX_PATH={self.package_folder}',  # pylint: disable=no-member
                    f'-DPACKAGE_NAME={self.name}',
                    source_dir,
                ],
                cwd=build_dir,
            )
            # TODO: Is there somewhere to check the output?

            spec = importlib.util.spec_from_file_location( # type: ignore
                'cpp_info', f'{build_dir}/cpp_info.py'
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore
            module.fill(self.cpp_info)

        # TODO: Can we set dependency options from ``conanfile.txt``?
