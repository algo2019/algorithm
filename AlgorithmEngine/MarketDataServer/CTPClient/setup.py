from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import os


root = os.path.abspath(os.path.join(__file__, '..', '..', '..'))

setup(ext_modules=cythonize(Extension(
    './target/client',
    sources=['client.pyx', 'InstrumnetGainer/InstrumnetGainer.cpp', 'CSimpleHandler/CSimpleHandler.cpp'],
    language='c++',
    include_dirs=[os.path.join(root, 'include'), os.path.abspath('./InstrumnetGainer/'), os.path.abspath('./CSimpleHandler/')],
    library_dirs=[os.path.join(root, 'lib')],
    libraries=['thostmduserapi', 'thosttraderapi', 'hiredis'],
    extra_compile_args=[],
    extra_link_args=[]
)))
