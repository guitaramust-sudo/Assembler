#!/usr/bin/env python3
"""
Простейший тест для проверки работы ассемблера и интерпретатора
"""

import subprocess
import os


def create_test_program():
    """Создает простую тестовую программу"""
    program = {
        "name": "Простейший тест",
        "instructions": [
            # Загрузка константы 100 в регистр 1
            {"opcode": 72, "field_b": 1, "field_c": 100},
            # Загрузка адреса 0x100 в регистр 2
            {"opcode": 72, "field_b": 2, "field_c": 0x100},
            # Запись значения из R1 в память по адресу в R2
            {"opcode": 8, "field_b": 1, "field_c": 2},
            # Чтение из памяти по адресу в R2 в регистр 3
            {"opcode": 113, "field_b": 3, "field_c": 2}
        ]
    }

    import json
    with open('test_simple.json', 'w') as f:
        json.dump(program, f, indent=2)

    return 'test_simple.json'


def main():
    print("=== Простейший тест ассемблера и интерпретатора ===")

    # Создаем тестовую программу
    json_file = create_test_program()
    print(f"1. Создана тестовая программа: {json_file}")

    # Ассемблируем
    print("\n2. Ассемблируем программу...")
    result = subprocess.run(
        ['python', 'assembler.py', json_file, 'test_simple.bin'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Ошибка ассемблирования:")
        print(result.stderr)
        return

    print("✓ Программа успешно ассемблирована")
    if result.stdout:
        print(result.stdout)

    # Проверяем бинарный файл
    if os.path.exists('test_simple.bin'):
        size = os.path.getsize('test_simple.bin')
        print(f"  Создан файл: test_simple.bin ({size} байт)")

        # Показываем содержимое бинарного файла
        with open('test_simple.bin', 'rb') as f:
            data = f.read()
            print("  Содержимое (hex):", ' '.join(f'{b:02X}' for b in data))

    # Запускаем интерпретатор
    print("\n3. Запускаем интерпретатор...")
    result = subprocess.run(
        ['python', 'interpreter.py', 'test_simple.bin', 'test_simple.csv',
         '--start', '0x90', '--end', '0x110'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Ошибка интерпретации:")
        print(result.stderr)
    else:
        print("✓ Интерпретатор успешно выполнил программу")
        print("\nВывод интерпретатора:")
        print(result.stdout)

        # Показываем CSV файл
        if os.path.exists('test_simple.csv'):
            print("\nПервые строки дампа памяти:")
            with open('test_simple.csv', 'r') as f:
                for i, line in enumerate(f):
                    if i < 10:  # Показываем первые 10 строк
                        print(f"  {line.strip()}")
                    else:
                        break

    # Очистка
    print("\n4. Очистка временных файлов...")
    for file in [json_file, 'test_simple.bin', 'test_simple.csv']:
        if os.path.exists(file):
            os.unlink(file)
            print(f"  Удален: {file}")

    print("\n=== Тест завершен ===")


if __name__ == '__main__':
    main()