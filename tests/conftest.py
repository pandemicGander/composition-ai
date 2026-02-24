import sys
import os
import importlib

# Add tests/ and src/ to sys.path for bare imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest

from helpers import generate_row

# ---------------------------------------------------------------------------
# Variant registry
# ---------------------------------------------------------------------------

VARIANTS = {
    'pure_harmony': {
        'num_features': 12,
        'train_module': 'train_lstm_pure_harmony',
        'predict_module': 'predict_pure_harmony',
        'converter_module': 'data_conversion.converter_pure_harmony',
    },
    'octave_range_harmony': {
        'num_features': 20,
        'train_module': 'train_lstm_octave_range_harmony',
        'predict_module': 'predict_octave_range_harmony',
        'converter_module': 'data_conversion.converter_octave_range_harmony',
    },
    'exact_harmony': {
        'num_features': 108,
        'train_module': 'train_lstm_exact_harmony',
        'predict_module': 'predict_exact_harmony',
        'converter_module': 'data_conversion.converter_exact_harmony',
    },
}

# ---------------------------------------------------------------------------
# Parametrized fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(params=list(VARIANTS.keys()))
def variant_name(request):
    """Yield each variant name in turn."""
    return request.param


@pytest.fixture
def num_features(variant_name):
    return VARIANTS[variant_name]['num_features']


@pytest.fixture
def train_module(variant_name):
    return importlib.import_module(VARIANTS[variant_name]['train_module'])


@pytest.fixture
def predict_module(variant_name):
    return importlib.import_module(VARIANTS[variant_name]['predict_module'])


@pytest.fixture
def converter_module(variant_name):
    return importlib.import_module(VARIANTS[variant_name]['converter_module'])


# ---------------------------------------------------------------------------
# Synthetic data helpers
# ---------------------------------------------------------------------------

def _write_synthetic_file(path, num_features, num_rows=30):
    """Write a synthetic CSV data file with the given number of rows."""
    with open(path, 'w') as f:
        for _ in range(num_rows):
            f.write(','.join(str(b) for b in generate_row(num_features)) + '\n')


@pytest.fixture
def synthetic_data_file(tmp_path, num_features):
    """A single synthetic data file with 30 rows."""
    p = tmp_path / 'song_processed.txt'
    _write_synthetic_file(str(p), num_features, num_rows=30)
    return str(p)


@pytest.fixture
def synthetic_data_files(tmp_path, num_features):
    """Three synthetic data files (enough for train/val split)."""
    paths = []
    for i in range(3):
        p = tmp_path / f'song_{i}_processed.txt'
        _write_synthetic_file(str(p), num_features, num_rows=30)
        paths.append(str(p))
    return paths
