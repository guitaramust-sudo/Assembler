#!/usr/bin/env python3
"""
Ассемблер для учебной виртуальной машины (УВМ)
Этап 2: Формирование машинного кода
"""

import sys
import json
import argparse
from pathlib import Path
from parser import parse_program
from encoder import encode_instruction, encode_program


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

    # Кодирование всей программы в бинарный формат
    binary_data = encode_program(instructions)

    if args.test:
        # Режим тестирования: вывод байтового представления
        print("Результат ассемблирования:")
        print("=" * 60)

        # Вывод в формате из спецификации УВМ
        byte_strings = []
        for i, byte in enumerate(binary_data):
            byte_strings.append(f'0x{byte:02X}')

            # Перенос строки каждые 6 байт для читаемости
            if (i + 1) % 6 == 0 and i != len(binary_data) - 1:
                byte_strings.append('\n')

        # Вывод байтов
        print(f"Байтовая последовательность ({len(binary_data)} байт):")
        print('[' + ', '.join(byte_strings).replace('\n, ', '\n') + ']')
        print()

        # Детальная информация о командах
        print("Детализация команд:")
        print("-" * 60)

        byte_offset = 0
        for i, instr in enumerate(instructions):
            encoded = encode_instruction(instr)
            hex_bytes = ', '.join(f'0x{b:02X}' for b in encoded)

            print(f"Команда {i} (смещение 0x{byte_offset:04X}):")
            print(f"  Тип: ", end="")
            if instr.opcode == 72:
                print("Загрузка константы")
            elif instr.opcode == 113:
                print("Чтение из памяти")
            elif instr.opcode == 8:
                print("Запись в память")
            elif instr.opcode == 91:
                print("Унарный минус")
            else:
                print(f"Неизвестный (код {instr.opcode})")

            print(f"  Размер: {instr.size} байт")
            print(f"  Байты: [{hex_bytes}]")
            print()

            byte_offset += instr.size

    # Запись в выходной файл
    try:
        with open(args.output_file, 'wb') as f:
            f.write(binary_data)

        print(f"Размер двоичного файла: {len(binary_data)} байт")
        if not args.test:
            print(f"Программа успешно ассемблирована в файл: {args.output_file}")
    except IOError as e:
        print(f"Ошибка записи в файл {args.output_file}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()