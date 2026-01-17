| Command | Mean [ms] | Min [ms] | Max [ms] | Relative |
|:---|---:|---:|---:|---:|
| `python3 bench_01_baseline.py` | 297.0 ± 5.4 | 286.4 | 303.0 | 21.92 ± 1.76 |
| `python3 bench_02_inline.py` | 109.4 ± 3.5 | 103.9 | 118.7 | 8.07 ± 0.68 |
| `python3 bench_03_local_cache.py` | 106.8 ± 3.1 | 101.0 | 112.5 | 7.88 ± 0.66 |
| `python3 bench_04_loop_unroll.py` | 34.1 ± 1.8 | 31.2 | 40.8 | 2.51 ± 0.24 |
| `python3 bench_05_pypy.py` | 298.0 ± 10.5 | 280.9 | 311.6 | 21.99 ± 1.88 |
| `./bench_06_cython` | 13.6 ± 1.1 | 12.0 | 18.6 | 1.00 |
| `python3 bench_07_numpy.py` | 66.8 ± 9.3 | 61.9 | 126.8 | 4.93 ± 0.79 |
| `python3 bench_08_refcount_aware.py` | 97.4 ± 3.8 | 91.8 | 108.2 | 7.19 ± 0.63 |
| `python3 bench_09_ctypes.py` | 106.6 ± 3.2 | 100.5 | 114.1 | 7.87 ± 0.66 |
| `python3 bench_10_combined.py` | 35.8 ± 2.4 | 32.7 | 47.9 | 2.64 ± 0.27 |
| `pypy3 bench_01_baseline.py` | 30.4 ± 2.2 | 26.7 | 38.1 | 2.24 ± 0.24 |
| `pypy3 bench_05_pypy.py` | 30.3 ± 2.1 | 26.2 | 36.4 | 2.23 ± 0.23 |
