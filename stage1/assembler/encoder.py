"""
Кодировщик команд УВМ в бинарный формат
"""

from parser import Instruction


def encode_load_constant(instr: Instruction) -> bytearray:
    """
    Кодирование команды загрузки константы (6 байт)
    Формат: A (7 бит) | B (7 бит) | C (28 бит)
    """
    if instr.size != 6:
        raise ValueError("Некорректный размер для команды загрузки константы")

    # Упаковка полей
    # Байт 0-1: A (биты 0-6) и B (биты 7-13)
    byte0 = instr.opcode & 0x7F  # Младшие 7 бит A
    byte1 = instr.field_b & 0x7F  # 7 бит B

    # Байты 2-5: C (28 бит)
    c_value = instr.field_c & 0xFFFFFFF  # 28 бит

    # Создание байтового массива
    data = bytearray(6)
    data[0] = byte0
    data[1] = byte1
    data[2] = (c_value >> 20) & 0xFF
    data[3] = (c_value >> 12) & 0xFF
    data[4] = (c_value >> 4) & 0xFF
    data[5] = (c_value & 0x0F) << 4  # Младшие 4 бита в старшей части байта

    return data


def encode_memory_operation(instr: Instruction) -> bytearray:
    """
    Кодирование команд чтения/записи памяти (3 байта)
    Формат: A (7 бит) | B (7 бит) | C (7 бит)
    """
    if instr.size != 3:
        raise ValueError("Некорректный размер для команды памяти")

    data = bytearray(3)
    data[0] = instr.opcode & 0x7F
    data[1] = instr.field_b & 0x7F
    data[2] = instr.field_c & 0x7F

    return data


def encode_unary_minus(instr: Instruction) -> bytearray:
    """
    Кодирование команды унарного минуса (4 байта)
    Формат: A (7 бит) | B (6 бит) | C (7 бит) | D (7 бит)
    """
    if instr.size != 4:
        raise ValueError("Некорректный размер для команды унарного минуса")

    data = bytearray(4)
    data[0] = instr.opcode & 0x7F
    data[1] = instr.field_b & 0x3F  # 6 бит
    data[2] = instr.field_c & 0x7F  # 7 бит
    data[3] = instr.field_d & 0x7F  # 7 бит

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