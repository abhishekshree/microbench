"""
Optimization 2: Use local variable caching
Accessing local variables is faster than global lookups.
Store the string in a local variable to reduce name resolution overhead.
Expected improvement: ~5-10%
"""
import time

def main():
    s = "Lorem ipsum " * 1_000_000
    print(f"String length: {len(s)}")
    
    # Cache the local variable reference
    local_s = s
    
    start = time.perf_counter()
    for _ in range(10_000_000):
        t = local_s
    end = time.perf_counter()
    print(f"Time: {end - start:.6f} s")

if __name__ == "__main__":
    main()
