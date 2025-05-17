
import os
import pandas as pd
import importlib
from strategies import breaker_pivot_ma_strategy

strategy_module = breaker_pivot_ma_strategy
strategy_config = strategy_module.strategy_config
parameters = strategy_config["parameters"]

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# List of pairs to test
pairs = [
    "EURUSD", "USDJPY", "GBPUSD", "USDCHF",
    "AUDUSD", "NZDUSD", "USDCAD"
]

def load_pair_data(pair):
    m5_path = f"data/{pair}_Candlestick_5_M_BID_26.04.2023-26.04.2025.csv"
    m30_path = f"data/{pair}_Candlestick_30_M_BID_26.04.2023-26.04.2025.csv"
    if not os.path.exists(m5_path) or not os.path.exists(m30_path):
        return None, None
    m5_df = pd.read_csv(m5_path).rename(columns=lambda x: x.strip().lower())
    m30_df = pd.read_csv(m30_path).rename(columns=lambda x: x.strip().lower())
    m5_df = m5_df.rename(columns={"local time": "timestamp"})
    m30_df = m30_df.rename(columns={"local time": "timestamp"})
    return m5_df, m30_df

def run_strategy_for_all_pairs():
    import itertools
    param_names = list(parameters.keys())
    param_values = list(parameters.values())
    all_combos = list(itertools.product(*param_values))

    summary = []

    for pair in pairs:
        m5_df, m30_df = load_pair_data(pair)
        if m5_df is None:
            print(f"⚠️ Missing data for {pair}")
            continue
        print(f"📈 Testing {pair} with {len(all_combos)} combinations")

        for i, combo in enumerate(all_combos, 1):
            print(f"   ⏳ Combo {i}/{len(all_combos)}: {combo}")
            kwargs = dict(zip(param_names, combo))
            kwargs["initial_balance"] = 400
            kwargs["lot_size"] = 0.01

            try:
                trades, equity = strategy_module.run(m5_df.copy(), m30_df.copy(), **kwargs)
                profit = equity - 400
                drawdown = min([t["profit"] for t in trades], default=0)
                summary.append({
                    "pair": pair,
                    **kwargs,
                    "profit": round(profit, 2),
                    "drawdown": round(abs(drawdown), 2),
                    "trades": len(trades)
                })
            except Exception as e:
                print(f"❌ Failed on {pair} combo {combo}: {e}")

    df = pd.DataFrame(summary)
    df.to_csv(os.path.join(output_dir, "summary_all_pairs.csv"), index=False)
    print("✅ All pair backtests complete. Saved to output/summary_all_pairs.csv")

if __name__ == "__main__":
    run_strategy_for_all_pairs()
