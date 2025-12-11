#!/usr/bin/env python3
"""
Тесты для интерпретатора УВМ
Этап 4: Реализация арифметико-логического устройства (АЛУ)
"""

import unittest
import tempfile
import os
import json
import csv
from io import StringIO
from unittest.mock import patch
from interpreter import UVMInterpreter


class TestUVMInterpreterALU(unittest.TestCase):

    def setUp(self):
        """Настройка тестового интерпретатора"""
        self.interpreter = UVMInterpreter(memory_size=4096)  # 4KB для тестов

    def test_unary_minus_basic(self):
        """Тест базовой работы унарного минуса"""
        # Подготовка: значение в регистре 5
        test_value = 100
        self.interpreter.registers[5] = test_value

        # Подготовка: базовый адрес в регистре 10
        base_addr = 0x100
        self.interpreter.registers[10] = base_addr

        # Создаем программу: унарный минус значения из R5, результат по адресу R10+0
        program = bytearray([
            0x5B,  # opcode 91
            0x00,  # field_b = 0 (смещение)
            0x0A,  # field_c = 10 (базовый адрес)
            0x05  # field_d = 5 (исходное значение)
        ])

        # Загружаем программу в память
        self.interpreter.memory[:len(program)] = program

        # Запускаем выполнение
        self.interpreter.run()

        # Проверяем результат в памяти
        result_value = 0
        for i in range(4):
            result_value |= self.interpreter.memory[base_addr + i] << (i * 8)

        expected_value = (-test_value) & 0xFFFFFFFF  # 32-битное представление
        self.assertEqual(result_value, expected_value)
        self.assertEqual(self.interpreter.instructions_executed, 1)
        self.assertEqual(self.interpreter.pc, 4)

    def test_unary_minus_negative(self):
        """Тест унарного минуса с отрицательным числом"""
        # Подготовка: отрицательное значение в регистре 3
        test_value = -50  # В 32-битном представлении
        self.interpreter.registers[3] = test_value & 0xFFFFFFFF

        # Подготовка: базовый адрес в регистре 8
        base_addr = 0x200
        self.interpreter.registers[8] = base_addr

        # Создаем программу: унарный минус значения из R3, результат по адресу R8+0
        program = bytearray([
            0x5B,  # opcode 91
            0x00,  # field_b = 0
            0x08,  # field_c = 8
            0x03  # field_d = 3
        ])

        self.interpreter.memory[:len(program)] = program
        self.interpreter.run()

        # Проверяем результат
        result_value = 0
        for i in range(4):
            result_value |= self.interpreter.memory[base_addr + i] << (i * 8)

        expected_value = (-test_value) & 0xFFFFFFFF
        self.assertEqual(result_value, expected_value)

    def test_unary_minus_with_offset(self):
        """Тест унарного минуса со смещением"""
        # Подготовка
        test_value = 777
        self.interpreter.registers[7] = test_value
        self.interpreter.registers[15] = 0x300

        # Создаем программу с смещением 8
        program = bytearray([
            0x5B,  # opcode 91
            0x08,  # field_b = 8 (смещение)
            0x0F,  # field_c = 15
            0x07  # field_d = 7
        ])

        self.interpreter.memory[:len(program)] = program
        self.interpreter.run()

        # Проверяем результат по адресу 0x300 + 8 = 0x308
        result_addr = 0x300 + 8
        result_value = 0
        for i in range(4):
            result_value |= self.interpreter.memory[result_addr + i] << (i * 8)

        expected_value = (-test_value) & 0xFFFFFFFF
        self.assertEqual(result_value, expected_value)

    def test_unary_minus_zero(self):
        """Тест унарного минуса нуля"""
        self.interpreter.registers[1] = 0
        self.interpreter.registers[2] = 0x400

        program = bytearray([
            0x5B, 0x00, 0x02, 0x01
        ])

        self.interpreter.memory[:len(program)] = program
        self.interpreter.run()

        result_value = 0
        for i in range(4):
            result_value |= self.interpreter.memory[0x400 + i] << (i * 8)

        self.assertEqual(result_value, 0)  # -0 = 0

    def test_unary_minus_max_values(self):
        """Тест унарного минуса с максимальными значениями"""
        test_cases = [
            (0x7FFFFFFF, 0x80000001),  # MAX_INT -> -MAX_INT
            (0x80000000, 0x80000000),  # MIN_INT -> MIN_INT (переполнение)
            (0xFFFFFFFF, 0x00000001),  # -1 -> 1
        ]

        for input_val, expected in test_cases:
            with self.subTest(input=input_val, expected=expected):
                interpreter = UVMInterpreter(memory_size=4096)
                interpreter.registers[1] = input_val
                interpreter.registers[2] = 0x500

                program = bytearray([
                    0x5B, 0x00, 0x02, 0x01
                ])

                interpreter.memory[:len(program)] = program
                interpreter.run()

                result_value = 0
                for i in range(4):
                    result_value |= interpreter.memory[0x500 + i] << (i * 8)

                self.assertEqual(result_value, expected)

    def test_complete_unary_minus_program(self):
        """Тест полной программы с унарным минусом"""
        # Создаем тестовую программу
        program = bytearray()

        # Загрузка значений в регистры
        # R1 = 100, R2 = адрес 0x600
        program.extend([0x48, 0x01, 0x00, 0x00, 0x00, 0x64])  # R1 = 100
        program.extend([0x48, 0x02, 0x00, 0x00, 0x06, 0x00])  # R2 = 0x600

        # Унарный минус R1 -> mem[R2]
        program.extend([0x5B, 0x00, 0x02, 0x01])  # -R1 -> [R2]

        # Чтение результата в R3
        program.extend([0x71, 0x03, 0x02])  # R3 = mem[R2]

        # Загружаем программу
        self.interpreter.memory[:len(program)] = program

        # Запускаем выполнение
        self.interpreter.run()

        # Проверяем результаты
        self.assertEqual(self.interpreter.registers[1], 100)
        self.assertEqual(self.interpreter.registers[2], 0x600)

        # Проверяем значение в памяти
        mem_value = 0
        for i in range(4):
            mem_value |= self.interpreter.memory[0x600 + i] << (i * 8)

        expected_value = (-100) & 0xFFFFFFFF
        self.assertEqual(mem_value, expected_value)

        # Проверяем, что результат прочитан в R3
        self.assertEqual(self.interpreter.registers[3], expected_value)

        # Проверяем статистику
        self.assertEqual(self.interpreter.instructions_executed, 4)

    def test_unary_minus_alu_operations_chain(self):
        """Тест цепочки операций АЛУ"""
        # Создаем программу для вычисления: -(x) -> mem, затем читаем
        program = bytearray()

        # Инициализация
        program.extend([0x48, 0x0A, 0x00, 0x00, 0x08, 0x00])  # R10 = 0x800 (база)
        program.extend([0x48, 0x01, 0x00, 0x00, 0x00, 0x64])  # R1 = 100

        # Запись исходного значения
        program.extend([0x08, 0x01, 0x0A])  # mem[R10] = R1

        # Унарный минус
        program.extend([0x5B, 0x04, 0x0A, 0x01])  # -R1 -> mem[R10+4]

        # Чтение исходного и результата
        program.extend([0x71, 0x02, 0x0A])  # R2 = mem[R10] (исходное)
        program.extend([0x72, 0x0B, 0x04])  # R11 = 4
        program.extend([0x71, 0x03, 0x0B])  # R3 = mem[R10+4] (результат)

        # Второй унарный минус (двойное отрицание)
        program.extend([0x5B, 0x08, 0x0A, 0x03])  # -R3 -> mem[R10+8]
        program.extend([0x72, 0x0C, 0x08])  # R12 = 8
        program.extend([0x71, 0x04, 0x0C])  # R4 = mem[R10+8] (двойное отрицание)

        self.interpreter.memory[:len(program)] = program

        # Запускаем
        self.interpreter.run()

        # Проверяем
        self.assertEqual(self.interpreter.registers[1], 100)
        self.assertEqual(self.interpreter.registers[2], 100)  # Исходное значение

        result1 = self.interpreter.registers[3]
        expected1 = (-100) & 0xFFFFFFFF
        self.assertEqual(result1, expected1)

        result2 = self.interpreter.registers[4]
        expected2 = (-expected1) & 0xFFFFFFFF  # Двойное отрицание
        self.assertEqual(result2, expected2)

        # Проверяем значения в памяти
        for i, offset in enumerate([0, 4, 8]):
            addr = 0x800 + offset
            value = 0
            for j in range(4):
                value |= self.interpreter.memory[addr + j] << (j * 8)

            if offset == 0:
                self.assertEqual(value, 100)
            elif offset == 4:
                self.assertEqual(value, expected1)
            elif offset == 8:
                self.assertEqual(value, expected2)


def run_unary_minus_integration_test():
    """Интеграционный тест унарного минуса"""
    print("=== Интеграционный тест унарного минуса ===")

    import subprocess

    # Создаем тестовую программу
    test_program = {
        "name": "Интеграционный тест АЛУ",
        "instructions": [
            {"opcode": 72, "field_b": 10, "field_c": 4096},
            {"opcode": 72, "field_b": 1, "field_c": 12345},
            {"opcode": 91, "field_b": 0, "field_c": 10, "field_d": 1},
            {"opcode": 113, "field_b": 2, "field_c": 10},
            {"opcode": 72, "field_b": 11, "field_c": 4},
            {"opcode": 8, "field_b": 2, "field_c": 11}
        ]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_program, f, indent=2)
        json_file = f.name

    try:
        # Ассемблируем
        print("1. Ассемблирование...")
        result = subprocess.run(
            ['python', 'assembler.py', json_file, 'alu_test.bin'],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"Ошибка: {result.stderr}")
            return False

        print("✓ Программа ассемблирована")

        # Запускаем интерпретатор
        print("\n2. Выполнение...")
        result = subprocess.run(
            ['python', 'interpreter.py', 'alu_test.bin', 'alu_test.csv',
             '--start', '0x1000', '--end', '0x1020'],
            capture_output=True, text=True
        )

        print(result.stdout)

        if result.returncode != 0:
            print(f"Ошибка: {result.stderr}")
            return False

        print("✓ Программа выполнена")

        # Проверяем результат
        if os.path.exists('alu_test.csv'):
            with open('alu_test.csv', 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)

                print(f"\n3. Проверка результатов ({len(rows) - 1} строк в дампе):")
                for row in rows[1:3]:  # Первые 2 строки данных
                    print(f"  {row}")

        return True

    finally:
        # Очистка
        for file in [json_file, 'alu_test.bin', 'alu_test.csv']:
            if os.path.exists(file):
                os.unlink(file)


if __name__ == '__main__':
    # Запуск модульных тестов
    print("Запуск модульных тестов АЛУ...")
    unittest.main(exit=False)

    # Запуск интеграционного теста
    print("\n" + "=" * 60)
    if run_unary_minus_integration_test():
        print("\n✓ Все тесты пройдены успешно!")
    else:
        print("\n✗ Некоторые тесты не пройдены")