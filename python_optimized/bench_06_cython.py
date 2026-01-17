"""
Optimization 5: Use Cython with type annotations
Cython compiles Python to C, eliminating PyObject overhead for typed variables.
This requires compilation but can provide C-like performance.
Expected improvement: 10-100x (depending on type annotations)

To compile and run:
    pip install cython
    cython --embed -o bench_06_cython.c bench_06_cython.py
    gcc -O3 -I/usr/include/python3.10 -o bench_06_cython bench_06_cython.c -lpython3.10
    ./bench_06_cython
"""
import time

def f(x: str) -> str:
    return x

def main():
    s: str = "Lorem ipsum " * 1_000_000
    print(f"String length: {len(s)}")
    
    start: float = time.perf_counter()
    i: int
    for i in range(10_000_000):
        t: str = f(s)
    end: float = time.perf_counter()
    print(f"Time: {end - start:.6f} s")

if __name__ == "__main__":
    main()
