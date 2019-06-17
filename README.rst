.. start-include

===========
autorecipes
===========

Generic Conan_ recipes for C/C++ and Python projects.

.. _Conan: https://docs.conan.io/

.. image:: https://travis-ci.org/thejohnfreeman/autorecipes.svg?branch=master
   :target: https://travis-ci.org/thejohnfreeman/autorecipes
   :alt: Build status: Linux and OSX

.. image:: https://ci.appveyor.com/api/projects/status/github/thejohnfreeman/autorecipes?branch=master&svg=true
   :target: https://ci.appveyor.com/project/thejohnfreeman/autorecipes
   :alt: Build status: Windows

.. .. image:: https://readthedocs.org/projects/autorecipes/badge/?version=latest
   :target: https://autorecipes.readthedocs.io/
   :alt: Documentation status

.. .. image:: https://api.bintray.com/packages/thejohnfreeman/autorecipes/autorecipes%3Aautorecipes/images/download.svg
   :target: https://bintray.com/thejohnfreeman/autorecipes/autorecipes%3Aautorecipes/_latestVersion
   :alt: Latest Bintray version

C/C++
=====

If your project

- uses CMake_,
- and installs a `package configuration file`__
- that defines the variable ``<PACKAGE_NAME>_COMPONENTS``
- with a list of components,
- and for each of them defines a target ``<package_name>::<component>``,

then you should be able to copy this recipe to package it for Conan:

.. _CMake: https://cmake.org/cmake/help/latest/
.. __: https://cmake.org/cmake/help/latest/manual/cmake-packages.7.html#package-configuration-file

.. code-block:: python

   from conans import python_requires

   CMakeConanFile = python_requires('autorecipes/[*]@jfreeman/testing').cmake()

   class Recipe(CMakeConanFile):
       name = CMakeConanFile.name
       version = CMakeConanFile.version

.. warning::
   You'll need to declare any dependencies in ``conanfile.txt``, not in this
   recipe, until `Issue #1`__ is resolved.

.. __: https://github.com/thejohnfreeman/autorecipes/issues/1


Python
======

If your project

- uses Poetry_,
- with a ``pyproject.toml`` package metadata file as defined in `PEP 518`_,

.. _Poetry: https://poetry.eustace.io/docs/
.. _PEP 518: https://www.python.org/dev/peps/pep-0518/

then you should be able to copy this recipe to package it for Conan:

.. code-block:: python

   from conans import python_requires

   PythonConanFile = python_requires('autorecipes/[*]@jfreeman/testing').python()

   class Recipe(PythonConanFile):
       name = PythonConanFile.name
       version = PythonConanFile.version


FAQ
===

.. Look at this fucking joke of a syntax. Just let me nest!

- **Why do I need to copy the** ``name`` **and** ``version`` **attributes from
  the base class?**

  Conan parses the recipe looking for the ``name`` and ``version`` attributes,
  instead of just executing it. Thus, we must copy the attributes to move past
  that check.

.. end-include
