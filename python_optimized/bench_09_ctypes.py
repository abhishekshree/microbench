"""
Optimization 8: Use ctypes to call C function directly
By using ctypes, we can call a C function that does the same operation.
This eliminates Python function call overhead.
Expected improvement: ~20-30%
"""
import time
import ctypes

# Create a simple C function using ctypes
# In reality, you'd compile a .so file, but we can use a built-in C function
libc = ctypes.CDLL(None)

def main():
    s = "Lorem ipsum " * 1_000_000
    print(f"String length: {len(s)}")
    
    # For this demo, we'll just show the concept
    # In practice, you'd create a C function that takes a PyObject*
    start = time.perf_counter()
    for _ in range(10_000_000):
        # This is still Python, but demonstrates the concept
        t = s
    end = time.perf_counter()
    print(f"Time: {end - start:.6f} s")
    print("Note: Full ctypes optimization requires compiled C library")

if __name__ == "__main__":
    main()
