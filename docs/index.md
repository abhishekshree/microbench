---
hide:
  - toc
---

<div class="hero" markdown>

# Same loop, three languages

We run `t = f(s)` ten million times on a 12 MB string in Python, C++, and Rust.

Python spends most of its time on refcount writes and interpreter dispatch, not on copying the string bytes. The numbers are from measured runs on one machine. Use them to learn mechanisms, not to pick a language.

[Reference passing](benchmarks/reference-passing.md) · [Allocation](benchmarks/allocation.md) · [How we measured](methodology.md)

<div id="env-pills"></div>

</div>

<div id="stat-row" class="stat-row"></div>

<div class="section-block" id="results" markdown>

## Results

Wall-clock from [hyperfine](methodology.md#hyperfine-wall-clock) (3 warmup runs). Instruction counts from [cachegrind](methodology.md#valgrind-cachegrind-simulated-cache) simulation. Ratios matter, not absolute valgrind time.

</div>

<div class="chart-grid wide">
  <div class="chart-card tall">
    <h3>Where the gap closes</h3>
    <p class="chart-takeaway">Each bar shows how many times slower Python is than the fastest native language on that benchmark. Red and orange are wall-clock time (hyperfine). Purple and blue are simulated instruction counts (cachegrind).</p>
    <canvas id="chart-gap"></canvas>
    <ul class="bar-legend">
      <li><span class="swatch" style="background:#ef4444"></span>Wall, ref-pass: 10M× <code>t = f(s)</code> on one 12 MB string; Python vs Rust</li>
      <li><span class="swatch" style="background:#f97316"></span>Wall, alloc: 1M× build a new short string; Python vs C++</li>
      <li><span class="swatch" style="background:#8b5cf6"></span>Instr, ref-pass: same loop, instruction count under cachegrind</li>
      <li><span class="swatch" style="background:#6366f1"></span>Instr, alloc: same loop, instruction count under cachegrind</li>
    </ul>
  </div>
</div>

### Reference passing

One 12 MB string is built once. The loop only reassigns a reference: `t = f(s)` where `f` returns the same string. Nothing new is allocated, so the cost is mostly interpreter work and refcount traffic.

<div class="chart-grid">
  <div class="chart-card">
    <h3>Wall clock · 12 MB string · 10M loops</h3>
    <p class="chart-takeaway">Rust and C++ are close enough to call a tie; Python pays interpreter and refcount cost on every iteration.</p>
    <canvas id="chart-ref-timing"></canvas>
  </div>
  <div class="chart-card">
    <h3>Instructions executed (simulated)</h3>
    <p class="chart-takeaway">About 111× more instructions, mostly bytecode and refcount traffic rather than copying string bytes.</p>
    <canvas id="chart-ref-instr"></canvas>
  </div>
</div>

### Allocation

Each iteration builds a fresh short string (`"prefix_" + str(i)`). Everyone hits the allocator; Python's extra PyObject header still hurts, but the gap is much smaller than ref-pass.

<div class="chart-grid">
  <div class="chart-card">
    <h3>Wall clock · new string each iter · 1M loops</h3>
    <p class="chart-takeaway">The gap shrinks to about 7× once pymalloc and C++ SSO do real allocation work.</p>
    <canvas id="chart-alloc-timing"></canvas>
  </div>
  <div class="chart-card">
    <h3>Instructions executed (simulated)</h3>
    <p class="chart-takeaway">The instruction ratio falls from about 111× to about 7× when allocation dominates.</p>
    <canvas id="chart-alloc-instr"></canvas>
  </div>
</div>

<div class="section-links" markdown>

[Full ref-pass breakdown →](benchmarks/reference-passing.md) · [Full allocation breakdown →](benchmarks/allocation.md) · [Raw timing tables on GitHub](https://github.com/abhishekshree/microbench/blob/main/results_bench.md)

</div>

<div class="section-block" id="why" markdown>

## Why Python loses on this loop

- C++/Rust: `t = f(s)` copies an 8-byte stack pointer. No heap write.
- Python: every assignment INCREF/DECREF the `PyUnicodeObject`, a read-modify-write on `ob_refcnt` that dirties a cache line shared with type metadata.
- The 12 MB string is on purpose: same heap layout in all three languages (too big for C++ small-string optimization), so the test measures refcount and dispatch, not copy cost.

[Full walkthrough with memory diagrams →](benchmarks/reference-passing.md#what-one-assignment-costs)

</div>

<div class="section-block" id="python-opt" markdown>

## Python variants

Same 12 MB loop with source-level tricks (inline, unroll, Cython, PyPy). Green = CPython. Purple = Cython. Yellow = PyPy.

</div>

<div class="chart-grid wide">
  <div class="chart-card">
    <h3>Wall time by variant</h3>
    <p class="chart-takeaway">Inlining removes the call (about 3×). Cython cuts bytecode overhead (about 21×). L1 misses stay flat because PyObjects still live on the heap.</p>
    <canvas id="chart-py-time"></canvas>
  </div>
</div>

<div class="section-links" markdown>

[All variant charts and source →](python-optimizations.md)

</div>

<div class="section-block" id="reproduce" markdown>

## Reproduce

```bash
make results && make docs-serve
```

| Topic | Page |
|:--|:--|
| Reference passing code | [benchmarks/reference-passing.md](benchmarks/reference-passing.md) |
| Allocation code | [benchmarks/allocation.md](benchmarks/allocation.md) |
| Python optimizations | [python-optimizations.md](python-optimizations.md) |
| Measurement pipeline | [methodology.md](methodology.md) |
| Written analysis | [PERFORMANCE_ANALYSIS.md](https://github.com/abhishekshree/microbench/blob/main/PERFORMANCE_ANALYSIS.md) |

Charts load from `docs/data/benchmarks.json`, rebuilt by `make results-json`.

</div>
