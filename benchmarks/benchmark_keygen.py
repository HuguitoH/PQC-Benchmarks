#!/usr/bin/env python3
"""
Benchmark de generación de claves - Experimento preliminar
Kyber512 vs RSA-2048 vs ML-DSA-44
Versión mejorada con warm-up y métricas de memoria detalladas
"""

import time
import csv
import os
from datetime import datetime
import oqs
from cryptography.hazmat.primitives.asymmetric import rsa
from helpers import (
    get_cpu_temp, 
    get_memory_usage, 
    setup_ina219, 
    get_ina219_reading,
    wait_cooldown
)

# Configuración
ITERATIONS = 500  # Iteraciones por algoritmo
WARMUP_ITERATIONS = 10  # Iteraciones de calentamiento (se descartan)
DATA_DIR = "../data"
os.makedirs(DATA_DIR, exist_ok=True)

def benchmark_kyber512(iterations, ina):
    """Benchmark Kyber512 KeyGen"""
    print(f"\n Benchmarking Kyber512 KeyGen")
    print(f"   Warm-up: {WARMUP_ITERATIONS} iteraciones (descartadas)")
    print(f"   Medición: {iterations} iteraciones")
    
    # WARM-UP: ejecutar y descartar
    print("Ejecutando warm-up...")
    for _ in range(WARMUP_ITERATIONS):
        kem = oqs.KeyEncapsulation("Kyber512")
        public_key = kem.generate_keypair()
    
    print("Iniciando mediciones...")
    results = []
    
    for i in range(iterations):
        # Mediciones ANTES
        temp_before = get_cpu_temp()
        mem_before = get_memory_usage()
        ina_before = get_ina219_reading(ina) or 0
        
        # EJECUTAR operación
        start = time.perf_counter()
        kem = oqs.KeyEncapsulation("Kyber512")
        public_key = kem.generate_keypair()
        end = time.perf_counter()
        
        # Mediciones DESPUÉS
        temp_after = get_cpu_temp()
        mem_after = get_memory_usage()
        ina_after = get_ina219_reading(ina) or 0
        
        # Calcular diferencias
        time_ms = (end - start) * 1000
        temp_delta = (temp_after - temp_before) if temp_before and temp_after else 0
        mem_process_delta = mem_after['process_mb'] - mem_before['process_mb']
        mem_system_delta = mem_after['system_mb'] - mem_before['system_mb']
        ina_delta = ina_after - ina_before
        
        results.append({
            'iteration': i + 1,
            'timestamp': datetime.now().isoformat(),
            'time_ms': time_ms,
            'memory_process_mb': mem_process_delta,
            'memory_system_mb': mem_system_delta,
            'temp_delta_c': temp_delta,
            'temp_absolute_c': temp_after if temp_after else 0,
            'current_ma': ina_delta
        })
        
        # Progreso
        if (i + 1) % 50 == 0:
            print(f"      ✓ {i + 1}/{iterations} completadas")
        
        # Pequeña pausa cada 100 iteraciones
        if (i + 1) % 100 == 0:
            wait_cooldown(1)
    
    # Guardar en CSV
    filename = os.path.join(DATA_DIR, "kyber512_keygen.csv")
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Datos guardados: {filename}")
    return results

def benchmark_rsa2048(iterations, ina):
    """Benchmark RSA-2048 KeyGen"""
    print(f"\n Benchmarking RSA-2048 KeyGen")
    print(f"   Warm-up: {WARMUP_ITERATIONS} iteraciones (descartadas)")
    print(f"   Medición: {iterations} iteraciones")
    
    # WARM-UP
    print("Ejecutando warm-up...")
    for _ in range(WARMUP_ITERATIONS):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
    
    print("Iniciando mediciones...")
    results = []
    
    for i in range(iterations):
        # Mediciones ANTES
        temp_before = get_cpu_temp()
        mem_before = get_memory_usage()
        ina_before = get_ina219_reading(ina) or 0
        
        # EJECUTAR operación
        start = time.perf_counter()
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        end = time.perf_counter()
        
        # Mediciones DESPUÉS
        temp_after = get_cpu_temp()
        mem_after = get_memory_usage()
        ina_after = get_ina219_reading(ina) or 0
        
        # Calcular diferencias
        time_ms = (end - start) * 1000
        temp_delta = (temp_after - temp_before) if temp_before and temp_after else 0
        mem_process_delta = mem_after['process_mb'] - mem_before['process_mb']
        mem_system_delta = mem_after['system_mb'] - mem_before['system_mb']
        ina_delta = ina_after - ina_before
        
        results.append({
            'iteration': i + 1,
            'timestamp': datetime.now().isoformat(),
            'time_ms': time_ms,
            'memory_process_mb': mem_process_delta,
            'memory_system_mb': mem_system_delta,
            'temp_delta_c': temp_delta,
            'temp_absolute_c': temp_after if temp_after else 0,
            'current_ma': ina_delta
        })
        
        # Progreso
        if (i + 1) % 50 == 0:
            print(f"      ✓ {i + 1}/{iterations} completadas")
        
        # Pequeña pausa cada 100 iteraciones
        if (i + 1) % 100 == 0:
            wait_cooldown(1)
    
    # Guardar en CSV
    filename = os.path.join(DATA_DIR, "rsa2048_keygen.csv")
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Datos guardados: {filename}")
    return results

def benchmark_mldsa44(iterations, ina):
    """Benchmark ML-DSA-44 KeyGen"""
    print(f"\nBenchmarking ML-DSA-44 KeyGen")
    print(f"   Warm-up: {WARMUP_ITERATIONS} iteraciones (descartadas)")
    print(f"   Medición: {iterations} iteraciones")
    
    # WARM-UP
    print("Ejecutando warm-up...")
    for _ in range(WARMUP_ITERATIONS):
        sig = oqs.Signature("ML-DSA-44")
        public_key = sig.generate_keypair()
    
    print("Iniciando mediciones...")
    results = []
    
    for i in range(iterations):
        # Mediciones ANTES
        temp_before = get_cpu_temp()
        mem_before = get_memory_usage()
        ina_before = get_ina219_reading(ina) or 0
        
        # EJECUTAR operación
        start = time.perf_counter()
        sig = oqs.Signature("ML-DSA-44")
        public_key = sig.generate_keypair()
        end = time.perf_counter()
        
        # Mediciones DESPUÉS
        temp_after = get_cpu_temp()
        mem_after = get_memory_usage()
        ina_after = get_ina219_reading(ina) or 0
        
        # Calcular diferencias
        time_ms = (end - start) * 1000
        temp_delta = (temp_after - temp_before) if temp_before and temp_after else 0
        mem_process_delta = mem_after['process_mb'] - mem_before['process_mb']
        mem_system_delta = mem_after['system_mb'] - mem_before['system_mb']
        ina_delta = ina_after - ina_before
        
        results.append({
            'iteration': i + 1,
            'timestamp': datetime.now().isoformat(),
            'time_ms': time_ms,
            'memory_process_mb': mem_process_delta,
            'memory_system_mb': mem_system_delta,
            'temp_delta_c': temp_delta,
            'temp_absolute_c': temp_after if temp_after else 0,
            'current_ma': ina_delta
        })
        
        # Progreso
        if (i + 1) % 50 == 0:
            print(f"      ✓ {i + 1}/{iterations} completadas")
        
        # Pequeña pausa cada 100 iteraciones
        if (i + 1) % 100 == 0:
            wait_cooldown(1)
    
    # Guardar en CSV
    filename = os.path.join(DATA_DIR, "mldsa44_keygen.csv")
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Datos guardados: {filename}")
    return results

def main():
    print("=" * 70)
    print("EXPERIMENTO PRELIMINAR - GENERACIÓN DE CLAVES")
    print("=" * 70)
    print(f"Configuración:")
    print(f"  • Warm-up: {WARMUP_ITERATIONS} iteraciones por algoritmo (descartadas)")
    print(f"  • Mediciones: {ITERATIONS} iteraciones por algoritmo")
    print(f"  • Total mediciones: {ITERATIONS * 3} operaciones × 7 métricas = {ITERATIONS * 21}")
    print(f"  • Algoritmos: Kyber512, RSA-2048, ML-DSA-44")
    print("=" * 70)
    
    # Configurar INA219
    print("\nConfigurando sensores...")
    ina = setup_ina219()
    if ina:
        print("INA219: OK (métrica secundaria)")
    else:
        print("INA219: No disponible (continuando sin ella)")
    print("Temperatura CPU: OK")
    print("Memoria: OK")
    
    # Ejecutar benchmarks
    start_time = time.time()
    
    results_kyber = benchmark_kyber512(ITERATIONS, ina)
    results_rsa = benchmark_rsa2048(ITERATIONS, ina)
    results_mldsa = benchmark_mldsa44(ITERATIONS, ina)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Resumen
    print("\n" + "=" * 70)
    print("EXPERIMENTO COMPLETADO")
    print("=" * 70)
    print(f"Tiempo total: {total_time/60:.2f} minutos ({total_time:.1f} segundos)")
    print(f"\nArchivos generados en: {DATA_DIR}/")
    print("  • kyber512_keygen.csv")
    print("  • rsa2048_keygen.csv")
    print("  • mldsa44_keygen.csv")
    print(f"\nCada CSV contiene {ITERATIONS} filas × 8 columnas")
    print("=" * 70)

if __name__ == "__main__":
    main()
