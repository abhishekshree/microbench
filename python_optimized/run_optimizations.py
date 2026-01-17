#!/usr/bin/env python3
"""
Runner script for Python optimization experiments.
Runs all optimization variants and compares their performance.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_benchmark(cmd_args, description):
    """Run a single benchmark and return the timing."""
    script_display = " ".join(cmd_args)
    print(f"\n{'='*80}")
    print(f"Running: {script_display}")
    print(f"Description: {description}")
    print('='*80)
    
    try:
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            timeout=120
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Extract timing from output
        for line in result.stdout.split('\n'):
            if line.startswith('Time:'):
                time_str = line.split(':')[1].strip().split()[0]
                return float(time_str)
        return None
    except subprocess.TimeoutExpired:
        print("TIMEOUT: Benchmark took too long")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    # Change to the python_optimized directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check dependencies
    has_pypy = subprocess.run(["which", "pypy3"], capture_output=True).returncode == 0
    
    # Ensure Cython is compiled
    if not Path("./bench_06_cython").exists():
        print("Compiling Cython benchmark...")
        subprocess.run("cython3 --embed -o bench_06_cython.c bench_06_cython.pyx && gcc -O3 -I/usr/include/python3.10 -o bench_06_cython bench_06_cython.c -lpython3.10", shell=True)

    benchmarks = [
        ([sys.executable, "bench_01_baseline.py"], "01 Baseline - Original implementation"),
        ([sys.executable, "bench_02_inline.py"], "02 Inline function - Call overhead"),
        ([sys.executable, "bench_03_local_cache.py"], "03 Local variable caching"),
        ([sys.executable, "bench_04_loop_unroll.py"], "04 Loop unrolling (10x)"),
        ([sys.executable, "bench_05_pypy.py"], "05 PyPy script (run on CPython)"),
        (["./bench_06_cython"], "06 Cython (Native Compiled)"),
        ([sys.executable, "bench_07_numpy.py"], "07 NumPy (Vectorized Array Demo)"),
        ([sys.executable, "bench_08_refcount_aware.py"], "08 Minimize refcount operations"),
        ([sys.executable, "bench_09_ctypes.py"], "09 ctypes (C interface demo)"),
        ([sys.executable, "bench_10_combined.py"], "10 Combined optimizations"),
    ]
    
    if has_pypy:
        benchmarks.append((["pypy3", "bench_01_baseline.py"], "PyPy 3 JIT - Baseline code run"))
        benchmarks.append((["pypy3", "bench_05_pypy.py"], "PyPy 3 JIT - Dedicated script run"))
    else:
        print("\nNote: pypy3 not found, skipping PyPy benchmarks.")
    
    results = []
    baseline_time = None
    
    print("="*80)
    print("PYTHON OPTIMIZATION EXPERIMENTS")
    print("="*80)
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    for cmd, description in benchmarks:
        script_name = cmd[-1] if cmd[0] != "./bench_06_cython" else cmd[0]
        
        time_taken = run_benchmark(cmd, description)
        
        if time_taken is not None:
            name = " ".join(cmd)
            results.append((name, description, time_taken))
            if baseline_time is None and "bench_01_baseline.py" in name and "python3" in name:
                baseline_time = time_taken
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY OF RESULTS")
    print("="*80)
    print(f"{'Benchmark':<40} {'Time (s)':<12} {'Speedup':<12} {'Description'}")
    print("-"*80)
    
    for name, description, time_taken in results:
        speedup = (baseline_time / time_taken) if baseline_time else 1.0
        speedup_str = f"{speedup:.2f}x"
        print(f"{name:<40} {time_taken:>10.4f}s  {speedup_str:>10}  {description[:30]}")
    
    print("="*80)
    
    # Save results to file
    with open("optimization_results.md", "w") as f:
        f.write("# Python Optimization Experiment Results\n\n")
        f.write(f"**Python Version:** {sys.version}\n\n")
        f.write("| Benchmark | Time (s) | Speedup | Description |\n")
        f.write("|:----------|----------:|--------:|:------------|\n")
        for name, description, time_taken in results:
            speedup = (baseline_time / time_taken) if baseline_time else 1.0
            f.write(f"| `{name}` | {time_taken:.4f} | {speedup:.2f}x | {description} |\n")
    
    print("\nResults saved to: optimization_results.md")

if __name__ == "__main__":
    main()
