"""
pytest configuration for PQC Benchmarks test suite.

DATA_DIR is resolved relative to the repo root so tests work
regardless of where pytest is invoked from.
"""
# No fixtures needed — DATA_DIR is resolved inside each test class.
# This file exists to mark the tests/ directory as a pytest root.
