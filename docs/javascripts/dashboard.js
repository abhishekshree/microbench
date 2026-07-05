(function () {
  const COLORS = {
    rust: "#f97316",
    cpp: "#3b82f6",
    python: "#22c55e",
    cpython: "#22c55e",
    native: "#6366f1",
    jit: "#eab308",
    other: "#94a3b8",
    grid: "rgba(128,128,128,0.15)",
    text: "rgba(128,128,128,0.7)",
  };

  const LANG_COLORS = { Rust: COLORS.rust, "C++": COLORS.cpp, Python: COLORS.python };

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function chartDefaults() {
    Chart.defaults.color = cssVar("--md-default-fg-color--light") || COLORS.text;
    Chart.defaults.borderColor = COLORS.grid;
    Chart.defaults.font.family = "inherit";
  }

  function benchmarksJsonUrl() {
    const script = document.querySelector('script[src*="dashboard.js"]');
    if (script) return new URL("../data/benchmarks.json", script.src).href;
    return new URL("data/benchmarks.json", document.baseURI).href;
  }

  function barChart(id, labels, datasets, opts) {
    const el = document.getElementById(id);
    if (!el) return;
    const existing = Chart.getChart(el);
    if (existing) existing.destroy();
    new Chart(el, {
      type: "bar",
      data: { labels, datasets },
      options: Object.assign(
        {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { display: datasets.length > 1 },
            tooltip: { mode: "index", intersect: false },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: COLORS.grid },
              ticks: opts && opts.logY ? { callback: (v) => formatNum(v) } : {},
            },
            x: { grid: { display: false } },
          },
        },
        opts || {}
      ),
    });
  }

  function formatNum(n) {
    if (n >= 1e9) return (n / 1e9).toFixed(1) + "B";
    if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
    if (n >= 1e3) return (n / 1e3).toFixed(1) + "K";
    return n;
  }

  function pieChart(id, labels, values, colors) {
    const el = document.getElementById(id);
    if (!el) return;
    const existing = Chart.getChart(el);
    if (existing) existing.destroy();
    new Chart(el, {
      type: "doughnut",
      data: {
        labels,
        datasets: [{ data: values, backgroundColor: colors, borderWidth: 0 }],
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "right", labels: { boxWidth: 12 } } },
      },
    });
  }

  function timingChart(id, rows) {
    barChart(
      id,
      rows.map((r) => r.lang),
      [
        {
          label: "mean ms",
          data: rows.map((r) => r.mean_ms),
          backgroundColor: rows.map((r) => LANG_COLORS[r.lang] || COLORS.other),
          borderRadius: 6,
        },
        {
          label: "± std",
          data: rows.map((r) => r.std_ms),
          backgroundColor: rows.map((r) => (LANG_COLORS[r.lang] || COLORS.other) + "55"),
          borderRadius: 6,
        },
      ],
      { plugins: { legend: { display: true } } }
    );
  }

  function cacheMetricChart(id, rows, field, label, logY) {
    barChart(
      id,
      rows.map((r) => r.lang),
      [
        {
          label,
          data: rows.map((r) => r[field]),
          backgroundColor: rows.map((r) => LANG_COLORS[r.lang] || COLORS.other),
          borderRadius: 6,
        },
      ],
      logY ? { scales: { y: { type: "logarithmic", min: 1 } } } : {}
    );
  }

  function ratioChart(id, ratios) {
    barChart(
      id,
      Object.keys(ratios),
      [
        {
          label: "Python / C++",
          data: Object.values(ratios),
          backgroundColor: "#ef4444",
          borderRadius: 6,
        },
      ]
    );
  }

  function pyOptChart(id, variants, field, label, logY) {
    const groupColor = { cpython: COLORS.cpython, native: COLORS.native, jit: COLORS.jit };
    barChart(
      id,
      variants.map((v) => v.name),
      [
        {
          label,
          data: variants.map((v) => v[field]),
          backgroundColor: variants.map((v) => groupColor[v.group] || COLORS.other),
          borderRadius: 5,
        },
      ],
      {
        scales: {
          y: logY ? { type: "logarithmic", min: 1 } : { beginAtZero: true },
          x: { ticks: { maxRotation: 45, minRotation: 25, font: { size: 10 } } },
        },
      }
    );
  }

  function gapChart(id, summary) {
    barChart(
      id,
      [
        "Wall clock · ref-pass",
        "Wall clock · alloc",
        "Instructions · ref-pass",
        "Instructions · alloc",
      ],
      [
        {
          label: "× slower (Python vs fastest native)",
          data: [
            summary.wall_clock_ref_pass,
            summary.wall_clock_alloc,
            summary.instructions_ref_pass,
            summary.instructions_alloc,
          ],
          backgroundColor: ["#ef4444", "#f97316", "#8b5cf6", "#6366f1"],
          borderRadius: 6,
        },
      ],
      {
        plugins: {
          tooltip: {
            callbacks: {
              afterLabel(ctx) {
                const hints = [
                  "hyperfine · t = f(s) on 12 MB string",
                  "hyperfine · new short string each loop",
                  "cachegrind · simulated instruction count",
                  "cachegrind · simulated instruction count",
                ];
                return hints[ctx.dataIndex] || "";
              },
            },
          },
        },
        scales: {
          x: { ticks: { maxRotation: 30, minRotation: 20, font: { size: 10 } } },
        },
      }
    );
  }

  function renderStats(data) {
    const el = document.getElementById("stat-row");
    if (!el) return;
    const g = data.gap_summary;
    const cards = [
      { label: "String passing", value: g.wall_clock_ref_pass + "×", sub: "slower than Rust (wall clock)" },
      { label: "Allocating strings", value: g.wall_clock_alloc + "×", sub: "slower than C++ (wall clock)" },
      { label: "Bytecode cost", value: g.instructions_ref_pass + "×", sub: "more instructions (ref-pass)" },
    ];
    el.innerHTML = cards
      .map(
        (c) =>
          `<div class="stat-card"><div class="label">${c.label}</div><div class="value">${c.value}</div><div class="sub">${c.sub}</div></div>`
      )
      .join("");
  }

  function renderEnv(data) {
    const el = document.getElementById("env-pills");
    if (!el) return;
    const e = data.environment;
    const pills = [e.cpu, e.os, e.python, e.compiler_cpp, e.compiler_rust];
    el.innerHTML = pills.map((p) => `<span class="env-pill">${p}</span>`).join("");
  }

  async function init() {
    if (typeof Chart === "undefined") return;
    chartDefaults();

    const url = benchmarksJsonUrl();
    const res = await fetch(url);
    if (!res.ok) return;
    const data = await res.json();

    renderStats(data);
    renderEnv(data);

    const ref = data.cross_language.reference_passing;
    const alloc = data.cross_language.allocation;
    const py = data.python_optimized.string_comparable;

    timingChart("chart-ref-timing", ref.timing);
    timingChart("chart-alloc-timing", alloc.timing);

    cacheMetricChart("chart-ref-instr", ref.cachegrind, "instructions_m", "instructions (M)", true);
    cacheMetricChart("chart-ref-data", ref.cachegrind, "data_refs_m", "data refs (M)", true);
    cacheMetricChart("chart-ref-d1", ref.cachegrind, "d1_misses", "L1 data misses", false);
    cacheMetricChart("chart-ref-ll", ref.cachegrind, "ll_misses", "LL cache misses", false);

    cacheMetricChart("chart-alloc-instr", alloc.cachegrind, "instructions_m", "instructions (M)", true);
    cacheMetricChart("chart-alloc-d1", alloc.cachegrind, "d1_misses", "L1 data misses", true);
    cacheMetricChart("chart-alloc-ll", alloc.cachegrind, "ll_misses", "LL cache misses", false);

    ratioChart("chart-ref-ratio", ref.python_cpp_ratio);
    ratioChart("chart-alloc-ratio", alloc.python_cpp_ratio);
    gapChart("chart-gap", data.gap_summary);

    pieChart(
      "chart-ref-overhead",
      ["refcount", "indirection", "interpreter"],
      Object.values(ref.overhead_split_pct),
      ["#ef4444", "#f97316", "#6366f1"]
    );
    pieChart(
      "chart-alloc-overhead",
      ["allocator", "PyObject init", "refcount"],
      Object.values(alloc.overhead_split_pct),
      ["#3b82f6", "#22c55e", "#eab308"]
    );

    pyOptChart("chart-py-time", py, "time_ms", "time (ms)", false);
    pyOptChart("chart-py-speedup", py, "speedup", "speedup vs baseline", false);
    pyOptChart("chart-py-instr", py, "instructions_m", "instructions (M)", true);
    pyOptChart("chart-py-d1", py, "d1_misses", "L1 misses", false);
    pyOptChart("chart-py-cycles", py, "cycles_m", "cycles (M)", false);
    pyOptChart("chart-py-ipc", py, "ipc", "IPC", false);
  }

  document$.subscribe(init);
})();
