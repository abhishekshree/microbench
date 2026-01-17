# Python Optimization Experiment Results

**Python Version:** 3.10.12 (main, Jan  8 2026, 06:52:19) [GCC 11.4.0]

| Benchmark | Time (s) | Speedup | Description |
|:----------|----------:|--------:|:------------|
| `/usr/bin/python3 bench_01_baseline.py` | 0.2794 | 1.00x | 01 Baseline - Original implementation |
| `/usr/bin/python3 bench_02_inline.py` | 0.0934 | 2.99x | 02 Inline function - Call overhead |
| `/usr/bin/python3 bench_03_local_cache.py` | 0.0957 | 2.92x | 03 Local variable caching |
| `/usr/bin/python3 bench_04_loop_unroll.py` | 0.0222 | 12.56x | 04 Loop unrolling (10x) |
| `/usr/bin/python3 bench_05_pypy.py` | 0.2958 | 0.94x | 05 PyPy script (run on CPython) |
| `./bench_06_cython` | 0.0024 | 114.61x | 06 Cython (Native Compiled) |
| `/usr/bin/python3 bench_07_numpy.py` | 0.0365 | 7.66x | 07 NumPy (Vectorized Array Demo) |
| `/usr/bin/python3 bench_08_refcount_aware.py` | 0.0875 | 3.19x | 08 Minimize refcount operations |
| `/usr/bin/python3 bench_09_ctypes.py` | 0.0958 | 2.92x | 09 ctypes (C interface demo) |
| `/usr/bin/python3 bench_10_combined.py` | 0.0305 | 9.15x | 10 Combined optimizations |
| `pypy3 bench_01_baseline.py` | 0.0028 | 101.31x | PyPy 3 JIT - Baseline code run |
| `pypy3 bench_05_pypy.py` | 0.0030 | 94.05x | PyPy 3 JIT - Dedicated script run |
