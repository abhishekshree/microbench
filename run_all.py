import os
import subprocess
import shutil
import re

CWD = "/home/shree/microbench"
ENV = os.environ.copy()
# Add cargo bin to path
ENV["PATH"] = f"{os.path.expanduser('~/.cargo/bin')}:{ENV.get('PATH', '')}"

def run_command(cmd, cwd=CWD, capture=True):
    print(f"Running: {cmd}")
    try:
        res = subprocess.run(cmd, shell=True, cwd=cwd, env=ENV, 
                             stdout=subprocess.PIPE if capture else None, 
                             stderr=subprocess.PIPE if capture else None,
                             text=True)
        if res.returncode != 0:
            print(f"Error running {cmd}:")
            print(res.stdout)
            print(res.stderr)
            return None
        return res
    except Exception as e:
        print(f"Exception running {cmd}: {e}")
        return None

def parse_time_output(stderr):
    # Parse /usr/bin/time -v output
    rss = None
    if stderr:
        for line in stderr.splitlines():
            if "Maximum resident set size" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    rss = parts[1].strip()
    return rss or "N/A"

def parse_prog_output(stdout):
    # Parse program output: "Time: 0.12345 s"
    if stdout:
        for line in stdout.splitlines():
            if line.startswith("Time:"):
                return line.split()[1] # Gets the number
    return "N/A"

def benchmark():
    results = []

    # Compile C++
    print("--- Compiling C++ ---")
    if run_command("g++ -O3 -o cpp_bench cpp/bench.cpp"):
        # Run C++
        print("--- Running C++ ---")
        res = run_command("/usr/bin/time -v ./cpp_bench")
        if res:
            t = parse_prog_output(res.stdout)
            rss = parse_time_output(res.stderr)
            results.append(("C++", t, rss))
    
    # Compile Rust
    print("--- Compiling Rust ---")
    # Check if rustc works
    if run_command("rustc --version"):
        if run_command("rustc -C opt-level=3 -o rust_bench rust/bench.rs"):
            # Run Rust
            print("--- Running Rust ---")
            res = run_command("/usr/bin/time -v ./rust_bench")
            if res:
                t = parse_prog_output(res.stdout)
                rss = parse_time_output(res.stderr)
                results.append(("Rust", t, rss))
    else:
        print("Skipping Rust (rustc not found)")

    # Run Python
    print("--- Running Python ---")
    res = run_command("/usr/bin/time -v python3 python/bench.py")
    if res:
        t = parse_prog_output(res.stdout)
        rss = parse_time_output(res.stderr)
        results.append(("Python", t, rss))

    print("\n\n=== Results (10M iterations, assignment + passing) ===")
    print(f"{'Language':<10} | {'Time (s)':<15} | {'Max RSS (KB)':<15}")
    print("-" * 46)
    for lang, t, rss in results:
        print(f"{lang:<10} | {t:<15} | {rss:<15}")

def benchmark_alloc():
    # Phase 2: Allocation
    print("\n\n=== Phase 2: Allocation (1M iterations) ===")
    results = []

    # Compile C++ Alloc
    if run_command("g++ -O3 -o cpp_bench_alloc cpp/bench_alloc.cpp"):
        res = run_command("/usr/bin/time -v ./cpp_bench_alloc")
        if res:
            t = parse_prog_output(res.stdout)
            rss = parse_time_output(res.stderr)
            results.append(("C++ (Alloc)", t, rss))
    
    # Compile Rust Alloc
    if run_command("rustc -C opt-level=3 -o rust_bench_alloc rust/bench_alloc.rs"):
        res = run_command("/usr/bin/time -v ./rust_bench_alloc")
        if res:
            t = parse_prog_output(res.stdout)
            rss = parse_time_output(res.stderr)
            results.append(("Rust (Alloc)", t, rss))

    # Run Python Alloc
    res = run_command("/usr/bin/time -v python3 python/bench_alloc.py")
    if res:
        t = parse_prog_output(res.stdout)
        rss = parse_time_output(res.stderr)
        results.append(("Python (Alloc)", t, rss))

    print(f"{'Language':<15} | {'Time (s)':<15} | {'Max RSS (KB)':<15}")
    print("-" * 51)
    for lang, t, rss in results:
        print(f"{lang:<15} | {t:<15} | {rss:<15}")

if __name__ == "__main__":
    benchmark()
    benchmark_alloc()
