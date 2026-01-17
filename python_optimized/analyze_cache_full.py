import subprocess
import os
import re
import sys
from pathlib import Path

def run_cmd(cmd, capture=True):
    """Run a command and return stdout, stderr, and success status."""
    if isinstance(cmd, list):
        cmd_str = " ".join(cmd)
    else:
        cmd_str = cmd
        
    print(f"\n[RUNNING] {cmd_str}")
    try:
        if capture:
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            return process.stdout, process.stderr, process.returncode == 0
        else:
            process = subprocess.run(cmd, shell=True, timeout=120)
            return "", "", process.returncode == 0
    except Exception as e:
        return "", str(e), False

def parse_valgrind(stderr):
    """Extract metrics from Valgrind Cachegrind output."""
    metrics = {
        'instructions': 0,
        'data_refs': 0,
        'd1_misses': 0,
        'll_misses': 0
    }
    
    # Valgrind output format example:
    # ==24012== I   refs:      79,319,271
    # ==24012== D   refs:      21,761,371  (13,559,670 rd + 8,201,701 wr)
    # ==24012== D1  misses:       202,527  (    12,616 rd +   189,911 wr)
    # ==24012== LL  misses:       199,038  (     9,898 rd +   189,140 wr)
    
    pat_i = re.search(r"I\s+refs:\s+([\d,.]+)", stderr)
    pat_d = re.search(r"D\s+refs:\s+([\d,.]+)", stderr)
    pat_d1 = re.search(r"D1\s+misses:\s+([\d,.]+)", stderr)
    pat_ll = re.search(r"LL\s+misses:\s+([\d,.]+)", stderr)
    
    if pat_i: metrics['instructions'] = int(pat_i.group(1).replace(",", "").replace(".", ""))
    if pat_d: metrics['data_refs'] = int(pat_d.group(1).replace(",", "").replace(".", ""))
    if pat_d1: metrics['d1_misses'] = int(pat_d1.group(1).replace(",", "").replace(".", ""))
    if pat_ll: metrics['ll_misses'] = int(pat_ll.group(1).replace(",", "").replace(".", ""))
    
    return metrics

def parse_perf(stderr):
    """Extract metrics from Perf Stat output."""
    metrics = {
        'instructions': 0,
        'cycles': 0,
        'cache_misses': 0,
        'l1_misses': 0
    }
    
    # Perf output format example:
    # 79,319,271      instructions
    # 21,761,371      cycles
    
    pat_i = re.search(r"([\d,.]+)\s+instructions", stderr)
    pat_c = re.search(r"([\d,.]+)\s+cycles", stderr)
    pat_cm = re.search(r"([\d,.]+)\s+cache-misses", stderr)
    pat_l1 = re.search(r"([\d,.]+)\s+L1-dcache-load-misses", stderr)
    
    if pat_i: metrics['instructions'] = int(pat_i.group(1).replace(",", "").replace(".", ""))
    if pat_c: metrics['cycles'] = int(pat_c.group(1).replace(",", "").replace(".", ""))
    if pat_cm: metrics['cache_misses'] = int(pat_cm.group(1).replace(",", "").replace(".", ""))
    if pat_l1: metrics['l1_misses'] = int(pat_l1.group(1).replace(",", "").replace(".", ""))
    
    return metrics

def main():
    os.chdir('/home/shree/microbench/python_optimized')
    
    # Compile Cython if needed
    if not Path("./bench_06_cython").exists():
        print("Compiling Cython...")
        run_cmd("cython3 --embed -o bench_06_cython.c bench_06_cython.pyx && gcc -O3 -I/usr/include/python3.10 -o bench_06_cython bench_06_cython.c -lpython3.10")

    benchmarks = [
        ("CPython Baseline", "python3 bench_01_baseline.py"),
        ("CPython Inline", "python3 bench_02_inline.py"),
        ("CPython LocalCache", "python3 bench_03_local_cache.py"),
        ("CPython LoopUnroll", "python3 bench_04_loop_unroll.py"),
        ("CPython PyPyScript", "python3 bench_05_pypy.py"),
        ("Cython Native", "./bench_06_cython"),
        ("CPython NumPy", "python3 bench_07_numpy.py"),
        ("CPython Refcount", "python3 bench_08_refcount_aware.py"),
        ("CPython ctypes", "python3 bench_09_ctypes.py"),
        ("CPython Combined", "python3 bench_10_combined.py"),
        ("PyPy Baseline", "pypy3 bench_01_baseline.py"),
    ]
    
    all_results = []
    
    for name, cmd in benchmarks:
        print(f"\n--- Analyzing {name} ---")
        
        # 1. Run Valgrind
        _, vg_stderr, ok = run_cmd(f"valgrind --tool=cachegrind --cachegrind-out-file=/tmp/cg.out {cmd}")
        vg_metrics = parse_valgrind(vg_stderr) if ok else {}
        
        # 2. Run Perf (might fail on WSL2 without proper setup, but we try)
        _, perf_stderr, ok = run_cmd(f"perf stat -e instructions,cycles,cache-misses,L1-dcache-load-misses {cmd}")
        perf_metrics = parse_perf(perf_stderr) if ok else {}
        
        all_results.append({
            'name': name,
            'valgrind': vg_metrics,
            'perf': perf_metrics
        })

    # Generate Markdown Report
    report = "# Full Cache & Performance Analysis: 10 Variants\n\n"
    report += "This report summarizes the hardware-level efficiency of various Python optimization strategies.\n\n"
    
    report += "## 1. Valgrind Cachegrind Analysis (Instruction & Cache Efficiency)\n\n"
    report += "| Variant | Instructions (M) | Data Refs (M) | D1 Misses | LL Misses |\n"
    report += "|:---|---:|---:|---:|---:|\n"
    
    for res in all_results:
        vg = res['valgrind']
        if vg:
            report += f"| {res['name']} | {vg['instructions']/1e6:.1f} | {vg['data_refs']/1e6:.1f} | {vg['d1_misses']:,} | {vg['ll_misses']:,} |\n"
        else:
            report += f"| {res['name']} | N/A | N/A | N/A | N/A |\n"

    report += "\n## 2. Perf Stat Analysis (Cycles & CPU Events)\n\n"
    report += "| Variant | Instructions (M) | Cycles (M) | Cache Misses | L1 D-Cache Misses |\n"
    report += "|:---|---:|---:|---:|---:|\n"
    
    has_perf = False
    for res in all_results:
        p = res['perf']
        if p and p['instructions'] > 0:
            has_perf = True
            report += f"| {res['name']} | {p['instructions']/1e6:.1f} | {p['cycles']/1e6:.1f} | {p['cache_misses']:,} | {p['l1_misses']:,} |\n"
        else:
            report += f"| {res['name']} | N/A | N/A | N/A | N/A |\n"
            
    if not has_perf:
        report += "\n*Note: Perf was unable to collect hardware counters (common in WSL2 without specialized setup). Falling back to Valgrind for analysis.*\n"

    report += "\n## 3. Comparative Observations\n\n"
    
    # Find bests
    valid_vg = [r for r in all_results if r['valgrind']]
    if valid_vg:
        best_instr = min(valid_vg, key=lambda x: x['valgrind']['instructions'])
        report += f"- **Fewest Instructions**: `{best_instr['name']}` ({best_instr['valgrind']['instructions']/1e6:.1f}M)\n"
        
        baseline = next(r for r in valid_vg if r['name'] == "CPython Baseline")
        reduction = (baseline['valgrind']['instructions'] - best_instr['valgrind']['instructions']) / baseline['valgrind']['instructions'] * 100
        report += f"  - A **{reduction:.1f}% reduction** from baseline.\n"
        
        best_cache = min(valid_vg, key=lambda x: x['valgrind']['d1_misses'])
        report += f"- **Most Cache Efficient (L1)**: `{best_cache['name']}` ({best_cache['valgrind']['d1_misses']:,} misses)\n"

    with open("CACHE_PERF_ANALYSIS.md", "w") as f:
        f.write(report)
        
    print("\n[COMPLETE] Detailed cache analysis saved to: CACHE_PERF_ANALYSIS.md")

if __name__ == "__main__":
    main()
