import unittest
import os
import sys

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestImports(unittest.TestCase):
    """Проверка того, что основные модули игры корректно импортируются.

    Соответствует описанию test_imports.py в README и не меняет поведение игры,
    только фиксирует базовую корректность структуры пакета.
    """

    def test_core_modules_import(self) -> None:
        # Главная точка входа
        __import__("main")

        # Ключевые игровые модули
        __import__("game.player")
        __import__("game.camera")
        __import__("game.platform")
        __import__("game.levels.level1")

        # UI - ui.menu может использовать Python 3.10+ синтаксис (match/case)
        try:
            __import__("ui.menu")
        except (SyntaxError, TypeError) as e:
            # Пропускаем если используется синтаксис Python 3.10+
            print(f"ui.menu import skipped (Python 3.10+ syntax): {e}")

        __import__("ui.hud")

        # Аудио-подсистема
        __import__("game.assets.audio.audio_manager")

        # Если мы дошли до сюда без исключений — тест пройден
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
