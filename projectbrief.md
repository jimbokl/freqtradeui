# Project Brief: RDP v0.2 – Drag-&-Drop Strategy Builder для Freqtrade

## Цель
Создать визуальный конструктор стратегий для Freqtrade в стиле ComfyUI/Node-RED, позволяющий собирать торговые стратегии без кода и запускать их через стандартный Freqtrade CLI.

## Заинтересованные стороны
- Крипто-трейдер: хочет проверять идеи без кода, но на open-source.
- Квант-программист: ускорить прототипирование, визуально → Python-файл.
- Инфраструктурщик: никаких доп. API-слоёв, только GUI + Freqtrade CLI.
- Продакт: MVP ≤ 2 недели, zero-coding как ключевая фича.

## Область проекта
- Визуальная канва drag-&-drop (NodeGraphQt)
- 8 базовых узлов: MarketData, Indicator, Math, Logic, Enter, Exit, HyperoptParam, Plot
- Сохранение/загрузка графов в JSON
- Экспорт в IStrategy-класс (Jinja2)
- Кнопки: Backtest, Hyperopt, Live
- Отображение equity-кривой, сделок, метрик
- Конфиг-визард Freqtrade (config.json)

## Ограничения
- Только визуальный слой, ядро Freqtrade не трогаем
- Общение только через CLI
- Код-генератор ≤ 300 строк
- MVP = desktop GUI

## Архитектура (слои)
- ui/ – окно, панели, канва
- nodes/ – классы-узлы
- exporter.py – граф → Python-код
- runner.py – запуск CLI + логика
- results_view.py – парсинг и отрисовка 