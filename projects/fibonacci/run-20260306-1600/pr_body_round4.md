## Round 4: Use gmpy2.fib() built-in

### Changes
- Replaced custom fast doubling loop with `gmpy2.fib()` which calls GMP's `mpz_fib_ui`
- GMP's internal implementation uses optimized binary splitting with tuned thresholds
- Simplified code from 10 lines to 1 line

### Test Results

| Metric | Round 3 | Round 4 | Speedup |
|--------|---------|---------|---------|
| Tests Passed | 19/19 | 19/19 | - |
| fib(100000) | 0.16ms | 0.07ms | 2.3x |
| fib(500000) | 1.31ms | 0.64ms | 2.0x |
| fib(1000000) | 2.39ms | 1.33ms | 1.8x |

### Phase: Performance

### Verdict: ACCEPT

All tests pass. ~2x improvement by leveraging GMP's built-in Fibonacci which has hand-tuned assembly and optimized memory allocation patterns.
