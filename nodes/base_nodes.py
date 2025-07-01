"""
Base node classes for the visual strategy builder
"""

from NodeGraphQt import BaseNode
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class BaseStrategyNode(BaseNode):
    """Base class for all strategy nodes"""
    
    # Node identifier for the node graph
    __identifier__ = 'frequi.nodes'
    
    # Node type name
    NODE_NAME = 'BaseNode'
    
    def __init__(self):
        super().__init__()
        
        # Set default node properties
        self.set_color(100, 100, 100)
        
        # Dictionary to store node parameters - инициализируем пустым словарем
        self._parameters = {}
        
        # Setup node-specific properties - ОБЯЗАТЕЛЬНО вызываем
        self.setup_node()
        
        # Убеждаемся что параметры проинициализированы
        if not self._parameters:
            print(f"Warning: Node {self.__class__.__name__} has no parameters after setup!")
    
    def setup_node(self):
        """Override this method to setup node-specific properties"""
        pass
    
    def get_parameter(self, name, default=None):
        """Get parameter value"""
        return self._parameters.get(name, default)
    
    def set_parameter(self, name, value):
        """Set parameter value"""
        self._parameters[name] = value
    
    def get_parameters(self):
        """Get all parameters"""
        return self._parameters.copy()
    
    def set_parameters(self, parameters):
        """Set multiple parameters"""
        self._parameters.update(parameters)
    
    def to_dict(self):
        """Export node to dictionary"""
        data = super().to_dict()
        data['parameters'] = self._parameters
        return data
    
    def from_dict(self, data):
        """Import node from dictionary"""
        super().from_dict(data)
        self._parameters = data.get('parameters', {})
        
        # Если параметров нет после загрузки, инициализируем их
        if not self._parameters:
            self.setup_node()
    
    def ensure_parameters_initialized(self):
        """Принудительная инициализация параметров, если они не инициализированы"""
        if not self._parameters:
            print(f"Force initializing parameters for {self.__class__.__name__}")
            self.setup_node()
        return self._parameters


class MarketDataNode(BaseStrategyNode):
    """Node for providing market data"""
    
    __identifier__ = 'frequi.nodes.MarketDataNode'
    NODE_NAME = 'Market Data'
    
    def setup_node(self):
        # Set node appearance
        self.set_color(70, 130, 180)  # Steel blue
        self.set_name('Market Data')
        
        # No input ports for market data
        
        # Output port for candles data
        self.add_output('candles', color=(255, 255, 255))
        
        # Default parameters
        self.set_parameter('pair', 'BTC/USDT')
        self.set_parameter('timeframe', '1h')  # 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w
        self.set_parameter('lookback', 500)  # Number of candles to fetch
        
        # Data source settings
        self.set_parameter('exchange', 'binance')  # binance, kraken, bittrex, etc.
        self.set_parameter('data_source', 'live')  # live, backtest, file
        self.set_parameter('data_file', '')  # Path to data file if using file source
        
        # Data validation
        self.set_parameter('validate_data', True)  # Validate data quality
        self.set_parameter('fill_missing', True)  # Fill missing data points
        self.set_parameter('remove_outliers', False)  # Remove statistical outliers
        
        # Performance settings
        self.set_parameter('cache_data', True)  # Cache data for performance
        self.set_parameter('refresh_interval', 60)  # Refresh interval in seconds
        
        # Additional market data parameters
        self.set_parameter('data_quality_threshold', 0.95)  # Minimum data quality threshold
        self.set_parameter('max_gap_minutes', 30)  # Maximum gap in minutes between candles
        self.set_parameter('timezone', 'UTC')  # Timezone for data processing
        self.set_parameter('round_timestamps', True)  # Round timestamps to timeframe
        self.set_parameter('backtest_start_date', '')  # Custom backtest start date
        self.set_parameter('use_ohlcv_preprocessing', False)  # Apply OHLCV preprocessing
        self.set_parameter('volume_filter_enabled', False)  # Enable volume filtering


class IndicatorNode(BaseStrategyNode):
    """Node for technical indicators"""
    
    __identifier__ = 'frequi.nodes.IndicatorNode'
    NODE_NAME = 'Indicator'
    
    def setup_node(self):
        # Set node appearance
        self.set_color(255, 165, 0)  # Orange
        self.set_name('Indicator')
        
        # Input port for candles data
        self.add_input('candles', color=(255, 255, 255))
        
        # Output port for indicator values
        self.add_output('values', color=(255, 255, 0))
        
        # Default parameters
        self.set_parameter('indicator_type', 'EMA')  # EMA, SMA, RSI, MACD, BOLLINGER, STOCH, ADX
        self.set_parameter('period', 14)
        self.set_parameter('source', 'close')  # close, high, low, open, hl2, hlc3, ohlc4
        
        # RSI specific parameters
        self.set_parameter('rsi_overbought', 70)
        self.set_parameter('rsi_oversold', 30)
        
        # MACD specific parameters  
        self.set_parameter('macd_fast', 12)
        self.set_parameter('macd_slow', 26)
        self.set_parameter('macd_signal', 9)
        
        # Bollinger Bands parameters
        self.set_parameter('bb_period', 20)
        self.set_parameter('bb_std', 2.0)
        
        # Stochastic parameters
        self.set_parameter('stoch_k', 14)
        self.set_parameter('stoch_d', 3)
        self.set_parameter('stoch_smooth_k', 3)
        
        # ADX parameters
        self.set_parameter('adx_period', 14)
        self.set_parameter('adx_threshold', 25)
        
        # Additional indicator parameters
        self.set_parameter('smooth_indicator', False)  # Apply smoothing to indicator
        self.set_parameter('smooth_method', 'SMA')  # Smoothing method: SMA, EMA, WMA
        self.set_parameter('smooth_period', 3)  # Smoothing period
        self.set_parameter('normalize_values', False)  # Normalize indicator values
        self.set_parameter('apply_filters', False)  # Apply noise filters
        self.set_parameter('filter_strength', 0.1)  # Filter strength (0.0-1.0)
        self.set_parameter('use_heiken_ashi', False)  # Use Heiken Ashi candles


class MathNode(BaseStrategyNode):
    """Node for mathematical operations"""
    
    __identifier__ = 'frequi.nodes.MathNode'
    NODE_NAME = 'Math'
    
    def setup_node(self):
        # Set node appearance
        self.set_color(128, 0, 128)  # Purple
        self.set_name('Math')
        
        # Input ports for operands
        self.add_input('A', color=(255, 255, 0))
        self.add_input('B', color=(255, 255, 0))
        
        # Output port for result
        self.add_output('result', color=(255, 255, 0))
        
        # Default parameters
        self.set_parameter('operation', 'add')  # add, subtract, multiply, divide, power, abs, min, max
        self.set_parameter('constant', 0.0)
        self.set_parameter('use_constant', False)  # Use constant instead of input B
        
        # Comparison operations
        self.set_parameter('comparison', 'greater')  # greater, less, equal, greater_equal, less_equal
        self.set_parameter('threshold', 0.0)
        
        # Signal processing
        self.set_parameter('shift_periods', 0)  # Shift signal by N periods
        self.set_parameter('rolling_window', 1)  # Rolling average window
        self.set_parameter('normalize', False)  # Normalize to 0-1 range
        
        # Additional math parameters
        self.set_parameter('precision_digits', 8)  # Number of decimal places
        self.set_parameter('handle_nan_values', 'forward_fill')  # forward_fill, backward_fill, zero, drop
        self.set_parameter('apply_rounding', False)  # Apply rounding to results
        self.set_parameter('min_value_threshold', None)  # Minimum value threshold
        self.set_parameter('max_value_threshold', None)  # Maximum value threshold
        self.set_parameter('outlier_detection', False)  # Enable outlier detection
        self.set_parameter('outlier_method', 'iqr')  # Outlier detection method: iqr, zscore


class LogicNode(BaseStrategyNode):
    """Node for logical operations"""
    
    __identifier__ = 'frequi.nodes.LogicNode'
    NODE_NAME = 'Logic'
    
    def setup_node(self):
        # Set node appearance
        self.set_color(220, 20, 60)  # Crimson
        self.set_name('Logic')
        
        # Input ports for conditions
        self.add_input('condition1', color=(0, 255, 0))
        self.add_input('condition2', color=(0, 255, 0))
        self.add_input('condition3', color=(0, 255, 0))  # Optional third condition
        
        # Output port for boolean result
        self.add_output('result', color=(0, 255, 0))
        
        # Default parameters
        self.set_parameter('operation', 'AND')  # AND, OR, NOT, XOR, NAND, NOR
        self.set_parameter('use_condition3', False)  # Enable third condition
        
        # Signal filters
        self.set_parameter('consecutive_bars', 1)  # Require N consecutive bars
        self.set_parameter('within_bars', 5)  # Signal must occur within N bars
        self.set_parameter('invert_result', False)  # Invert the final result
        
        # Additional logic parameters
        self.set_parameter('confidence_threshold', 0.5)  # Confidence threshold for signals
        self.set_parameter('signal_persistence', 1)  # How many bars signal should persist
        self.set_parameter('reset_on_opposite', True)  # Reset signal on opposite condition
        self.set_parameter('enable_debugging', False)  # Enable debug output
        self.set_parameter('custom_logic_formula', '')  # Custom logic formula string
        self.set_parameter('priority_weight', 1.0)  # Priority weight for this logic node
        self.set_parameter('timeout_bars', 10)  # Timeout for logic condition in bars
        self.set_parameter('memory_enabled', False)  # Enable logic state memory
        self.set_parameter('state_duration', 1)  # How long to remember state
        self.set_parameter('complex_evaluation', False)  # Enable complex evaluation mode


class EnterNode(BaseStrategyNode):
    """Node for entry signals"""
    
    __identifier__ = 'frequi.nodes.EnterNode'
    NODE_NAME = 'Enter Signal'
    
    def setup_node(self):
        # Set node appearance
        self.set_color(0, 255, 0)  # Green
        self.set_name('Enter')
        
        # Input port for entry signal
        self.add_input('signal', color=(0, 255, 0))
        
        # Output port for entry flags
        self.add_output('entry', color=(0, 255, 0))
        
        # Default parameters
        self.set_parameter('side', 'long')  # long, short, both
        self.set_parameter('position_size', 1.0)  # 0.1 = 10%, 1.0 = 100%
        
        # Entry conditions
        self.set_parameter('require_volume', False)  # Check volume spike
        self.set_parameter('min_volume_ratio', 1.5)  # Minimum volume vs average
        self.set_parameter('max_spread_pct', 0.5)  # Maximum spread percentage
        
        # Position management
        self.set_parameter('max_open_positions', 1)  # Maximum concurrent positions
        self.set_parameter('min_roi', 0.01)  # Minimum expected ROI
        self.set_parameter('cooldown_bars', 5)  # Bars to wait between entries
        
        # Risk management
        self.set_parameter('enable_stop_loss', True)
        self.set_parameter('stop_loss_pct', 2.0)  # Stop loss percentage
        self.set_parameter('enable_take_profit', True) 
        self.set_parameter('take_profit_pct', 5.0)  # Take profit percentage
        
        # Additional entry parameters
        self.set_parameter('entry_signal_strength', 1.0)  # Signal strength multiplier
        self.set_parameter('confirm_with_volume', False)  # Confirm entry with volume
        self.set_parameter('avoid_weekend_entries', False)  # Avoid entries on weekends
        self.set_parameter('market_condition_filter', 'any')  # any, trending, ranging, volatile
        self.set_parameter('time_window_start', '00:00')  # Start time for entries (HH:MM)
        self.set_parameter('time_window_end', '23:59')  # End time for entries (HH:MM)
        self.set_parameter('max_entries_per_day', 10)  # Maximum entries per day


class ExitNode(BaseStrategyNode):
    """Node for exit signals"""
    
    __identifier__ = 'frequi.nodes.ExitNode'
    NODE_NAME = 'Exit Signal'
    
    def setup_node(self):
        # Set node appearance
        self.set_color(255, 0, 0)  # Red
        self.set_name('Exit')
        
        # Input port for exit signal
        self.add_input('signal', color=(0, 255, 0))
        
        # Output port for exit flags
        self.add_output('exit', color=(255, 0, 0))
        
        # Default parameters
        self.set_parameter('side', 'long')  # long, short, both
        self.set_parameter('exit_type', 'signal')  # signal, stop_loss, take_profit, trailing_stop, time_based
        
        # Stop Loss settings
        self.set_parameter('stop_loss_pct', 2.0)  # Stop loss percentage
        self.set_parameter('stop_loss_type', 'fixed')  # fixed, trailing, atr_based
        
        # Take Profit settings  
        self.set_parameter('take_profit_pct', 5.0)  # Take profit percentage
        self.set_parameter('take_profit_type', 'fixed')  # fixed, scaled, dynamic
        
        # Trailing Stop settings
        self.set_parameter('trailing_stop', False)
        self.set_parameter('trailing_stop_positive', 0.01)  # Start trailing at +1%
        self.set_parameter('trailing_stop_positive_offset', 0.0)  # Additional offset
        
        # Time-based exit
        self.set_parameter('max_hold_hours', 24)  # Maximum hold time in hours
        self.set_parameter('force_exit_at_close', False)  # Exit before market close
        
        # Partial exit settings
        self.set_parameter('partial_exit', False)
        self.set_parameter('partial_exit_at_pct', 3.0)  # First partial exit at +3%
        self.set_parameter('partial_exit_ratio', 0.5)  # Exit 50% of position
        
        # Additional exit parameters
        self.set_parameter('exit_signal_strength', 1.0)  # Exit signal strength multiplier
        self.set_parameter('confirm_exit_with_volume', False)  # Confirm exit with volume
        self.set_parameter('emergency_exit_enabled', True)  # Enable emergency exit conditions
        self.set_parameter('max_hold_days', 30)  # Maximum hold time in days
        self.set_parameter('exit_on_weekend', False)  # Force exit before weekend
        self.set_parameter('break_even_enabled', False)  # Enable break-even exit
        self.set_parameter('break_even_threshold', 1.0)  # Break-even threshold percentage


class HyperoptParamNode(BaseStrategyNode):
    """Node for hyperoptimization parameters"""
    
    __identifier__ = 'frequi.nodes.HyperoptParamNode'
    NODE_NAME = 'Hyperopt Param'
    
    def setup_node(self):
        # Set node appearance
        self.set_color(255, 215, 0)  # Gold
        self.set_name('Hyperopt Param')
        
        # No input ports
        
        # Output port for parameter value
        self.add_output('value', color=(255, 215, 0))
        
        # Default parameters
        self.set_parameter('param_name', 'param')
        self.set_parameter('param_type', 'Integer')  # Integer, Real, Categorical
        self.set_parameter('min_value', 0)
        self.set_parameter('max_value', 100)
        self.set_parameter('step', 1)  # Step size for optimization
        self.set_parameter('default_value', 50)  # Default value if not optimizing
        self.set_parameter('choices', [])  # For categorical parameters
        
        # Optimization settings
        self.set_parameter('optimize', True)  # Enable optimization
        self.set_parameter('load_from_file', False)  # Load optimized value from file
        self.set_parameter('description', '')  # Parameter description
        
        # Additional hyperopt parameters
        self.set_parameter('optimization_metric', 'profit')  # profit, sharpe, winrate, drawdown
        self.set_parameter('enable_constraints', False)  # Enable parameter constraints
        self.set_parameter('constraint_formula', '')  # Constraint formula
        self.set_parameter('adaptive_ranges', False)  # Use adaptive parameter ranges
        self.set_parameter('correlation_analysis', False)  # Analyze parameter correlations
        self.set_parameter('parameter_importance', 1.0)  # Parameter importance weight


class PlotNode(BaseStrategyNode):
    """Node for plotting data"""
    
    __identifier__ = 'frequi.nodes.PlotNode'
    NODE_NAME = 'Plot'
    
    def setup_node(self):
        # Set node appearance
        self.set_color(0, 191, 255)  # Deep sky blue
        self.set_name('Plot')
        
        # Input port for data to plot
        self.add_input('data', color=(255, 255, 0))
        
        # No output ports (plotting is a sink)
        
        # Default parameters
        self.set_parameter('label', 'Plot')
        self.set_parameter('color', 'blue')  # blue, red, green, orange, purple, cyan, magenta, yellow
        self.set_parameter('plot_type', 'line')  # line, scatter, bar, fill_area
        self.set_parameter('subplot', False)  # Plot in separate subplot
        
        # Plot styling
        self.set_parameter('line_width', 1.0)  # Line width
        self.set_parameter('line_style', 'solid')  # solid, dashed, dotted, dashdot
        self.set_parameter('opacity', 1.0)  # Transparency (0.0 - 1.0)
        
        # Data processing
        self.set_parameter('normalize_data', False)  # Normalize to 0-1 range
        self.set_parameter('smooth_data', False)  # Apply smoothing
        self.set_parameter('smooth_periods', 3)  # Smoothing window size
        
        # Display options
        self.set_parameter('show_legend', True)  # Show in legend
        self.set_parameter('plot_on_volume', False)  # Plot on volume subplot
        
        # Additional plot parameters
        self.set_parameter('plot_markers', False)  # Show markers on data points
        self.set_parameter('marker_size', 5)  # Size of markers
        self.set_parameter('plot_fill_alpha', 0.3)  # Fill area transparency
        self.set_parameter('custom_title', '')  # Custom plot title
        self.set_parameter('y_axis_label', '')  # Custom Y-axis label
        self.set_parameter('plot_grid', True)  # Show grid lines
        self.set_parameter('plot_annotations', False)  # Enable plot annotations


# Dictionary mapping node types to classes
NODE_CLASSES = {
    'market_data': MarketDataNode,
    'indicator': IndicatorNode,
    'math': MathNode,
    'logic': LogicNode,
    'enter': EnterNode,
    'exit': ExitNode,
    'hyperopt_param': HyperoptParamNode,
    'plot': PlotNode,
}
