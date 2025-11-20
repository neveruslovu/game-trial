import unittest
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestBasic(unittest.TestCase):
    """Базовые тесты для проверки окружения"""

    def test_environment(self):
        """Проверка что тесты запускаются"""
        self.assertTrue(True, "Тестовое утверждение")

    def test_project_files(self):
        """Проверка существования основных файлов"""
        project_root = os.path.dirname(os.path.dirname(__file__))

        required_files = [
            "main.py",
            os.path.join("game", "player.py"),
            os.path.join("game", "platform.py"),
            os.path.join("game", "camera.py"),
        ]

        missing_files = []
        for file in required_files:
            file_path = os.path.join(project_root, file)
            if not os.path.exists(file_path):
                missing_files.append(file)

        self.assertEqual(len(missing_files), 0, f"Отсутствуют файлы: {missing_files}")


if __name__ == "__main__":
    unittest.main()
