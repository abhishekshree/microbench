CC = g++
CFLAGS = -O3 -std=c++17
RUSTC = rustc
RUSTFLAGS = -C opt-level=3
PY = python3
CYTHON = cython3

# Targets
CPP_BIN = cpp/bench
CPP_ALLOC_BIN = cpp/bench_alloc
RUST_BIN = rust/bench
RUST_ALLOC_BIN = rust/bench_alloc
CYTHON_BIN = python_optimized/bench_06_cython

CACHEGRIND_DIR = results/cachegrind
RESULTS_JSON = docs/data/benchmarks.json

CACHEGRIND_TXTS = \
	$(CACHEGRIND_DIR)/cpp_bench.txt \
	$(CACHEGRIND_DIR)/rust_bench.txt \
	$(CACHEGRIND_DIR)/py_bench.txt \
	$(CACHEGRIND_DIR)/cpp_bench_alloc.txt \
	$(CACHEGRIND_DIR)/rust_bench_alloc.txt \
	$(CACHEGRIND_DIR)/py_bench_alloc.txt

.PHONY: all clean bench_languages bench_python profile cachegrind \
        results-json docs-serve docs-build results

all: $(CPP_BIN) $(CPP_ALLOC_BIN) $(RUST_BIN) $(RUST_ALLOC_BIN)

$(CPP_BIN): cpp/bench.cpp
	$(CC) $(CFLAGS) -o $@ $<

$(CPP_ALLOC_BIN): cpp/bench_alloc.cpp
	$(CC) $(CFLAGS) -o $@ $<

$(RUST_BIN): rust/bench.rs
	$(RUSTC) $(RUSTFLAGS) -o $@ $<

$(RUST_ALLOC_BIN): rust/bench_alloc.rs
	$(RUSTC) $(RUSTFLAGS) -o $@ $<

# Run language comparison (C++ vs Rust vs Python Baseline)
bench_languages: all
	@echo "=== Running Cross-Language Benchmarks ==="
	@echo "--- Python Baseline ---"
	@$(PY) python/bench.py
	@echo "--- C++ ---"
	@./$(CPP_BIN)
	@echo "--- Rust ---"
	@./$(RUST_BIN)
	@echo "\n=== Running Allocation Benchmarks ==="
	@$(PY) python/bench_alloc.py
	@./$(CPP_ALLOC_BIN)
	@./$(RUST_ALLOC_BIN)

# Run Python Optimization Suite
bench_python:
	@echo "=== Running Python Optimization Benchmarks ==="
	@$(PY) python_optimized/benchmark_python.py

# valgrind cachegrind -> results/cachegrind/*.txt (stderr summaries)
$(CACHEGRIND_DIR):
	mkdir -p $@

$(CACHEGRIND_DIR)/cpp_bench.txt: $(CPP_BIN) | $(CACHEGRIND_DIR)
	valgrind --tool=cachegrind --cachegrind-out-file=$(CACHEGRIND_DIR)/cpp_bench.out ./$(CPP_BIN) 2>&1 | tee $@

$(CACHEGRIND_DIR)/rust_bench.txt: $(RUST_BIN) | $(CACHEGRIND_DIR)
	valgrind --tool=cachegrind --cachegrind-out-file=$(CACHEGRIND_DIR)/rust_bench.out ./$(RUST_BIN) 2>&1 | tee $@

$(CACHEGRIND_DIR)/py_bench.txt: python/bench.py | $(CACHEGRIND_DIR)
	valgrind --tool=cachegrind --cachegrind-out-file=$(CACHEGRIND_DIR)/py_bench.out $(PY) python/bench.py 2>&1 | tee $@

$(CACHEGRIND_DIR)/cpp_bench_alloc.txt: $(CPP_ALLOC_BIN) | $(CACHEGRIND_DIR)
	valgrind --tool=cachegrind --cachegrind-out-file=$(CACHEGRIND_DIR)/cpp_bench_alloc.out ./$(CPP_ALLOC_BIN) 2>&1 | tee $@

$(CACHEGRIND_DIR)/rust_bench_alloc.txt: $(RUST_ALLOC_BIN) | $(CACHEGRIND_DIR)
	valgrind --tool=cachegrind --cachegrind-out-file=$(CACHEGRIND_DIR)/rust_bench_alloc.out ./$(RUST_ALLOC_BIN) 2>&1 | tee $@

$(CACHEGRIND_DIR)/py_bench_alloc.txt: python/bench_alloc.py | $(CACHEGRIND_DIR)
	valgrind --tool=cachegrind --cachegrind-out-file=$(CACHEGRIND_DIR)/py_bench_alloc.out $(PY) python/bench_alloc.py 2>&1 | tee $@

profile: cachegrind

cachegrind: $(CACHEGRIND_TXTS)
	@echo "=== Cachegrind summaries in $(CACHEGRIND_DIR)/ ==="

# Regenerate docs/data/benchmarks.json from hyperfine md + cachegrind txt + PERF_REPORT
results-json: $(RESULTS_JSON)

$(RESULTS_JSON): results_bench.md results_bench_alloc.md python_optimized/PERF_REPORT.md scripts/build_results_json.py
	$(PY) scripts/build_results_json.py

# Convenience: cachegrind + json refresh
results: cachegrind results-json

docs-build: results-json
	mkdocs build

docs-serve: results-json
	mkdocs serve

clean:
	rm -f $(CPP_BIN) $(CPP_ALLOC_BIN) $(RUST_BIN) $(RUST_ALLOC_BIN)
	rm -f python_optimized/bench_06_cython.c python_optimized/bench_06_cython
	rm -f cachegrind.out.* /tmp/cg_*.out
	rm -f python_optimized/hf_results.json

clean-results:
	rm -rf $(CACHEGRIND_DIR)
