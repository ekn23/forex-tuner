# tuner_runner.py
import argparse
from tuner_engine import run_parameter_sweep

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", required=True, help="Name of strategy module to run")
    parser.add_argument("--symbol", required=False, help="Optional symbol to override default (e.g., USDJPY)")
    args = parser.parse_args()

    # Pass symbol override to tuner_engine
    run_parameter_sweep(args.strategy, symbol=args.symbol)

