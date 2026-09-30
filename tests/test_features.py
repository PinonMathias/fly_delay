from src.flightradar.features import FEATURES, FORBIDDEN_COLS


def test_no_leakage_in_features():
    assert not set(FEATURES) & FORBIDDEN_COLS
