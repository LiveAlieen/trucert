"""Pytest configuration file"""

import sys
import os
import pytest

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from cert_manager.core.utils import initialize_dependencies


def pytest_sessionstart(session):
    """Initialize dependencies before tests start"""
    print("Initializing dependencies for tests...")
    initialize_dependencies()
    print("Dependencies initialized successfully!")

