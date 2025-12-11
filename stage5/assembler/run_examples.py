#!/usr/bin/env python3
"""
Скрипт для запуска всех примеров и тестов
Этап 4: Добавлена поддержка АЛУ и унарного минуса
"""

import os
import subprocess
import tempfile
import json
from pathlib import Path


def run_alu_tests():
    """Запуск тестов этапа 4"""
    print("\n" + "=" * 80)
    print("ТЕСТЫ ЭТАПА 4: АРИФМЕТИКО-ЛОГИЧЕСКОЕ УСТРОЙСТВО")
    print("=" * 80)

    # Запускаем тест АЛУ
    result = subprocess.run(
        ['python', 'test_alu.py'],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print("Ошибки:", result.stderr)

    return result.returncode == 0


def main():
    """Запуск всех примеров"""
    examples_dir = Path('examples')

    if not examples_dir.exists():
        print(f"Ошибка: директория {examples_dir} не найдена")
        return

    # Создаем выходную директорию для бинарных файлов
    bin_dir = Path('bin')
    bin_dir.mkdir(exist_ok=True)

    print("=" * 80)
    print("ПОЛНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ УВМ")
    print("=" * 80)

    # 1. Запускаем тесты этапа 4
    if not run_alu_tests():
        print("\n✗ Тесты этапа 4 не пройдены")
        return

    # 2. Запускаем все примеры из спецификации
    print("\n" + "=" * 80)
    print("ТЕСТЫ ИЗ СПЕЦИФИКАЦИИ УВМ")
    print("=" * 80)

    spec_tests = ['test_load.json', 'test_read.json', 'test_write.json', 'test_unary.json', 'all_tests.json']

    for test_file in spec_tests:
        json_path = examples_dir / test_file
        if json_path.exists():
            # Ассемблируем
            binary_path = bin_dir / f"{test_file.replace('.json', '.bin')}"

            print(f"\nАссемблирование {test_file}...")
            result = subprocess.run(
                ['python', 'assembler.py', str(json_path), str(binary_path)],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"✓ Создан {binary_path}")
            else:
                print(f"✗ Ошибка: {result.stderr}")

    # 3. Запускаем демонстрационные программы этапа 4
    print("\n" + "=" * 80)
    print("ДЕМОНСТРАЦИОННЫЕ ПРОГРАММЫ ЭТАПА 4")
    print("=" * 80)

    alu_tests = ['unary_minus_test.json', 'alu_test.json', 'alu_demo.json']

    for test_file in alu_tests:
        json_path = examples_dir / test_file
        if json_path.exists():
            binary_path = bin_dir / f"{test_file.replace('.json', '.bin')}"
            dump_path = bin_dir / f"{test_file.replace('.json', '.csv')}"

            print(f"\nАссемблирование {test_file}...")
            result = subprocess.run(
                ['python', 'assembler.py', str(json_path), str(binary_path)],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"✓ Создан {binary_path}")

                # Запускаем интерпретатор
                print(f"  Выполнение...")
                result = subprocess.run(
                    ['python', 'interpreter.py', str(binary_path), str(dump_path),
                     '--start', '0x1000', '--end', '0x1050'],
                    capture_output=True, text=True
                )

                if result.returncode == 0:
                    print(f"  ✓ Создан дамп {dump_path}")
                    # Показываем краткий вывод
                    lines = result.stdout.split('\n')
                    for line in lines[:5]:
                        if line:
                            print(f"    {line}")
                else:
                    print(f"  ✗ Ошибка выполнения: {result.stderr}")
            else:
                print(f"✗ Ошибка ассемблирования: {result.stderr}")

    print("\n" + "=" * 80)
    print("ВСЕ ТЕСТЫ ВЫПОЛНЕНЫ")
    print("=" * 80)
    print("\nСозданные файлы в директории bin/:")
    for file in sorted(bin_dir.glob('*')):
        print(f"  {file.name} ({file.stat().st_size} байт)")


if __name__ == '__main__':
    main()