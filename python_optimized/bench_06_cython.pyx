# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
"""
Cython optimized version with type annotations.
This compiles to C and eliminates PyObject overhead for typed variables.
"""
import time

cdef str f(str x):
    return x

def main():
    cdef str s = "Lorem ipsum " * 1_000_000
    cdef double start, end
    cdef long i
    cdef str t
    
    print(f"String length: {len(s)}")
    
    start = time.perf_counter()
    for i in range(10_000_000):
        t = f(s)
    end = time.perf_counter()
    print(f"Time: {end - start:.6f} s")

if __name__ == "__main__":
    main()
