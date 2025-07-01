
# Generated strategy from RDP visual builder
# PRAGMA pylint: disable=missing-docstring, invalid-name, pointless-string-statement


import pandas as pd

import numpy as np

from freqtrade.strategy import IStrategy, merge_informative_pair

from pandas import DataFrame

import talib.abstract as ta

import freqtrade.vendor.qtpylib.indicators as qtpylib


class GeneratedStrategy(IStrategy):
    """
    Generated strategy class
    """
    
    # Strategy interface version
    INTERFACE_VERSION = 3
    
    # Minimal ROI designed for the strategy
    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04
    }
    
    # Optimal stoploss
    stoploss = -0.10
    
    # Optimal timeframe for the strategy
    timeframe = '5m'
    
    # Can this strategy go short?
    can_short: bool = False
    
    # These values can be overridden in the config
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    
    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30
    


    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame
        """

        dataframe['indicator_0x1284fd660'] = ta.EMA(dataframe['close'], timeperiod=12)

        dataframe['indicator_0x1284fd780'] = ta.EMA(dataframe['close'], timeperiod=26)

        dataframe['math_0x1284fd9f0'] = dataframe['indicator_0x1284fd660'] - dataframe['indicator_0x1284fd780']

        
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        """
        # Initialize entry columns
        dataframe['enter_long'] = 0
        dataframe['enter_short'] = 0
        

        dataframe.loc[(dataframe['math_0x1284fd9f0'] > 0), 'enter_long'] = 1

        
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        """
        # Initialize exit columns
        dataframe['exit_long'] = 0
        dataframe['exit_short'] = 0
        

        dataframe.loc[(dataframe['math_0x1284fd9f0'] < 0), 'exit_long'] = 1

        
        return dataframe

