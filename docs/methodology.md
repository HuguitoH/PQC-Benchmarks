# Methodology

## Hardware

| Component | Specification |
|---|---|
| Device | Raspberry Pi 5, 8GB RAM |
| CPU | Cortex-A76 @ 2.4GHz, ARM64 |
| Storage | SanDisk 64GB MicroSD A2 |
| Power supply | 27W USB-C |
| Current sensor | INA219 (0–3.2V, 0–400mA, 1kHz sampling) |
| Enclosure | ARGON NEO 5 with heatsink |

---

## Software

| Component | Version |
|---|---|
| OS | Raspberry Pi OS 64-bit (Debian Bookworm) |
| Python | 3.11 |
| liboqs | 0.10+ — Open Quantum Safe, PQC implementations |
| OpenSSL | 3.0+ — RSA and ECC implementations |
| psutil | process and system memory measurement |
| adafruit-circuitpython-ina219 | INA219 sensor driver |
| numpy, pandas, scipy | statistical analysis |
| matplotlib, seaborn, plotly | visualizations |
| qiskit, qiskit-aer | Shor's algorithm simulation |

---

## Experimental design

**Type**: Quantitative experimental with deductive approach.

**Scope**: 16 cryptographic operations across 5 schemes:

| Algorithm | Operations |
|---|---|
| Kyber-512 | keygen, encaps, decaps |
| ML-DSA-44 | keygen, sign, verify |
| RSA-2048 | keygen, encrypt, decrypt, sign, verify |
| ECDH-256 | keygen, derive |
| ECDSA-256 | keygen, sign, verify |

**Sample size**: n=1,000 iterations per operation.

Statistical justification: n=1,000 provides statistical power >0.80 for detecting medium effect sizes (d=0.5, α=0.05). This means an 80% probability of detecting real differences between algorithms when they exist, with a 5% error margin.

**Total dataset**: 16,000 records × 8 metrics = 128,000 data points.

---

## Measurement procedure

For each iteration, the following sequence was executed:

```
1. Record CPU temperature (before)
2. Record memory usage — process and system (before)
3. Record INA219 current reading (before)
4. Start timer — time.perf_counter() (nanosecond precision)
5. Execute cryptographic operation
6. Stop timer
7. Record CPU temperature (after)
8. Record memory usage (after)
9. Record INA219 current reading (after)
10. Store delta values to CSV
```

**Warm-up**: 10 iterations executed and discarded before each measurement series, to stabilize CPU caches and eliminate cold-start effects.

**Cooldown**: 1 second pause every 100 iterations to prevent thermal drift from affecting subsequent measurements.

---

## Metrics captured

| Column | Description |
|---|---|
| `iteration` | Iteration number (1–1000) |
| `timestamp` | ISO 8601 datetime |
| `time_ms` | Operation latency in milliseconds |
| `memory_process_mb` | Delta in process memory (MB) |
| `memory_system_mb` | Delta in system memory (MB) |
| `temp_delta_c` | CPU temperature change during operation (°C) |
| `temp_absolute_c` | Absolute CPU temperature after operation (°C) |
| `current_ma` | Delta in current draw from INA219 (mA) |

---

## Controlled variables

To ensure internal validity, the following variables were held constant:

- Hardware: same Raspberry Pi 5 unit throughout
- OS: no updates applied during experiment
- Ambient temperature: 20–25°C
- Concurrent load: no background processes during measurement
- Software versions: pinned for reproducibility

---

## INA219 sensor — known limitations

The INA219 sensor was connected to the Raspberry Pi 5's power rail via I2C (address 0x40). During the experiment, a measurement limitation was identified: the sensor captures total bus current rather than the isolated per-process current draw of each cryptographic operation.

As a result, the `current_ma` column in the CSVs represents delta values (after − before each operation) and should be interpreted as a **relative indicator of energy impact**, not as absolute per-operation energy consumption.

This limitation was documented in the thesis and is a target for improvement in Phase 2. See [Future work in README](../README.md#future-work).

---

## Statistical methodology

### Normality testing

Shapiro-Wilk test (α=0.05) applied to all 16 distributions. Results:

| Algorithm | Operation | W statistic | Result |
|---|---|---|---|
| Kyber-512 | keygen | 0.8117 | Non-normal |
| RSA-2048 | keygen | 0.8753 | Non-normal |
| ML-DSA-44 | sign | 0.7998 | Non-normal |
| ECDSA-256 | sign | 0.7612 | Non-normal |

Non-normality is expected in benchmarks due to OS interruptions, garbage collection, and the probabilistic nature of RSA KeyGen (Miller-Rabin primality testing) and ML-DSA Sign (rejection sampling).

### Non-parametric tests used

| Test | Purpose |
|---|---|
| Kruskal-Wallis | Multi-group comparison (3+ algorithms simultaneously) |
| Mann-Whitney U | Pairwise comparison with effect size and speedup calculation |
| Spearman ρ | Correlation between latency, memory, and temperature |

### Hypotheses

- **H1**: Kyber-512 presents lower energy consumption than RSA-2048 on encapsulation
- **H2**: ML-DSA-44 exhibits lower latency than RSA-2048 on signing
- **H3**: PQC algorithms use more memory than traditional algorithms due to larger key sizes
- **H4**: Shor's algorithm factorizes RSA-2048 in polynomial time; Kyber-512 remains resistant
- **H0**: No statistically significant differences (α=0.05) exist between evaluated algorithms

---

## Reproducibility

The benchmark scripts require:
- Raspberry Pi 5 (ARM64) — results are not reproducible on x86 hardware
- `liboqs` installed and linked to Python via `oqs` module
- INA219 sensor connected via I2C GPIO pins
- No concurrent system load during execution

For analysis reproduction only (no hardware required): the full dataset is in `data/results/` and can be analysed with `analysis/PQC_analysis.ipynb` on any machine.
