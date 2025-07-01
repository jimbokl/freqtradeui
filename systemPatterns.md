# System Patterns: RDP v0.2

## Ключевые паттерны
- Drag-&-Drop канва (NodeGraphQt)
- Топологическая сортировка графа для экспорта
- Экспорт в Python через шаблоны Jinja2
- Вызов Freqtrade CLI через subprocess
- Асинхронный запуск задач (QThread)
- Парсинг результатов и отображение в UI

## Алгоритм экспорта
1. graph.to_dict() → топологически отсортированный список
2. Для каждого типа нода добавляем строку в секцию шаблона:
   - индикаторы/математика → populate_indicators()
   - сигналы → populate_entry_trend()/populate_exit_trend()
   - гиперпараметры → в атрибутах класса
3. Jinja2.render → GenStrategy.py
4. Файл сохраняется в user_data/strategies + временная подпапка

## Взаимодействие слоёв
- UI (NodeGraphQt, PySide6) ↔ Exporter (Jinja2) ↔ Freqtrade CLI (subprocess) ↔ Parser (результаты)

## Риски и меры
- Изменится API Freqtrade CLI — абстракция runner + e2e-тест
- Qt-плагины в Docker — offscreen-режим (QT_QPA_PLATFORM=offscreen)
- Крупные графы → кеш шаблонов, профилировать топо-обход
- Требование web-версии — запланировать React/Typescript фронт как M2 