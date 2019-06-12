from conan_cmake import CMakeConanFile as _CMakeConanFile
from conan_cmake.python_conanfile import PythonConanFile


class Recipe(PythonConanFile):
    name = PythonConanFile.name
    version = PythonConanFile.version


def base():
    return _CMakeConanFile
