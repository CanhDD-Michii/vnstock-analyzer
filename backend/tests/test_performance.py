from datetime import date

from app.modules.stocks.performance import compute_performance_from_bars


def test_compute_performance_from_bars_two_days():
    bars = [
        {"trading_date": date(2026, 4, 7), "close_price": 100.0},
        {"trading_date": date(2026, 4, 8), "close_price": 102.0},
    ]
    p = compute_performance_from_bars(bars)
    assert p["close_price"] == 102.0
    assert p["pct_day"] == 2.0
    assert p["as_of_date"] == date(2026, 4, 8)


def test_compute_performance_empty():
    p = compute_performance_from_bars([])
    assert p["close_price"] is None
