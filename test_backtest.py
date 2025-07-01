#!/usr/bin/env python3
"""
Тестовый скрипт для диагностики проблем с бэктестом
"""

import sys
import os
import json
import subprocess
import tempfile
from pathlib import Path
import pandas as pd

def test_freqtrade_installation():
    """Тест установки freqtrade"""
    print("🔍 Проверка установки Freqtrade...")
    try:
        result = subprocess.run(['freqtrade', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Freqtrade установлен:")
            print(result.stdout)
            return True
        else:
            print("❌ Freqtrade не работает:")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("❌ Freqtrade не найден")
        return False

def test_data_availability():
    """Тест наличия данных"""
    print("\n🔍 Проверка данных...")
    data_dir = Path("user_data/data/binance")
    
    if not data_dir.exists():
        print("❌ Папка с данными не существует")
        return False
    
    data_files = list(data_dir.glob("*.feather"))
    if not data_files:
        print("❌ Нет файлов данных (.feather)")
        return False
    
    print(f"✅ Найдено файлов данных: {len(data_files)}")
    for file in data_files:
        print(f"  - {file.name}")
        
        # Проверим содержимое
        try:
            df = pd.read_feather(file)
            print(f"    Строк: {len(df)}, Период: {df.index[0]} - {df.index[-1]}")
        except Exception as e:
            print(f"    ❌ Ошибка чтения: {e}")
    
    return True

def test_strategy_syntax():
    """Тест синтаксиса стратегии"""
    print("\n🔍 Проверка синтаксиса стратегии...")
    strategy_file = Path("user_data/strategies/GeneratedStrategy.py")
    
    if not strategy_file.exists():
        print("❌ Файл стратегии не найден")
        return False
    
    try:
        # Проверим синтаксис Python
        with open(strategy_file, 'r') as f:
            code = f.read()
        
        compile(code, strategy_file, 'exec')
        print("✅ Синтаксис стратегии корректен")
        
        # Проверим импорт
        sys.path.insert(0, str(strategy_file.parent))
        from GeneratedStrategy import GeneratedStrategy
        strategy = GeneratedStrategy()
        print("✅ Стратегия успешно импортирована")
        
        return True
    except SyntaxError as e:
        print(f"❌ Синтаксическая ошибка: {e}")
        return False
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_config_validity():
    """Тест валидности конфигурации"""
    print("\n🔍 Проверка конфигурации...")
    config_file = Path("user_data/config.json")
    
    if not config_file.exists():
        print("❌ Файл конфигурации не найден")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print("✅ JSON конфигурации валиден")
        
        # Проверим обязательные поля
        required_fields = ['stake_currency', 'exchange', 'timeframe']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            print(f"❌ Отсутствуют обязательные поля: {missing_fields}")
            return False
        
        print("✅ Все обязательные поля присутствуют")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def create_minimal_test_config():
    """Создание минимальной тестовой конфигурации"""
    print("\n🔧 Создание минимальной тестовой конфигурации...")
    
    config = {
        "max_open_trades": 1,
        "stake_currency": "USDT",
        "stake_amount": 100,
        "dry_run": True,
        "timeframe": "1h",
        "exchange": {
            "name": "binance",
            "pair_whitelist": ["BTC/USDT"],
            "ccxt_config": {},
            "ccxt_async_config": {}
        },
        "pairlists": [{"method": "StaticPairList"}],
        "entry_pricing": {
            "price_side": "same",
            "use_order_book": True,
            "order_book_top": 1
        },
        "exit_pricing": {
            "price_side": "same", 
            "use_order_book": True,
            "order_book_top": 1
        }
    }
    
    test_config_file = Path("test_config.json")
    with open(test_config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Создан файл: {test_config_file}")
    return test_config_file

def test_minimal_backtest():
    """Тест минимального бэктеста"""
    print("\n🔍 Тестирование минимального бэктеста...")
    
    # Создаем минимальную конфигурацию
    config_file = create_minimal_test_config()
    
    try:
        cmd = [
            'freqtrade', 'backtesting',
            '--config', str(config_file),
            '--strategy', 'GeneratedStrategy',
            '--user-data-dir', 'user_data',
            '--timerange', '20250410-20250420',  # Период, когда есть данные
            '--cache', 'none'
        ]
        
        print(f"Выполняю команду: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,  # 1 минута timeout
            cwd=str(Path.cwd())
        )
        
        if result.returncode == 0:
            print("✅ Бэктест успешно завершен!")
            print("Результат:")
            print(result.stdout[-1000:])  # Последние 1000 символов
            return True
        else:
            print("❌ Бэктест завершился с ошибкой:")
            print("STDOUT:", result.stdout[-1000:])
            print("STDERR:", result.stderr[-1000:])
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Бэктест превысил время ожидания")
        return False
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        return False
    finally:
        # Очистка
        if config_file.exists():
            config_file.unlink()

def test_data_download():
    """Тест загрузки данных"""
    print("\n🔍 Тестирование загрузки данных...")
    
    config_file = create_minimal_test_config()
    
    try:
        cmd = [
            'freqtrade', 'download-data',
            '--config', str(config_file),
            '--pairs', 'BTC/USDT',
            '--timeframe', '1h',
            '--days', '7',
            '--exchange', 'binance'
        ]
        
        print(f"Выполняю команду: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2 минуты timeout
            cwd=str(Path.cwd())
        )
        
        if result.returncode == 0:
            print("✅ Данные успешно загружены!")
            return True
        else:
            print("❌ Ошибка загрузки данных:")
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Загрузка данных превысила время ожидания")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        if config_file.exists():
            config_file.unlink()

def main():
    """Основная функция тестирования"""
    print("🚀 Диагностика системы бэктестирования\n")
    
    tests = [
        ("Установка Freqtrade", test_freqtrade_installation),
        ("Наличие данных", test_data_availability),
        ("Синтаксис стратегии", test_strategy_syntax),
        ("Валидность конфигурации", test_config_validity),
        ("Загрузка данных", test_data_download),
        ("Минимальный бэктест", test_minimal_backtest),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
            results[test_name] = False
    
    # Итоговый отчет
    print("\n" + "="*50)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("="*50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    print(f"\nРезультат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Система готова к работе.")
    else:
        print("⚠️  Есть проблемы, которые нужно исправить.")
    
    return passed == total

if __name__ == "__main__":
    main() 