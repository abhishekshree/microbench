import time

def make_obj(i):
    # Create a new string dynamically to force allocation
    # str(i) creates a new PyObject
    return "prefix_" + str(i)

def main():
    start = time.perf_counter()
    for i in range(1_000_000): # Reduced to 1M to save time
        t = make_obj(i)
    end = time.perf_counter()
    print(f"Time: {end - start:.6f} s")

if __name__ == "__main__":
    main()
