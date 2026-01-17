"""
Optimization 1: Eliminate function call overhead
By inlining the function, we avoid the function call overhead and frame creation.
Expected improvement: ~10-15%
"""
import time

def main():
    s = "Lorem ipsum " * 1_000_000
    print(f"String length: {len(s)}")
    start = time.perf_counter()
    for _ in range(10_000_000):
        t = s  # Inline the function - direct assignment
    end = time.perf_counter()
    print(f"Time: {end - start:.6f} s")

if __name__ == "__main__":
    main()
