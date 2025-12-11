#!/usr/bin/env python3
"""
Простой тест для проверки работы ассемблера и интерпретатора УВМ
"""

import subprocess
import os
import json


def create_simple_program():
    """Создает простую тестовую программу"""
    program = {
        "name": "Простой тест УВМ",
        "instructions": [
            # Загружаем число 100 в регистр R1
            {"opcode": 72, "field_b": 1, "field_c": 100},
            # Загружаем адрес 0x200 в регистр R2
            {"opcode": 72, "field_b": 2, "field_c": 0x200},
            # Записываем значение из R1 в память по адресу в R2
            {"opcode": 8, "field_b": 1, "field_c": 2},
            # Читаем значение обратно в регистр R3
            {"opcode": 113, "field_b": 3, "field_c": 2},
            # Загружаем число -50 (в 32-битном представлении) в регистр R4
            {"opcode": 72, "field_b": 4, "field_c": 0xFFFFFFCE},
            # Вычисляем унарный минус (-R4) и сохраняем по адресу R2+4
            {"opcode": 91, "field_b": 4, "field_c": 2, "field_d": 4}
        ]
    }

    with open('test_simple.json', 'w') as f:
        json.dump(program, f, indent=2)

    return 'test_simple.json'


def main():
    print("=" * 60)
    print("ПРОСТОЙ ТЕСТ УВМ")
    print("=" * 60)

    # 1. Создаем тестовую программу
    print("\n1. Создаем тестовую программу...")
    json_file = create_simple_program()
    print(f"   Создан файл: {json_file}")

    # 2. Ассемблируем
    print("\n2. Ассемблируем программу...")
    result = subprocess.run(
        ['python', 'assembler.py', json_file, 'test_simple.bin'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"   Ошибка: {result.stderr}")
        return

    print("   ✓ Программа успешно ассемблирована")
    if result.stdout:
        print(f"   {result.stdout.strip()}")

    # 3. Проверяем бинарный файл
    if os.path.exists('test_simple.bin'):
        size = os.path.getsize('test_simple.bin')
        print(f"   Размер бинарного файла: {size} байт")

    # 4. Запускаем интерпретатор
    print("\n3. Запускаем интерпретатор...")
    result = subprocess.run(
        ['python', 'interpreter.py', 'test_simple.bin', 'test_simple.csv',
         '--start', '0x200', '--end', '0x210'],
        capture_output=True,
        text=True
    )

    print("   Вывод интерпретатора:")
    for line in result.stdout.split('\n'):
        if line and not line.startswith("Состояние регистров"):
            print(f"   {line}")

    if result.returncode != 0:
        print(f"   Ошибка: {result.stderr}")
        return

    # 5. Проверяем CSV файл
    print("\n4. Проверяем результаты в памяти...")
    if os.path.exists('test_simple.csv'):
        with open('test_simple.csv', 'r') as f:
            lines = f.readlines()
            print(f"   Всего строк в дампе: {len(lines) - 1}")
            print("\n   Содержимое памяти по адресу 0x200:")
            for line in lines[1:]:  # Пропускаем заголовок
                if '0x00000200' in line or '0x00000204' in line:
                    parts = line.strip().split(',')
                    addr = parts[0]
                    value = parts[5]
                    print(f"   {addr}: {value}")

    # 6. Очистка
    print("\n5. Очистка временных файлов...")
    files_to_clean = ['test_simple.json', 'test_simple.bin', 'test_simple.csv']
    for file in files_to_clean:
        if os.path.exists(file):
            os.remove(file)
            print(f"   Удален: {file}")

    print("\n" + "=" * 60)
    print("ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
    print("=" * 60)


if __name__ == '__main__':
    main()