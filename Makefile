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

.PHONY: all clean bench_languages bench_python profile analyze

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

profile: all
	@echo "=== Generating Cache Statistics ==="
	valgrind --tool=cachegrind --cachegrind-out-file=/tmp/cg_cpp.out ./$(CPP_BIN)
	valgrind --tool=cachegrind --cachegrind-out-file=/tmp/cg_py.out $(PY) python/bench.py

clean:
	rm -f $(CPP_BIN) $(CPP_ALLOC_BIN) $(RUST_BIN) $(RUST_ALLOC_BIN)
	rm -f python_optimized/bench_06_cython.c python_optimized/bench_06_cython
	rm -f cachegrind.out.* /tmp/cg_*.out
	rm -f python_optimized/hf_results.json
