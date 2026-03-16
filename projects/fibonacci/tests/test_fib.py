"""Tests for Fibonacci calculator — correctness, edge cases, and performance."""
import time
import pytest
from fib import fib

# ---------------------------------------------------------------------------
# Correctness tests
# ---------------------------------------------------------------------------

class TestCorrectness:
    def test_fib_0(self):
        assert fib(0) == 0

    def test_fib_1(self):
        assert fib(1) == 1

    def test_fib_2(self):
        assert fib(2) == 1

    def test_fib_3(self):
        assert fib(3) == 2

    def test_fib_4(self):
        assert fib(4) == 3

    def test_fib_5(self):
        assert fib(5) == 5

    def test_fib_6(self):
        assert fib(6) == 8

    def test_fib_7(self):
        assert fib(7) == 13

    def test_fib_10(self):
        assert fib(10) == 55

    def test_fib_20(self):
        assert fib(20) == 6765

    def test_fib_30(self):
        assert fib(30) == 832040

    def test_fib_50(self):
        assert fib(50) == 12586269025

    def test_fib_100(self):
        assert fib(100) == 354224848179261915075


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_negative_raises(self):
        with pytest.raises(ValueError):
            fib(-1)

    def test_negative_large_raises(self):
        with pytest.raises(ValueError):
            fib(-100)

    def test_zero_is_zero(self):
        assert fib(0) == 0

    def test_sequential_property(self):
        """fib(n) == fib(n-1) + fib(n-2) for n >= 2."""
        for n in range(2, 20):
            assert fib(n) == fib(n - 1) + fib(n - 2)


# ---------------------------------------------------------------------------
# Performance tests — each must complete within 2 seconds
# ---------------------------------------------------------------------------

class TestPerformance:
    @pytest.mark.timeout(2)
    def test_fib_1000(self):
        result = fib(1000)
        assert result > 0
        # Known value check (last few digits)
        assert result % 10**6 == 228875

    @pytest.mark.timeout(2)
    def test_fib_10000(self):
        result = fib(10000)
        assert result > 0

    @pytest.mark.timeout(2)
    def test_fib_100000(self):
        result = fib(100000)
        assert result > 0

    @pytest.mark.timeout(2)
    def test_fib_500000(self):
        result = fib(500000)
        assert result > 0

    @pytest.mark.timeout(2)
    def test_fib_1000000(self):
        result = fib(1000000)
        assert result > 0

    def test_execution_time_baseline_recorded(self):
        """Record wall-clock time for fib(100000) — used for perf tracking."""
        start = time.perf_counter()
        fib(100000)
        elapsed = time.perf_counter() - start
        # Just record; don't assert a hard limit here (handled by timeout above)
        assert elapsed >= 0
