#!/usr/bin/env python3

import time
import csv
import os
from datetime import datetime
import oqs
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives import hashes
from helpers import (
    get_cpu_temp, 
    get_memory_usage, 
    setup_ina219, 
    get_ina219_reading,
    wait_cooldown
)

# CONFIGURACIÓN 
ITERATIONS = 1000  
WARMUP_ITERATIONS = 10
DATA_DIR = "../data"
os.makedirs(DATA_DIR, exist_ok=True)

# FUNCIONES AUXILIARES

def save_results(results, filename):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"✓ {filename}")

def measure_operation(operation_func, iterations, warmup, ina, operation_name):
    print(f"\n{operation_name}...", end=" ", flush=True)
    
    # Warm-up silencioso
    for _ in range(warmup):
        operation_func()
    
    results = []
    
    for i in range(iterations):
        # Mediciones ANTES
        temp_before = get_cpu_temp()
        mem_before = get_memory_usage()
        ina_before = get_ina219_reading(ina) or 0
        
        # EJECUTAR operación
        start = time.perf_counter()
        operation_func()
        end = time.perf_counter()
        
        # Mediciones DESPUÉS
        temp_after = get_cpu_temp()
        mem_after = get_memory_usage()
        ina_after = get_ina219_reading(ina) or 0
        
        # Calcular diferencias
        results.append({
            'iteration': i + 1,
            'timestamp': datetime.now().isoformat(),
            'time_ms': (end - start) * 1000,
            'memory_process_mb': mem_after['process_mb'] - mem_before['process_mb'],
            'memory_system_mb': mem_after['system_mb'] - mem_before['system_mb'],
            'temp_delta_c': (temp_after - temp_before) if temp_before and temp_after else 0,
            'temp_absolute_c': temp_after if temp_after else 0,
            'current_ma': ina_after - ina_before
        })
        
        # Progreso compacto
        if (i + 1) % 250 == 0:
            print(f"{i+1}...", end=" ", flush=True)
        
        # Cooldown cada 100
        if (i + 1) % 100 == 0:
            wait_cooldown(1)
    
    print("OK")
    return results

# BENCHMARKS 

def benchmark_kyber512(iterations, warmup, ina):
    print("\n[1/5] KYBER-512")
    
    # KeyGen
    kem_keygen = oqs.KeyEncapsulation("Kyber512")
    results = measure_operation(
        lambda: kem_keygen.generate_keypair(),
        iterations, warmup, ina, "KeyGen"
    )
    save_results(results, "kyber512_keygen.csv")
    
    # Encaps
    kem_encaps = oqs.KeyEncapsulation("Kyber512")
    public_key = kem_encaps.generate_keypair()
    results = measure_operation(
        lambda: kem_encaps.encap_secret(public_key),
        iterations, warmup, ina, "Encaps"
    )
    save_results(results, "kyber512_encaps.csv")
    
    # Decaps
    kem_decaps = oqs.KeyEncapsulation("Kyber512")
    public_key_decaps = kem_decaps.generate_keypair()
    ciphertext, _ = kem_decaps.encap_secret(public_key_decaps)
    results = measure_operation(
        lambda: kem_decaps.decap_secret(ciphertext),
        iterations, warmup, ina, "Decaps"
    )
    save_results(results, "kyber512_decaps.csv")

def benchmark_mldsa44(iterations, warmup, ina):
    print("\n[2/5] ML-DSA-44")
    
    message = b"Test message for digital signature" * 10
    
    # KeyGen
    sig_keygen = oqs.Signature("ML-DSA-44")
    results = measure_operation(
        lambda: sig_keygen.generate_keypair(),
        iterations, warmup, ina, "KeyGen"
    )
    save_results(results, "mldsa44_keygen.csv")
    
    # Sign
    sig_sign = oqs.Signature("ML-DSA-44")
    public_key_sign = sig_sign.generate_keypair()
    results = measure_operation(
        lambda: sig_sign.sign(message),
        iterations, warmup, ina, "Sign"
    )
    save_results(results, "mldsa44_sign.csv")
    
    # Verify
    sig_verify = oqs.Signature("ML-DSA-44")
    public_key_verify = sig_verify.generate_keypair()
    signature = sig_verify.sign(message)
    results = measure_operation(
        lambda: sig_verify.verify(message, signature, public_key_verify),
        iterations, warmup, ina, "Verify"
    )
    save_results(results, "mldsa44_verify.csv")

def benchmark_rsa2048(iterations, warmup, ina):
    print("\n[3/5] RSA-2048")
    
    # KeyGen
    results = measure_operation(
        lambda: rsa.generate_private_key(public_exponent=65537, key_size=2048),
        iterations, warmup, ina, "KeyGen"
    )
    save_results(results, "rsa2048_keygen.csv")
    
    # Encrypt
    private_key_enc = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key_enc = private_key_enc.public_key()
    message_enc = b"Test message for encryption" * 5
    
    results = measure_operation(
        lambda: public_key_enc.encrypt(
            message_enc,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ),
        iterations, warmup, ina, "Encrypt"
    )
    save_results(results, "rsa2048_encrypt.csv")
    
    # Decrypt
    private_key_dec = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key_dec = private_key_dec.public_key()
    ciphertext = public_key_dec.encrypt(
        message_enc,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    results = measure_operation(
        lambda: private_key_dec.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ),
        iterations, warmup, ina, "Decrypt"
    )
    save_results(results, "rsa2048_decrypt.csv")
    
    # Sign
    message_sig = b"Test message for digital signature" * 10
    private_key_sign = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    
    results = measure_operation(
        lambda: private_key_sign.sign(
            message_sig,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        ),
        iterations, warmup, ina, "Sign"
    )
    save_results(results, "rsa2048_sign.csv")
    
    # Verify
    private_key_verify = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key_verify = private_key_verify.public_key()
    signature = private_key_verify.sign(
        message_sig,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    def verify_rsa():
        try:
            public_key_verify.verify(
                signature, message_sig,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        except:
            pass
    
    results = measure_operation(verify_rsa, iterations, warmup, ina, "Verify")
    save_results(results, "rsa2048_verify.csv")

def benchmark_ecdh256(iterations, warmup, ina):
    print("\n[4/5] ECDH-256")
    
    # KeyGen
    results = measure_operation(
        lambda: ec.generate_private_key(ec.SECP256R1()),
        iterations, warmup, ina, "KeyGen"
    )
    save_results(results, "ecdh256_keygen.csv")
    
    # Derive
    private_key_alice = ec.generate_private_key(ec.SECP256R1())
    private_key_bob = ec.generate_private_key(ec.SECP256R1())
    public_key_bob = private_key_bob.public_key()
    
    results = measure_operation(
        lambda: private_key_alice.exchange(ec.ECDH(), public_key_bob),
        iterations, warmup, ina, "Derive"
    )
    save_results(results, "ecdh256_derive.csv")

def benchmark_ecdsa256(iterations, warmup, ina):
    print("\n[5/5] ECDSA-256")
    
    message = b"Test message for digital signature" * 10
    
    # KeyGen
    results = measure_operation(
        lambda: ec.generate_private_key(ec.SECP256R1()),
        iterations, warmup, ina, "KeyGen"
    )
    save_results(results, "ecdsa256_keygen.csv")
    
    # Sign
    private_key_sign = ec.generate_private_key(ec.SECP256R1())
    results = measure_operation(
        lambda: private_key_sign.sign(message, ec.ECDSA(hashes.SHA256())),
        iterations, warmup, ina, "Sign"
    )
    save_results(results, "ecdsa256_sign.csv")
    
    # Verify
    private_key_verify = ec.generate_private_key(ec.SECP256R1())
    public_key_verify = private_key_verify.public_key()
    signature = private_key_verify.sign(message, ec.ECDSA(hashes.SHA256()))
    
    def verify_ecdsa():
        try:
            public_key_verify.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        except:
            pass
    
    results = measure_operation(verify_ecdsa, iterations, warmup, ina, "Verify")
    save_results(results, "ecdsa256_verify.csv")


# MAIN

def main():
    print()
    print("BENCHMARK PQC vs TRADICIONAL - n=1000 iteraciones")
    print()
    print(f"Configuración: {ITERATIONS} iter/op, warm-up {WARMUP_ITERATIONS}")
    print(f"Directorio: {DATA_DIR}/")
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Setup sensores
    ina = setup_ina219()
    print(f"Temperatura inicial: {get_cpu_temp():.1f}°C")
    print(f"INA219: {'OK' if ina else 'No disponible'}")
    
    start_time = time.time()
    
    try:
        benchmark_kyber512(ITERATIONS, WARMUP_ITERATIONS, ina)
        benchmark_mldsa44(ITERATIONS, WARMUP_ITERATIONS, ina)
        benchmark_rsa2048(ITERATIONS, WARMUP_ITERATIONS, ina)
        benchmark_ecdh256(ITERATIONS, WARMUP_ITERATIONS, ina)
        benchmark_ecdsa256(ITERATIONS, WARMUP_ITERATIONS, ina)
        
    except KeyboardInterrupt:
        print("\n\nInterrumpido por usuario (Ctrl+C)")
        return
    except Exception as e:
        print(f"\n\nError: {e}")
        return
    
    # Resumen
    elapsed = time.time() - start_time
    print()
    print("COMPLETADO")
    print()
    print(f"Duración: {elapsed/60:.1f} min ({elapsed:.0f} seg)")
    print(f"Temperatura final: {get_cpu_temp():.1f}°C")

if __name__ == "__main__":
    main()
