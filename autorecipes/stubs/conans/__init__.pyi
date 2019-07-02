import typing as t


class ConanFile:
    build_folder: str
    build_requires: t.Iterable[str]
    generators: t.Iterable[str]
    requires: t.Iterable[str]


class CMake:

    def __init__(self, recipe: ConanFile):
        ...

    definitions: t.MutableMapping[str, str]

    def configure(self):
        ...

    def build(self):
        ...
