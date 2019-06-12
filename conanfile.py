from conans import ConanFile

from conan_cmake import CMakeConanFile as _CMakeConanFile


class Recipe(ConanFile):
    name = 'conan_cmake'
    version = '0.1.0'
    description = 'A generic Conan recipe for CMake projects.'
    author = 'John Freeman <jfreeman08@gmail.com>'
    homepage = 'https://conan-cmake.readthedocs.io/'
    url = 'https://github.com/thejohnfreeman/conan-cmake/'
    license = 'ISC'
    exports = 'conan_cmake/**.py'


def base():
    return _CMakeConanFile
