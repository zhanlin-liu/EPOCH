import sys
import os

# Allow `from fib import fib` without package install
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
