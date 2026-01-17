from setuptools import setup
from Cython.Build import cythonize

setup(
    name='bench_cython',
    ext_modules=cythonize(
        "bench_06_cython.pyx",
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False,
        }
    ),
)
