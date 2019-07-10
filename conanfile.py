import subprocess as sp

from conans import ConanFile

import autorecipes
from autorecipes.descriptors import cached_classproperty


class Recipe(ConanFile):
    name = 'autorecipes'
    version = '0.3.1'
    description = 'Generic Conan recipes for CMake and Python projects.'
    author = 'John Freeman <jfreeman08@gmail.com>'
    homepage = 'https://autorecipes.readthedocs.io/'
    url = 'https://github.com/thejohnfreeman/autorecipes/'
    license = 'ISC'

    @cached_classproperty
    def exports(cls):
        return sp.check_output(['git', 'ls-files']).decode().strip().split()

    no_copy_source = True


def cmake():
    return autorecipes.CMakeConanFile


def python():
    return autorecipes.PythonConanFile
