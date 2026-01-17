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

.PHONY: all clean bench profile analyze

all: $(CPP_BIN) $(CPP_ALLOC_BIN) $(RUST_BIN) $(RUST_ALLOC_BIN) $(CYTHON_BIN)

$(CPP_BIN): cpp/bench.cpp
	$(CC) $(CFLAGS) -o $@ $<

$(CPP_ALLOC_BIN): cpp/bench_alloc.cpp
	$(CC) $(CFLAGS) -o $@ $<

$(RUST_BIN): rust/bench.rs
	$(RUSTC) $(RUSTFLAGS) -o $@ $<

$(RUST_ALLOC_BIN): rust/bench_alloc.rs
	$(RUSTC) $(RUSTFLAGS) -o $@ $<

$(CYTHON_BIN): python_optimized/bench_06_cython.pyx
	$(CYTHON) --embed -o python_optimized/bench_06_cython.c $<
	$(CC) $(CFLAGS) -I/usr/include/python3.10 -o $@ python_optimized/bench_06_cython.c -lpython3.10

bench: all
	@echo "=== Running Baseline Benchmarks ==="
	@$(PY) python/bench.py
	@./$(CPP_BIN)
	@./$(RUST_BIN)
	@echo "\n=== Running Allocation Benchmarks ==="
	@$(PY) python/bench_alloc.py
	@./$(CPP_ALLOC_BIN)
	@./$(RUST_ALLOC_BIN)

profile: all
	@echo "=== Generating Cache Statistics ==="
	valgrind --tool=cachegrind --cachegrind-out-file=/tmp/cg_cpp.out ./$(CPP_BIN)
	valgrind --tool=cachegrind --cachegrind-out-file=/tmp/cg_py.out $(PY) python/bench.py

clean:
	rm -f $(CPP_BIN) $(CPP_ALLOC_BIN) $(RUST_BIN) $(RUST_ALLOC_BIN) $(CYTHON_BIN)
	rm -f python_optimized/bench_06_cython.c
	rm -f cachegrind.out.*
