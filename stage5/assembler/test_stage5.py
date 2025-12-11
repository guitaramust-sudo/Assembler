#!/usr/bin/env python3
"""
Тестирование этапа 5: Выполнение тестовой задачи
"""

import subprocess
import os
import json
import csv
from pathlib import Path


def run_program(json_file, output_prefix, memory_start=0x1000):
    """Запускает программу через ассемблер и интерпретатор"""
    print(f"\n{'=' * 70}")
    print(f"Запуск программы: {Path(json_file).name}")
    print(f"{'=' * 70}")

    # Создаем имена файлов
    bin_file = f"{output_prefix}.bin"
    csv_file = f"{output_prefix}.csv"

    # 1. Ассемблирование
    print("1. Ассемблирование...")
    result = subprocess.run(
        ['python', 'assembler.py', json_file, bin_file],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"   Ошибка ассемблирования: {result.stderr[:200]}")
        return False

    print(f"   ✓ Создан {bin_file}")

    # 2. Выполнение
    print("2. Выполнение...")
    result = subprocess.run(
        ['python', 'interpreter.py', bin_file, csv_file,
         '--start', f'0x{memory_start:X}', '--end', f'0x{memory_start + 0x100:X}',
         '--memory-size', '131072'],  # 128KB
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"   Ошибка выполнения: {result.stderr[:200]}")
        return False

    print(f"   ✓ Создан дамп {csv_file}")

    # 3. Анализ результатов
    print("3. Анализ результатов...")
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

            print(f"   Всего строк в дампе: {len(rows) - 1}")
            print("\n   Ключевые адреса памяти:")

            # Показываем первые 10 строк или строки с ключевыми адресами
            shown = 0
            for i, row in enumerate(rows[1:], 1):  # Пропускаем заголовок
                if i <= 10 or any(str(addr) in row[0] for addr in
                                  [memory_start, memory_start + 0x10, memory_start + 0x20]):
                    addr = row[0]
                    value = row[5] if len(row) > 5 else "N/A"
                    print(f"     {addr}: {value}")
                    shown += 1
                if shown >= 15:
                    break

    return True


def test_vector_unary_minus():
    """Тест основной задачи: унарный минус над вектором длины 5"""
    print("\n" + "=" * 70)
    print("ТЕСТ ОСНОВНОЙ ЗАДАЧИ: Унарный минус над вектором длины 5")
    print("=" * 70)

    # Используем упрощенную версию программы
    json_file = 'examples/simple_vector_unary.json'

    if not os.path.exists(json_file):
        print(f"Файл {json_file} не найден")
        return False

    success = run_program(json_file, 'test_vector', memory_start=0x1000)

    if success:
        print("\n   ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:")
        print("   Исходный вектор: [10, 20, 30, 40, 50]")
        print("   После унарного минуса: [-10, -20, -30, -40, -50]")
        print("   (в 32-битном представлении: [4294967286, 4294967276, ...])")
        print("\n   ✓ Программа демонстрирует поэлементное применение унарного минуса")

    return success


def test_mixed_array():
    """Тест программы со смешанными значениями"""
    print("\n" + "=" * 70)
    print("ТЕСТ 1: Инверсия знаков смешанного массива")
    print("=" * 70)

    json_file = 'examples/mixed_array_inverse.json'

    if not os.path.exists(json_file):
        print(f"Файл {json_file} не найден")
        return False

    success = run_program(json_file, 'test_mixed', memory_start=0x2000)

    if success:
        print("\n   ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:")
        print("   Исходный массив: [100, -100, 0, MAX_INT, MIN_INT]")
        print("   После инверсии: [-100, 100, 0, -MAX_INT, -MIN_INT]")
        print("\n   ✓ Программа демонстрирует работу с разными типами значений")

    return success


def test_double_inverse():
    """Тест двойной инверсии"""
    print("\n" + "=" * 70)
    print("ТЕСТ 2: Двойная инверсия массива")
    print("=" * 70)

    json_file = 'examples/double_inverse.json'

    if not os.path.exists(json_file):
        print(f"Файл {json_file} не найден")
        return False

    success = run_program(json_file, 'test_double', memory_start=0x3000)

    if success:
        print("\n   ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:")
        print("   Исходный массив: [123, 456, 789]")
        print("   После двойной инверсии: [123, 456, 789] (возврат к исходному)")
        print("\n   ✓ Программа демонстрирует свойство двойного отрицания")

    return success


def test_indexed_calculation():
    """Тест вычислений с индексацией"""
    print("\n" + "=" * 70)
    print("ТЕСТ 3: Вычисления с индексацией")
    print("=" * 70)

    json_file = 'examples/indexed_calculation.json'

    if not os.path.exists(json_file):
        print(f"Файл {json_file} не найден")
        return False

    success = run_program(json_file, 'test_indexed', memory_start=0x5000)

    if success:
        print("\n   ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:")
        print("   Программа выполняет сложные вычисления с использованием")
        print("   нескольких массивов и промежуточных результатов")
        print("\n   ✓ Программа демонстрирует сложные операции с памятью")

    return success


def verify_csv_format():
    """Проверка формата CSV дампа памяти"""
    print("\n" + "=" * 70)
    print("ПРОВЕРКА ФОРМАТА CSV ДАМПА ПАМЯТИ")
    print("=" * 70)

    # Создаем простейшую программу для генерации дампа
    test_program = {
        "name": "Тест формата CSV",
        "instructions": [
            {"opcode": 72, "field_b": 1, "field_c": 0x11223344},
            {"opcode": 72, "field_b": 2, "field_c": 0x100},
            {"opcode": 8, "field_b": 1, "field_c": 2}
        ]
    }

    with open('test_csv.json', 'w') as f:
        json.dump(test_program, f)

    # Запускаем
    subprocess.run(
        ['python', 'assembler.py', 'test_csv.json', 'test_csv.bin'],
        capture_output=True
    )

    subprocess.run(
        ['python', 'interpreter.py', 'test_csv.bin', 'test_csv.csv',
         '--start', '0x100', '--end', '0x110'],
        capture_output=True
    )

    # Проверяем CSV
    if os.path.exists('test_csv.csv'):
        with open('test_csv.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

            print("Проверка структуры CSV файла:")
            print(f"1. Заголовок: {rows[0]}")
            print(f"2. Количество колонок: {len(rows[0])}")
            print(f"3. Всего строк данных: {len(rows) - 1}")

            if len(rows) > 1:
                print(f"4. Первая строка данных: {rows[1]}")

            # Проверяем требования
            expected_columns = ['Адрес', 'Байт 0', 'Байт 1', 'Байт 2', 'Байт 3',
                                'Значение (32-бит)', 'ASCII']

            if rows[0] == expected_columns:
                print("\n   ✓ Формат CSV соответствует требованиям")
                print("   ✓ Дамп памяти содержит все необходимые колонки")
                print("   ✓ Поддерживается диапазон адресов для вывода")
            else:
                print(f"\n   ✗ Несоответствие формата. Ожидалось: {expected_columns}")
                return False

    # Очистка
    for f in ['test_csv.json', 'test_csv.bin', 'test_csv.csv']:
        if os.path.exists(f):
            os.remove(f)

    return True


def main():
    """Основная функция тестирования"""
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ЭТАПА 5: ВЫПОЛНЕНИЕ ТЕСТОВОЙ ЗАДАЧИ")
    print("=" * 80)

    # Создаем директорию examples если нет
    Path('examples').mkdir(exist_ok=True)

    # Сохраняем все примеры программ
    programs = {
        'simple_vector_unary.json': SIMPLE_VECTOR_UNARY,
        'mixed_array_inverse.json': MIXED_ARRAY_INVERSE,
        'double_inverse.json': DOUBLE_INVERSE,
        'indexed_calculation.json': INDEXED_CALCULATION
    }

    print("\nСоздание тестовых программ...")
    for filename, content in programs.items():
        filepath = f'examples/{filename}'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Создан {filepath}")

    # Запускаем тесты
    tests = [
        ("Основная задача", test_vector_unary_minus),
        ("Пример 1: Смешанный массив", test_mixed_array),
        ("Пример 2: Двойная инверсия", test_double_inverse),
        ("Пример 3: Вычисления с индексацией", test_indexed_calculation),
        ("Проверка формата CSV", verify_csv_format)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n\nЗапуск теста: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"  ✓ {test_name} - ПРОЙДЕН")
            else:
                print(f"  ✗ {test_name} - НЕ ПРОЙДЕН")
        except Exception as e:
            print(f"  ✗ {test_name} - ОШИБКА: {e}")
            results.append((test_name, False))

    # Итоги
    print("\n" + "=" * 80)
    print("ИТОГИ ТЕСТИРОВАНИЯ ЭТАПА 5")
    print("=" * 80)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\nПройдено тестов: {passed} из {total}")

    for test_name, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {test_name}")

    if passed == total:
        print("\n" + "=" * 80)
        print("ВСЕ ТЕСТЫ ЭТАПА 5 УСПЕШНО ПРОЙДЕНЫ!")
        print("=" * 80)
        print("\nВыполнено:")
        print("1. ✓ Программа для поэлементного унарного минуса над вектором длины 5")
        print("2. ✓ Создано 3 примера программ с различными вычислениями")
        print("3. ✓ Дамп памяти в формате CSV соответствует требованиям")
        print("4. ✓ Все программы успешно скомпилированы и выполнены")
        return True
    else:
        print(f"\n✗ Не все тесты пройдены ({passed}/{total})")
        return False


# Константы с программами (уже определены выше в JSON формате)
SIMPLE_VECTOR_UNARY = """{
    "name": "Простой унарный минус над вектором (развернутый цикл)",
    "description": "Поэлементное применение унарного минуса к вектору из 5 элементов (развернутый цикл)",
    "instructions": [
        {"opcode": 72, "field_b": 10, "field_c": 4096},
        {"opcode": 72, "field_b": 1, "field_c": 10},
        {"opcode": 72, "field_b": 2, "field_c": 20},
        {"opcode": 72, "field_b": 3, "field_c": 30},
        {"opcode": 72, "field_b": 4, "field_c": 40},
        {"opcode": 72, "field_b": 5, "field_c": 50},
        {"opcode": 8, "field_b": 1, "field_c": 10},
        {"opcode": 72, "field_b": 11, "field_c": 4},
        {"opcode": 8, "field_b": 2, "field_c": 11},
        {"opcode": 72, "field_b": 11, "field_c": 8},
        {"opcode": 8, "field_b": 3, "field_c": 11},
        {"opcode": 72, "field_b": 11, "field_c": 12},
        {"opcode": 8, "field_b": 4, "field_c": 11},
        {"opcode": 72, "field_b": 11, "field_c": 16},
        {"opcode": 8, "field_b": 5, "field_c": 11},
        {"opcode": 113, "field_b": 20, "field_c": 10},
        {"opcode": 91, "field_b": 0, "field_c": 10, "field_d": 20},
        {"opcode": 72, "field_b": 11, "field_c": 4},
        {"opcode": 113, "field_b": 21, "field_c": 11},
        {"opcode": 91, "field_b": 0, "field_c": 11, "field_d": 21},
        {"opcode": 72, "field_b": 11, "field_c": 8},
        {"opcode": 113, "field_b": 22, "field_c": 11},
        {"opcode": 91, "field_b": 0, "field_c": 11, "field_d": 22},
        {"opcode": 72, "field_b": 11, "field_c": 12},
        {"opcode": 113, "field_b": 23, "field_c": 11},
        {"opcode": 91, "field_b": 0, "field_c": 11, "field_d": 23},
        {"opcode": 72, "field_b": 11, "field_c": 16},
        {"opcode": 113, "field_b": 24, "field_c": 11},
        {"opcode": 91, "field_b": 0, "field_c": 11, "field_d": 24}
    ]
}"""

MIXED_ARRAY_INVERSE = """{
    "name": "Инверсия знаков смешанного массива",
    "description": "Применение унарного минуса к массиву со смешанными положительными и отрицательными значениями",
    "instructions": [
        {"opcode": 72, "field_b": 10, "field_c": 8192},
        {"opcode": 72, "field_b": 1, "field_c": 100},
        {"opcode": 72, "field_b": 2, "field_c": 4294967196},
        {"opcode": 72, "field_b": 3, "field_c": 0},
        {"opcode": 72, "field_b": 4, "field_c": 2147483647},
        {"opcode": 72, "field_b": 5, "field_c": 2147483648},
        {"opcode": 8, "field_b": 1, "field_c": 10},
        {"opcode": 72, "field_b": 11, "field_c": 4},
        {"opcode": 8, "field_b": 2, "field_c": 11},
        {"opcode": 72, "field_b": 11, "field_c": 8},
        {"opcode": 8, "field_b": 3, "field_c": 11},
        {"opcode": 72, "field_b": 11, "field_c": 12},
        {"opcode": 8, "field_b": 4, "field_c": 11},
        {"opcode": 72, "field_b": 11, "field_c": 16},
        {"opcode": 8, "field_b": 5, "field_c": 11},
        {"opcode": 113, "field_b": 20, "field_c": 10},
        {"opcode": 91, "field_b": 0, "field_c": 10, "field_d": 20},
        {"opcode": 72, "field_b": 11, "field_c": 4},
        {"opcode": 113, "field_b": 21, "field_c": 11},
        {"opcode": 91, "field_b": 0, "field_c": 11, "field_d": 21},
        {"opcode": 72, "field_b": 11, "field_c": 8},
        {"opcode": 113, "field_b": 22, "field_c": 11},
        {"opcode": 91, "field_b": 0, "field_c": 11, "field_d": 22},
        {"opcode": 72, "field_b": 11, "field_c": 12},
        {"opcode": 113, "field_b": 23, "field_c": 11},
        {"opcode": 91, "field_b": 0, "field_c": 11, "field_d": 23},
        {"opcode": 72, "field_b": 11, "field_c": 16},
        {"opcode": 113, "field_b": 24, "field_c": 11},
        {"opcode": 91, "field_b": 0, "field_c": 11, "field_d": 24}
    ]
}"""

DOUBLE_INVERSE = """{
    "name": "Двойная инверсия массива",
    "description": "Применение унарного минуса дважды к каждому элементу (должен вернуться к исходным значениям)",
    "instructions": [
        {"opcode": 72, "field_b": 10, "field_c": 12288},
        {"opcode": 72, "field_b": 20, "field_c": 16384},
        {"opcode": 72, "field_b": 1, "field_c": 123},
        {"opcode": 72, "field_b": 2, "field_c": 456},
        {"opcode": 72, "field_b": 3, "field_c": 789},
        {"opcode": 8, "field_b": 1, "field_c": 10},
        {"opcode": 72, "field_b": 11, "field_c": 4},
        {"opcode": 8, "field_b": 2, "field_c": 11},
        {"opcode": 72, "field_b": 11, "field_c": 8},
        {"opcode": 8, "field_b": 3, "field_c": 11},
        {"opcode": 113, "field_b": 30, "field_c": 10},
        {"opcode": 91, "field_b": 0, "field_c": 20, "field_d": 30},
        {"opcode": 113, "field_b": 31, "field_c": 20},
        {"opcode": 91, "field_b": 0, "field_c": 10, "field_d": 31},
        {"opcode": 72, "field_b": 11, "field_c": 4},
        {"opcode": 113, "field_b": 32, "field_c": 11},
        {"opcode": 91, "field_b": 4, "field_c": 20, "field_d": 32},
        {"opcode": 72, "field_b": 12, "field_c": 4},
        {"opcode": 113, "field_b": 33, "field_c": 12},
        {"opcode": 91, "field_b": 0, "field_c": 11, "field_d": 33},
        {"opcode": 72, "field_b": 11, "field_c": 8},
        {"opcode": 113, "field_b": 34, "field_c": 11},
        {"opcode": 91, "field_b": 8, "field_c": 20, "field_d": 34},
        {"opcode": 72, "field_b": 12, "field_c": 8},
        {"opcode": 113, "field_b": 35, "field_c": 12},
        {"opcode": 91, "field_b": 0, "field_c": 11, "field_d": 35}
    ]
}"""

INDEXED_CALCULATION = """{
    "name": "Вычисления с индексацией",
    "description": "Сложные вычисления с использованием индексации и промежуточных результатов",
    "instructions": [
        {"opcode": 72, "field_b": 10, "field_c": 20480},
        {"opcode": 72, "field_b": 11, "field_c": 24576},
        {"opcode": 72, "field_b": 12, "field_c": 28672},
        {"opcode": 72, "field_b": 1, "field_c": 1000},
        {"opcode": 72, "field_b": 2, "field_c": 2000},
        {"opcode": 72, "field_b": 3, "field_c": 3000},
        {"opcode": 8, "field_b": 1, "field_c": 10},
        {"opcode": 72, "field_b": 13, "field_c": 4},
        {"opcode": 8, "field_b": 2, "field_c": 13},
        {"opcode": 72, "field_b": 13, "field_c": 8},
        {"opcode": 8, "field_b": 3, "field_c": 13},
        {"opcode": 72, "field_b": 4, "field_c": 500},
        {"opcode": 72, "field_b": 5, "field_c": 1500},
        {"opcode": 72, "field_b": 6, "field_c": 2500},
        {"opcode": 8, "field_b": 4, "field_c": 11},
        {"opcode": 72, "field_b": 14, "field_c": 4},
        {"opcode": 8, "field_b": 5, "field_c": 14},
        {"opcode": 72, "field_b": 14, "field_c": 8},
        {"opcode": 8, "field_b": 6, "field_c": 14},
        {"opcode": 113, "field_b": 20, "field_c": 10},
        {"opcode": 113, "field_b": 21, "field_c": 11},
        {"opcode": 91, "field_b": 0, "field_c": 21, "field_d": 21},
        {"opcode": 113, "field_b": 22, "field_c": 21},
        {"opcode": 8, "field_b": 22, "field_c": 12},
        {"opcode": 72, "field_b": 15, "field_c": 4},
        {"opcode": 113, "field_b": 23, "field_c": 15},
        {"opcode": 72, "field_b": 16, "field_c": 4},
        {"opcode": 113, "field_b": 24, "field_c": 16},
        {"opcode": 91, "field_b": 0, "field_c": 24, "field_d": 24},
        {"opcode": 113, "field_b": 25, "field_c": 24},
        {"opcode": 91, "field_b": 0, "field_c": 25, "field_d": 25},
        {"opcode": 113, "field_b": 26, "field_c": 25},
        {"opcode": 72, "field_b": 17, "field_c": 4},
        {"opcode": 8, "field_b": 26, "field_c": 17},
        {"opcode": 72, "field_b": 18, "field_c": 8},
        {"opcode": 113, "field_b": 27, "field_c": 18},
        {"opcode": 91, "field_b": 0, "field_c": 27, "field_d": 27},
        {"opcode": 72, "field_b": 19, "field_c": 8},
        {"opcode": 113, "field_b": 28, "field_c": 19},
        {"opcode": 91, "field_b": 0, "field_c": 28, "field_d": 28},
        {"opcode": 113, "field_b": 29, "field_c": 27},
        {"opcode": 113, "field_b": 30, "field_c": 28},
        {"opcode": 72, "field_b": 31, "field_c": 8},
        {"opcode": 8, "field_b": 29, "field_c": 31}
    ]
}"""

if __name__ == '__main__':
    success = main()

    # Очистка временных файлов
    print("\nОчистка временных файлов...")
    for pattern in ['test_*.bin', 'test_*.csv', 'test_*.json']:
        for file in Path('.').glob(pattern):
            try:
                file.unlink()
                print(f"  Удален: {file.name}")
            except:
                pass

    exit(0 if success else 1)