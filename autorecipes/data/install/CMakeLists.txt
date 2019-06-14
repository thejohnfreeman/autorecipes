cmake_minimum_required(VERSION 3.7)

project(autorecipes LANGUAGES NONE)

# No point in continuing if no package configuration file was installed.
find_package("${PACKAGE_NAME}" CONFIG REQUIRED)

function(print_property target property)
  get_target_property(var ${target} ${property})
  message("${property} = ${var}")
endfunction()

macro(builder line)
  message(STATUS "${line}")
  list(APPEND assignments "builder.${line}")
endmacro()

# This is our only chance to query the target properties,
# so we have to build the `cpp_info` data structure here.
foreach(component ${${PACKAGE_NAME}_COMPONENTS})
  set(target ${PACKAGE_NAME}::${component})

  get_target_property(type ${target} TYPE)

  # TODO: We probably need to add the standard to c{,xx}flags.
  # print_property(${target} INTERFACE_C_EXTENSIONS)
  # print_property(${target} INTERFACE_C_STANDARD)
  # print_property(${target} INTERFACE_C_STANDARD_REQUIRED)
  # print_property(${target} INTERFACE_CXX_EXTENSIONS)
  # print_property(${target} INTERFACE_CXX_STANDARD)
  # print_property(${target} INTERFACE_CXX_STANDARD_REQUIRED)

  # General rules:
  # - We must check for `name-NOTFOUND` before iterating with `foreach`.
  # - None of the assignment strings can have a semicolon because we iterate
  #   over them later. A line would be broken on semicolons.

  get_target_property(includedirs ${target} INTERFACE_INCLUDE_DIRECTORIES)
  if(includedirs)
    foreach(dir ${includedirs})
      file(RELATIVE_PATH dir "${CMAKE_PREFIX_PATH}" "${dir}")
      builder("add('${component}', 'includedirs', '${dir}')")
    endforeach()
  endif()

  get_target_property(defines ${target} INTERFACE_COMPILE_DEFINITIONS)
  if(defines)
    foreach(def ${defines})
      builder("add('${component}', 'defines', '${def}')")
    endforeach()
  endif()

  get_target_property(options ${target} INTERFACE_COMPILE_OPTIONS)
  if(options)
    foreach(opt ${options})
      # TODO: What about cflags?
      builder("add('${component}', 'cxxflags', '${opt}')")
    endforeach()
  endif()

  # TODO: What about INTERFACE_LINK_DEPENDS?
  # print_property(${target} INTERFACE_LINK_DEPENDS)

  get_target_property(dependencies ${target} INTERFACE_LINK_LIBRARIES)
  if(dependencies)
    foreach(dep ${dependencies})
      # TODO: How to handle namespaces?
      # https://github.com/conan-io/conan/issues/5090#issuecomment-501857996
      # string(REGEX REPLACE "${PACKAGE_NAME}::" "" dep "${dep}")
      builder("add_dependency('${component}', '${dep}')")
    endforeach()
    # TODO: How to handle external dependencies? Does Conan handle them for us?
    # Should we iterate over dependencies if they are in the same namespace?
    # No. If they are components, they should be in ${PACKAGE_NAME}_COMPONENTS.
  endif()

  # TODO: When is INTERFACE_LINK_DIRECTORIES ever set?
  get_target_property(libdirs ${target} INTERFACE_LINK_DIRECTORIES)
  if(libdirs)
    foreach(dir ${libdirs})
      file(RELATIVE_PATH dir "${CMAKE_PREFIX_PATH}" "${dir}")
      builder("add('${component}', 'libdirs', '${dir}')")
    endforeach()
  endif()

  get_target_property(options ${target} INTERFACE_LINK_OPTIONS)
  if(options)
    foreach(opt ${options})
      # TODO: What about sharedlinkflags?
      builder("add('${component}', 'exelinkflags', '${opt}')")
    endforeach()
  endif()

  if(type STREQUAL STATIC_LIBRARY)
    # Per the documentation, projects may skip setting the IMPORTED_LOCATION
    # if they set the IMPORTED_LOCATION_<CONFIG>.
    get_target_property(path ${target} LOCATION_${CMAKE_BUILD_TYPE})
    if(NOT path)
      get_target_property(path ${target} LOCATION)
    endif()
    file(RELATIVE_PATH path "${CMAKE_PREFIX_PATH}" "${path}")
    get_filename_component(dir "${path}" DIRECTORY)
    get_filename_component(lib "${path}" NAME)
    builder("add('${component}', 'libdirs', '${dir}')")
    builder("add_library('${component}', '${lib}')")
  endif()

  if(type STREQUAL EXECUTABLE)
    get_target_property(path ${target} LOCATION_${CMAKE_BUILD_TYPE})
    if(NOT path)
      get_target_property(path ${target} LOCATION)
    endif()
    file(RELATIVE_PATH path "${CMAKE_PREFIX_PATH}" "${path}")
    get_filename_component(dir "${path}" DIRECTORY)
    get_filename_component(exe "${path}" NAME)
    builder("add('${component}', 'bindirs', '${dir}')")
    builder("add_executable('${component}', '${exe}')")
  endif()

endforeach()

foreach(assignment ${assignments})
  set(block "${block}    ${assignment}\n")
endforeach()
configure_file(cpp_info.py.in cpp_info.py @ONLY)
