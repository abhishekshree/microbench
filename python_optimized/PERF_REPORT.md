# Integrated Performance Analysis: All Variants

This report combines precise timing (Hyperfine), instruction simulation (Valgrind), and hardware counters (Perf).

## 1. Executive Summary Table

| Variant | Time (ms) | Speedup | Instructions (M) | D1 Cache Misses |
|:---|---:|---:|---:|---:|
| 01 Baseline | 295.90 | 1.00x | 8943.6 | 1,199,613 |
| 02 Inline | 106.76 | 2.77x | 2913.5 | 1,198,692 |
| 03 LocalCache | 108.84 | 2.72x | 2913.8 | 1,200,167 |
| 04 LoopUnroll | 34.56 | 8.56x | 897.8 | 1,200,882 |
| 05 PyPyScript (CPython) | 298.49 | 0.99x | 9113.8 | 1,202,573 |
| 06 Cython Native | 14.17 | 20.88x | 104.0 | 1,205,540 |
| 07 NumPy | 66.89 | 4.42x | 459.1 | 8,337,969 |
| 08 RefcountAware | 98.78 | 3.00x | 2913.8 | 1,199,548 |
| 09 ctypes Demo | 107.32 | 2.76x | 2919.6 | 1,286,254 |
| 10 Combined | 35.91 | 8.24x | 897.8 | 1,200,390 |
| PyPy3 JIT | 29.73 | 9.95x | 230.0 | 2,384,698 |

## 2. Hardware Resource Usage (Perf Stats)

| Variant | Cycles (M) | IPC | Cache Misses (Perf) | L1 D-Cache Misses |
|:---|---:|---:|---:|---:|
| 01 Baseline | 1489.6 | 5.86 | 532,560 | 1,353,982 |
| 02 Inline | 548.0 | 5.31 | 566,037 | 1,330,158 |
| 03 LocalCache | 540.1 | 5.39 | 484,041 | 1,309,413 |
| 04 LoopUnroll | 178.1 | 5.03 | 452,525 | 1,296,439 |
| 05 PyPyScript (CPython) | 1614.3 | 5.72 | 504,094 | 1,348,459 |
| 06 Cython Native | 51.3 | 1.99 | 426,392 | 1,292,542 |
| 07 NumPy | 267.7 | 1.71 | 2,715,894 | 9,972,364 |
| 08 RefcountAware | 481.4 | 6.05 | 486,942 | 1,320,913 |
| 09 ctypes Demo | 534.4 | 5.46 | 508,033 | 1,426,357 |
| 10 Combined | 163.1 | 5.49 | 494,220 | 1,323,270 |
| PyPy3 JIT | 95.3 | 2.46 | 1,135,590 | 2,035,103 |

## 3. Deep Interpretation

### Interpreter Tax vs Native Execution
- **CPython (Baseline)** executed **8943.6M** instructions to complete the task.
- **Cython (Native)** executed only **104.0M** instructions.
- That's a **86.0x reduction** in instructions, explaining the massive speedup.

### JIT Complexity (PyPy)
- **PyPy3 JIT** shows a high instruction count during warmup, but as seen in its **10.0x speedup**, the generated assembly is extremely efficient.
- Note that PyPy's L1 cache misses (**2,384,698**) are often higher than CPython's due to the complexity of the JIT-generated code and the garbage collector.

### The Constant Cache Cost
- Across almost all CPython optimizations (Baseline to Combined), the **D1 Cache Misses** remain near **1.2M**.
- This proves that while we can optimize the *evaluation logic*, we haven't changed the *data layout* on the heap of the PyObject itself.
