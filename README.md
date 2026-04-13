# pqc-benchmarks

**Empirical performance evaluation of NIST-standardized post-quantum cryptography algorithms on ARM64 IoT hardware.**

Kyber-512 (ML-KEM) and ML-DSA-44 benchmarked against RSA-2048 and ECC-256 across 16,000 measurements on a Raspberry Pi 5. Part of my undergraduate thesis at MSMK University, 2025/2026.

---

## Research question

> Are NIST-standardized post-quantum cryptography algorithms (ML-KEM/Kyber-512 and ML-DSA/ML-DSA-44) superior to traditional algorithms (RSA-2048 and ECC-256) for IoT devices based on modern ARM64 architecture (Raspberry Pi 5), considering operational efficiency — latency, energy consumption, memory usage — and differential resistance against the quantum threat projected for 2028–2035?

---

## Key findings

| Algorithm | Operation | Median latency (ms) | vs RSA-2048       |
| --------- | --------- | ------------------- | ----------------- |
| Kyber-512 | keygen    | 0.085               | **2,345× faster** |
| Kyber-512 | decaps    | 0.070               | —                 |
| ML-DSA-44 | sign      | 0.645               | **6× faster**     |
| ECDH-256  | derive    | 0.245               | 1,685× faster     |
| ECDSA-256 | sign      | 0.185               | 20× faster        |
| RSA-2048  | keygen    | 198.606             | baseline          |
| RSA-2048  | sign      | 3.619               | baseline          |

- **Kyber-512 is 2,345× faster than RSA-2048 on keygen** — Mann-Whitney U=0.0, p<0.001 (perfect statistical separation). Kyber KeyGen profile is ideal for IoT: extreme speed with thermal neutrality (−3.3°C cumulative over 1,000 iterations).
- **ML-DSA-44 sign is 6× faster than RSA-2048 sign** — despite generating more cumulative heat (+6.1°C vs −7.3°C), demonstrating that computational intensity per ms matters more than total duration.
- **All distributions are non-normal** — Shapiro-Wilk confirms non-normality across all algorithms (W range: 0.76–0.88), justifying the use of non-parametric tests throughout.
- **Statistical significance confirmed** — Kruskal-Wallis: KeyGen H=2651.34 p<0.001, Sign H=2663.30 p<0.001. All pairwise comparisons significant at α=0.05.
- **PQC algorithms are viable for ARM64 IoT deployment** at this hardware tier.

---

## Dataset

- **16 CSV files**, 1,000 iterations each → **16,000 total measurements**
- **8 metrics per measurement**: latency (ms), process memory (MB), system memory (MB), temperature delta (°C), absolute temperature (°C), current draw (mA)
- **Hardware**: Raspberry Pi 5, 8GB RAM, ARM64, Ubuntu Server 24.04
- **Warm-up**: 10 iterations discarded before each measurement series
- **Cooldown**: 1s pause every 100 iterations to prevent thermal drift

| Algorithm | Operations measured                    |
| --------- | -------------------------------------- |
| Kyber-512 | keygen, encaps, decaps                 |
| ML-DSA-44 | keygen, sign, verify                   |
| RSA-2048  | keygen, encrypt, decrypt, sign, verify |
| ECDSA-256 | keygen, sign, verify                   |
| ECDH-256  | keygen, derive                         |

---

## Repository structure

```
pqc-benchmarks/
├── benchmarks/
│   ├── benchmark_complete.py     ← main benchmark script (n=1,000)
│   ├── benchmark_keygen.py       ← preliminary keygen experiment (n=500)
│   └── helpers.py                ← sensor utilities: INA219, CPU temp, memory
├── scripts/
│   ├── shor_demo.py              ← animated terminal demo of Shor's algorithm
│   ├── test_ina219.py            ← INA219 sensor validation
│   ├── test_oled.py              ← OLED display validation
│   └── test_quick.py             ← quick 10-iteration test
├── data/
│   └── results/                  ← 16 CSVs, raw measurements
├── analysis/
│   └── PQC_analysis.ipynb        ← full statistical analysis
├── figures/                      ← generated visualizations
└── docs/
    └── methodology.md            ← hardware setup, sensor limitations, decisions
```

---

## Run locally

```bash
git clone https://github.com/HuguitoH/pqc-benchmarks
cd pqc-benchmarks
pip install -r requirements.txt

# Run the full statistical analysis
jupyter notebook analysis/PQC_analysis.ipynb

# Run Shor's algorithm demo
python scripts/shor_demo.py
```

> [!NOTE] `benchmarks/benchmark_complete.py` requires a Raspberry Pi 5 with `liboqs` and the INA219 sensor configured. It cannot be run on standard hardware.

---

## Statistical methodology

All distributions were tested for normality using Shapiro-Wilk (α=0.05). Non-normality was confirmed across all algorithms — expected in benchmarks due to OS interruptions, garbage collection, and the probabilistic nature of RSA KeyGen (Miller-Rabin) and ML-DSA Sign (rejection sampling).

This justifies the exclusive use of non-parametric tests:

| Test           | Purpose                                              |
| -------------- | ---------------------------------------------------- |
| Kruskal-Wallis | Multi-group comparison (3+ algorithms)               |
| Mann-Whitney U | Pairwise comparison with effect size                 |
| Spearman ρ     | Correlation between latency, memory, and temperature |

---

## Hardware limitations

**INA219 current sensor**: The sensor was configured to measure current draw on the Raspberry Pi 5's power rail. Due to bus measurement limitations, the readings capture total system current rather than the isolated cryptographic operation. The `current_ma` column in the CSVs reflects delta values (after − before each operation) and should be interpreted as an indicator of relative energy impact, not absolute per-operation consumption.

This limitation is documented in the thesis and is a target for improvement in Phase 2 (see Future work).

---

## Key size comparison

Beyond latency, key and signature sizes have direct implications for IoT bandwidth — especially on constrained networks (LoRaWAN, MQTT over 2G).

| Algorithm | Public key | Private key | Signature / Ciphertext |
| --------- | ---------- | ----------- | ---------------------- |
| Kyber-512 | 800 B      | 1,632 B     | 768 B                  |
| ML-DSA-44 | 1,312 B    | 2,560 B     | 2,420 B                |
| RSA-2048  | 256 B      | 1,193 B     | 256 B                  |
| ECDSA-256 | 64 B       | 32 B        | 64 B                   |
| ECDH-256  | 64 B       | 32 B        | —                      |

PQC algorithms have significantly larger key and signature sizes. While latency favours PQC, bandwidth-constrained IoT deployments must account for this overhead.

---

## Estimated TLS 1.3 handshake latency

> [!CAUTION] This is a calculated projection, not a direct measurement.Network overhead, certificate parsing, and protocol framing are excluded. See [Future work](#future-work) for the planned direct TLS measurement.

Estimated from empirical medians — summing the cryptographic operations involved in a TLS 1.3 handshake:

| Scenario             | Components                               | Estimated latency |
| -------------------- | ---------------------------------------- | ----------------- |
| RSA-2048 (legacy)    | keygen + sign + verify + ECDH derive     | ~202.7 ms         |
| PQC (Kyber + ML-DSA) | keygen + encaps + decaps + sign + verify | ~1.07 ms          |

**~189× reduction in estimated TLS handshake latency** when migrating from RSA-2048 to Kyber-512 + ML-DSA-44.

---

## Future work

1. **Direct TLS 1.3 measurement** — OQS-OpenSSL fork with Kyber and ML-DSA support on RPi 5 acting as server, measuring real handshake latency end-to-end
2. **Isolated energy consumption** — improve INA219 setup to measure per-process current draw, not total bus current
3. **ML-KEM comparison** — benchmark the final NIST standard (ML-KEM, FIPS 203) vs the Kyber-512 implementation used here
4. **Hybrid PQC + Classical** — NIST recommends hybrid schemes during the transition period; measure the overhead of combining Kyber + ECDH
5. **Lower hardware tier** — reproduce on ESP32 or similar microcontroller to evaluate feasibility below the RPi 5 tier

---

## Context

Post-quantum cryptography addresses the threat that sufficiently powerful quantum computers pose to current asymmetric cryptography. RSA and ECC security relies on the hardness of integer factorization and discrete logarithm problems — both solvable in polynomial time by Shor's algorithm on a quantum computer.

NIST finalized its PQC standards in 2024: FIPS 203 (ML-KEM, based on Kyber) and FIPS 204 (ML-DSA, based on Dilithium). This benchmark evaluates whether these standards are viable for resource-constrained IoT environments — not just on server hardware.

The quantum threat timeline is estimated at 2028–2035 for cryptographically relevant quantum computers. The migration window is now.

---

**Hugo Hernández Moreno** · MSMK University · 2025/2026 ·
[github.com/HuguitoH](https://github.com/HuguitoH)
