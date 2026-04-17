# Methodology

## Hardware

| Component | Specification |
|---|---|
| Device | Raspberry Pi 5, 8GB RAM |
| CPU | ARM Cortex-A76 @ 2.4GHz, ARM64 |
| Storage | SanDisk 64GB MicroSD A2 |
| Power supply | 27W USB-C |
| Current sensor | INA219 (0–3.2V, 0–400mA, I2C @ 0x40) |
| Enclosure | ARGON NEO 5 with passive heatsink |
| OS | Ubuntu Server 24.04 LTS (64-bit) |

---

## Software

| Component | Version | Purpose |
|---|---|---|
| Python | 3.11 | Runtime |
| liboqs | 0.10+ | PQC implementations (Kyber-512, ML-DSA-44) |
| cryptography | 41.0.3 | RSA-2048, ECDH-256, ECDSA-256 |
| psutil | 5.9.5 | Process and system memory measurement |
| adafruit-circuitpython-ina219 | 3.4.4 | INA219 sensor driver |
| qiskit | 2.3.1 | Shor's algorithm simulation |
| qiskit-aer | 0.17.2 | Quantum circuit simulator |
| pandas / numpy / scipy | see requirements.txt | Statistical analysis |

---

## Experimental design

**Type**: Quantitative experimental with deductive approach.

**Scope**: 5 cryptographic schemes × 16 operations:

| Algorithm | Operations | Type |
|---|---|---|
| Kyber-512 | keygen, encaps, decaps | PQC KEM (FIPS 203) |
| ML-DSA-44 | keygen, sign, verify | PQC signature (FIPS 204) |
| RSA-2048 | keygen, encrypt, decrypt, sign, verify | Classical |
| ECDH-256 | keygen, derive | Classical ECC |
| ECDSA-256 | keygen, sign, verify | Classical ECC |

**Sample size**: n=1,000 iterations per operation.

Statistical justification: n=1,000 provides power >0.80 for detecting medium effect sizes (d=0.5, α=0.05) — 80% probability of detecting real differences with 5% type-I error. In practice, observed effect sizes were much larger (r≥0.989), making 1,000 iterations well above the minimum required.

**Total dataset**: 16,000 records × 8 metrics = 128,000 data points.

---

## Measurement procedure

For each iteration, the following sequence was executed atomically:

```
1. Record CPU temperature   — vcgencmd measure_temp
2. Record process memory    — psutil.Process().memory_info().rss
3. Record system memory     — psutil.virtual_memory().used
4. Record INA219 current    — ina.current
5. Start timer              — time.perf_counter() (nanosecond resolution)
6. Execute cryptographic operation
7. Stop timer
8. Record CPU temperature   (after)
9. Record process memory    (after)
10. Record system memory    (after)
11. Record INA219 current   (after)
12. Store delta values → CSV row
```

**Warm-up**: 10 iterations executed and discarded before each measurement series, to eliminate cold-start effects (CPU cache, memory allocator, JIT-equivalent initialization).

**Cooldown**: 1 second pause every 100 iterations to prevent thermal drift from accumulating and biasing subsequent latency measurements.

**Warm-up validation results**: most operations within 10% difference between first 10 and remaining 990 iterations. Three operations showed higher warm-up effects:

| Operation | Diff (%) | Note |
|---|---|---|
| mldsa44_sign | 26.2% | Rejection sampling — high variance by design |
| rsa2048_verify | 26.3% | OpenSSL internal state initialization |
| rsa2048_encrypt | 20.2% | OAEP padding initialization |

These warnings reflect structural variability of the algorithms, not experimental artefacts. All 1,000 iterations (including warm-up) are retained in the dataset with the warm-up behaviour documented.

---

## Metrics captured

| Column | Type | Description |
|---|---|---|
| `iteration` | int | Iteration number (1–1,000) |
| `timestamp` | ISO 8601 | Datetime of measurement |
| `time_ms` | float | Operation latency in milliseconds |
| `memory_process_mb` | float | Delta in process RSS memory (MB) |
| `memory_system_mb` | float | Delta in system used memory (MB) |
| `temp_delta_c` | float | CPU temperature change during operation (°C) |
| `temp_absolute_c` | float | Absolute CPU temperature after operation (°C) |
| `current_ma` | float | Delta in INA219 current reading (mA) |

---

## Controlled variables

To ensure internal validity:

- **Hardware**: same Raspberry Pi 5 unit throughout all experiments
- **OS**: no system updates applied during experiment window
- **Ambient temperature**: 20–25°C (measured room temperature)
- **Concurrent load**: no background services during measurement (SSH only)
- **Software versions**: pinned in `requirements-rpi.txt`
- **Thermal throttling**: confirmed absent — max recorded temperature 40.0°C, 45°C below BCM2712 throttle threshold (85°C)

---

## INA219 sensor — known limitation

The INA219 was connected to the Raspberry Pi 5 main power rail via I2C (address 0x40, shunt 0.1Ω). During the experiment, a measurement limitation was identified: the sensor captures **total board current**, not the isolated current draw of each cryptographic process.

As a result, `current_ma` represents `after − before` delta values and should be interpreted as a **relative indicator of energy impact**, not as absolute per-operation energy consumption. The values are retained in the dataset for completeness and relative comparison, but are not used as primary metrics in the statistical analysis.

This limitation is targeted for improvement in Phase 2 via a dedicated per-process measurement setup. See [Future work in README](../README.md#future-work).

---

## Statistical methodology

### Decision pipeline

```
Shapiro-Wilk (α=0.05)
    │
    ▼ All 16 distributions non-normal
    │
Kruskal-Wallis H
    │ H=2651 (KeyGen), H=2663 (Sign), p<0.001
    ▼ Significant differences confirmed
    │
Mann-Whitney U (pairwise)
    │
    ├── Rank-biserial r (effect size)
    │   r = 1 − 2U / (n₁ × n₂)
    │
    └── Bonferroni correction
        α_corrected = 0.05 / k comparisons
```

### Normality test results (Shapiro-Wilk, α=0.05)

All 16 operations confirmed non-normal. Full results:

| Operation | W | p-value | Result |
|---|---|---|---|
| kyber512_decaps | 0.3726 | 6.27e-50 | Non-normal |
| rsa2048_decrypt | 0.2898 | 6.21e-52 | Non-normal |
| rsa2048_sign | 0.2963 | 8.77e-52 | Non-normal |
| kyber512_encaps | 0.5405 | 4.47e-45 | Non-normal |
| ecdsa256_keygen | 0.6133 | 1.70e-42 | Non-normal |
| ecdh256_derive | 0.6314 | 8.54e-42 | Non-normal |
| mldsa44_verify | 0.6156 | 2.08e-42 | Non-normal |
| ecdh256_keygen | 0.6378 | 1.54e-41 | Non-normal |
| ecdsa256_verify | 0.7287 | 1.91e-37 | Non-normal |
| ecdsa256_sign | 0.7612 | 1.04e-35 | Non-normal |
| rsa2048_verify | 0.7605 | 9.47e-36 | Non-normal |
| mldsa44_keygen | 0.7686 | 2.73e-35 | Non-normal |
| mldsa44_sign | 0.7998 | 2.22e-33 | Non-normal |
| kyber512_keygen | 0.8117 | 1.37e-32 | Non-normal |
| rsa2048_encrypt | 0.8214 | 6.46e-32 | Non-normal |
| rsa2048_keygen | 0.8753 | 1.56e-27 | Non-normal |

Non-normality is structurally expected in benchmark data due to: OS scheduling interruptions, Python garbage collection, probabilistic operations (RSA KeyGen uses Miller-Rabin primality testing; ML-DSA Sign uses rejection sampling), and the physical lower bound at 0 ms creating right-skewed distributions.

### Effect size interpretation

Rank-biserial r is interpreted using Cohen's conventions:

| r | Interpretation |
|---|---|
| 0.10–0.29 | Small |
| 0.30–0.49 | Medium |
| 0.50–0.69 | Large |
| ≥0.70 | Very large |

All PQC vs RSA comparisons returned r≥0.989 — the distributions are essentially non-overlapping.

### Bonferroni correction

With k=3 pairwise comparisons per operation group, α_corrected = 0.05/3 = 0.0167. All comparisons remained significant after correction (all p<0.001 ≪ 0.0167).

### Hypotheses

| Hypothesis | Statement | Outcome |
|---|---|---|
| H0 | No significant differences between algorithms (α=0.05) | Rejected (all p<0.001) |
| H1 | Kyber-512 presents lower latency than RSA-2048 | Confirmed (2,345× faster, r=1.000) |
| H2 | ML-DSA-44 presents lower latency than RSA-2048 on signing | Confirmed (5.6× faster, r=0.998) |
| H3 | PQC algorithms use more memory (larger key sizes) | Partially confirmed — key sizes larger, but runtime memory delta ≈ 0 |
| H4 | Shor's algorithm breaks RSA; Kyber-512 resists | Confirmed (RSA-15/21 factored; Kyber LWE R²≈0) |

---

## Outlier handling

Outliers were detected using the Tukey extended fence (Q3 + 3×IQR) rather than the standard 1.5×IQR, as benchmark data is expected to contain occasional high-latency spikes from OS interruptions. Outliers were **retained** — they are part of the real-world performance profile on ARM IoT hardware.

Notable outlier rates:

| Operation | Rate | Notes |
|---|---|---|
| ecdh256_derive | 20.2% | High — ECDH key derivation sensitive to memory bus contention |
| ecdsa256_verify | 19.2% | Signature verification involves variable-time modular arithmetic |
| mldsa44_verify | 15.0% | Lattice polynomial operations sensitive to cache state |

---

## Reproducibility

**Full reproduction** (hardware required):
- Raspberry Pi 5 (ARM64) — results are not reproducible on x86; latency is architecture-specific
- `liboqs` installed and linked via `oqs` Python module
- INA219 sensor connected via I2C GPIO pins
- No concurrent system load during measurement
- See `requirements-rpi.txt` for pinned versions

**Analysis reproduction only** (no hardware required):
```bash
git clone https://github.com/HuguitoH/pqc-benchmarks
cd pqc-benchmarks
pip install -r requirements.txt
jupyter notebook analysis/PQC_analysis.ipynb
```

The full dataset is available in `data/results/` (16 CSVs, 16,000 rows). Tests validate dataset integrity:
```bash
pytest tests/ -v   # 123 tests — data integrity, statistical functions, Shor oracle
```
