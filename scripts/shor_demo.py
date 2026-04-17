"""
Shor's Algorithm — Terminal demo for AB presentation.

Simulates the conceptual steps of Shor's algorithm factoring N=15
with animated terminal output. Not a real quantum circuit — intended
as a pedagogical demonstration of the algorithm's structure.

Usage:
    python scripts/shor_demo.py
"""

import time
from math import gcd

# ── Display constants
_WIDTH      = 55
_SEPARATOR  = "\033[90m" + "─" * _WIDTH + "\033[0m"
_BAR_WIDTH  = 40

# Shor target (N=15, a=7) — fixed for demo reproducibility
_N: int = 15
_A: int = 7
_R: int = 4   # known period of 7^x mod 15


# ── Terminal utilities

def _slow_print(text: str, delay: float = 0.03) -> None:
    """Print text character by character with a delay."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def _pause(seconds: float) -> None:
    time.sleep(seconds)


def _progress_bar(label: str, duration: float = 2.0) -> None:
    """Render an animated ASCII progress bar."""
    print(f"\n  {label}")
    for i in range(_BAR_WIDTH + 1):
        filled  = '█' * i
        empty   = '░' * (_BAR_WIDTH - i)
        percent = int((i / _BAR_WIDTH) * 100)
        print(f"\r  [{filled}{empty}] {percent}%", end='', flush=True)
        time.sleep(duration / _BAR_WIDTH)
    print()


# ── Demo phases

def _phase_intro() -> None:
    print("\033[2J\033[H")   # clear screen
    print(_SEPARATOR)
    _slow_print("\033[1;37m  QUANTUM THREAT SIMULATOR v1.0\033[0m", 0.04)
    _slow_print("\033[90m  Shor's Algorithm — RSA Factorization Demo\033[0m", 0.02)
    print(_SEPARATOR)
    _pause(0.8)

    print()
    _slow_print(f"\033[33m  TARGET:\033[0m RSA Public Key", 0.04)
    _pause(0.4)
    _slow_print(f"\033[33m  N =\033[0m {_N}  \033[90m(RSA modulus)\033[0m", 0.04)
    _slow_print(f"\033[33m  a =\033[0m {_A}   \033[90m(random base)\033[0m", 0.04)
    _pause(0.6)


def _phase_superposition() -> None:
    print()
    _slow_print("\033[36m  [1/3] Initializing quantum superposition...\033[0m", 0.03)
    _progress_bar("Hadamard gates applied", 1.2)
    _slow_print("  \033[90m→ 8 qubits in superposition: |0⟩+|1⟩+...+|7⟩\033[0m", 0.02)
    _pause(0.5)


def _phase_qft() -> None:
    print()
    _slow_print("\033[36m  [2/3] Quantum Fourier Transform...\033[0m", 0.03)
    _progress_bar("Detecting periodic pattern", 1.5)

    _slow_print("  \033[90m→ Measuring quantum states...\033[0m", 0.02)
    _pause(0.3)

    # Expected measurement outcomes for period r=4 with 4-qubit register
    measurements = [0, 4, 8, 12, 4, 0, 8, 12]
    print("  \033[90m  States: ", end='')
    for m in measurements:
        print(f"|{m:04b}⟩ ", end='', flush=True)
        time.sleep(0.15)
    print("\033[0m")

    _pause(0.4)
    _slow_print(f"\033[33m→ Period detected: r = {_R}\033[0m", 0.03)
    _pause(0.5)


def _phase_factorize() -> None:
    print()
    _slow_print("\033[36m  [3/3] Computing factors via GCD...\033[0m", 0.03)
    _pause(0.6)

    half_power = pow(_A, _R // 2)
    f1 = gcd(half_power - 1, _N)
    f2 = gcd(half_power + 1, _N)

    _slow_print(
        f"  \033[90m→ gcd({_A}² - 1, {_N}) = gcd({half_power - 1}, {_N}) = {f1}\033[0m",
        0.02,
    )
    _pause(0.3)
    _slow_print(
        f"  \033[90m→ gcd({_A}² + 1, {_N}) = gcd({half_power + 1}, {_N}) = {f2}\033[0m",
        0.02,
    )
    _pause(0.4)

    return f1, f2


def _phase_result(f1: int, f2: int) -> None:
    print()
    print(_SEPARATOR)
    print()
    _slow_print("\033[1;32m  ✓ RSA KEY FACTORIZED\033[0m", 0.05)
    print()
    _slow_print(f"  \033[1;37m  N = {_N}  →  {f1} × {f2}\033[0m", 0.04)
    print()
    _slow_print("\033[90m  Circuit depth:    13 gates\033[0m", 0.02)
    _slow_print("\033[90m  Qubits used:      8\033[0m", 0.02)

    # Animated execution time reveal
    for t in ["0.1s", "0.4s", "0.8s"]:
        print(f"\r\033[90m  Execution time:   {t}", end='', flush=True)
        time.sleep(0.3)
    print(f"\r  Execution time:   \033[1;32m0.847s\033[0m          ")

    print()
    print(_SEPARATOR)
    print()
    _slow_print("\033[1;31m  RSA-2048: ~400,000 physical qubits needed\033[0m", 0.03)
    _slow_print("\033[1;31m  Estimated availability: 2032–2035\033[0m", 0.03)
    print()


# ── Entry point

def main() -> None:
    """Run the Shor's algorithm terminal demo."""
    _phase_intro()
    _phase_superposition()
    _phase_qft()
    f1, f2 = _phase_factorize()
    _phase_result(f1, f2)


if __name__ == "__main__":
    main()
