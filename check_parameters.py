#!/usr/bin/env python3
"""
Проверка параметров узлов без GUI
"""

import sys
from pathlib import Path

def check_node_parameters():
    """Проверка параметров в исходном коде узлов"""
    print("🔍 Проверка параметров узлов в исходном коде...")
    print("=" * 60)
    
    nodes_file = Path("nodes/base_nodes.py")
    if not nodes_file.exists():
        print("❌ Файл nodes/base_nodes.py не найден")
        return False
    
    with open(nodes_file, 'r') as f:
        content = f.read()
    
    # Определяем классы узлов и их параметры
    node_classes = [
        'MarketDataNode',
        'IndicatorNode', 
        'MathNode',
        'LogicNode',
        'EnterNode',
        'ExitNode',
        'HyperoptParamNode',
        'PlotNode'
    ]
    
    all_passed = True
    
    for node_class in node_classes:
        # Находим класс в коде
        class_start = content.find(f"class {node_class}")
        if class_start == -1:
            print(f"❌ Класс {node_class} не найден")
            all_passed = False
            continue
        
        # Находим конец класса (начало следующего класса или конец файла)
        next_class_start = content.find("class ", class_start + 1)
        if next_class_start == -1:
            class_content = content[class_start:]
        else:
            class_content = content[class_start:next_class_start]
        
        # Считаем количество set_parameter вызовов
        param_count = class_content.count("self.set_parameter(")
        
        print(f"📊 {node_class:20} : {param_count:2d} параметров", end="")
        
        if param_count >= 15:
            print(" ✅")
        else:
            print(" ❌ (нужно минимум 15)")
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✅ Все узлы имеют достаточное количество параметров!")
    else:
        print("❌ Некоторые узлы требуют дополнительных параметров")
    
    return all_passed


def check_config_fixes():
    """Проверка исправлений в конфигурации"""
    print("\n🔧 Проверка исправлений конфигурации...")
    print("=" * 60)
    
    runner_file = Path("runner.py")
    if not runner_file.exists():
        print("❌ Файл runner.py не найден")
        return False
    
    with open(runner_file, 'r') as f:
        content = f.read()
    
    # Проверяем исправления
    fixes = [
        ("telegram token", '"token": "dummy_token"'),
        ("telegram chat_id", '"chat_id": "dummy_chat_id"'),
        ("api_server listen_ip", '"listen_ip_address": "127.0.0.1"'),
        ("api_server port", '"listen_port": 8080'),
        ("api_server username", '"username": "dummy_user"'),
        ("api_server password", '"password": "dummy_password"')
    ]
    
    all_fixed = True
    for fix_name, fix_text in fixes:
        if fix_text in content:
            print(f"✅ {fix_name:20} - исправлено")
        else:
            print(f"❌ {fix_name:20} - НЕ исправлено")
            all_fixed = False
    
    print("=" * 60)
    if all_fixed:
        print("✅ Все исправления конфигурации применены!")
    else:
        print("❌ Некоторые исправления отсутствуют")
    
    return all_fixed


def check_strategy_files():
    """Проверка файлов стратегий"""
    print("\n📄 Проверка файлов стратегий...")
    print("=" * 60)
    
    strategy_files = [
        "user_data/strategies/GeneratedStrategy.py",
        "user_data/strategies/WorkingStrategy.py"
    ]
    
    valid_strategies = 0
    for strategy_file in strategy_files:
        strategy_path = Path(strategy_file)
        if strategy_path.exists():
            try:
                with open(strategy_path, 'r') as f:
                    content = f.read()
                
                # Проверяем обязательные компоненты
                required = [
                    "class",
                    "IStrategy",
                    "populate_indicators",
                    "populate_entry_trend", 
                    "populate_exit_trend"
                ]
                
                missing = []
                for req in required:
                    if req not in content:
                        missing.append(req)
                
                if not missing:
                    print(f"✅ {strategy_file:40} - валидная структура")
                    valid_strategies += 1
                else:
                    print(f"❌ {strategy_file:40} - отсутствует: {', '.join(missing)}")
                    
            except Exception as e:
                print(f"❌ {strategy_file:40} - ошибка чтения: {e}")
        else:
            print(f"⚠️  {strategy_file:40} - файл не найден")
    
    print("=" * 60)
    print(f"📊 Валидных стратегий: {valid_strategies}/{len(strategy_files)}")
    
    return valid_strategies > 0


def main():
    """Основная функция"""
    print("🚀 Комплексная проверка RDP системы")
    print("🎯 Цель: убедиться, что все исправления применены")
    print("\n")
    
    # Проверки
    params_ok = check_node_parameters()
    config_ok = check_config_fixes()
    strategies_ok = check_strategy_files()
    
    print("\n" + "=" * 60)
    print("📋 ИТОГОВЫЙ ОТЧЕТ:")
    print(f"   Параметры узлов:     {'✅ OK' if params_ok else '❌ FAIL'}")
    print(f"   Конфигурация:        {'✅ OK' if config_ok else '❌ FAIL'}")
    print(f"   Файлы стратегий:     {'✅ OK' if strategies_ok else '❌ FAIL'}")
    
    if params_ok and config_ok and strategies_ok:
        print("\n🎉 ВСЕ ИСПРАВЛЕНИЯ УСПЕШНО ПРИМЕНЕНЫ!")
        print("✅ Система готова к использованию")
        print("✅ Узлы имеют расширенные параметры (15+ каждый)")
        print("✅ Конфигурация бэктеста исправлена")
        print("✅ Стратегии имеют валидную структуру")
        return True
    else:
        print("\n⚠️  ТРЕБУЮТСЯ ДОПОЛНИТЕЛЬНЫЕ ИСПРАВЛЕНИЯ")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 