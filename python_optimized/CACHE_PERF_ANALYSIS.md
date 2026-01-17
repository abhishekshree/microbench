# Full Cache & Performance Analysis: 10 Variants

This report summarizes the hardware-level efficiency of various Python optimization strategies.

## 1. Valgrind Cachegrind Analysis (Instruction & Cache Efficiency)

| Variant | Instructions (M) | Data Refs (M) | D1 Misses | LL Misses |
|:---|---:|---:|---:|---:|
| CPython Baseline | 8943.7 | 3942.1 | 1,199,514 | 259,755 |
| CPython Inline | 2913.7 | 1142.1 | 1,199,690 | 259,658 |
| CPython LocalCache | 2913.8 | 1142.1 | 1,200,729 | 259,731 |
| CPython LoopUnroll | 897.8 | 323.1 | 1,200,731 | 259,865 |
| CPython PyPyScript | 8943.7 | 3942.1 | 1,201,931 | 259,747 |
| Cython Native | 104.0 | 37.2 | 1,204,982 | 264,383 |
| CPython NumPy | 458.8 | 172.4 | 8,341,153 | 4,267,695 |
| CPython Refcount | 2913.8 | 1142.1 | 1,200,196 | 259,824 |
| CPython ctypes | 2919.6 | 1144.3 | 1,285,375 | 264,180 |
| CPython Combined | 898.0 | 323.2 | 1,202,314 | 259,862 |
| PyPy Baseline | 230.0 | 94.3 | 2,385,862 | 826,586 |

## 2. Perf Stat Analysis (Cycles & CPU Events)

| Variant | Instructions (M) | Cycles (M) | Cache Misses | L1 D-Cache Misses |
|:---|---:|---:|---:|---:|
| CPython Baseline | N/A | N/A | N/A | N/A |
| CPython Inline | N/A | N/A | N/A | N/A |
| CPython LocalCache | N/A | N/A | N/A | N/A |
| CPython LoopUnroll | N/A | N/A | N/A | N/A |
| CPython PyPyScript | N/A | N/A | N/A | N/A |
| Cython Native | N/A | N/A | N/A | N/A |
| CPython NumPy | N/A | N/A | N/A | N/A |
| CPython Refcount | N/A | N/A | N/A | N/A |
| CPython ctypes | N/A | N/A | N/A | N/A |
| CPython Combined | N/A | N/A | N/A | N/A |
| PyPy Baseline | N/A | N/A | N/A | N/A |

*Note: Perf was unable to collect hardware counters (common in WSL2 without specialized setup). Falling back to Valgrind for analysis.*

## 3. Comparative Observations

- **Fewest Instructions**: `Cython Native` (104.0M)
  - A **98.8% reduction** from baseline.
- **Most Cache Efficient (L1)**: `CPython Baseline` (1,199,514 misses)

