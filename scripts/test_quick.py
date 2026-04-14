import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'benchmarks'))

from benchmark_complete import (
    benchmark_kyber512,
    benchmark_mldsa44,
    benchmark_rsa2048,
    setup_ina219,
    get_cpu_temp
)

QUICK_ITERATIONS = 10
QUICK_WARMUP = 2

def main() -> None:
    """Run a quick 10-iteration validation of all benchmark functions."""
    print("Quick validation — n=10 iterations")
    print()

    ina = setup_ina219()
    print(f"INA219: {'OK' if ina else 'Not detected'}")
    print(f"CPU temperature: {get_cpu_temp()}°C")
    print()

    benchmark_kyber512(QUICK_ITERATIONS, QUICK_WARMUP, ina)
    benchmark_mldsa44(QUICK_ITERATIONS, QUICK_WARMUP, ina)
    benchmark_rsa2048(QUICK_ITERATIONS, QUICK_WARMUP, ina)

    print()
    print("Validation complete — ready to run benchmark_complete.py")

if __name__ == "__main__":
    main()
