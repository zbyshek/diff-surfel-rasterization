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

import os

os.environ["DISTUTILS_USE_SDK"] = "1"

from setuptools import setup
from torch.utils.cpp_extension import CUDAExtension, BuildExtension
os.path.dirname(os.path.abspath(__file__))

setup(
    name="diff_surfel_rasterization",
    packages=['diff_surfel_rasterization'],
    version='0.0.1',
    ext_modules=[
        CUDAExtension(
            name="diff_surfel_rasterization.diff_surfel_rasterization_C",
            sources=[
            "cuda_rasterizer/rasterizer_impl.cu",
            "cuda_rasterizer/forward.cu",
            "cuda_rasterizer/backward.cu",
            "rasterize_points.cu",
            "ext.cpp"],
            extra_compile_args={"nvcc": ["-I" + os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "build/_deps/glm-src/"
            )]})
        ],
    cmdclass={
        'build_ext': BuildExtension
    }
)
