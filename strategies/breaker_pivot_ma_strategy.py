strategy_name = "breaker_pivot_ma_strategy"

parameter_grid = {
    "ma_type": ["SMA", "EMA"],
    "ma_length": [20, 50],
    "osc_length": [10],
    "osc_threshold": [0.3],
    "pivot_left": [3],
    "pivot_right": [3],
    "volatility_threshold": [2],
    "entry_mode": ["both"],
    "retest_enabled": [True]
}

def run_strategy(data_m5, data_m30, params):
    # Example logic (simplified; replace with full logic if needed)
    trades = []
    equity_curve = []
    balance = 400  # Start with $400
    equity_curve.append(balance)

    for i in range(50, len(data_m5)):
        close = data_m5['Close'].iloc[i]
        open_price = close - 0.001
        tp = close + 0.002
        sl = close - 0.001

        # Example: trigger on every 100th bar
        if i % 100 == 0:
            trades.append({
                "entry_time": data_m5.index[i],
                "entry_price": open_price,
                "exit_time": data_m5.index[i+5] if i+5 < len(data_m5) else data_m5.index[-1],
                "exit_price": tp,
                "pnl": tp - open_price,
                "direction": "long"
            })
            balance += tp - open_price
        equity_curve.append(balance)

    stats = {
        "total_trades": len(trades),
        "net_profit": balance - 400,
        "win_rate": 100 if trades else 0,
        "max_drawdown": 0
    }

    return {
        "trades": trades,
        "equity_curve": equity_curve,
        "stats": stats
    }

