"""
Optimization 3: Loop unrolling
Reduce loop overhead by processing multiple iterations per loop cycle.
This reduces the number of branch instructions and loop counter updates.
Expected improvement: ~15-25%
"""
import time

def main():
    s = "Lorem ipsum " * 1_000_000
    print(f"String length: {len(s)}")
    
    start = time.perf_counter()
    # Unroll the loop 10x - do 10 assignments per iteration
    for _ in range(1_000_000):
        t = s
        t = s
        t = s
        t = s
        t = s
        t = s
        t = s
        t = s
        t = s
        t = s
    end = time.perf_counter()
    print(f"Time: {end - start:.6f} s")

if __name__ == "__main__":
    main()
