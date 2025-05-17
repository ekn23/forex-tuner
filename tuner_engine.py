import os
import pandas as pd
import numpy as np
from strategies import get_strategy_config
import matplotlib.pyplot as plt
from itertools import product

def run_backtest(strategy_runner, data_m5, data_m30, params):
    result = strategy_runner(data_m5, data_m30, params)
    trades = result["trades"]
    equity = result["equity_curve"]
    stats = result["stats"]
    return trades, equity, stats

def run_parameter_sweep(strategy_name, symbol, data_path="data", output_path="output"):
    config = get_strategy_config(strategy_name)
    strategy_runner = config["runner"]
    param_grid = config["params"]

    # Load data
    m5_file = f"{symbol}_Candlestick_5_M_BID_26.04.2023-26.04.2025.csv"
    m30_file = f"{symbol}_Candlestick_30_M_BID_26.04.2023-26.04.2025.csv"

    m5_df = pd.read_csv(
        os.path.join(data_path, m5_file),
        parse_dates=["Local time"],
        index_col="Local time",
        dayfirst=True
    ).head(5000)

    m30_df = pd.read_csv(
        os.path.join(data_path, m30_file),
        parse_dates=["Local time"],
        index_col="Local time",
        dayfirst=True
    ).head(2000)

    keys, values = zip(*param_grid.items())
    combos = [dict(zip(keys, v)) for v in product(*values)]

    summary = []
    os.makedirs(output_path, exist_ok=True)

    for i, combo in enumerate(combos):
        print(f"🔁 Running combo {i+1}/{len(combos)}: {combo}")
        try:
            trades, equity, stats = run_backtest(strategy_runner, m5_df.copy(), m30_df.copy(), combo)

            print(f"[DEBUG] Trades: {len(trades)} | Final Equity: {equity[-1] if equity else 'N/A'} | Net: {stats.get('net_profit', 0)}")

            equity_series = pd.Series(equity)
            equity_series.index = range(len(equity_series))

            summary.append({
                "Parameters": combo,
                "Total Trades": stats.get("total_trades", 0),
                "Net Profit": stats.get("net_profit", 0),
                "Win Rate": stats.get("win_rate", 0),
                "Max Drawdown": stats.get("max_drawdown", 0),
            })

            # Save equity chart
            chart_filename = f"{symbol}_combo_{i+1}_equity.png"
            chart_path = os.path.join(output_path, chart_filename)
            print(f"[DEBUG] Saving chart to: {chart_path}")

            plt.figure(figsize=(10, 4))
            plt.plot(equity_series)
            plt.title(f"Equity Curve - {symbol} - Combo {i+1}")
            plt.xlabel("Trade #")
            plt.ylabel("Equity ($)")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(chart_path)
            plt.close()

        except Exception as e:
            print(f"❌ Failed on combo {combo}: {e}")

    # Save summary file
    summary_df = pd.DataFrame(summary)
    summary_csv = os.path.join(output_path, f"{symbol}_summary.csv")
    print(f"[DEBUG] Saving summary to: {summary_csv}")
    summary_df.to_csv(summary_csv, index=False)

