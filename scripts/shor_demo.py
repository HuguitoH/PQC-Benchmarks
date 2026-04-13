import time
import sys
import random
import math

def slow_print(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def dramatic_pause(seconds):
    time.sleep(seconds)

def progress_bar(label, duration=2.0, width=40):
    print(f"\n  {label}")
    for i in range(width + 1):
        filled = '█' * i
        empty = '░' * (width - i)
        pct = int((i / width) * 100)
        print(f"\r  [{filled}{empty}] {pct}%", end='', flush=True)
        time.sleep(duration / width)
    print()

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def shor_simple(N, a):
    """Simulación clásica simplificada del periodo de Shor"""
    r = 1
    val = a % N
    while val != 1:
        val = (val * a) % N
        r += 1
        if r > N:
            return None
    return r

def main():
    # ─── PANTALLA INICIAL
    print("\033[2J\033[H")  # limpiar pantalla
    print("\033[90m" + "─" * 55 + "\033[0m")
    slow_print("\033[1;37m  QUANTUM THREAT SIMULATOR v1.0\033[0m", 0.04)
    slow_print("\033[90m  Shor's Algorithm — RSA Factorization Demo\033[0m", 0.02)
    print("\033[90m" + "─" * 55 + "\033[0m")
    dramatic_pause(0.8)

    # ─── OBJETIVO
    print()
    slow_print("\033[33m  TARGET:\033[0m RSA Public Key", 0.04)
    dramatic_pause(0.4)
    slow_print("\033[33m  N =\033[0m 15  \033[90m(RSA modulus)\033[0m", 0.04)
    slow_print("\033[33m  a =\033[0m 7   \033[90m(random base)\033[0m", 0.04)
    dramatic_pause(0.6)

    # ─── FASE 1: SUPERPOSICIÓN
    print()
    slow_print("\033[36m  [1/3] Initializing quantum superposition...\033[0m", 0.03)
    progress_bar("Hadamard gates applied", 1.2)
    slow_print("  \033[90m→ 8 qubits in superposition: |0⟩+|1⟩+...+|7⟩\033[0m", 0.02)
    dramatic_pause(0.5)

    # ─── FASE 2: QFT
    print()
    slow_print("\033[36m  [2/3] Quantum Fourier Transform...\033[0m", 0.03)
    progress_bar("Detecting periodic pattern", 1.5)

    # Mostrar "mediciones" falsas que convergen al periodo
    slow_print("  \033[90m→ Measuring quantum states...\033[0m", 0.02)
    dramatic_pause(0.3)
    measurements = [0, 4, 8, 12, 4, 0, 8, 12]
    print("  \033[90m  States: ", end='')
    for m in measurements:
        print(f"|{m:04b}⟩ ", end='', flush=True)
        time.sleep(0.15)
    print("\033[0m")
    dramatic_pause(0.4)
    slow_print("  \033[33m→ Period detected: r = 4\033[0m", 0.03)
    dramatic_pause(0.5)

    # ─── FASE 3: FACTORIZACIÓN
    print()
    slow_print("\033[36m  [3/3] Computing factors via GCD...\033[0m", 0.03)
    dramatic_pause(0.6)

    r = 4
    a = 7
    N = 15
    f1 = gcd(pow(a, r//2) - 1, N)
    f2 = gcd(pow(a, r//2) + 1, N)

    slow_print(f"  \033[90m→ gcd(7² - 1, 15) = gcd(48, 15) = {f1}\033[0m", 0.02)
    dramatic_pause(0.3)
    slow_print(f"  \033[90m→ gcd(7² + 1, 15) = gcd(50, 15) = {f2}\033[0m", 0.02)
    dramatic_pause(0.4)

    # ─── RESULTADO
    print()
    print("\033[90m" + "─" * 55 + "\033[0m")
    print()
    slow_print(f"\033[1;32m  ✓ RSA KEY FACTORIZED\033[0m", 0.05)
    print()
    slow_print(f"  \033[1;37m  N = {N}  →  {f1} × {f2}\033[0m", 0.04)
    print()
    slow_print(f"\033[90m  Circuit depth:    13 gates\033[0m", 0.02)
    slow_print(f"\033[90m  Qubits used:      8\033[0m", 0.02)
    slow_print(f"\033[90m  Execution time:   \033[0m", 0.02)
    # Tiempo dramático
    print("\033[90m", end='')
    for t in ["0.1s", "0.4s", "0.8s"]:
        print(f"\r\033[90m  Execution time:   {t}", end='', flush=True)
        time.sleep(0.3)
    print(f"\r  Execution time:   \033[1;32m0.847s\033[0m          ")
    print()
    print("\033[90m" + "─" * 55 + "\033[0m")
    print()
    slow_print("\033[1;31m  RSA-2048: ~400,000 physical qubits needed\033[0m", 0.03)
    slow_print("\033[1;31m  Estimated availability: 2032-2035\033[0m", 0.03)
    print()

if __name__ == "__main__":
    main()
