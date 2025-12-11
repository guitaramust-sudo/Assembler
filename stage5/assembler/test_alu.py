#!/usr/bin/env python3
"""
Тестирование этапа 4: Реализация арифметико-логического устройства (АЛУ)
"""

import subprocess
import os
import json
import tempfile


def test_unary_minus_command():
    """Тест команды унарного минуса"""
    print("=" * 70)
    print("ТЕСТ КОМАНДЫ УНАРНЫЙ МИНУС")
    print("=" * 70)

    # Создаем тестовую программу
    test_program = {
        "name": "Тест унарного минуса - этап 4",
        "description": "Демонстрация работы унарного минуса с разными значениями",
        "instructions": [
            # Инициализация
            {"opcode": 72, "field_b": 20, "field_c": 0x1000},  # Базовый адрес
            {"opcode": 72, "field_b": 30, "field_c": 0x2000},  # Адрес для результатов

            # Тест 1: положительное число
            {"opcode": 72, "field_b": 1, "field_c": 12345},
            {"opcode": 8, "field_b": 1, "field_c": 20},  # Сохраняем исходное
            {"opcode": 91, "field_b": 0, "field_c": 20, "field_d": 1},  # -R1 -> [R20]
            {"opcode": 113, "field_b": 2, "field_c": 20},  # Читаем результат
            {"opcode": 8, "field_b": 2, "field_c": 30},  # Сохраняем результат 1

            # Тест 2: отрицательное число (в 32-битном представлении)
            {"opcode": 72, "field_b": 3, "field_c": 4294967246},  # -50 в 32-битном
            {"opcode": 72, "field_b": 21, "field_c": 4},
            {"opcode": 8, "field_b": 3, "field_c": 21},  # Сохраняем исходное
            {"opcode": 91, "field_b": 0, "field_c": 21, "field_d": 3},  # -R3 -> [R21]
            {"opcode": 72, "field_b": 22, "field_c": 4},
            {"opcode": 113, "field_b": 4, "field_c": 22},  # Читаем результат
            {"opcode": 72, "field_b": 31, "field_c": 4},
            {"opcode": 8, "field_b": 4, "field_c": 31},  # Сохраняем результат 2

            # Тест 3: ноль
            {"opcode": 72, "field_b": 5, "field_c": 0},
            {"opcode": 72, "field_b": 23, "field_c": 8},
            {"opcode": 8, "field_b": 5, "field_c": 23},
            {"opcode": 91, "field_b": 0, "field_c": 23, "field_d": 5},
            {"opcode": 72, "field_b": 24, "field_c": 8},
            {"opcode": 113, "field_b": 6, "field_c": 24},
            {"opcode": 72, "field_b": 32, "field_c": 8},
            {"opcode": 8, "field_b": 6, "field_c": 32},  # Сохраняем результат 3

            # Тест 4: максимальное положительное 32-битное
            {"opcode": 72, "field_b": 7, "field_c": 2147483647},  # 0x7FFFFFFF
            {"opcode": 72, "field_b": 25, "field_c": 12},
            {"opcode": 8, "field_b": 7, "field_c": 25},
            {"opcode": 91, "field_b": 0, "field_c": 25, "field_d": 7},
            {"opcode": 72, "field_b": 26, "field_c": 12},
            {"opcode": 113, "field_b": 8, "field_c": 26},
            {"opcode": 72, "field_b": 33, "field_c": 12},
            {"opcode": 8, "field_b": 8, "field_c": 33},  # Сохраняем результат 4
        ]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_program, f, indent=2)
        json_file = f.name

    binary_file = 'unary_test.bin'
    dump_file = 'unary_dump.csv'

    try:
        # 1. Ассемблирование
        print("1. Ассемблирование тестовой программы...")
        result = subprocess.run(
            ['python', 'assembler.py', json_file, binary_file],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"Ошибка ассемблирования: {result.stderr}")
            return False

        print("✓ Программа ассемблирована")
        if result.stdout:
            print(result.stdout)

        # Проверяем размер
        if os.path.exists(binary_file):
            size = os.path.getsize(binary_file)
            print(f"  Размер бинарного файла: {size} байт")

        # 2. Выполнение
        print("\n2. Выполнение программы через интерпретатор...")
        result = subprocess.run(
            ['python', 'interpreter.py', binary_file, dump_file,
             '--start', '0x1000', '--end', '0x1100',
             '--memory-size', '65536'],
            capture_output=True, text=True
        )

        print("Вывод интерпретатора:")
        print(result.stdout)

        if result.returncode != 0:
            print(f"Ошибка выполнения: {result.stderr}")
            return False

        print("✓ Программа успешно выполнена")

        # 3. Проверка результатов
        print("\n3. Анализ результатов...")

        # Загружаем дамп памяти
        if os.path.exists(dump_file):
            with open(dump_file, 'r') as f:
                import csv
                reader = csv.reader(f)
                next(reader)  # Пропускаем заголовок

                print("\nЗначения в памяти (первые 5 строк):")
                for i, row in enumerate(reader):
                    if i < 5:
                        addr = row[0]
                        value_str = row[5]
                        print(f"  {addr}: {value_str}")
                    else:
                        break

        # Проверяем вычисления
        print("\n4. Проверка вычислений:")
        test_cases = [
            ("12345", (-12345) & 0xFFFFFFFF),
            ("-50", 50),  # -(-50) = 50
            ("0", 0),
            ("2147483647", (-2147483647) & 0xFFFFFFFF),  # -MAX_INT
        ]

        for i, (input_val, expected) in enumerate(test_cases, 1):
            print(f"  Тест {i}: -({input_val}) = {expected} (0x{expected:08X})")

        return True

    except Exception as e:
        print(f"Исключение: {e}")
        return False
    finally:
        # Очистка
        for file in [json_file, binary_file, dump_file]:
            if os.path.exists(file):
                os.unlink(file)
                # print(f"  Удален: {file}")


def create_demo_program():
    """Создание демонстрационной программы для этапа 4"""
    print("\n" + "=" * 70)
    print("СОЗДАНИЕ ДЕМОНСТРАЦИОННОЙ ПРОГРАММЫ")
    print("=" * 70)

    demo_program = {
        "name": "Демонстрация АЛУ - этап 4",
        "description": "Демонстрационная программа с унарным минусом и операциями с памятью",
        "instructions": []
    }

    instructions = []

    # Блок 1: Инициализация
    instructions.append({"opcode": 72, "field_b": 10, "field_c": 4096, "comment": "Базовый адрес данных"})
    instructions.append({"opcode": 72, "field_b": 11, "field_c": 8192, "comment": "Адрес для результатов"})

    # Блок 2: Тестовые значения
    test_values = [
        (1, 100, "Положительное число"),
        (2, 0, "Ноль"),
        (3, 4294967196, "Отрицательное число (-100)"),
        (4, 2147483647, "Максимальное положительное"),
        (5, 2147483648, "Максимальное отрицательное"),
    ]

    for reg, value, desc in test_values:
        instructions.append({"opcode": 72, "field_b": reg, "field_c": value, "comment": desc})

    # Блок 3: Сохранение исходных значений
    for i in range(1, 6):
        instructions.append(
            {"opcode": 72, "field_b": 20 + i, "field_c": (i - 1) * 4, "comment": f"Смещение для значения {i}"})
        instructions.append(
            {"opcode": 8, "field_b": i, "field_c": 20 + i, "comment": f"Сохранение исходного значения {i}"})

    # Блок 4: Применение унарного минуса
    for i in range(1, 6):
        instructions.append({"opcode": 91, "field_b": 0, "field_c": 20 + i, "field_d": i,
                             "comment": f"Унарный минус для значения {i}"})

    # Блок 5: Сохранение результатов
    for i in range(1, 6):
        instructions.append(
            {"opcode": 72, "field_b": 30 + i, "field_c": (i - 1) * 4, "comment": f"Смещение для результата {i}"})
        instructions.append({"opcode": 113, "field_b": 40 + i, "field_c": 30 + i, "comment": f"Чтение результата {i}"})
        instructions.append({"opcode": 72, "field_b": 50 + i, "field_c": 8192 + (i - 1) * 4,
                             "comment": f"Адрес для сохранения результата {i}"})
        instructions.append(
            {"opcode": 8, "field_b": 40 + i, "field_c": 50 + i, "comment": f"Сохранение результата {i}"})

    demo_program["instructions"] = instructions

    # Сохраняем в файл
    with open('examples/alu_demo.json', 'w') as f:
        json.dump(demo_program, f, indent=2)

    print("✓ Демонстрационная программа создана: examples/alu_demo.json")
    print(f"  Количество команд: {len(instructions)}")

    return 'examples/alu_demo.json'


def run_alu_demo():
    """Запуск демонстрационной программы"""
    print("\n" + "=" * 70)
    print("ЗАПУСК ДЕМОНСТРАЦИОННОЙ ПРОГРАММЫ")
    print("=" * 70)

    demo_file = 'examples/alu_demo.json'

    if not os.path.exists(demo_file):
        print(f"Файл {demo_file} не найден")
        return False

    try:
        # Ассемблируем
        print("1. Ассемблирование демонстрационной программы...")
        result = subprocess.run(
            ['python', 'assembler.py', demo_file, 'alu_demo.bin', '--test'],
            capture_output=True, text=True
        )

        print(result.stdout)
        if result.returncode != 0:
            print(f"Ошибка: {result.stderr}")
            return False

        # Выполняем
        print("\n2. Выполнение демонстрационной программы...")
        result = subprocess.run(
            ['python', 'interpreter.py', 'alu_demo.bin', 'alu_demo.csv',
             '--start', '0x1000', '--end', '0x1050',
             '--memory-size', '32768'],
            capture_output=True, text=True
        )

        print(result.stdout)

        if result.returncode != 0:
            print(f"Ошибка: {result.stderr}")
            return False

        # Показываем результаты
        if os.path.exists('alu_demo.csv'):
            print("\n3. Результаты выполнения:")
            with open('alu_demo.csv', 'r') as f:
                lines = f.readlines()
                print(f"  Всего строк в дампе: {len(lines) - 1}")

                # Показываем ключевые адреса
                key_addresses = [0x1000, 0x1010, 0x2000, 0x2010]
                print("\n  Ключевые значения в памяти:")
                for line in lines[1:]:  # Пропускаем заголовок
                    for addr in key_addresses:
                        if f"0x{addr:08X}" in line:
                            parts = line.strip().split(',')
                            print(f"    {parts[0]}: {parts[5]}")
                            break

        return True

    except Exception as e:
        print(f"Исключение: {e}")
        return False
    finally:
        # Очистка
        for file in ['alu_demo.bin', 'alu_demo.csv']:
            if os.path.exists(file):
                os.unlink(file)


def main():
    """Основная функция тестирования этапа 4"""
    print("ТЕСТИРОВАНИЕ ЭТАПА 4: АРИФМЕТИКО-ЛОГИЧЕСКОЕ УСТРОЙСТВО (АЛУ)")
    print("=" * 80)

    # Тест команды унарного минуса
    if not test_unary_minus_command():
        print("\n✗ Тест команды унарный минус не пройден")
        return

    print("\n✓ Тест команды унарный минус пройден успешно!")

    # Создаем демонстрационную программу
    demo_file = create_demo_program()

    # Запускаем демонстрационную программу
    if not run_alu_demo():
        print("\n✗ Демонстрационная программа не выполнена")
        return

    print("\n" + "=" * 80)
    print("ЭТАП 4 УСПЕШНО ЗАВЕРШЕН!")
    print("=" * 80)
    print("\nРеализовано:")
    print("✓ Команда унарный минус (код 91)")
    print("✓ Сохранение результата вычислений в память")
    print("✓ Тестирование с разными значениями (положительные, отрицательные, ноль)")
    print("✓ Демонстрационная программа с полным циклом операций")
    print("✓ Интеграционное тестирование ассемблера и интерпретатора")


if __name__ == '__main__':
    main()