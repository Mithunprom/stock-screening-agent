import pandas as pd

from src.features.volatility import average_true_range, realized_volatility


def test_realized_volatility_positive() -> None:
    series = pd.Series([0.01, -0.02, 0.015, 0.03, -0.01, 0.02])
    rv = realized_volatility(series, window=5)
    assert rv.iloc[-1] > 0


def test_average_true_range_positive() -> None:
    frame = pd.DataFrame(
        {
            "ticker": ["ABC"] * 5,
            "close": [10, 11, 12, 11, 13],
            "high": [11, 12, 13, 12, 14],
            "low": [9, 10, 11, 10, 12],
        }
    )
    atr = average_true_range(frame, window=3)
    assert atr.iloc[-1] > 0

