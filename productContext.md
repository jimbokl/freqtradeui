# Product Context: RDP v0.2

## Пользовательские сценарии
- Сборка стратегии из узлов на канве
- Сохранение/загрузка стратегии (JSON)
- Экспорт стратегии в Python (IStrategy)
- Запуск Backtest/Hyperopt/Live через Freqtrade CLI
- Просмотр результатов: equity, сделки, метрики

## UX-карта
- File → New / Open / Save
- Левая панель: палитра узлов
- Центральная канва: zoom/pan, группировки
- Правая панель: свойства узла
- Toolbar: [Backtest] [Hyperopt] [Live] + индикатор статуса
- Нижняя область вкладок: Equity | Trades | Logs

## Спецификация узлов (MVP)
| Node          | Inputs     | Параметры                  | Outputs      |
|---------------|------------|----------------------------|--------------|
| MarketData    | —          | pair, timeframe, lookback  | candles df   |
| Indicator     | candles    | тип (EMA/RSI/BB), window   | series       |
| Math          | A, B       | expr (A-B, A/B, ...)       | series       |
| Logic         | cond1…N    | AND/OR/NOT                 | bool mask    |
| Enter         | signal     | side (long/short)          | flag-series  |
| Exit          | signal     | side                       | flag-series  |
| HyperoptParam | —          | name, range/type           | value        |
| Plot          | series     | цвет, подпись              | —            |

</rewritten_file> 