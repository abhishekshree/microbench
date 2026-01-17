# Full Cache & Performance Analysis: 10 Variants

This report summarizes the hardware-level efficiency of various Python optimization strategies.

## 1. Valgrind Cachegrind Analysis (Instruction & Cache Efficiency)

| Variant | Instructions (M) | Data Refs (M) | D1 Misses | LL Misses |
|:---|---:|---:|---:|---:|
| CPython Baseline | 8773.8 | 3912.1 | 1,200,197 | 259,758 |
| CPython Inline | 2913.7 | 1142.1 | 1,199,507 | 259,661 |
| CPython LocalCache | 2913.7 | 1142.1 | 1,199,559 | 259,737 |
| CPython LoopUnroll | 897.7 | 323.1 | 1,200,268 | 259,868 |
| CPython PyPyScript | 8773.7 | 3912.1 | 1,201,434 | 259,751 |
| Cython Native | 104.1 | 37.2 | 1,206,385 | 264,391 |
| CPython NumPy | 458.7 | 172.4 | 8,335,025 | 4,267,527 |
| CPython Refcount | 2913.8 | 1142.1 | 1,198,839 | 259,831 |
| CPython ctypes | 2919.7 | 1144.3 | 1,283,999 | 264,185 |
| CPython Combined | 897.8 | 323.1 | 1,201,154 | 259,868 |
| PyPy Baseline | 229.9 | 94.3 | 2,384,467 | 826,822 |

## 2. Perf Stat Analysis (Cycles & CPU Events)

| Variant | Instructions (M) | Cycles (M) | Cache Misses | L1 D-Cache Misses |
|:---|---:|---:|---:|---:|
| CPython Baseline | 8731.8 | 1505.2 | 495,442 | 1,341,663 |
| CPython Inline | 2911.7 | 538.5 | 461,064 | 1,314,735 |
| CPython LocalCache | 2911.7 | 596.8 | 574,233 | 1,350,100 |
| CPython LoopUnroll | 895.8 | 164.5 | 506,145 | 1,314,978 |
| CPython PyPyScript | 8731.6 | 1569.8 | 460,091 | 25,399,493 |
| Cython Native | 102.3 | 53.8 | 498,244 | 1,315,400 |
| CPython NumPy | 457.1 | 288.0 | 3,184,830 | 10,342,457 |
| CPython Refcount | 2911.9 | 487.9 | 545,191 | 1,335,484 |
| CPython ctypes | 2917.6 | 540.1 | 520,217 | 1,430,827 |
| CPython Combined | 895.8 | 171.1 | 465,414 | 1,350,456 |
| PyPy Baseline | 234.6 | 105.7 | 1,227,672 | 2,060,426 |

## 3. Comparative Observations

- **Fewest Instructions**: `Cython Native` (104.1M)
  - A **98.8% reduction** from baseline.
- **Most Cache Efficient (L1)**: `CPython Refcount` (1,198,839 misses)
