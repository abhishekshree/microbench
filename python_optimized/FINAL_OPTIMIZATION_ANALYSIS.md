# Deep Optimization Analysis: Python vs PyPy vs Cython

## 1. Timing Performance

| Implementation | Mean Time (ms) | Speedup (vs Baseline) |
| :--- | :---: | :---: |
| CPython Baseline | 296.02 | 1.00x |
| CPython Inline | 107.31 | 2.76x |
| CPython Combined | 36.08 | 8.21x |
| PyPy Baseline | 28.90 | 10.24x |
| Cython (Compiled) | 13.99 | 21.15x |

## 2. Instruction & Cache Efficiency

| Implementation | I Refs (M) | D Refs (M) | D1 Misses | LL Misses |
| :--- | :---: | :---: | :---: | :---: |
| CPython Baseline | 8943.8 | 3942.1 | 1,200,948 | 259,747 |
| CPython Inline | 2913.7 | 1142.0 | 1,200,048 | 259,653 |
| CPython Combined | 897.8 | 323.1 | 1,200,721 | 259,859 |
| PyPy Baseline | 229.9 | 94.3 | 2,379,277 | 826,709 |
| Cython (Compiled) | 104.0 | 37.2 | 1,205,908 | 264,382 |

## 3. Analysis Findings

### The Power of JIT (PyPy)
- PyPy achieves massive speedups by compiling the hot loop to native assembly at runtime.
- Notice the **Instruction References**: PyPy might show higher instruction counts during warmup/compilation, but in the steady state, it executes far fewer bytecode-equivalent operations.

### Cython: The Bridge to C
- By compiling to C with `cython --embed`, we eliminate the interpreter loop entirely.
- The **Data Access Efficiency** is significantly higher because types are (partially) resolved at compile time.

### Why CPython Combined is Faster than Baseline
- Reduced function call overhead and loop unrolling reduce the number of instructions executed by the interpreter to perform the same task.
