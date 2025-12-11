"""
Кодировщик команд УВМ в бинарный формат
Этап 2: Формирование машинного кода
"""

from parser import Instruction
from typing import List, ByteString


def encode_load_constant(instr: Instruction) -> bytearray:
    """
    Кодирование команды загрузки константы (6 байт)
    Формат: A (7 бит) | B (7 бит) | C (28 бит)
    """
    if instr.size != 6:
        raise ValueError("Некорректный размер для команды загрузки константы")

    # Проверка диапазонов
    if instr.opcode != 72:
        raise ValueError(f"Некорректный код операции для загрузки константы: {instr.opcode}")

    if not (0 <= instr.field_b <= 0x7F):  # 7 бит
        raise ValueError(f"Поле B вне диапазона: {instr.field_b}")

    # Автоматически ограничиваем поле C 28 битами
    field_c = instr.field_c & 0xFFFFFFF  # Оставляем только младшие 28 бит

    if instr.field_c != field_c:
        print(f"Предупреждение: поле C урезано с 0x{instr.field_c:X} до 0x{field_c:X} (28 бит)")

    # Упаковка полей
    # Байт 0: A (7 бит) в младших 7 битах
    # Байт 1: B (7 бит)
    # Байты 2-5: C (28 бит)

    # Создание байтового массива
    data = bytearray(6)

    # Байт 0: opcode в младших 7 битах
    data[0] = instr.opcode & 0x7F

    # Байт 1: field_b
    data[1] = instr.field_b & 0x7F

    # Байты 2-5: field_c (28 бит)
    # Распределяем 28 бит по 4 байтам:
    # data[2]: биты 20-27
    # data[3]: биты 12-19
    # data[4]: биты 4-11
    # data[5]: биты 0-3 в старшей части байта (биты 4-7), младшие 4 бита = 0

    data[2] = (field_c >> 20) & 0xFF  # Старшие 8 бит из 28
    data[3] = (field_c >> 12) & 0xFF  # Следующие 8 бит
    data[4] = (field_c >> 4) & 0xFF  # Следующие 8 бит
    data[5] = (field_c & 0x0F) << 4  # Младшие 4 бита в старшей части байта

    return data

def encode_memory_operation(instr: Instruction) -> bytearray:
    """
    Кодирование команд чтения/записи памяти (3 байта)
    Формат: A (7 бит) | B (7 бит) | C (7 бит)
    """
    if instr.size != 3:
        raise ValueError("Некорректный размер для команды памяти")

    # Проверка кода операции
    if instr.opcode not in [113, 8]:
        raise ValueError(f"Некорректный код операции для команды памяти: {instr.opcode}")

    # Проверка диапазонов
    if not (0 <= instr.field_b <= 0x7F):  # 7 бит
        raise ValueError(f"Поле B вне диапазона: {instr.field_b}")

    if not (0 <= instr.field_c <= 0x7F):  # 7 бит
        raise ValueError(f"Поле C вне диапазона: {instr.field_c}")

    data = bytearray(3)

    # Байт 0: opcode
    data[0] = instr.opcode & 0x7F

    # Байт 1: field_b
    data[1] = instr.field_b & 0x7F

    # Байт 2: field_c
    data[2] = instr.field_c & 0x7F

    return data

def encode_unary_minus(instr: Instruction) -> bytearray:
    """
    Кодирование команды унарного минуса (4 байта)
    Формат: A (7 бит) | B (6 бит) | C (7 бит) | D (7 бит)
    """
    if instr.size != 4:
        raise ValueError("Некорректный размер для команды унарного минуса")

    # Проверка кода операции
    if instr.opcode != 91:
        raise ValueError(f"Некорректный код операции для унарного минуса: {instr.opcode}")

    # Проверка диапазонов
    if not (0 <= instr.field_b <= 0x3F):  # 6 бит
        raise ValueError(f"Поле B (смещение) вне диапазона: {instr.field_b}")

    if not (0 <= instr.field_c <= 0x7F):  # 7 бит
        raise ValueError(f"Поле C вне диапазона: {instr.field_c}")

    if not (0 <= instr.field_d <= 0x7F):  # 7 бит
        raise ValueError(f"Поле D вне диапазона: {instr.field_d}")

    data = bytearray(4)

    # Байт 0: opcode
    data[0] = instr.opcode & 0x7F

    # Байт 1: field_b (6 бит) в младших 6 битах
    data[1] = instr.field_b & 0x3F

    # Байт 2: field_c
    data[2] = instr.field_c & 0x7F

    # Байт 3: field_d
    data[3] = instr.field_d & 0x7F

    return data

def encode_instruction(instr: Instruction) -> bytearray:
    """
    Кодирование команды в бинарный формат в зависимости от типа
    """
    if instr.opcode == 72:  # Загрузка константы
        return encode_load_constant(instr)
    elif instr.opcode in [113, 8]:  # Чтение/запись
        return encode_memory_operation(instr)
    elif instr.opcode == 91:  # Унарный минус
        return encode_unary_minus(instr)
    else:
        raise ValueError(f"Неизвестный код операции: {instr.opcode}")

def encode_program(instructions: List[Instruction]) -> bytearray:
    """
    Кодирование всей программы в бинарный формат
    """
    binary_data = bytearray()

    for i, instr in enumerate(instructions):
        try:
            encoded = encode_instruction(instr)
            binary_data.extend(encoded)
        except ValueError as e:
            raise ValueError(f"Ошибка кодирования команды {i}: {e}")

    return binary_data

def bytes_to_hex_string(data: bytes) -> str:
    """
    Преобразование байтовой последовательности в строку в формате
    из спецификации УВМ: 0xXX, 0xXX, 0xXX, ...
    """
    return ', '.join(f'0x{b:02X}' for b in data)