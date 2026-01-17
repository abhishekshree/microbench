"""
Optimization 6: Use NumPy for array operations
NumPy uses C arrays internally, avoiding PyObject overhead.
This is effective for numeric/array operations but not applicable to string passing.
Expected improvement: N/A (not applicable to this benchmark)

Note: This demonstrates why NumPy is fast - it bypasses PyObject for array elements.
"""
import time
import numpy as np

def main():
    # Create a NumPy array of integers instead of strings
    # This demonstrates the concept, though it's not the same benchmark
    arr = np.arange(10_000_000, dtype=np.int64)
    print(f"Array length: {len(arr)}")
    
    start = time.perf_counter()
    # NumPy operations are vectorized and use C loops internally
    result = arr + 1  # This is much faster than Python loop
    end = time.perf_counter()
    print(f"Time: {end - start:.6f} s")
    print("Note: This is a different benchmark showing NumPy's efficiency")

if __name__ == "__main__":
    main()
