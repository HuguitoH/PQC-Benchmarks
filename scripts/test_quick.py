"""
Quick validation run — 10 iterations per algorithm.

Runs a minimal subset of the full benchmark to confirm the environment
is configured correctly before committing to the full 1,000-iteration run.

Requires Raspberry Pi 5 with liboqs and INA219 configured.

Usage:
    python scripts/test_quick.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'benchmarks'))

from benchmark_complete import (
    benchmark_kyber512,
    benchmark_mldsa44,
    benchmark_rsa2048,
)
from helpers import setup_ina219, get_cpu_temp

_QUICK_ITERATIONS = 10
_QUICK_WARMUP     = 2


def main() -> None:
    """Run a 10-iteration validation of all benchmark functions."""
    print("Quick validation — n=10 iterations")
    print()

    ina = setup_ina219()
    print(f"INA219      : {'OK' if ina else 'Not detected'}")
    print(f"CPU temp    : {get_cpu_temp():.1f}°C")
    print()

    benchmark_kyber512(ITERATIONS=_QUICK_ITERATIONS, WARMUP_ITERATIONS=_QUICK_WARMUP, ina=ina)
    benchmark_mldsa44 (ITERATIONS=_QUICK_ITERATIONS, WARMUP_ITERATIONS=_QUICK_WARMUP, ina=ina)
    benchmark_rsa2048 (ITERATIONS=_QUICK_ITERATIONS, WARMUP_ITERATIONS=_QUICK_WARMUP, ina=ina)

    print()
    print("Validation complete — ready to run benchmark_complete.py")


if __name__ == "__main__":
    main()
