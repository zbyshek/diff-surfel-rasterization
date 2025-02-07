#
# Copyright (C) 2023, Inria
# GRAPHDECO research group, https://team.inria.fr/graphdeco
# All rights reserved.
#
# This software is free for non-commercial, research and evaluation use 
# under the terms of the LICENSE.md file.
#
# For inquiries contact  george.drettakis@inria.fr
#

# NOTE:
# This is the CMakeLists.txt file was updated due to simplification of 
# the build process using Makefile by Alexey Mazurenko.

cmake_minimum_required(VERSION 3.20)

project(DiffRast LANGUAGES CUDA CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CUDA_STANDARD 17)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")

if (WIN32 AND NOT TARGET CUDA::nvToolsExt)
    find_library(NVTOOLSEXT_LIB
        NAMES nvToolsExt64_1 nvToolsExt
        PATHS "${CUDAToolkit_LIBRARY_DIRS}" 
        ${CMAKE_CURRENT_SOURCE_DIR}/third_party/windows/NvToolsExt/lib/x64
    )
    message(STATUS "NVTOOLSEXT_LIB: ${NVTOOLSEXT_LIB}")

    add_library(CUDA::nvToolsExt INTERFACE IMPORTED)
    set_target_properties(CUDA::nvToolsExt PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${CUDAToolkit_INCLUDE_DIRS}"
        INTERFACE_LINK_LIBRARIES "${NVTOOLSEXT_LIB}"
    )
endif()

if(WIN32)
    find_package(
        Torch REQUIRED 
        PATHS 
        venv/Lib/site-packages/torch/share/cmake/Torch
    )
else()
    find_package(Python REQUIRED COMPONENTS Interpreter)
    find_package(
        Torch REQUIRED 
        PATHS 
        venv/lib/python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}/site-packages/torch/share/cmake/Torch
    )
endif()

message(STATUS "TORCH_LIBRARIES: ${TORCH_LIBRARIES}")

include(FetchContent)

FetchContent_Declare(
    glm
	GIT_REPOSITORY	https://github.com/g-truc/glm.git
	GIT_TAG 	bf71a834948186f4097caa076cd2663c69a10e1e #refs/tags/1.0.1
)

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG stable
)

FetchContent_MakeAvailable(glm)
FetchContent_MakeAvailable(pybind11)

add_library(CudaRasterizer
	cuda_rasterizer/backward.h
	cuda_rasterizer/backward.cu
	cuda_rasterizer/forward.h
	cuda_rasterizer/forward.cu
	cuda_rasterizer/auxiliary.h
	cuda_rasterizer/rasterizer_impl.cu
	cuda_rasterizer/rasterizer_impl.h
	cuda_rasterizer/rasterizer.h
)

set_target_properties(CudaRasterizer PROPERTIES CUDA_ARCHITECTURES "70;75;86")

target_include_directories(
    CudaRasterizer 
    PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/cuda_rasterizer
)
target_include_directories(
    CudaRasterizer 
    PRIVATE 
    ${glm_SOURCE_DIR} ${CMAKE_CUDA_TOOLKIT_INCLUDE_DIRECTORIES}
)

# Python bindings
set(
    cuda_rasterizer_py_module diff_surfel_rasterization_C 
    CACHE STRING "The name of the pyd to build"
)

pybind11_add_module(${cuda_rasterizer_py_module}
    cuda_rasterizer/rasterizer_impl.cu
    cuda_rasterizer/forward.cu
    cuda_rasterizer/backward.cu
    rasterize_points.cu
    ext.cpp
)

target_include_directories(${cuda_rasterizer_py_module}
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/cuda_rasterizer
    ${glm_SOURCE_DIR} 
    ${CMAKE_CUDA_TOOLKIT_INCLUDE_DIRECTORIES}
    ${TORCH_INCLUDE_DIRS}
)

target_link_libraries(${cuda_rasterizer_py_module} 
  PRIVATE pybind11::module
  CUDA::cudart
  ${TORCH_LIBRARIES}
)

find_library(TORCH_PYTHON_LIBRARY
    NAMES torch_python
    HINTS
      "${TORCH_INSTALL_PREFIX}/lib"
      "${TORCH_INSTALL_PREFIX}"
      "${TORCH_LIBRARY_DIRS}"
      "${CMAKE_CURRENT_SOURCE_DIR}/venv/Lib/site-packages/torch/lib"
)

if (TORCH_PYTHON_LIBRARY)
    message(STATUS "Found torch_python: ${TORCH_PYTHON_LIBRARY}")
    target_link_libraries(${cuda_rasterizer_py_module}
      PRIVATE
        ${TORCH_PYTHON_LIBRARY}
    )
else()
    message(
        WARNING 
        "Could not find torch_python.lib; you may still have link errors."
    )
endif()

set_target_properties(${cuda_rasterizer_py_module} PROPERTIES 
    CUDA_INCLUDE_DIRS "${CMAKE_CURRENT_SOURCE_DIR};${glm_SOURCE_DIR}"
    CUDA_SEPARABLE_COMPILATION ON)

# Prints
message (STATUS "TORCH_INCLUDE_DIRS: ${TORCH_INCLUDE_DIRS}")
message (STATUS "TORCH_LIBRARIES: ${TORCH_LIBRARIES}")
message (STATUS "TORCH_PYTHON_LIBRARY: ${TORCH_PYTHON_LIBRARY}")
message(STATUS "glm_SOURCE_DIR: ${glm_SOURCE_DIR}")
message (STATUS "Configuring done.")
