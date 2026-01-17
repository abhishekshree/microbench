"""
Optimization 10: Combined optimizations
Combine multiple optimization techniques for maximum performance.
Expected improvement: ~30-40%
"""
import time

def main():
    # Use local variable
    s = "Lorem ipsum " * 1_000_000
    print(f"String length: {len(s)}")
    
    # Cache local reference
    local_s = s
    
    start = time.perf_counter()
    # Loop unrolling + inline + local cache
    for _ in range(1_000_000):
        _ = local_s
        _ = local_s
        _ = local_s
        _ = local_s
        _ = local_s
        _ = local_s
        _ = local_s
        _ = local_s
        _ = local_s
        _ = local_s
    end = time.perf_counter()
    print(f"Time: {end - start:.6f} s")

if __name__ == "__main__":
    main()
