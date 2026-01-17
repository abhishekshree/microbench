# Assignment and Passing Benchmark

This project benchmarks the cost of passing a small string to a function in C++, Rust, and Python.

## Structure
- `cpp/bench.cpp`: C++ implementation (g++ -O3)
- `rust/bench.rs`: Rust implementation (rustc -O)
- `python/bench.py`: Python implementation
- `run_all.py`: Runner script that compiles and executes all benchmarks.

## Prerequisites
- g++
- rustc (ensure `~/.cargo/bin` is in PATH or source cargo env)
- python3

## usage
Run the full benchmark suite:
```bash
python3 run_all.py
```

## Expected Results
You should see C++ and Rust performance being 150x+ faster than Python.

### Assignment & Passing Cost (O(1))
The size of the string (5 bytes vs 12MB) **does not affect** the passing cost.
- **C++/Rust**: Pass a pointer (8 bytes). 0.002s total.
- **Python**: Pass a reference (pointer to PyObject). 0.3s total.
- **Result**: Constant time regardless of payload size.

## Cache Efficiency & PyObject Overhead
The Python slowdown comes from the `PyObject` structure:
1.  **Indirection**: Python variables are pointers to `PyObject` structs on the heap. C++/Rust variables (in this test) are direct pointers or stack values.
2.  **Refcounting**: Every assignment `t = s` triggers:
    -   `s->ob_refcnt++` (Write to Heap)
    -   `old_t->ob_refcnt--` (Write to Heap)
    -   **Cache Impact**: These writes dirty the cache line where the PyObject lives, potentially evicting other useful data.
    -   **C++/Rust**: Passing `const string&` reads the pointer from the stack. It does **not** write to the heap string object.
3.  **No SSO**: C++ uses Small String Optimization (SSO) to store small strings directly on the stack. Python always allocates a PyObject header + data on the heap.

### Measuring Cache Efficiency
To measure L1/L2 cache misses, use the `perf` tool (Linux):
```bash
perf stat -e instructions,cycles,cache-misses,L1-dcache-load-misses ./cpp_bench
perf stat -e instructions,cycles,cache-misses,L1-dcache-load-misses python3 python/bench.py
```
*Note: `perf` requires system privileges not available in all environments.*

**For a comprehensive performance analysis with detailed cache metrics, see [PERFORMANCE_ANALYSIS.md](PERFORMANCE_ANALYSIS.md)**
