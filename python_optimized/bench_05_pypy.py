"""
Optimization 4: Use PyPy JIT compiler
PyPy uses a Just-In-Time compiler to optimize hot loops.
This can provide 5-50x speedup for compute-intensive code.
Expected improvement: 5-20x (if PyPy is available)

Run with: pypy3 bench_05_pypy.py
"""
import time

def f(x):
    return x

def main():
    s = "Lorem ipsum " * 1_000_000
    print(f"String length: {len(s)}")
    start = time.perf_counter()
    for _ in range(10_000_000):
        t = f(s)
    end = time.perf_counter()
    print(f"Time: {end - start:.6f} s")

if __name__ == "__main__":
    main()
