## Round 3: Performance Optimization with gmpy2

### Changes
- Added gmpy2 dependency for GMP-backed bigint arithmetic
- Fast doubling now uses `mpz` type when gmpy2 is available
- Falls back to pure Python implementation if gmpy2 not installed

### Test Results

| Metric | Before | After | Speedup |
|--------|--------|-------|---------|
| Tests Passed | 19/19 | 19/19 | - |
| fib(10000) | 0.04ms | 0.01ms | 4x |
| fib(100000) | 1.00ms | 0.16ms | 6.3x |
| fib(500000) | 11.70ms | 1.31ms | 8.9x |
| fib(1000000) | 34.30ms | 2.39ms | 14.4x |

### Phase: Performance

### Verdict: ACCEPT

All tests pass. GMP's optimized bigint multiplication (Karatsuba, Toom-Cook, FFT) provides 6-14x speedup over Python's built-in int for large N. Graceful fallback to pure Python if gmpy2 is unavailable.
