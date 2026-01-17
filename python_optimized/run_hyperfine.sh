#!/bin/bash

# Ensure we are in the script's directory
cd "$(dirname "$0")"

echo "=== Pre-run: Compiling Cython version ==="
# Compile Cython if needed (using the same command as run_optimizations.py)
cython3 --embed -o bench_06_cython.c bench_06_cython.pyx && \
gcc -O3 -I/usr/include/python3.10 -o bench_06_cython bench_06_cython.c -lpython3.10

echo -e "\n=== Running Hyperfine benchmarks ===\n"
hyperfine --warmup 3 --export-markdown results_python_optimized.md \
  'python3 bench_01_baseline.py' \
  'python3 bench_02_inline.py' \
  'python3 bench_03_local_cache.py' \
  'python3 bench_04_loop_unroll.py' \
  'python3 bench_05_pypy.py' \
  './bench_06_cython' \
  'python3 bench_07_numpy.py' \
  'python3 bench_08_refcount_aware.py' \
  'python3 bench_09_ctypes.py' \
  'python3 bench_10_combined.py' \
  'pypy3 bench_01_baseline.py' \
  'pypy3 bench_05_pypy.py'

echo -e "\n=== Done! Results saved to results_python_optimized.md ==="
