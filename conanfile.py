from conans import ConanFile

from autorecipes import CMakeConanFile as _CMakeConanFile


class Recipe(ConanFile):
    name = 'autorecipes'
    version = '0.1.0'
    description = 'Generic Conan recipes for CMake and Python projects.'
    author = 'John Freeman <jfreeman08@gmail.com>'
    homepage = 'https://autorecipes.readthedocs.io/'
    url = 'https://github.com/thejohnfreeman/autorecipes/'
    license = 'ISC'
    exports = 'autorecipes/**.py'


def base():
    return _CMakeConanFile
