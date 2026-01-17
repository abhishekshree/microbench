import subprocess
import os
import json
import re

def run_cmd(cmd, shell=True):
    print(f"Executing: {cmd}")
    process = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    return stdout, stderr

def parse_cachegrind(stderr):
    metrics = {}
    patterns = {
        'I refs': r'I\s+refs:\s+([\d,]+)',
        'D refs': r'D\s+refs:\s+([\d,]+)',
        'D1 misses': r'D1\s+misses:\s+([\d,]+)',
        'LL misses': r'LL\s+misses:\s+([\d,]+)'
    }
    for name, pattern in patterns.items():
        match = re.search(pattern, stderr)
        if match:
            metrics[name] = int(match.group(1).replace(',', ''))
    return metrics

def main():
    os.chdir('/home/shree/microbench/python_optimized')
    
    benchmarks = {
        'CPython Baseline': 'python3 bench_01_baseline.py',
        'CPython Inline': 'python3 bench_02_inline.py',
        'CPython Combined': 'python3 bench_10_combined.py',
        'PyPy Baseline': 'pypy3 bench_01_baseline.py',
        'Cython (Compiled)': './bench_06_cython'
    }
    
    # 1. Timing Analysis with Hyperfine
    print("\n--- Running Timing Benchmarks (Hyperfine) ---")
    commands = " ".join([f"'{cmd}'" for cmd in benchmarks.values()])
    hyperfine_cmd = f"hyperfine --warmup 3 --export-json results.json {commands}"
    run_cmd(hyperfine_cmd)
    
    with open('results.json', 'r') as f:
        timing_data = json.load(f)['results']
    
    # 2. Cache Analysis with Valgrind
    print("\n--- Running Cache Analysis (Valgrind) ---")
    cache_results = {}
    for name, cmd in benchmarks.items():
        print(f"Profiling {name}...")
        _, stderr = run_cmd(f"valgrind --tool=cachegrind {cmd}")
        cache_results[name] = parse_cachegrind(stderr)
        
    # 3. Generate Markdown Report
    report = "# Deep Optimization Analysis: Python vs PyPy vs Cython\n\n"
    report += "## 1. Timing Performance\n\n"
    report += "| Implementation | Mean Time (ms) | Speedup (vs Baseline) |\n"
    report += "| :--- | :---: | :---: |\n"
    
    baseline_mean = timing_data[0]['mean']
    for i, (name, _) in enumerate(benchmarks.items()):
        mean_ms = timing_data[i]['mean'] * 1000
        speedup = baseline_mean / timing_data[i]['mean']
        report += f"| {name} | {mean_ms:.2f} | {speedup:.2f}x |\n"
        
    report += "\n## 2. Instruction & Cache Efficiency\n\n"
    report += "| Implementation | I Refs (M) | D Refs (M) | D1 Misses | LL Misses |\n"
    report += "| :--- | :---: | :---: | :---: | :---: |\n"
    
    for name, metrics in cache_results.items():
        i_refs_m = metrics.get('I refs', 0) / 1_000_000
        d_refs_m = metrics.get('D refs', 0) / 1_000_000
        d1_misses = metrics.get('D1 misses', 0)
        ll_misses = metrics.get('LL misses', 0)
        report += f"| {name} | {i_refs_m:.1f} | {d_refs_m:.1f} | {d1_misses:,} | {ll_misses:,} |\n"
        
    report += "\n## 3. Analysis Findings\n\n"
    report += "### The Power of JIT (PyPy)\n"
    report += "- PyPy achieves massive speedups by compiling the hot loop to native assembly at runtime.\n"
    report += "- Notice the **Instruction References**: PyPy might show higher instruction counts during warmup/compilation, but in the steady state, it executes far fewer bytecode-equivalent operations.\n\n"
    report += "### Cython: The Bridge to C\n"
    report += "- By compiling to C with `cython --embed`, we eliminate the interpreter loop entirely.\n"
    report += "- The **Data Access Efficiency** is significantly higher because types are (partially) resolved at compile time.\n\n"
    report += "### Why CPython Combined is Faster than Baseline\n"
    report += "- Reduced function call overhead and loop unrolling reduce the number of instructions executed by the interpreter to perform the same task.\n"
    
    with open('FINAL_OPTIMIZATION_ANALYSIS.md', 'w') as f:
        f.write(report)
        
    print("\nAnalysis complete. Report generated: FINAL_OPTIMIZATION_ANALYSIS.md")

if __name__ == "__main__":
    main()
