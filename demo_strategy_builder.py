"""
Demo strategy builder for testing the visual strategy builder
Creates a complete working strategy with proper node connections
"""

import json
from pathlib import Path


def create_demo_strategy():
    """Create a demo strategy with all necessary nodes and connections"""
    
    # Define a complete EMA crossover strategy with RSI filter
    strategy_data = {
        "strategy_name": "EMA_RSI_Demo",
        "description": "Demo strategy using EMA crossover with RSI filter",
        "nodes": [
            {
                "id": "market_data_1",
                "type": "market_data",
                "position": [100, 100],
                "parameters": {
                    "pair": "BTC/USDT",
                    "timeframe": "1h",
                    "lookback": 500
                }
            },
            {
                "id": "ema_fast_1",
                "type": "indicator",
                "position": [300, 50],
                "parameters": {
                    "indicator_type": "EMA",
                    "period": 10,
                    "source": "close"
                }
            },
            {
                "id": "ema_slow_1",
                "type": "indicator",
                "position": [300, 150],
                "parameters": {
                    "indicator_type": "EMA",
                    "period": 20,
                    "source": "close"
                }
            },
            {
                "id": "rsi_1",
                "type": "indicator",
                "position": [300, 250],
                "parameters": {
                    "indicator_type": "RSI",
                    "period": 14,
                    "source": "close"
                }
            },
            {
                "id": "crossover_1",
                "type": "math",
                "position": [500, 100],
                "parameters": {
                    "operation": "crossover",
                    "constant": 0.0
                }
            },
            {
                "id": "rsi_filter_1",
                "type": "logic",
                "position": [500, 200],
                "parameters": {
                    "operation": "greater_than",
                    "threshold": 30
                }
            },
            {
                "id": "entry_signal_1",
                "type": "logic",
                "position": [700, 150],
                "parameters": {
                    "operation": "AND"
                }
            },
            {
                "id": "enter_1",
                "type": "enter",
                "position": [900, 100],
                "parameters": {
                    "side": "long",
                    "position_size": 1.0
                }
            },
            {
                "id": "crossunder_1",
                "type": "math",
                "position": [500, 300],
                "parameters": {
                    "operation": "crossunder",
                    "constant": 0.0
                }
            },
            {
                "id": "exit_1",
                "type": "exit",
                "position": [900, 300],
                "parameters": {
                    "side": "long",
                    "stop_loss": -0.05,
                    "take_profit": 0.10
                }
            },
            {
                "id": "plot_ema_fast",
                "type": "plot",
                "position": [500, 50],
                "parameters": {
                    "label": "EMA Fast",
                    "color": "blue",
                    "plot_type": "line",
                    "subplot": False
                }
            },
            {
                "id": "plot_ema_slow",
                "type": "plot",
                "position": [500, 350],
                "parameters": {
                    "label": "EMA Slow",
                    "color": "red",
                    "plot_type": "line",
                    "subplot": False
                }
            },
            {
                "id": "plot_rsi",
                "type": "plot",
                "position": [700, 250],
                "parameters": {
                    "label": "RSI",
                    "color": "purple",
                    "plot_type": "line",
                    "subplot": True
                }
            }
        ],
        "connections": [
            # Market data to indicators
            {"from": "market_data_1.candles", "to": "ema_fast_1.candles"},
            {"from": "market_data_1.candles", "to": "ema_slow_1.candles"},
            {"from": "market_data_1.candles", "to": "rsi_1.candles"},
            
            # EMA crossover logic
            {"from": "ema_fast_1.values", "to": "crossover_1.A"},
            {"from": "ema_slow_1.values", "to": "crossover_1.B"},
            
            # RSI filter
            {"from": "rsi_1.values", "to": "rsi_filter_1.condition1"},
            
            # Entry signal (EMA crossover AND RSI > 30)
            {"from": "crossover_1.result", "to": "entry_signal_1.condition1"},
            {"from": "rsi_filter_1.result", "to": "entry_signal_1.condition2"},
            {"from": "entry_signal_1.result", "to": "enter_1.signal"},
            
            # Exit signal (EMA crossunder)
            {"from": "ema_fast_1.values", "to": "crossunder_1.A"},
            {"from": "ema_slow_1.values", "to": "crossunder_1.B"},
            {"from": "crossunder_1.result", "to": "exit_1.signal"},
            
            # Plotting
            {"from": "ema_fast_1.values", "to": "plot_ema_fast.data"},
            {"from": "ema_slow_1.values", "to": "plot_ema_slow.data"},
            {"from": "rsi_1.values", "to": "plot_rsi.data"}
        ]
    }
    
    return strategy_data


def save_demo_strategy():
    """Save demo strategy to file"""
    strategy_data = create_demo_strategy()
    
    # Save to user_data/strategies directory
    strategies_dir = Path("user_data/strategies")
    strategies_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = strategies_dir / "ema_rsi_demo.json"
    
    with open(file_path, 'w') as f:
        json.dump(strategy_data, f, indent=2)
    
    print(f"Demo strategy saved to: {file_path}")
    return file_path


if __name__ == "__main__":
    save_demo_strategy()
