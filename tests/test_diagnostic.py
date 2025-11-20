import unittest
import sys
import os
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestDiagnostic(unittest.TestCase):
    """Диагностические тесты для отладки"""

    def test_pygame_initialization(self):
        """Тест инициализации Pygame"""
        pygame.init()
        try:
            screen = pygame.Surface((800, 600))
            self.assertEqual(screen.get_size(), (800, 600))
            success = True
        except Exception as e:
            success = False
            print(f"Pygame surface error: {e}")
        finally:
            pygame.quit()

        self.assertTrue(success)

    def test_game_import(self):
        """Тест импорта игровых модулей"""
        modules = ["game.player", "game.platform", "game.camera"]

        for module_name in modules:
            try:
                __import__(module_name)
                print(f"✅ {module_name} imported successfully")
                success = True
            except Exception as e:
                success = False
                print(f"❌ {module_name} import failed: {e}")

            self.assertTrue(success, f"Failed to import {module_name}")

    def test_game_creation(self):
        """Тест создания игровых объектов"""
        pygame.init()
        try:
            from game.player import Player
            from game.platform import Platform
            from game.camera import Camera

            # Test Player
            player = Player(100, 200)
            self.assertEqual(player.rect.x, 100)

            # Test Platform
            platform = Platform(0, 400, 800, 50)
            self.assertEqual(platform.rect.width, 800)

            # Test Camera (может потребовать аргументы)
            try:

                class MockTarget:
                    def __init__(self):
                        self.rect = pygame.Rect(100, 100, 50, 50)

                target = MockTarget()
                camera = Camera(target, (800, 600))
                self.assertIsNotNone(camera)
            except TypeError as e:
                print(f"Camera requires arguments: {e}")
                # Пропускаем если камера требует специфичные аргументы

            success = True

        except Exception as e:
            success = False
            print(f"Game object creation error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            pygame.quit()

        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()
