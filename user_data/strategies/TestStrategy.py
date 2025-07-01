
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class TestStrategy(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '1h'
    minimal_roi = {"0": 0.1}
    stoploss = -0.1
    
    def __init__(self, config: dict = None):
        if config is None:
            config = {}
        super().__init__(config)
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe['close'], timeperiod=14)
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['enter_long'] = 0
        dataframe.loc[(dataframe['rsi'] < 30), 'enter_long'] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['exit_long'] = 0
        dataframe.loc[(dataframe['rsi'] > 70), 'exit_long'] = 1
        return dataframe
