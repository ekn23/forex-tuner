from .breaker_pivot_ma_strategy import run_strategy as run_breaker_strategy
from .rci_strategy import run_strategy as run_rci_strategy

def get_strategy_config(strategy_name):
    if strategy_name == "breaker_pivot_ma_strategy":
        return {
            "parameter_grid": {
                "ma_type": ["SMA", "EMA"],
                "ma_length": [10, 20, 30],
                "osc_length": [5, 10],
                "osc_threshold": [0.2, 0.3, 0.4],
                "pivot_left": [3],
                "pivot_right": [2],
                "volatility_threshold": [1, 2],
                "calc_window": [None],
                "entry_mode": ["both"],
                "retest_enabled": [True, False],
            }
        }
    elif strategy_name == "rci_strategy":
        return {
            "parameter_grid": {
                "rci_length": [9, 14, 21],
                "threshold": [0.7, 0.8, 0.9],
                "smoothing": [True, False],
                "lookback_window": [20, 30],
            }
        }
    else:
        raise ValueError(f"Unknown strategy config: {strategy_name}")

def run_backtest(strategy_name, symbol, params):
    if strategy_name == "breaker_pivot_ma_strategy":
        return run_breaker_strategy(symbol, params)
    elif strategy_name == "rci_strategy":
        return run_rci_strategy(symbol, params)
    else:
        raise ValueError(f"No backtest runner for: {strategy_name}")

