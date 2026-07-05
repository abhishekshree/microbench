#!/usr/bin/env python3
"""Regenerate docs/data/benchmarks.json from result files."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "data" / "benchmarks.json"
CACHEGRIND_DIR = ROOT / "results" / "cachegrind"

CACHEGRIND_MAP = {
    "reference_passing": {
        "C++": "cpp_bench.txt",
        "Rust": "rust_bench.txt",
        "Python": "py_bench.txt",
    },
    "allocation": {
        "C++": "cpp_bench_alloc.txt",
        "Rust": "rust_bench_alloc.txt",
        "Python": "py_bench_alloc.txt",
    },
}

DEFAULTS = {
    "environment": {
        "os": "Linux WSL2",
        "cpu": "AMD Ryzen 7 9700X",
        "python": "CPython 3.10.12",
        "compiler_cpp": "g++ 11.4 -O3",
        "compiler_rust": "rustc 1.93 -C opt-level=3",
        "tools": ["hyperfine", "valgrind cachegrind", "perf stat"],
    },
    "cross_language": {
        "reference_passing": {
            "description": "12 MB string, t = f(s), 10M iterations",
            "overhead_split_pct": {"refcount": 45, "indirection": 35, "interpreter": 20},
        },
        "allocation": {
            "description": "prefix_ + i, 1M iterations",
            "overhead_split_pct": {"allocator": 55, "pyobject_creation": 35, "refcount": 10},
        },
    },
    "python_optimized": {
        "description": "Same 12 MB string loop, CPython variants + Cython + PyPy",
        "other_workload": [
            {
                "id": "07",
                "name": "NumPy (vector add)",
                "time_ms": 66.9,
                "speedup": 4.42,
                "instructions_m": 459.1,
                "d1_misses": 8337969,
                "note": "different benchmark",
            }
        ],
    },
}


def parse_num(s: str) -> float:
    return float(s.replace(",", "").strip())


def parse_hyperfine_table(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        if not line.startswith("|") or "Mean" in line or ":---" in line:
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) < 5:
            continue
        cmd, mean, mn, mx, rel = parts[:5]
        lang = "Python"
        if "rust" in cmd.lower():
            lang = "Rust"
        elif "cpp" in cmd.lower():
            lang = "C++"
        m = re.match(r"([\d.]+)\s*±\s*([\d.]+)", mean)
        if not m:
            continue
        rows.append({
            "lang": lang,
            "mean_ms": float(m.group(1)),
            "std_ms": float(m.group(2)),
            "min_ms": float(mn),
            "max_ms": float(mx),
            "relative": float(rel.split()[0]),
        })
    return rows


def parse_cachegrind(path: Path) -> dict | None:
    if not path.is_file():
        return None
    text = path.read_text()
    patterns = {
        "instructions": r"I\s+refs:\s+([\d,]+)",
        "data_refs": r"D\s+refs:\s+([\d,]+)",
        "d1_misses": r"D1\s+misses:\s+([\d,]+)",
        "ll_misses": r"LL\s+misses:\s+([\d,]+)",
        "d1_miss_rate": r"D1\s+miss rate:\s+([\d.]+)%",
        "ll_miss_rate": r"LL\s+miss rate:\s+([\d.]+)%",
    }
    out = {}
    for key, pat in patterns.items():
        m = re.search(pat, text)
        if not m:
            continue
        val = parse_num(m.group(1))
        if key in ("instructions", "data_refs"):
            out[f"{key}_m"] = round(val / 1e6, 1)
        elif key.endswith("_rate"):
            out[key] = val
        else:
            out[key] = int(val)
    return out if out else None


def load_cachegrind(bench: str) -> list[dict]:
    rows = []
    missing = []
    for lang, fname in CACHEGRIND_MAP[bench].items():
        path = CACHEGRIND_DIR / fname
        parsed = parse_cachegrind(path)
        if parsed is None:
            missing.append(fname)
            continue
        rows.append({"lang": lang, **parsed})
    if missing:
        print(f"[warn] missing cachegrind for {bench}: {', '.join(missing)}", file=sys.stderr)
        print(f"       run: make profile", file=sys.stderr)
    return rows


def python_cpp_ratio(cachegrind: list[dict]) -> dict | None:
    by_lang = {r["lang"]: r for r in cachegrind}
    if "Python" not in by_lang or "C++" not in by_lang:
        return None
    py, cpp = by_lang["Python"], by_lang["C++"]

    def ratio(key):
        if key not in py or key not in cpp or cpp[key] == 0:
            return None
        return round(py[key] / cpp[key], 1)

    out = {}
    for k in ("instructions_m", "data_refs_m", "d1_misses", "ll_misses"):
        short = k.replace("_m", "").replace("instructions", "instructions")
        short = {"instructions_m": "instructions", "data_refs_m": "data_refs"}.get(k, k)
        r = ratio(k)
        if r is not None:
            out[short] = r
    return out or None


def parse_perf_report(text: str) -> list[dict]:
    variants = []
    for line in text.splitlines():
        if "Hardware Resource Usage" in line:
            break
        if not line.startswith("|") or "Variant" in line or ":---" in line:
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) < 5:
            continue
        name = parts[0].replace("**", "")
        if not (name.startswith("0") or name.startswith("PyPy")):
            continue
        vid = name.split()[0].lower().replace("pypy3", "pypy")
        group = "jit" if "pypy" in vid else ("native" if "cython" in name.lower() else "cpython")
        variants.append({
            "id": vid,
            "name": name.split(" ", 1)[-1] if " " in name else name,
            "time_ms": float(parts[1]),
            "speedup": float(parts[2].replace("x", "")),
            "instructions_m": float(parts[3]),
            "d1_misses": int(parts[4].replace(",", "")),
            "group": group,
        })
    return variants


def parse_perf_cycles(text: str) -> dict[str, dict]:
    out = {}
    in_perf = False
    for line in text.splitlines():
        if "Hardware Resource Usage" in line:
            in_perf = True
            continue
        if in_perf and line.startswith("## "):
            break
        if not in_perf or not line.startswith("|"):
            continue
        if "Variant" in line or ":---" in line:
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) < 5:
            continue
        key = parts[0].split()[0].lower().replace("pypy3", "pypy")
        out[key] = {"cycles_m": float(parts[1]), "ipc": float(parts[2])}
    return out


def gap_summary(data: dict) -> dict:
    ref = data["cross_language"]["reference_passing"]
    alloc = data["cross_language"]["allocation"]

    def py_vs_fastest(timing):
        py = next(r for r in timing if r["lang"] == "Python")
        fastest = min(r["mean_ms"] for r in timing)
        return round(py["mean_ms"] / fastest, 1)

    out = {
        "wall_clock_ref_pass": py_vs_fastest(ref["timing"]),
        "wall_clock_alloc": py_vs_fastest(alloc["timing"]),
    }
    for bench, key in (("reference_passing", "instructions_ref_pass"),
                       ("allocation", "instructions_alloc")):
        ratio = data["cross_language"][bench].get("python_cpp_ratio", {})
        if "instructions" in ratio:
            out[key] = ratio["instructions"]
    return out


def main():
    data = json.loads(json.dumps(DEFAULTS))

    ref_md = ROOT / "results_bench.md"
    alloc_md = ROOT / "results_bench_alloc.md"
    perf_md = ROOT / "python_optimized" / "PERF_REPORT.md"

    if ref_md.is_file():
        data["cross_language"]["reference_passing"]["timing"] = parse_hyperfine_table(
            ref_md.read_text()
        )
    else:
        print(f"[warn] missing {ref_md}", file=sys.stderr)

    if alloc_md.is_file():
        data["cross_language"]["allocation"]["timing"] = parse_hyperfine_table(
            alloc_md.read_text()
        )
    else:
        print(f"[warn] missing {alloc_md}", file=sys.stderr)

    for bench in ("reference_passing", "allocation"):
        cg = load_cachegrind(bench)
        if cg:
            data["cross_language"][bench]["cachegrind"] = cg
            ratio = python_cpp_ratio(cg)
            if ratio:
                data["cross_language"][bench]["python_cpp_ratio"] = ratio

    if perf_md.is_file():
        perf_text = perf_md.read_text()
        variants = parse_perf_report(perf_text)
        cycles = parse_perf_cycles(perf_text)
        for v in variants:
            cid = v["id"]
            if cid in cycles:
                v.update(cycles[cid])
            if "cython" in v["name"].lower():
                v["group"] = "native"
            if cid == "pypy":
                v["name"] = "PyPy3 JIT"
        data["python_optimized"]["string_comparable"] = [
            v for v in variants if v["id"] not in ("05", "07", "09")
        ]
        base = next((v for v in variants if v["id"] == "01"), None)
        cython = next((v for v in variants if "cython" in v["name"].lower()), None)
        if base and cython and cython["instructions_m"]:
            data["python_optimized"]["cython_instruction_reduction"] = round(
                base["instructions_m"] / cython["instructions_m"], 1
            )
    else:
        print(f"[warn] missing {perf_md}", file=sys.stderr)

    data["gap_summary"] = gap_summary(data)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
