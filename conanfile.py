from conans import ConanFile

import autorecipes


class Recipe(ConanFile):
    name = 'autorecipes'
    version = '0.1.0'
    description = 'Generic Conan recipes for CMake and Python projects.'
    author = 'John Freeman <jfreeman08@gmail.com>'
    homepage = 'https://autorecipes.readthedocs.io/'
    url = 'https://github.com/thejohnfreeman/autorecipes/'
    license = 'ISC'
    exports = 'autorecipes/**.py', 'autorecipes/data/**'


def cmake():
    return autorecipes.CMakeConanFile


def python():
    return autorecipes.PythonConanFile
