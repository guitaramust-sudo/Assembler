import os
import subprocess
import tempfile


def test_minimal():
    """Тест минимальной программы"""
    print("=== Тест минимальной программы ===")

    # Создаем минимальную тестовую программу - только одну команду
    minimal_program = {
        "name": "Минимальный тест - одна команда",
        "instructions": [
            {"opcode": 72, "field_b": 1, "field_c": 123}
        ]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(minimal_program, f, indent=2)
        json_file = f.name

    try:
        # Ассемблируем
        print("1. Ассемблируем программу...")
        result = subprocess.run(
            ['python', 'assembler.py', json_file, 'test_minimal.bin'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Ошибка ассемблирования: {result.stderr}")
            return False

        print("✓ Программа ассемблирована")

        # Показываем байты
        with open('test_minimal.bin', 'rb') as f:
            data = f.read()
            print(f"  Байты: {' '.join(f'0x{b:02X}' for b in data)}")

        # Запускаем интерпретатор
        print("\n2. Запускаем интерпретатор...")
        result = subprocess.run(
            ['python', 'interpreter.py', 'test_minimal.bin', 'test_minimal_dump.csv',
             '--start', '0', '--end', '0x10'],
            capture_output=True,
            text=True
        )

        print("Вывод интерпретатора:")
        print(result.stdout)

        if result.returncode != 0:
            print(f"Ошибка интерпретации: {result.stderr}")
            return False

        return True

    finally:
        # Удаляем временные файлы
        if os.path.exists(json_file):
            os.unlink(json_file)