"""Fibonacci CLI calculator."""

import sys

try:
    import gmpy2

    def fibonacci(n: int) -> int:
        """Compute the nth Fibonacci number using GMP's optimized mpz_fib_ui.

        Uses gmpy2.fib() which leverages GMP's highly optimized internal
        Fibonacci implementation with binary splitting.
        """
        if n < 0:
            raise ValueError("n must be non-negative")
        return int(gmpy2.fib(n))

except ImportError:

    def fibonacci(n: int) -> int:
        """Compute the nth Fibonacci number using fast doubling.

        fib(0) = 0, fib(1) = 1, fib(n) = fib(n-1) + fib(n-2)

        Uses the fast doubling identities for O(log n) complexity:
          fib(2k)   = fib(k) * [2*fib(k+1) - fib(k)]
          fib(2k+1) = fib(k)^2 + fib(k+1)^2
        """
        if n < 0:
            raise ValueError("n must be non-negative")
        if n <= 1:
            return n
        a, b = 0, 1
        for bit in bin(n)[2:]:
            c = a * ((b << 1) - a)
            d = a * a + b * b
            if bit == '0':
                a, b = c, d
            else:
                a, b = d, c + d
        return a


def main():
    if len(sys.argv) != 2:
        print("Usage: python fib.py <n>", file=sys.stderr)
        sys.exit(1)
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Error: n must be an integer", file=sys.stderr)
        sys.exit(1)
    print(fibonacci(n))


if __name__ == "__main__":
    main()
