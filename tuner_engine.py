import itertools
import time
import traceback
import pandas as pd
from strategies import get_strategy_config, run_backtest

def run_parameter_sweep(strategy_name, symbol="EURUSD"):
    try:
        config = get_strategy_config(strategy_name)
        param_grid = config["parameter_grid"]
        combinations = list(itertools.product(*param_grid.values()))

        print(f"🧠 Total parameter combinations: {len(combinations)}")

        results_list = []
        start_time = time.time()

        for idx, combo in enumerate(combinations, 1):
            combo_start = time.time()
            params = dict(zip(param_grid.keys(), combo))
            print(f"🔁 Running combo {idx}/{len(combinations)}: {params}")

            try:
                result = run_backtest(strategy_name, symbol, params)
                full_result = {**params, **result}
                results_list.append(full_result)
                print(f"✅ Result: {result}")
            except Exception as e:
                print(f"❌ Failed on combo {params}: {e}")
                traceback.print_exc()

            elapsed = time.time() - combo_start
            total_elapsed = time.time() - start_time
            est_total = (total_elapsed / idx) * len(combinations)
            est_remaining = est_total - total_elapsed
            print(f"⏱ Combo took {round(elapsed, 2)}s — ETA: {round(est_remaining, 2)}s left\n")

        # ✅ Save all results to CSV
        df = pd.DataFrame(results_list)
        output_path = f"output/{strategy_name}_results.csv"
        df.to_csv(output_path, index=False)
        print(f"✅ All results saved to: {output_path}")
        print(f"✅ Finished all {len(combinations)} combos in {round(time.time() - start_time, 2)} seconds")

    except Exception as e:
        print(f"🔥 Error in run_parameter_sweep: {e}")
        traceback.print_exc()

