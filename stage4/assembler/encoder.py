"""
Кодировщик команд УВМ в бинарный формат
Этап 4: Реализация арифметико-логического устройства (АЛУ)
"""

from typing import Optional


# Убираем from parser import Instruction вверху, будем использовать аннотации строк

def encode_load_constant(instr: 'Instruction') -> bytearray:
    """
    Кодирование команды загрузки константы (6 байт)
    Формат: A (7 бит) | B (7 бит) | C (28 бит)
    По спецификации из теста: A=72, B=7, C=440 -> 0xC8, 0x03, 0x6E, 0x00, 0x00, 0x00
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

    # Создание байтового массива
    data = bytearray(6)

    # Распределение битов по спецификации:
    # Байт 0: биты 0-6 = A, бит 7 = старший бит B (бит 6 поля B)
    # Байт 1: биты 0-5 = младшие 6 бит B, биты 6-7 = старшие 2 бита C (биты 26-27)
    # Байт 2: биты 0-7 = биты 18-25 C
    # Байт 3: биты 0-7 = биты 10-17 C  
    # Байт 4: биты 0-7 = биты 2-9 C
    # Байт 5: биты 4-7 = младшие 2 бита C (биты 0-1), биты 0-3 = 0

    # Байт 0: A в битах 0-6, старший бит B в бите 7
    a_bits = instr.opcode & 0x7F
    b_bit7 = (instr.field_b >> 6) & 0x01  # Старший (7-й) бит B
    data[0] = (b_bit7 << 7) | a_bits

    # Байт 1: младшие 6 бит B в битах 0-5, старшие 2 бита C в битах 6-7
    b_bits_low = instr.field_b & 0x3F  # Младшие 6 бит B
    c_bits_high = (field_c >> 26) & 0x03  # Старшие 2 бита C (биты 26-27)
    data[1] = (c_bits_high << 6) | b_bits_low

    # Байт 2: биты 18-25 C
    data[2] = (field_c >> 18) & 0xFF

    # Байт 3: биты 10-17 C
    data[3] = (field_c >> 10) & 0xFF

    # Байт 4: биты 2-9 C
    data[4] = (field_c >> 2) & 0xFF

    # Байт 5: младшие 2 бита C в битах 4-7, биты 0-3 = 0
    data[5] = (field_c & 0x03) << 4

    return data


def encode_memory_operation(instr: 'Instruction') -> bytearray:
    """
    Кодирование команд чтения/записи памяти (3 байта)
    Формат: A (7 бит) | B (7 бит) | C (7 бит)
    По спецификации из теста: A=113, B=102, C=77 -> 0x71, 0x73, 0x13
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

    # Распределение битов по спецификации:
    # Байт 0: биты 0-6 = A, бит 7 = старший бит B (бит 6 поля B)
    # Байт 1: биты 0-5 = младшие 6 бит B, биты 6-7 = старшие 2 бита C (биты 5-6)
    # Байт 2: биты 0-4 = младшие 5 бит C, биты 5-7 = 0

    # Байт 0: A в битах 0-6, старший бит B в бите 7
    a_bits = instr.opcode & 0x7F
    b_bit6 = (instr.field_b >> 6) & 0x01  # Старший (7-й) бит B
    data[0] = (b_bit6 << 7) | a_bits

    # Байт 1: младшие 6 бит B в битах 0-5, старшие 2 бита C в битах 6-7
    b_bits_low = instr.field_b & 0x3F  # Младшие 6 бит B
    c_bits_high = (instr.field_c >> 5) & 0x03  # Старшие 2 бита C (биты 5-6)
    data[1] = (c_bits_high << 6) | b_bits_low

    # Байт 2: младшие 5 бит C в битах 0-4, биты 5-7 = 0
    data[2] = instr.field_c & 0x1F

    return data


def encode_unary_minus(instr: 'Instruction') -> bytearray:
    """
    Кодирование команды унарного минуса (4 байта)
    Формат: A (7 бит) | B (6 бит) | C (7 бит) | D (7 бит)
    По спецификации из теста: A=91, B=16, C=41, D=53 -> 0x5B, 0x28, 0x55, 0x03
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

    # Распределение битов по спецификации:
    # Байт 0: биты 0-6 = A, бит 7 = старший бит B (бит 5 поля B)
    # Байт 1: биты 0-4 = младшие 5 бит B, биты 5-7 = старшие 3 бита C (биты 4-6)
    # Байт 2: биты 0-3 = младшие 4 бита C, биты 4-7 = старшие 4 бита D (биты 3-6)
    # Байт 3: биты 0-2 = младшие 3 бита D, биты 3-7 = 0

    # Байт 0: A в битах 0-6, старший бит B в бите 7
    a_bits = instr.opcode & 0x7F
    b_bit5 = (instr.field_b >> 5) & 0x01  # Старший (6-й) бит B
    data[0] = (b_bit5 << 7) | a_bits

    # Байт 1: младшие 5 бит B в битах 0-4, старшие 3 бита C в битах 5-7
    b_bits_low = instr.field_b & 0x1F  # Младшие 5 бит B
    c_bits_high = (instr.field_c >> 4) & 0x07  # Старшие 3 бита C (биты 4-6)
    data[1] = (c_bits_high << 5) | b_bits_low

    # Байт 2: младшие 4 бита C в битах 0-3, старшие 4 бита D в битах 4-7
    c_bits_low = instr.field_c & 0x0F  # Младшие 4 бита C
    d_bits_high = (instr.field_d >> 3) & 0x0F  # Старшие 4 бита D (биты 3-6)
    data[2] = (d_bits_high << 4) | c_bits_low

    # Байт 3: младшие 3 бита D в битах 0-2, биты 3-7 = 0
    data[3] = instr.field_d & 0x07

    return data


def encode_instruction(instr: 'Instruction') -> bytearray:
    """
    Кодирование команды в бинарный формат в зависимости от типа
    """
    # Импортируем здесь, чтобы избежать циклического импорта
    from parser import Instruction

    if instr.opcode == 72:  # Загрузка константы
        return encode_load_constant(instr)
    elif instr.opcode in [113, 8]:  # Чтение/запись
        return encode_memory_operation(instr)
    elif instr.opcode == 91:  # Унарный минус
        return encode_unary_minus(instr)
    else:
        raise ValueError(f"Неизвестный код операции: {instr.opcode}")


def encode_program(instructions: list) -> bytearray:
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