# Generated strategy from RDP visual builder
# This is a demo strategy for testing purposes

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import numpy as np


class DemoStrategy(IStrategy):
    """
    Demo strategy generated from visual strategy builder
    """
    
    # Strategy interface version
    INTERFACE_VERSION = 3
    
    # Basic strategy settings
    timeframe = '1h'
    
    # ROI table
    minimal_roi = {
        "0": 0.10,
        "40": 0.05,
        "100": 0.01,
        "180": 0
    }
    
    # Stoploss
    stoploss = -0.10
    
    # Trailing stop
    trailing_stop = False
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Generate indicators from visual nodes
        """
        
        # Simple EMA indicators
        dataframe['ema_12'] = ta.EMA(dataframe, timeperiod=12)
        dataframe['ema_26'] = ta.EMA(dataframe, timeperiod=26)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Generate entry signals from visual nodes
        """
        
        # Simple EMA crossover strategy
        dataframe.loc[
            (
                (dataframe['ema_12'] > dataframe['ema_26']) &
                (dataframe['rsi'] < 70) &
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Generate exit signals from visual nodes
        """
        
        # Exit when EMA crosses back
        dataframe.loc[
            (
                (dataframe['ema_12'] < dataframe['ema_26']) |
                (dataframe['rsi'] > 80)
            ),
            'exit_long'] = 1
        
        return dataframe 