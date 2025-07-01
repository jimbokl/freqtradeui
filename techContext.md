# Tech Context: RDP v0.2

## Технологии
- GUI / Canvas: PySide6, NodeGraphQt
- Code templates: Jinja2
- Backtest engine: Freqtrade 2024.xx (ccxt встроен)
- Графики: Matplotlib, Pandas
- Packaging: Docker (опционально для MVP)

## Требования к окружению
- Python 3.11
- Кроссплатформенность (Windows, macOS, Linux)
- Работа без интернета (всё локально)

## Нефункциональные ограничения
- Время генерации стратегии ≤ 0.5 с
- UI не блокируется во время backtest (subprocess + QThread)
- Код-генератор ≤ 300 строк
- Только desktop GUI (web-версия — позже) 