"""
Feature Engineering Layer (engine doc §6–12).

Nhóm feature:
  A — Price action (return, gap, body, shadow, vị trí close trong range)
  B — Trend (SMA/EMA, khoảng cách tới MA, slope MA)
  C — Momentum (RSI Wilder, MACD, Stochastic, ROC)
  D — Volume (SMA volume, volume_ratio, xu hướng volume)
  E — Volatility (ATR, rolling std, Bollinger + width)
  F — Structure (đỉnh/đáy 20–50 phiên, support/resistance proxy, khoảng cách breakout)
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _rsi_wilder(close: pd.Series, period: int = 14) -> pd.Series:
    """RSI chuẩn Wilder (smoothing EMA alpha = 1/period), không dùng rolling mean đơn giản."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _atr_wilder(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """True Range rồi làm mượt Wilder — đo biến động thực tế từng phiên."""
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()


def enrich_features(df: pd.DataFrame) -> pd.DataFrame:
    """Bổ sung toàn bộ cột feature; input đã có cột date, open, high, low, close, volume, prev_close."""
    out = df.copy()
    c, h, l, o, v = out["close"], out["high"], out["low"], out["open"], out["volume"]

    # --- Nhóm A: Price action (§7) ---
    out["daily_return"] = c.pct_change()
    out["gap_percent"] = np.where(
        out["prev_close"].replace(0, np.nan).notna(),
        o / out["prev_close"] - 1.0,
        np.nan,
    )
    out["intraday_range"] = np.where(l.replace(0, np.nan) > 0, (h - l) / l, np.nan)
    out["body_size"] = (c - o).abs()
    out["upper_shadow"] = h - pd.concat([o, c], axis=1).max(axis=1)
    out["lower_shadow"] = pd.concat([o, c], axis=1).min(axis=1) - l
    rng = (h - l).replace(0, np.nan)
    # 0 = đóng sát đáy phiên, 1 = sát đỉnh — dùng cho momentum/scoring
    out["close_position_in_range"] = np.where(rng.notna() & (rng > 0), (c - l) / rng, np.nan)

    # --- Nhóm B: Trend (§8) ---
    for w in (5, 10, 20, 50, 200):
        out[f"sma_{w}"] = c.rolling(w, min_periods=w).mean()
    out["ema_12"] = c.ewm(span=12, adjust=False).mean()
    out["ema_26"] = c.ewm(span=26, adjust=False).mean()
    out["macd"] = out["ema_12"] - out["ema_26"]
    out["macd_signal"] = out["macd"].ewm(span=9, adjust=False).mean()
    out["macd_histogram"] = out["macd"] - out["macd_signal"]

    # --- Nhóm C: Momentum (§9) ---
    out["rsi_14"] = _rsi_wilder(c, 14)
    low_14 = l.rolling(14, min_periods=14).min()
    high_14 = h.rolling(14, min_periods=14).max()
    out["stoch_k"] = np.where(
        (high_14 - low_14).replace(0, np.nan) > 0,
        100 * (c - low_14) / (high_14 - low_14),
        np.nan,
    )
    out["stoch_d"] = out["stoch_k"].rolling(3, min_periods=3).mean()
    out["roc_10"] = (c / c.shift(10) - 1.0) * 100.0

    # --- Nhóm D: Volume (§10) ---
    out["volume_sma_5"] = v.rolling(5, min_periods=5).mean()
    out["volume_sma_20"] = v.rolling(20, min_periods=20).mean()
    out["volume_ratio"] = np.where(
        out["volume_sma_20"].replace(0, np.nan) > 0,
        v / out["volume_sma_20"],
        np.nan,
    )
    out["up_volume"] = np.where(c >= o, v, 0.0)
    out["down_volume"] = np.where(c < o, v, 0.0)
    out["volume_trend"] = out["volume_sma_5"] - out["volume_sma_20"]

    # --- Nhóm E: Volatility (§11) ---
    out["atr_14"] = _atr_wilder(h, l, c, 14)
    out["rolling_std_20"] = c.pct_change().rolling(20, min_periods=20).std()
    out["bollinger_middle"] = out["sma_20"]
    std20 = c.rolling(20, min_periods=20).std()
    out["bollinger_upper"] = out["bollinger_middle"] + 2 * std20
    out["bollinger_lower"] = out["bollinger_middle"] - 2 * std20
    out["bollinger_width"] = np.where(
        out["bollinger_middle"].replace(0, np.nan) > 0,
        (out["bollinger_upper"] - out["bollinger_lower"]) / out["bollinger_middle"],
        np.nan,
    )

    # --- Nhóm F: Structure (§12) ---
    out["highest_high_20"] = h.rolling(20, min_periods=20).max()
    out["lowest_low_20"] = l.rolling(20, min_periods=20).min()
    out["highest_high_50"] = h.rolling(50, min_periods=50).max()
    out["lowest_low_50"] = l.rolling(50, min_periods=50).min()
    out["support_zone"] = out["lowest_low_20"]
    out["resistance_zone"] = out["highest_high_20"]
    # Khoảng cách tới “breakout” = còn bao xa đỉnh 20 phiên (theo tỷ lệ trên giá)
    out["distance_to_breakout"] = np.where(
        c.replace(0, np.nan) > 0,
        (out["highest_high_20"] - c) / c,
        np.nan,
    )
    out["distance_to_support"] = np.where(
        c.replace(0, np.nan) > 0,
        (c - out["support_zone"]) / c,
        np.nan,
    )

    # Slope MA: so sánh SMA hôm nay vs 5 phiên trước (§8.4)
    sma20_lag5 = out["sma_20"].shift(5)
    out["trend_slope_20"] = np.where(
        sma20_lag5.replace(0, np.nan) > 0,
        (out["sma_20"] - sma20_lag5) / sma20_lag5,
        np.nan,
    )
    sma50_lag5 = out["sma_50"].shift(5)
    out["trend_slope_50"] = np.where(
        sma50_lag5.replace(0, np.nan) > 0,
        (out["sma_50"] - sma50_lag5) / sma50_lag5,
        np.nan,
    )

    # Cờ boolean / khoảng cách chuẩn hóa — phục vụ state & strategy
    out["close_above_sma20"] = c > out["sma_20"]
    out["close_above_sma50"] = c > out["sma_50"]
    out["close_above_sma200"] = c > out["sma_200"]
    out["sma20_above_sma50"] = out["sma_20"] > out["sma_50"]
    out["sma50_above_sma200"] = out["sma_50"] > out["sma_200"]
    out["distance_to_sma20"] = np.where(
        out["sma_20"].replace(0, np.nan) > 0,
        (c - out["sma_20"]) / out["sma_20"],
        np.nan,
    )
    out["distance_to_sma50"] = np.where(
        out["sma_50"].replace(0, np.nan) > 0,
        (c - out["sma_50"]) / out["sma_50"],
        np.nan,
    )
    out["distance_to_sma200"] = np.where(
        out["sma_200"].replace(0, np.nan) > 0,
        (c - out["sma_200"]) / out["sma_200"],
        np.nan,
    )

    return out


def last_numeric(row: pd.Series, key: str, default: float = 0.0) -> float:
    """Lấy giá trị số tại dòng cuối; NaN/None → default (tránh so sánh lỗi trong scoring)."""
    v = row.get(key)
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return default
    return float(v)
