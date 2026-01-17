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
