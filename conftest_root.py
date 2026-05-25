# Root conftest.py for pytest configuration

import pytest
import sys
from pathlib import Path

# Adicionar root ao path
ROOT_DIR = Path(__file__).resolve().parents[0]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Markers para categorizar testes
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: testes unitários")
    config.addinivalue_line("markers", "integration: testes de integração")
    config.addinivalue_line("markers", "e2e: testes end-to-end")
    config.addinivalue_line("markers", "slow: testes que demoram")
    config.addinivalue_line("markers", "api: testes de API")
    config.addinivalue_line("markers", "database: testes com banco de dados")
