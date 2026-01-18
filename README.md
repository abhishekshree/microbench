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

## Visualizing the Overhead

To understand *why* Python is slower, look at how memory is handled when passing a string `s`.

**C++ / Rust (Zero Overhead)**
The string lives on the stack. Passing it relies on a simple pointer or reference. **No heap writes occur.**

```mermaid
graph TD
    subgraph STACK [Stack Memory]
        func[Function Call frame]
        str[String Data: 'Hello']
        
        func -->|Direct Access| str
    end
    
    style STACK fill:#e1f5fe,stroke:#01579b
```

**Python (The PyObject Tax)**
The variable `s` is just a pointer. The actual data lives on the heap in a heavy `PyObject` struct. Every pass triggers a write to `ob_refcnt`.

```mermaid
graph TD
    subgraph STACK [Stack Memory]
        var_s[Variable 's']
    end

    subgraph HEAP [Heap Memory]
        pyobj[PyObject Header]
        refcnt[ob_refcnt++]
        type[ob_type]
        data[String Data: 'Hello']
        
        pyobj --- refcnt
        pyobj --- type
        pyobj --- data
    end
    
    var_s -->|Pointer Indirection| pyobj
    
    style STACK fill:#e1f5fe,stroke:#01579b
    style HEAP fill:#fff3e0,stroke:#e65100
    style refcnt fill:#ffcdd2,stroke:#b71c1c,stroke-width:2px
```

> **The Red Box**: That `ob_refcnt++` is the bottleneck. It forces a write to the heap on *every single assignment*, destroying L1 cache locality.

## Python's Memory Model
In C++, `int x = 42` allocates 4 bytes on the stack. In Python, `x = 42` allocates a heap object.

Every Python object is fundamentally a `PyObject` C-struct. This adds significant overhead:
1.  **Heap Allocation**: All objects live on the heap; the "variable" is just a stack pointer to them.
2.  **Metadata Overhead**: Even a simple integer wraps the value with reference counting and type information.
3.  **PyMalloc**: Python uses a specialized allocator (arenas/pools) for small objects to reduce fragmentation, but it still incurs management overhead compared to a raw pointer increment.

**Rough C++ Equivalent of a Python Integer:**
```cpp
// A "simple" Python integer is actually this struct on the heap
struct PyObject {
    long ob_refcnt;       // 8 bytes: Memory management
    PyTypeObject* ob_type;// 8 bytes: RTTI / Dynamic Dispatch
};

struct PyLongObject {
    PyObject ob_base;     // 16 bytes overhead
    long ob_digit[1];     // The actual value matches here
};
// Total: ~24+ bytes for a 4-byte integer value
```

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
