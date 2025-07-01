"""
Freqtrade runner - handles execution of Freqtrade CLI commands
"""

import subprocess
import json
import csv
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QThread, Signal
import tempfile
import shutil
import os


class FreqtradeRunner:
    """Handles execution of Freqtrade CLI commands"""
    
    def __init__(self):
        self.user_data_dir = Path(__file__).parent / 'user_data'
        self.strategies_dir = self.user_data_dir / 'strategies'
        self.temp_dir = Path(tempfile.mkdtemp(prefix='frequi_'))
        
        # Ensure directories exist
        self.user_data_dir.mkdir(exist_ok=True)
        self.strategies_dir.mkdir(exist_ok=True)
        
        # Default config
        self.default_config = {
            "max_open_trades": 3,
            "stake_currency": "USDT",
            "stake_amount": 100,
            "tradable_balance_ratio": 0.99,
            "fiat_display_currency": "USD",
            "dry_run": True,
            "dry_run_wallet": 1000,
            "cancel_open_orders_on_exit": False,
            "trading_mode": "spot",
            "margin_mode": "",
            "unfilledtimeout": {
                "entry": 10,
                "exit": 10,
                "exit_timeout_count": 0,
                "unit": "minutes"
            },
            "entry_pricing": {
                "price_side": "same",
                "use_order_book": True,
                "order_book_top": 1,
                "price_last_balance": 0.0,
                "check_depth_of_market": {
                    "enabled": False,
                    "bids_to_ask_delta": 1
                }
            },
            "exit_pricing": {
                "price_side": "same",
                "use_order_book": True,
                "order_book_top": 1
            },
            "exchange": {
                "name": "binance",
                "key": "",
                "secret": "",
                "ccxt_config": {},
                "ccxt_async_config": {},
                "pair_whitelist": ["BTC/USDT", "ETH/USDT"],
                "pair_blacklist": []
            },
            "pairlists": [
                {
                    "method": "StaticPairList"
                }
            ],
            "edge": {
                "enabled": False,
                "process_throttle_secs": 3600,
                "calculate_since_number_of_days": 7,
                "allowed_risk": 0.01,
                "stoploss_range_min": -0.01,
                "stoploss_range_max": -0.1,
                "stoploss_range_step": -0.01,
                "minimum_winrate": 0.60,
                "minimum_expectancy": 0.20,
                "min_trade_number": 10,
                "max_trade_duration_minute": 1440,
                "remove_pumps": False
            },
            "telegram": {
                "enabled": False,
                "token": "dummy_token",
                "chat_id": "dummy_chat_id"
            },
            "api_server": {
                "enabled": False,
                "listen_ip_address": "127.0.0.1",
                "listen_port": 8080,
                "username": "dummy_user",
                "password": "dummy_password"
            },
            "bot_name": "freqtrade",
            "initial_state": "running",
            "force_entry_enable": False,
            "internals": {
                "process_throttle_secs": 5
            }
        }
    
    def save_strategy(self, strategy_code: str, strategy_name: str = "GeneratedStrategy") -> Path:
        """Save strategy code to file"""
        strategy_file = self.strategies_dir / f"{strategy_name}.py"
        
        with open(strategy_file, 'w') as f:
            f.write(strategy_code)
        
        return strategy_file
    
    def create_config(self, config_overrides: Dict = None) -> Path:
        """Create Freqtrade config file"""
        config = self.default_config.copy()
        
        if config_overrides:
            config.update(config_overrides)
        
        config_file = self.temp_dir / "config.json"
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config_file
    
    def run_backtest(self, strategy_code: str, strategy_name: str = "GeneratedStrategy", 
                     config_overrides: Dict = None, timerange: str = None) -> Dict[str, Any]:
        """Run backtest and return results"""
        
        # Save strategy
        strategy_file = self.save_strategy(strategy_code, strategy_name)
        
        # Create config
        config_file = self.create_config(config_overrides)
        
        # Build command
        cmd = [
            "freqtrade", "backtesting",
            "--config", str(config_file),
            "--strategy", strategy_name,
            "--user-data-dir", str(self.user_data_dir),
            "--export", "trades",
            "--export-filename", f"{self.temp_dir}/backtest_results.json"
        ]
        
        if timerange:
            cmd.extend(["--timerange", timerange])
        
        # Run command
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=str(self.user_data_dir.parent),
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Backtest failed: {result.stderr}")
            
            # Parse results
            return self._parse_backtest_results(result.stdout, result.stderr)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Backtest timed out after 5 minutes")
        except Exception as e:
            raise RuntimeError(f"Failed to run backtest: {str(e)}")
    
    def run_hyperopt(self, strategy_code: str, strategy_name: str = "GeneratedStrategy",
                     config_overrides: Dict = None, epochs: int = 100) -> Dict[str, Any]:
        """Run hyperopt and return results"""
        
        # Save strategy
        strategy_file = self.save_strategy(strategy_code, strategy_name)
        
        # Create config
        config_file = self.create_config(config_overrides)
        
        # Build command
        cmd = [
            "freqtrade", "hyperopt",
            "--config", str(config_file),
            "--strategy", strategy_name,
            "--user-data-dir", str(self.user_data_dir),
            "--hyperopt-loss", "SharpeHyperOptLoss",
            "--epochs", str(epochs),
            "--spaces", "buy", "sell"
        ]
        
        # Run command
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.user_data_dir.parent),
                timeout=1800  # 30 minute timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Hyperopt failed: {result.stderr}")
            
            # Parse results
            return self._parse_hyperopt_results(result.stdout, result.stderr)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Hyperopt timed out after 30 minutes")
        except Exception as e:
            raise RuntimeError(f"Failed to run hyperopt: {str(e)}")
    
    def start_live_trading(self, strategy_code: str, strategy_name: str = "GeneratedStrategy",
                          config_overrides: Dict = None) -> subprocess.Popen:
        """Start live trading (returns process handle)"""
        
        # Save strategy
        strategy_file = self.save_strategy(strategy_code, strategy_name)
        
        # Create config for live trading
        live_config = config_overrides.copy() if config_overrides else {}
        live_config["dry_run"] = False  # Disable dry run for live trading
        config_file = self.create_config(live_config)
        
        # Build command
        cmd = [
            "freqtrade", "trade",
            "--config", str(config_file),
            "--strategy", strategy_name,
            "--user-data-dir", str(self.user_data_dir)
        ]
        
        # Start process (non-blocking)
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.user_data_dir.parent)
            )
            
            return process
            
        except Exception as e:
            raise RuntimeError(f"Failed to start live trading: {str(e)}")
    
    def _parse_backtest_results(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse backtest results from output"""
        
        results = {
            'success': True,
            'stdout': stdout,
            'stderr': stderr,
            'equity': None,
            'trades': None,
            'stats': {}
        }
        
        try:
            # Look for results file
            results_file = self.temp_dir / "backtest_results.json"
            
            if results_file.exists():
                with open(results_file, 'r') as f:
                    backtest_data = json.load(f)
                
                # Extract statistics
                if 'strategy' in backtest_data:
                    strategy_results = list(backtest_data['strategy'].values())[0]
                    
                    results['stats'] = {
                        'total_return': f"{strategy_results.get('profit_total_pct', 0):.2f}%",
                        'sharpe': f"{strategy_results.get('sharpe', 0):.2f}",
                        'max_drawdown': f"{strategy_results.get('max_drawdown_pct', 0):.2f}%",
                        'total_trades': strategy_results.get('trades', 0),
                        'profitable_trades': strategy_results.get('wins', 0),
                        'avg_profit': f"{strategy_results.get('profit_mean_pct', 0):.2f}%"
                    }
                
                # Extract trades
                if 'trades' in backtest_data:
                    trades_df = pd.DataFrame(backtest_data['trades'])
                    results['trades'] = trades_df
                
                # Generate equity curve (simplified)
                if not trades_df.empty:
                    equity_data = self._generate_equity_curve(trades_df)
                    results['equity'] = equity_data
            
            # Parse summary from stdout
            self._parse_summary_from_output(stdout, results)
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def _parse_hyperopt_results(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse hyperopt results from output"""
        
        results = {
            'success': True,
            'stdout': stdout,
            'stderr': stderr,
            'best_params': {},
            'best_result': {}
        }
        
        try:
            # Parse best parameters from output
            lines = stdout.split('\n')
            
            for i, line in enumerate(lines):
                if 'Best result:' in line:
                    # Extract best result info
                    if i + 1 < len(lines):
                        result_line = lines[i + 1]
                        # Parse result line for metrics
                        # This is a simplified parser
                        
                if 'Best parameters:' in line:
                    # Extract best parameters
                    param_lines = []
                    j = i + 1
                    while j < len(lines) and lines[j].strip():
                        param_lines.append(lines[j])
                        j += 1
                    
                    # Parse parameter lines
                    for param_line in param_lines:
                        if ':' in param_line:
                            key, value = param_line.split(':', 1)
                            results['best_params'][key.strip()] = value.strip()
        
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def _generate_equity_curve(self, trades_df: pd.DataFrame) -> pd.DataFrame:
        """Generate equity curve from trades"""
        
        if trades_df.empty:
            return pd.DataFrame()
        
        # Sort trades by close time
        trades_df = trades_df.sort_values('close_timestamp')
        
        # Calculate cumulative profit
        trades_df['cumulative_profit'] = trades_df['profit_ratio'].cumsum()
        
        # Create equity curve
        equity_data = pd.DataFrame({
            'date': pd.to_datetime(trades_df['close_timestamp']),
            'equity': 1000 * (1 + trades_df['cumulative_profit']),  # Assuming $1000 starting balance
            'drawdown': trades_df['cumulative_profit'] * 100  # Convert to percentage
        })
        
        return equity_data
    
    def _parse_summary_from_output(self, output: str, results: Dict):
        """Parse summary statistics from CLI output"""
        
        lines = output.split('\n')
        
        for line in lines:
            if 'Total trades' in line:
                try:
                    total_trades = int(line.split(':')[1].strip())
                    results['stats']['total_trades'] = total_trades
                except:
                    pass
            elif 'Total profit' in line:
                try:
                    profit = line.split(':')[1].strip()
                    results['stats']['total_return'] = profit
                except:
                    pass
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)


class BacktestThread(QThread):
    """Background thread for running backtests"""
    
    # Signals
    finished = Signal(dict)  # Results
    error = Signal(str)      # Error message
    progress = Signal(str)   # Progress update
    
    def __init__(self, runner: FreqtradeRunner, strategy_code: str, 
                 strategy_name: str = "GeneratedStrategy", config_overrides: Dict = None):
        super().__init__()
        self.runner = runner
        self.strategy_code = strategy_code
        self.strategy_name = strategy_name
        self.config_overrides = config_overrides or {}
    
    def run(self):
        """Run backtest in background thread"""
        try:
            self.progress.emit("Starting backtest...")
            
            results = self.runner.run_backtest(
                self.strategy_code,
                self.strategy_name,
                self.config_overrides
            )
            
            self.progress.emit("Backtest completed!")
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))


class HyperoptThread(QThread):
    """Background thread for running hyperopt"""
    
    # Signals
    finished = Signal(dict)  # Results
    error = Signal(str)      # Error message
    progress = Signal(str)   # Progress update
    
    def __init__(self, runner: FreqtradeRunner, strategy_code: str,
                 strategy_name: str = "GeneratedStrategy", config_overrides: Dict = None,
                 epochs: int = 100):
        super().__init__()
        self.runner = runner
        self.strategy_code = strategy_code
        self.strategy_name = strategy_name
        self.config_overrides = config_overrides or {}
        self.epochs = epochs
    
    def run(self):
        """Run hyperopt in background thread"""
        try:
            self.progress.emit(f"Starting hyperopt ({self.epochs} epochs)...")
            
            results = self.runner.run_hyperopt(
                self.strategy_code,
                self.strategy_name,
                self.config_overrides,
                self.epochs
            )
            
            self.progress.emit("Hyperopt completed!")
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))
