#!/usr/bin/env python3
"""
Ассемблер для учебной виртуальной машины (УВМ)
Этап 1: Перевод программы в промежуточное представление
"""

import sys
import json
import argparse
from pathlib import Path
from parser import parse_program
from encoder import encode_instruction, Instruction


def main():
    parser = argparse.ArgumentParser(description='Ассемблер для УВМ')
    parser.add_argument('input_file', help='Путь к исходному файлу с текстом программы')
    parser.add_argument('output_file', help='Путь к двоичному файлу-результату')
    parser.add_argument('--test', action='store_true', help='Режим тестирования')

    args = parser.parse_args()

    # Чтение входного файла
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            program_json = json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: файл {args.input_file} не найден")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Ошибка разбора JSON: {e}")
        sys.exit(1)

    # Парсинг программы
    instructions = parse_program(program_json)

    if args.test:
        # Режим тестирования: вывод промежуточного представления
        print("Промежуточное представление программы:")
        print("=" * 60)

        for i, instr in enumerate(instructions):
            print(f"Команда {i}:")
            print(f"  Код операции (A): {instr.opcode}")
            print(f"  Поле B: {instr.field_b}")
            print(f"  Поле C: {instr.field_c}")
            if instr.field_d is not None:
                print(f"  Поле D: {instr.field_d}")
            print(f"  Размер: {instr.size} байт")

            # Кодирование для проверки
            encoded = encode_instruction(instr)
            hex_bytes = ', '.join(f'0x{b:02X}' for b in encoded)
            print(f"  Закодированные байты: [{hex_bytes}]")
            print("-" * 60)

    # Кодирование всей программы в бинарный формат
    binary_data = bytearray()
    for instr in instructions:
        binary_data.extend(encode_instruction(instr))

    # Запись в выходной файл
    try:
        with open(args.output_file, 'wb') as f:
            f.write(binary_data)
        if not args.test:
            print(f"Программа успешно ассемблирована в файл: {args.output_file}")
            print(f"Размер программы: {len(binary_data)} байт")
    except IOError as e:
        print(f"Ошибка записи в файл {args.output_file}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()