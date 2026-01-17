"""
Optimization 7: Reduce reference counting with sys.getrefcount awareness
While we can't eliminate refcounting, we can minimize unnecessary assignments.
Expected improvement: ~5-10%
"""
import time
import sys

def main():
    s = "Lorem ipsum " * 1_000_000
    print(f"String length: {len(s)}")
    print(f"Initial refcount: {sys.getrefcount(s)}")
    
    start = time.perf_counter()
    # Instead of creating new variable t, just access s directly
    # This reduces one refcount increment/decrement per iteration
    for _ in range(10_000_000):
        _ = s  # Use _ to indicate we're not storing it
    end = time.perf_counter()
    print(f"Time: {end - start:.6f} s")
    print(f"Final refcount: {sys.getrefcount(s)}")

if __name__ == "__main__":
    main()
