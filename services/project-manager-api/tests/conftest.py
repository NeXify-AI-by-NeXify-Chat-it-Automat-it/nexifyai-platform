"""Pytest configuration for Project Manager API tests."""
import sys
import os

# Ensure app is importable from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
