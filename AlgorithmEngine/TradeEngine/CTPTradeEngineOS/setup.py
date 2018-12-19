# -*- coding: utf-8 -*-
"""
setup.py
    make python ext: ctptradeengine.so
"""
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import os


root = os.path.abspath(os.path.join(__file__, '..', '..', '..'))

setup(ext_modules=cythonize(Extension(
    'ctptradeengine',
    sources=['ctptradeengine.pyx', 'TraderSpi.cpp'],
    language='c++',
    include_dirs=[os.path.join(root, 'include')],
    library_dirs=[os.path.abspath(os.path.join(root, 'lib'))],
    libraries=['log4cplus', 'hiredis', 'thosttraderapi'],
    extra_compile_args=[],
    extra_link_args=[]
)))
