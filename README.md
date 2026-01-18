# Microbench: L1 Cache & Indirection Overhead

I designed this project to objectively measure the hardware-level cost of Python's object model (`PyObject`) compared to C++ and Rust.

## Objective
My goal was to isolate the performance impact of:
1.  **Pointer Indirection**: Python variables are pointers to variables on the heap, whereas C++/Rust use direct stack allocation.
2.  **Reference Counting**: Every variable assignment in Python involves writing to the heap (`ob_refcnt`), causing L1 cache pollution.
3.  **Memory Layout**: The lack of contiguous memory locality in standard Python.

## Benchmarks
I implemented the same logic—passing a small string to a function 100 million times—across three languages.

-   `cpp/`: C++ implementation (`g++ -O3`)
-   `rust/`: Rust implementation (`rustc -O`)
-   `python/`: Python implementation (CPython & PyPy)

## Results Summary
My experiments confirm that C++ and Rust are **150x+ faster** than standard Python for this workload.

### Key Insights
1.  **Constant Overhead**: The cost of passing a variable in Python is constant (0.3s) regardless of payload size (5 bytes vs 12MB), dominated by pointer dereferencing.
2.  **Heap Writes**: C++/Rust pass `const string&` without writing to the heap. Python must write to the `PyObject` header (refcount) on *every* pass, dirtying the cache.


## Cache Efficiency & PyObject Overhead
The Python slowdown comes from the `PyObject` structure:
1.  **Indirection**: Python variables are pointers to `PyObject` structs on the heap. C++/Rust variables (in this test) are direct pointers or stack values.
2.  **Refcounting**: Every assignment `t = s` triggers:
    -   `s->ob_refcnt++` (Write to Heap)
    -   `old_t->ob_refcnt--` (Write to Heap)
    -   **Cache Impact**: These writes dirty the cache line where the PyObject lives, potentially evicting other useful data.
    -   **C++/Rust**: Passing `const string&` reads the pointer from the stack. It does **not** write to the heap string object.
3.  **No SSO**: C++ uses Small String Optimization (SSO) to store small strings directly on the stack. Python always allocates a PyObject header + data on the heap.

## Usage

To run the full cross-language comparison:
```bash
make bench_languages
```

To run the detailed Python optimization analysis (including Cython, PyPy, etc.):
```bash
make bench_python
```

For a deep dive into the Python-specific optimizations and finding the "PyObject Ceiling", see [python_optimized/README.md](python_optimized/README.md).
