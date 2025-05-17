from . import breaker_pivot_ma_strategy

STRATEGY_REGISTRY = {
    "breaker_pivot_ma_strategy": breaker_pivot_ma_strategy,
}

def get_strategy_config(name):
    if name not in STRATEGY_REGISTRY:
        raise ValueError(f"Unknown strategy config: {name}")
    return {
        "name": STRATEGY_REGISTRY[name].strategy_name,
        "params": STRATEGY_REGISTRY[name].parameter_grid,
        "runner": STRATEGY_REGISTRY[name].run_strategy,
    }

