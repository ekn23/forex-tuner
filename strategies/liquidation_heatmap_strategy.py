strategy_name = "liquidation_heatmap_strategy"

parameter_grid = {
    "pivot_left": [3],
    "pivot_right": [3],
    "atr_length": [200],
    "atr_multiplier": [0.25, 0.3],
    "volume_window": [200],
}

def run_strategy(symbol, params):
    import pandas as pd
    import numpy as np
    import os

    filepath = f"data/{symbol}_Candlestick_5_M_BID_26.04.2023-26.04.2025.csv"
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")

    df = pd.read_csv(filepath).head(5000)

    # Detect and rename timestamp
    time_col = next((c for c in df.columns if "time" in c.lower()), None)
    if not time_col:
        raise KeyError("No timestamp column found in data.")

    df[time_col] = df[time_col].astype(str).str.replace(r" GMT[-+]\d+", "", regex=True)
    df["timestamp"] = pd.to_datetime(df[time_col], format="%d.%m.%Y %H:%M:%S.%f", errors="coerce")
    df.dropna(subset=["timestamp"], inplace=True)
    df.set_index("timestamp", inplace=True)

    # Rename OHLCV columns
    rename_map = {}
    for target in ["open", "high", "low", "close", "volume"]:
        match = next((col for col in df.columns if target in col.lower()), None)
        if match:
            rename_map[match] = target
        else:
            raise KeyError(f"Missing required column in CSV: {target}")

    df.rename(columns=rename_map, inplace=True)

    # Extract parameters
    left = params["pivot_left"]
    right = params["pivot_right"]
    atr_len = params["atr_length"]
    atr_mult = params["atr_multiplier"]
    vol_window = params["volume_window"]

    # Indicators
    df["atr"] = df["high"].rolling(atr_len).max() - df["low"].rolling(atr_len).min()
    df["atr"] *= atr_mult
    df["vol_avg"] = df["volume"].rolling(vol_window).mean()
    df["vol_max"] = df["volume"].rolling(vol_window).max()

    # Pivot detection
    df["pivot_high"] = df["high"].shift(left) > df["high"].rolling(window=left+right+1, center=True).max()
    df["pivot_low"] = df["low"].shift(left) < df["low"].rolling(window=left+right+1, center=True).min()

    zones = []
    balance = 400
    lot_size = 0.01
    trades = []

    for i in range(max(atr_len, vol_window) + right + 1, len(df)):
        row = df.iloc[i]
        price = row["close"]
        atr = row["atr"]
        vol = row["volume"]
        vol_max = row["vol_max"]

        # Create zone
        if df["pivot_high"].iloc[i - right]:
            zones.append({
                "top": row["high"] + atr,
                "bot": row["high"],
                "type": "short",
                "active": True,
                "strength": min(1, vol / vol_max if vol_max else 0),
            })

        if df["pivot_low"].iloc[i - right]:
            zones.append({
                "top": row["low"],
                "bot": row["low"] - atr,
                "type": "long",
                "active": True,
                "strength": min(1, vol / vol_max if vol_max else 0),
            })

        # Check zone interactions
        for zone in zones:
            if zone["active"] and zone["bot"] < price < zone["top"]:
                if zone["type"] == "long":
                    entry, exit = zone["bot"], zone["top"]
                    profit = (exit - entry) * 100000 * lot_size
                else:
                    entry, exit = zone["top"], zone["bot"]
                    profit = (entry - exit) * 100000 * lot_size

                trades.append(profit)
                balance += profit
                zone["active"] = False

    # Metrics
    total_trades = len(trades)
    net_profit = sum(trades)
    win_rate = len([p for p in trades if p > 0]) / total_trades if total_trades else 0
    max_drawdown = min(trades) if trades else 0

    return {
        "total_trades": total_trades,
        "net_profit": net_profit,
        "win_rate": win_rate,
        "max_drawdown": max_drawdown,
        "symbol": symbol
    }

