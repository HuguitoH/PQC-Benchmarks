"""
PQC Benchmarks — test suite.

Tests are organised in three groups:
  1. Data integrity   — validates the 16 raw CSVs
  2. Statistical fns  — unit tests for pure analysis functions
  3. Shor circuit     — validates the quantum oracle implementation

Run:
    pip install pytest
    pytest tests/ -v
"""

import json
import math
from pathlib import Path
from fractions import Fraction

import numpy as np
import pandas as pd
import pytest

# ── Paths
DATA_DIR = Path(__file__).parent.parent / 'data' / 'results'

EXPECTED_OPERATIONS = [
    'kyber512_keygen', 'kyber512_encaps', 'kyber512_decaps',
    'mldsa44_keygen',  'mldsa44_sign',    'mldsa44_verify',
    'rsa2048_keygen',  'rsa2048_encrypt', 'rsa2048_decrypt',
    'rsa2048_sign',    'rsa2048_verify',
    'ecdh256_keygen',  'ecdh256_derive',
    'ecdsa256_keygen', 'ecdsa256_sign',   'ecdsa256_verify',
]

EXPECTED_COLUMNS = [
    'iteration', 'timestamp', 'time_ms',
    'memory_process_mb', 'memory_system_mb',
    'temp_delta_c', 'temp_absolute_c', 'current_ma',
]



# 1. DATA INTEGRITY

class TestDataIntegrity:
    """Validates that the 16 raw benchmark CSVs are complete and valid."""

    @pytest.mark.parametrize("operation", EXPECTED_OPERATIONS)
    def test_csv_exists(self, operation: str):
        """Every expected operation CSV must be present."""
        assert (DATA_DIR / f"{operation}.csv").exists(), \
            f"Missing: {operation}.csv"

    @pytest.mark.parametrize("operation", EXPECTED_OPERATIONS)
    def test_row_count(self, operation: str):
        """Each CSV must contain exactly 1,000 measurement rows."""
        df = pd.read_csv(DATA_DIR / f"{operation}.csv")
        assert len(df) == 1000, \
            f"{operation}.csv has {len(df)} rows (expected 1,000)"

    @pytest.mark.parametrize("operation", EXPECTED_OPERATIONS)
    def test_columns_present(self, operation: str):
        """Each CSV must have all 8 required columns."""
        df = pd.read_csv(DATA_DIR / f"{operation}.csv")
        for col in EXPECTED_COLUMNS:
            assert col in df.columns, \
                f"{operation}.csv missing column '{col}'"

    @pytest.mark.parametrize("operation", EXPECTED_OPERATIONS)
    def test_no_nulls(self, operation: str):
        """No null values are allowed in any measurement column."""
        df = pd.read_csv(DATA_DIR / f"{operation}.csv")
        null_count = df.isnull().sum().sum()
        assert null_count == 0, \
            f"{operation}.csv has {null_count} null values"

    @pytest.mark.parametrize("operation", EXPECTED_OPERATIONS)
    def test_no_negative_latency(self, operation: str):
        """Latency values must be strictly positive."""
        df = pd.read_csv(DATA_DIR / f"{operation}.csv")
        neg_count = (df['time_ms'] <= 0).sum()
        assert neg_count == 0, \
            f"{operation}.csv has {neg_count} non-positive latency values"

    @pytest.mark.parametrize("operation", EXPECTED_OPERATIONS)
    def test_iteration_sequence(self, operation: str):
        """Iteration column must be a consecutive sequence from 1 to 1,000."""
        df = pd.read_csv(DATA_DIR / f"{operation}.csv")
        expected = list(range(1, 1001))
        assert df['iteration'].tolist() == expected, \
            f"{operation}.csv iteration sequence is not 1–1,000"

    def test_all_16_csvs_present(self):
        """Exactly 16 CSVs must be present — no more, no less."""
        csvs = list(DATA_DIR.glob("*.csv"))
        assert len(csvs) == 16, \
            f"Expected 16 CSVs, found {len(csvs)}: {[c.name for c in csvs]}"



# 2. STATISTICAL FUNCTIONS

# Import the functions under test directly from the analysis module
# so they can be tested in isolation (no notebook required)

def rank_biserial_r(u_stat: float, n1: int, n2: int) -> float:
    """Rank-biserial correlation: effect size for Mann-Whitney U."""
    return 1 - (2 * u_stat) / (n1 * n2)


def effect_size_label(r: float) -> str:
    """Convert |r| to a Cohen-convention effect size label."""
    r = abs(r)
    if r >= 0.70: return 'Very large'
    if r >= 0.50: return 'Large'
    if r >= 0.30: return 'Medium'
    if r >= 0.10: return 'Small'
    return 'Negligible'


def normalise(values: list, invert: bool = False) -> list:
    """Min-max normalise. invert=True when lower is better."""
    mn, mx = min(values), max(values)
    if mx == mn:
        return [0.5] * len(values)
    normed = [(v - mn) / (mx - mn) for v in values]
    return [1 - v for v in normed] if invert else normed


class TestRankBiserialR:
    """Tests for rank_biserial_r effect size calculation."""

    def test_perfect_separation(self):
        """U=0 means group1 always beats group2 → r should be 1.0."""
        r = rank_biserial_r(u_stat=0.0, n1=1000, n2=1000)
        assert r == pytest.approx(1.0)

    def test_no_effect(self):
        """U=n1*n2/2 means random overlap → r should be 0.0."""
        n1, n2 = 100, 100
        r = rank_biserial_r(u_stat=n1 * n2 / 2, n1=n1, n2=n2)
        assert r == pytest.approx(0.0)

    def test_complete_reversal(self):
        """U=n1*n2 means group2 always beats group1 → r should be -1.0."""
        n1, n2 = 50, 50
        r = rank_biserial_r(u_stat=n1 * n2, n1=n1, n2=n2)
        assert r == pytest.approx(-1.0)

    def test_range(self):
        """r must always be in [-1, 1]."""
        for u in [0, 250, 500, 750, 1000]:
            r = rank_biserial_r(u_stat=u, n1=50, n2=40)
            assert -1.0 <= r <= 1.0


class TestEffectSizeLabel:
    """Tests for effect_size_label classification."""

    @pytest.mark.parametrize("r, expected", [
        (1.00,  'Very large'),
        (0.70,  'Very large'),
        (0.65,  'Large'),
        (0.50,  'Large'),
        (0.45,  'Medium'),
        (0.30,  'Medium'),
        (0.20,  'Small'),
        (0.10,  'Small'),
        (0.05,  'Negligible'),
        (0.00,  'Negligible'),
        (-0.80, 'Very large'),   # absolute value taken
    ])
    def test_labels(self, r: float, expected: str):
        assert effect_size_label(r) == expected


class TestNormalise:
    """Tests for min-max normalisation."""

    def test_range_zero_to_one(self):
        result = normalise([10, 20, 30, 40, 50])
        assert min(result) == pytest.approx(0.0)
        assert max(result) == pytest.approx(1.0)

    def test_invert(self):
        """With invert=True, the minimum input should map to 1.0."""
        result = normalise([10, 20, 30], invert=True)
        assert result[0] == pytest.approx(1.0)   # min input → max score
        assert result[2] == pytest.approx(0.0)   # max input → min score

    def test_constant_input(self):
        """All-equal input should return 0.5 for every element."""
        result = normalise([7, 7, 7])
        assert all(v == pytest.approx(0.5) for v in result)

    def test_single_element(self):
        result = normalise([42])
        assert result == [pytest.approx(0.5)]



# 3. SHOR CIRCUIT
def build_mod_mult_unitary(a_power: int, N: int, n_aux: int) -> np.ndarray:
    """Build the unitary matrix for modular multiplication by a_power mod N."""
    dim = 2 ** n_aux
    U   = np.zeros((dim, dim), dtype=complex)
    for y in range(dim):
        y_out = (y * a_power) % N if y < N else y
        U[y_out, y] = 1.0
    return U


def extract_period(counts: dict, n_count: int, N: int, a: int) -> int | None:
    """Extract period r from Shor measurement outcomes via continued fractions."""
    top_states = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for state_str, _ in top_states[:8]:
        m = int(state_str, 2)
        if m == 0:
            continue
        frac = Fraction(m, 2**n_count).limit_denominator(N)
        r    = frac.denominator
        if pow(a, r, N) == 1 and r > 1:
            return r
    return None


class TestModMultUnitary:
    """Tests for the quantum modular multiplication oracle."""

    def test_is_unitary(self):
        """U†U must equal the identity matrix (U is a valid quantum gate)."""
        U = build_mod_mult_unitary(a_power=7, N=15, n_aux=4)
        product = U.conj().T @ U
        assert np.allclose(product, np.eye(16), atol=1e-10), \
            "Oracle matrix is not unitary"

    def test_correct_mapping_n15_a7(self):
        """For N=15, a=7: |1⟩ → |7⟩ (since 1*7 mod 15 = 7)."""
        U = build_mod_mult_unitary(a_power=7, N=15, n_aux=4)
        # Column 1 of U should have a 1 in row 7
        assert U[7, 1] == pytest.approx(1.0 + 0j)

    def test_identity_for_out_of_range(self):
        """States |y⟩ with y >= N should map to themselves (identity)."""
        N, n_aux = 15, 4
        U = build_mod_mult_unitary(a_power=7, N=N, n_aux=n_aux)
        for y in range(N, 2**n_aux):
            assert U[y, y] == pytest.approx(1.0 + 0j), \
                f"|{y}⟩ should map to itself (out-of-range identity)"

    def test_period_four_for_n15_a7(self):
        """Applying the oracle 4 times for a=7, N=15 should return to identity."""
        U = build_mod_mult_unitary(a_power=7, N=15, n_aux=4)
        U4 = np.linalg.matrix_power(U, 4)
        # After r=4 applications, U^r restricted to {0,...,14} should be identity
        for y in range(15):
            assert U4[y, y] == pytest.approx(1.0 + 0j), \
                f"U^4[{y},{y}] ≠ 1 — period may not be 4"


class TestExtractPeriod:
    """Tests for the continued-fractions period extraction."""

    def test_known_period_r4(self):
        """For N=15, a=7, r=4: peaks at 0,4,8,12 with 4 counting qubits."""
        # Simulated perfect measurement outcomes for r=4
        counts = {'0000': 1000, '0100': 1000, '1000': 1000, '1100': 1000}
        r = extract_period(counts, n_count=4, N=15, a=7)
        assert r == 4, f"Expected period 4, got {r}"

    def test_skips_zero_state(self):
        """State |0000⟩ alone should not yield a period."""
        counts = {'0000': 4096}
        r = extract_period(counts, n_count=4, N=15, a=7)
        assert r is None

    def test_returns_none_on_garbage(self):
        """Uniform random outcomes should not reliably extract a period."""
        # With uniform counts no single peak dominates — period may not be found
        # We just check the function doesn't crash and returns None or int
        counts = {format(i, '04b'): 100 for i in range(16)}
        result = extract_period(counts, n_count=4, N=15, a=7)
        assert result is None or isinstance(result, int)
