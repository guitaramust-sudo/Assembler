#!/usr/bin/env python3
"""
Интерпретатор для учебной виртуальной машины (УВМ)
Этап 4: Реализация арифметико-логического устройства (АЛУ)
"""

import sys
import argparse
import csv
from pathlib import Path
from typing import List, Tuple, Optional


class UVMInterpreter:
    """Интерпретатор Учебной Виртуальной Машины"""

    def __init__(self, memory_size: int = 1024 * 1024):  # 1MB памяти по умолчанию
        """
        Инициализация интерпретатора

        Args:
            memory_size: размер памяти в байтах
        """
        # Объединенная память команд и данных
        self.memory = bytearray(memory_size)

        # Регистры (128 регистров, каждый 32-битный)
        self.registers = [0] * 128

        # Счетчик команд (программный счетчик)
        self.pc = 0

        # Флаг завершения программы
        self.halted = False

        # Статистика выполнения
        self.instructions_executed = 0

    def load_program(self, binary_file: str) -> None:
        """
        Загрузка программы в память

        Args:
            binary_file: путь к бинарному файлу с программой
        """
        try:
            with open(binary_file, 'rb') as f:
                program_data = f.read()

            # Загружаем программу в начало памяти
            if len(program_data) > len(self.memory):
                raise ValueError(f"Программа слишком большая: {len(program_data)} байт > {len(self.memory)} байт")

            self.memory[:len(program_data)] = program_data
            print(f"Загружено {len(program_data)} байт программы по адресу 0x{0:08X}")

        except FileNotFoundError:
            print(f"Ошибка: файл {binary_file} не найден")
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка загрузки программы: {e}")
            sys.exit(1)

    def decode_instruction(self) -> Optional[Tuple[int, int, int, Optional[int]]]:
        """
        Декодирование команды по текущему PC

        Returns:
            Кортеж (opcode, field_b, field_c, field_d) или None если команда неполная
        """
        # Проверяем, есть ли достаточно данных для команды
        if self.pc + 3 > len(self.memory):
            return None

        # Читаем первый байт для определения типа команды
        first_byte = self.memory[self.pc]
        opcode = first_byte & 0x7F

        # Определяем размер команды и декодируем поля
        if opcode == 72:  # Загрузка константы (6 байт)
            if self.pc + 6 > len(self.memory):
                return None

            field_b = self.memory[self.pc + 1] & 0x7F

            # Собираем 28-битное поле C из байтов 2-5
            field_c = (
                    (self.memory[self.pc + 2] << 20) |
                    (self.memory[self.pc + 3] << 12) |
                    (self.memory[self.pc + 4] << 4) |
                    ((self.memory[self.pc + 5] >> 4) & 0x0F)
            )

            return (opcode, field_b, field_c, None)

        elif opcode in [113, 8]:  # Чтение/запись памяти (3 байта)
            if self.pc + 3 > len(self.memory):
                return None

            field_b = self.memory[self.pc + 1] & 0x7F
            field_c = self.memory[self.pc + 2] & 0x7F

            return (opcode, field_b, field_c, None)

        elif opcode == 91:  # Унарный минус (4 байта)
            if self.pc + 4 > len(self.memory):
                return None

            field_b = self.memory[self.pc + 1] & 0x3F  # 6 бит
            field_c = self.memory[self.pc + 2] & 0x7F  # 7 бит
            field_d = self.memory[self.pc + 3] & 0x7F  # 7 бит

            return (opcode, field_b, field_c, field_d)

        else:
            # Неизвестная команда - пропускаем байт и возвращаем None
            # чтобы цикл выполнения завершился
            print(f"Предупреждение: неизвестный код операции 0x{opcode:02X} по адресу 0x{self.pc:08X}")
            self.pc += 1  # Пропускаем неизвестный байт
            return None  # Возвращаем None вместо рекурсивного вызова

    def execute_instruction(self, opcode: int, field_b: int, field_c: int, field_d: Optional[int]) -> None:
        """
        Выполнение декодированной команды

        Args:
            opcode: код операции
            field_b: поле B
            field_c: поле C
            field_d: поле D (если есть)
        """
        try:
            if opcode == 72:  # Загрузка константы
                # Загружаем константу в регистр
                self.registers[field_b] = field_c
                self.pc += 6

            elif opcode == 113:  # Чтение из памяти
                # Читаем адрес из регистра field_c
                mem_addr = self.registers[field_c]

                # Проверяем границы памяти
                if mem_addr < 0 or mem_addr + 4 > len(self.memory):
                    raise MemoryError(f"Чтение по недопустимому адресу: 0x{mem_addr:08X}")

                # Читаем 32-битное значение из памяти (little-endian)
                value = 0
                for i in range(4):
                    value |= self.memory[mem_addr + i] << (i * 8)

                # Сохраняем в регистр field_b
                self.registers[field_b] = value
                self.pc += 3

            elif opcode == 8:  # Запись в память
                # Читаем значение из регистра field_b
                value = self.registers[field_b]

                # Читаем адрес из регистра field_c
                mem_addr = self.registers[field_c]

                # Проверяем границы памяти
                if mem_addr < 0 or mem_addr + 4 > len(self.memory):
                    raise MemoryError(f"Запись по недопустимому адресу: 0x{mem_addr:08X}")

                # Записываем 32-битное значение в память (little-endian)
                for i in range(4):
                    self.memory[mem_addr + i] = (value >> (i * 8)) & 0xFF

                self.pc += 3

            elif opcode == 91:  # Унарный минус
                # Выполняем унарный минус
                # Поле D: адрес регистра с исходным значением
                # Поле C: адрес регистра с базовым адресом памяти
                # Поле B: смещение

                # Читаем исходное значение из регистра field_d
                source_value = self.registers[field_d]

                # Вычисляем унарный минус (инверсия знака)
                result_value = -source_value

                # Приводим к 32-битному представлению
                result_value = result_value & 0xFFFFFFFF

                # Вычисляем адрес в памяти: базовый адрес + смещение
                base_addr = self.registers[field_c]
                offset = field_b
                mem_addr = base_addr + offset

                # Проверяем границы памяти
                if mem_addr < 0 or mem_addr + 4 > len(self.memory):
                    raise MemoryError(f"Запись результата по недопустимому адресу: 0x{mem_addr:08X}")

                # Записываем результат в память
                for i in range(4):
                    self.memory[mem_addr + i] = (result_value >> (i * 8)) & 0xFF

                print(f"  Унарный минус: -{source_value} = {result_value} -> mem[0x{mem_addr:X}]")
                self.pc += 4

            else:
                # Этого не должно случиться, так как decode_instruction уже фильтрует
                print(f"Ошибка: неизвестный код операции {opcode}")
                self.halted = True
                return

            # Увеличиваем счетчик выполненных команд
            self.instructions_executed += 1

        except MemoryError as e:
            print(f"Ошибка памяти при выполнении команды: {e}")
            self.halted = True
        except Exception as e:
            print(f"Ошибка выполнения команды: {e}")
            self.halted = True

    def run(self) -> None:
        """Основной цикл интерпретатора"""
        print("Запуск интерпретатора...")
        print(f"Начальный PC: 0x{self.pc:08X}")

        while not self.halted:
            # Декодируем следующую команду
            decoded = self.decode_instruction()

            if decoded is None:
                # Недостаточно данных или конец программы
                print("Достигнут конец программы или недостаточно данных для команды")
                self.halted = True
                break

            opcode, field_b, field_c, field_d = decoded

            # Выполняем команду
            self.execute_instruction(opcode, field_b, field_c, field_d)

            # Ограничим количество команд для безопасности
            if self.instructions_executed > 10000:
                print("Превышено максимальное количество команд (10,000)")
                self.halted = True

        print(f"\nВыполнение завершено.")
        print(f"Всего выполнено команд: {self.instructions_executed}")
        print(f"Конечный PC: 0x{self.pc:08X}")

    def dump_memory(self, start_addr: int, end_addr: int, output_file: str) -> None:
        """
        Дамп памяти в CSV файл

        Args:
            start_addr: начальный адрес
            end_addr: конечный адрес
            output_file: путь к выходному CSV файлу
        """
        try:
            # Проверяем границы
            if start_addr < 0 or end_addr >= len(self.memory) or start_addr > end_addr:
                print(f"Ошибка: недопустимый диапазон адресов: 0x{start_addr:08X}-0x{end_addr:08X}")
                return

            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Заголовок
                writer.writerow(['Адрес', 'Байт 0', 'Байт 1', 'Байт 2', 'Байт 3',
                                 'Значение (32-бит)', 'ASCII'])

                # Дамп по 4 байта в строке
                for addr in range(start_addr, end_addr + 1, 4):
                    row = [f"0x{addr:08X}"]

                    # Байты
                    for i in range(4):
                        if addr + i < len(self.memory):
                            byte_val = self.memory[addr + i]
                            row.append(f"0x{byte_val:02X}")
                        else:
                            row.append("N/A")

                    # 32-битное значение (little-endian)
                    if addr + 3 < len(self.memory):
                        value = 0
                        for i in range(4):
                            value |= self.memory[addr + i] << (i * 8)
                        row.append(f"0x{value:08X} ({value})")
                    else:
                        row.append("N/A")

                    # ASCII представление
                    ascii_str = ""
                    for i in range(4):
                        if addr + i < len(self.memory):
                            byte_val = self.memory[addr + i]
                            if 32 <= byte_val <= 126:  # Печатные символы
                                ascii_str += chr(byte_val)
                            else:
                                ascii_str += "."
                        else:
                            ascii_str += " "
                    row.append(ascii_str)

                    writer.writerow(row)

            print(f"Дамп памяти сохранен в {output_file}")
            print(f"Диапазон: 0x{start_addr:08X} - 0x{end_addr:08X}")
            print(f"Количество строк: {(end_addr - start_addr + 4) // 4}")

        except Exception as e:
            print(f"Ошибка при сохранении дампа памяти: {e}")

    def dump_registers(self) -> None:
        """Вывод состояния регистров"""
        print("\nСостояние регистров:")
        print("=" * 80)
        print(f"{'Регистр':<10} {'Значение (hex)':<15} {'Значение (dec)':<20} {'Значение (bin)':<32}")
        print("-" * 80)

        for i in range(128):
            value = self.registers[i]
            if value != 0:  # Выводим только ненулевые регистры для краткости
                print(f"R{i:<8} 0x{value:08X}      {value:<20} {value:032b}")


def main():
    parser = argparse.ArgumentParser(description='Интерпретатор УВМ')
    parser.add_argument('program_file', help='Путь к бинарному файлу с программой')
    parser.add_argument('dump_file', help='Путь к файлу для дампа памяти (CSV)')
    parser.add_argument('--start', type=lambda x: int(x, 0), default=0x0000,
                        help='Начальный адрес дампа (hex или dec)')
    parser.add_argument('--end', type=lambda x: int(x, 0), default=0x0100,
                        help='Конечный адрес дампа (hex или dec)')
    parser.add_argument('--memory-size', type=int, default=1024 * 1024,
                        help='Размер памяти в байтах (по умолчанию: 1MB)')

    args = parser.parse_args()

    # Создаем и настраиваем интерпретатор
    interpreter = UVMInterpreter(memory_size=args.memory_size)

    # Загружаем программу
    interpreter.load_program(args.program_file)

    # Запускаем выполнение
    interpreter.run()

    # Сохраняем дамп памяти
    interpreter.dump_memory(args.start, args.end, args.dump_file)

    # Выводим состояние регистров
    interpreter.dump_registers()


if __name__ == "__main__":
    main()