"""Tests for Fibonacci calculator - correctness and performance."""

import time

import pytest

from fib import fibonacci


# --- Correctness: Basic cases ---

class TestBasicCases:
    def test_fib_0(self):
        assert fibonacci(0) == 0

    def test_fib_1(self):
        assert fibonacci(1) == 1

    def test_fib_2(self):
        assert fibonacci(2) == 1

    def test_fib_3(self):
        assert fibonacci(3) == 2

    def test_fib_5(self):
        assert fibonacci(5) == 5

    def test_fib_10(self):
        assert fibonacci(10) == 55

    def test_fib_20(self):
        assert fibonacci(20) == 6765


# --- Correctness: Edge cases ---

class TestEdgeCases:
    def test_negative_raises(self):
        with pytest.raises(ValueError):
            fibonacci(-1)

    def test_negative_large_raises(self):
        with pytest.raises(ValueError):
            fibonacci(-100)


# --- Correctness: Known large values ---

class TestLargeValues:
    def test_fib_50(self):
        assert fibonacci(50) == 12586269025

    def test_fib_100(self):
        assert fibonacci(100) == 354224848179261915075

    def test_fib_200(self):
        expected = 280571172992510140037611932413038677189525
        assert fibonacci(200) == expected

    def test_fib_300(self):
        expected = 222232244629420445529739893461909967206666939096499764990979600
        assert fibonacci(300) == expected

    def test_fib_500(self):
        expected = 139423224561697880139724382870407283950070256587697307264108962948325571622863290691557658876222521294125
        assert fibonacci(500) == expected

    def test_fib_1000(self):
        # Verify fib(1000) using the recurrence: fib(1000) = fib(999) + fib(998)
        f998 = fibonacci(998)
        f999 = fibonacci(999)
        f1000 = fibonacci(1000)
        assert f1000 == f998 + f999
        # Known digit count of fib(1000) is 209
        assert len(str(f1000)) == 209
        # Known last 10 digits
        assert f1000 % 10**10 == 6849228875


# --- Performance: Large N computation ---

class TestPerformance:
    @pytest.mark.timeout(2)
    def test_fib_10000_under_2s(self):
        """fib(10000) should complete within 2 seconds."""
        start = time.perf_counter()
        result = fibonacci(10000)
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0
        assert result > 0

    @pytest.mark.timeout(2)
    def test_fib_100000_under_2s(self):
        """fib(100000) should complete within 2 seconds."""
        start = time.perf_counter()
        result = fibonacci(100000)
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0
        assert result > 0

    @pytest.mark.timeout(2)
    def test_fib_500000_under_2s(self):
        """fib(500000) should complete within 2 seconds."""
        start = time.perf_counter()
        result = fibonacci(500000)
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0
        assert result > 0

    @pytest.mark.timeout(2)
    def test_fib_1000000_under_2s(self):
        """fib(1000000) should complete within 2 seconds."""
        start = time.perf_counter()
        result = fibonacci(1000000)
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0
        assert result > 0
