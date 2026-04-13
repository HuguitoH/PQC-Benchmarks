#!/usr/bin/env python3
"""Test rápido con 10 iteraciones"""

import sys
sys.path.insert(0, '.')

# Cambiar temporalmente ITERATIONS
import benchmark_keygen
benchmark_keygen.ITERATIONS = 10

# Ejecutar
benchmark_keygen.main()
