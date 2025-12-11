"""
Парсер JSON-программ для УВМ
Этап 2: Формирование машинного кода
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class Instruction:
    """Промежуточное представление команды УВМ"""
    opcode: int        # Код операции (поле A)
    field_b: int       # Поле B
    field_c: int       # Поле C
    field_d: Optional[int] = None  # Поле D (только для 4-байтных команд)
    size: int = 0      # Размер команды в байтах

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

        # Проверка обязательности полей
        if self.opcode == 91 and self.field_d is None:
            raise ValueError("Для команды унарного минуса обязательно поле D")


def parse_instruction(instr_dict: Dict[str, Any]) -> Instruction:
    """Парсинг одной команды из JSON-словаря"""
    # Создаем копию словаря без нестандартных полей
    clean_dict = {k: v for k, v in instr_dict.items() if k in ['opcode', 'field_b', 'field_c', 'field_d']}

    opcode = clean_dict.get('opcode')

    if opcode is None:
        raise ValueError("Отсутствует код операции в команде")

    # Валидация кода операции
    valid_opcodes = [72, 113, 8, 91]
    if opcode not in valid_opcodes:
        raise ValueError(f"Недопустимый код операции: {opcode}. Допустимые: {valid_opcodes}")

    # Извлечение полей в зависимости от типа команды
    field_b = clean_dict.get('field_b', 0)
    field_c = clean_dict.get('field_c', 0)

    # Проверка типов полей
    if not isinstance(field_b, int):
        raise ValueError(f"Поле B должно быть целым числом, получено: {type(field_b)}")

    if not isinstance(field_c, int):
        raise ValueError(f"Поле C должно быть целым числом, получено: {type(field_c)}")

    # Для 4-байтных команд извлекаем поле D
    if opcode == 91:  # Унарный минус
        field_d = clean_dict.get('field_d')
        if field_d is None:
            raise ValueError("Для команды унарного минуса обязательно поле D")

        if not isinstance(field_d, int):
            raise ValueError(f"Поле D должно быть целым числом, получено: {type(field_d)}")

        return Instruction(opcode=opcode, field_b=field_b,
                           field_c=field_c, field_d=field_d)
    else:
        # Для других команд поле D не должно быть указано
        if 'field_d' in clean_dict:
            raise ValueError(f"Поле D не поддерживается для команды с кодом {opcode}")

        return Instruction(opcode=opcode, field_b=field_b, field_c=field_c)

def parse_program(program_json: Dict[str, Any]) -> List[Instruction]:
    """
    Парсинг всей программы из JSON

    Формат JSON:
    {
        "name": "название программы",
        "description": "описание программы",
        "instructions": [
            {"opcode": 72, "field_b": 7, "field_c": 440},
            ...
        ]
    }
    """
    if 'instructions' not in program_json:
        raise ValueError("Отсутствует список команд 'instructions' в JSON")

    instructions_list = program_json['instructions']
    if not isinstance(instructions_list, list):
        raise ValueError("Поле 'instructions' должно быть списком")

    if len(instructions_list) == 0:
        raise ValueError("Программа должна содержать хотя бы одну команду")

    instructions = []
    for i, instr_dict in enumerate(instructions_list):
        try:
            instruction = parse_instruction(instr_dict)
            instructions.append(instruction)
        except ValueError as e:
            raise ValueError(f"Ошибка в команде {i}: {e}")

    return instructions