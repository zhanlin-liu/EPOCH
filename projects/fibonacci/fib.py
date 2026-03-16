"""Fibonacci CLI calculator — baseline iterative implementation."""
import sys


def fib(n: int) -> int:
    """Return the nth Fibonacci number (0-indexed). fib(0)=0, fib(1)=1."""
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    if n == 0:
        return 0
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <n>", file=sys.stderr)
        sys.exit(1)
    try:
        n = int(sys.argv[1])
    except ValueError:
        print(f"Error: argument must be an integer, got '{sys.argv[1]}'", file=sys.stderr)
        sys.exit(1)
    print(fib(n))
