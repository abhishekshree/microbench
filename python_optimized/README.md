# Python Optimization Experiments

I have implemented various optimization techniques to explore the performance limits of Python relative to the "PyObject ceiling".

## Objective
To measure the impact of different optimization strategies on:
1.  **Execution Time**: Wall-clock time.
2.  **Instruction Count**: Number of CPU instructions executed.
3.  **Cache Efficiency**: L1 Data Cache misses, highlighting the impact of PyObject pointer indirection.

## Optimizations Tested
-   **Baseline**: Standard Python.
-   **Inlining**: Manually inlining functions.
-   **Local Caching**: Reducing global variable lookups.
-   **Loop Unrolling**: Reducing loop overhead.
-   **PyPy**: JIT compilation (Significant speedup).
-   **Cython**: Compiling to C (Native efficiency).
-   **NumPy/ctypes**: Bypassing the interpreter.

## Running the Benchmarks

All benchmarks are consolidated into a single runner that handles timing (Hyperfine) and hardware analysis (Valgrind/Perf).

To run the comprehensive suite:
```bash
make bench_python
```

This will generate a detailed report in `PYTHON_OPTIMIZATION_REPORT.md`.

## Analysis Summary

### The PyObject Ceiling
Pure Python optimizations (inlining, unrolling) provide modest gains (10-40%) but cannot overcome the fundamental cost of reference counting and pointer indirection. The L1 cache miss rate remains constant because the data layout of `PyObject` on the heap does not change.

### JIT and Compilation
-   **PyPy (JIT)**: Achieves 5-20x speedups by compiling hot loops to native code.
-   **Cython**: Achieving C-like performance by eliminating the interpreter loop entirely, reducing instruction count by orders of magnitude.
