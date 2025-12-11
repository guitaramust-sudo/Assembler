"""
Парсер JSON-программ для УВМ
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Instruction:
    """Промежуточное представление команды УВМ"""
    opcode: int  # Код операции (поле A)
    field_b: int  # Поле B
    field_c: int  # Поле C
    field_d: int = None  # Поле D (только для 4-байтных команд)
    size: int = 0  # Размер команды в байтах

    def __post_init__(self):
        """Автоматически определяем размер команды по коду операции"""
        if self.opcode == 72:  # Загрузка константы
            self.size = 6
        elif self.opcode in [113, 8]:  # Чтение/запись
            self.size = 3
        elif self.opcode == 91:  # Унарный минус
            self.size = 4
        else:
            raise ValueError(f"Неизвестный код операции: {self.opcode}")


def parse_instruction(instr_dict: Dict[str, Any]) -> Instruction:
    """Парсинг одной команды из JSON-словаря"""
    opcode = instr_dict.get('opcode')

    if opcode is None:
        raise ValueError("Отсутствует код операции в команде")

    # Извлечение полей в зависимости от типа команды
    field_b = instr_dict.get('field_b', 0)
    field_c = instr_dict.get('field_c', 0)

    # Для 4-байтных команд извлекаем поле D
    if opcode == 91:  # Унарный минус
        field_d = instr_dict.get('field_d', 0)
        return Instruction(opcode=opcode, field_b=field_b,
                           field_c=field_c, field_d=field_d)
    else:
        return Instruction(opcode=opcode, field_b=field_b, field_c=field_c)


def parse_program(program_json: Dict[str, Any]) -> List[Instruction]:
    """
    Парсинг всей программы из JSON

    Формат JSON:
    {
        "name": "название программы",
        "instructions": [
            {"opcode": 72, "field_b": 7, "field_c": 440},
            ...
        ]
    }
    """
    if 'instructions' not in program_json:
        raise ValueError("Отсутствует список команд 'instructions' в JSON")

    instructions = []
    for i, instr_dict in enumerate(program_json['instructions']):
        try:
            instruction = parse_instruction(instr_dict)
            instructions.append(instruction)
        except ValueError as e:
            raise ValueError(f"Ошибка в команде {i}: {e}")

    return instructions