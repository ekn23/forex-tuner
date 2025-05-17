import pandas as pd
import numpy as np
import os

def rci(series, length):
    n = length
    rank_price = series.rank(method='first')
    rank_time = pd.Series(np.arange(1, n + 1), index=series.index[-n:])
    d = ((rank_price[-n:].values - rank_time.values) ** 2).sum()
    return 100 * (1 - (6 * d) / (n * (n ** 2 - 1)))

def ma(series, length, ma_type="SMA"):
    if ma_type == "SMA":
        return series.rolling(window=length).mean()
    elif ma_type == "EMA":
        return series.ewm(span=length, adjust=False).mean()
    return series

def run_strategy(symbol, params):
    filepath = f"data/{symbol}_Candlestick_5_M_BID_26.04.2023-26.04.2025.csv"

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")

    m5_df = pd.read_csv(filepath)

    rci_len = params.get("rci_length", 10)
    ma_len = params.get("ma_length", 14)
    ma_type_value = params.get("ma_type", "SMA")
    initial_balance = 400
    lot_size = 0.01

    # Parse timestamp
    if 'timestamp' in m5_df.columns:
        m5_df['timestamp'] = m5_df['timestamp'].str.replace(r" GMT[-+]\d+", "", regex=True)
        m5_df.index = pd.to_datetime(m5_df['timestamp'], format='%d.%m.%Y %H:%M:%S.%f')

    # Calculate RCI & MA
    rci_series = [rci(m5_df['close'].iloc[i - rci_len:i], rci_len) for i in range(rci_len, len(m5_df))]
    m5_df = m5_df.iloc[rci_len:].copy()
    m5_df["RCI"] = rci_series
    m5_df["RCI_MA"] = ma(m5_df["RCI"], ma_len, ma_type_value)

    trades = []
    position = None
    equity = initial_balance

    for i in range(ma_len, len(m5_df)):
        price = m5_df['close'].iloc[i]
        time = m5_df.index[i]
        rci_now, rci_ma_now = m5_df['RCI'].iloc[i], m5_df['RCI_MA'].iloc[i]
        rci_prev, rci_ma_prev = m5_df['RCI'].iloc[i - 1], m5_df['RCI_MA'].iloc[i - 1]

        long_entry = rci_prev < rci_ma_prev and rci_now > rci_ma_now
        short_entry = rci_prev > rci_ma_prev and rci_now < rci_ma_now

        if position is None:
            if long_entry:
                position = {"type": "long", "entry_price": price, "entry_time": time}
            elif short_entry:
                position = {"type": "short", "entry_price": price, "entry_time": time}
        elif position:
            if position['type'] == "long" and (price >= position['entry_price'] + 0.004 or price <= position['entry_price'] - 0.002):
                profit = (price - position['entry_price']) * 100000 * lot_size
                trades.append({**position, "exit_time": time, "exit_price": price, "profit": profit})
                equity += profit
                position = None
            elif position['type'] == "short" and (price <= position['entry_price'] - 0.004 or price >= position['entry_price'] + 0.002):
                profit = (position['entry_price'] - price) * 100000 * lot_size
                trades.append({**position, "exit_time": time, "exit_price": price, "profit": profit})
                equity += profit
                position = None

    # Analyze results
    total_trades = len(trades)
    net_profit = sum(t['profit'] for t in trades)
    wins = [t for t in trades if t['profit'] > 0]
    win_rate = len(wins) / total_trades if total_trades > 0 else 0
    drawdowns = [t['profit'] for t in trades if t['profit'] < 0]
    max_drawdown = min(drawdowns) if drawdowns else 0

    return {
        "total_trades": total_trades,
        "net_profit": net_profit,
        "win_rate": win_rate,
        "max_drawdown": max_drawdown,
        "symbol": symbol
    }

