import importlib.util
import os

STRATEGY_FOLDER = os.path.dirname(__file__)
strategy_registry = {}

# Dynamically load each strategy
for file in os.listdir(STRATEGY_FOLDER):
    if file.endswith(".py") and file != "__init__.py":
        path = os.path.join(STRATEGY_FOLDER, file)
        spec = importlib.util.spec_from_file_location(file[:-3], path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "strategy_name") and hasattr(module, "run_strategy") and hasattr(module, "parameter_grid"):
            strategy_registry[module.strategy_name] = {
                "run": module.run_strategy,
                "params": module.parameter_grid
            }

def get_strategy_config(name):
    if name in strategy_registry:
        return {"parameter_grid": strategy_registry[name]["params"]}
    raise ValueError(f"Unknown strategy config: {name}")

def run_backtest(name, symbol, params):
    if name in strategy_registry:
        return strategy_registry[name]["run"](symbol, params)
    raise ValueError(f"Unknown strategy logic: {name}")

