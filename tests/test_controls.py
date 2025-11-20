import unittest
import sys
import os
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from game.player import Player


class TestControls(unittest.TestCase):
    def setUp(self):
        pygame.init()
        # Mock asset loader чтобы избежать ошибок загрузки
        import game.player

        class MockAssetLoader:
            def load_image(self, name, scale=1):
                return pygame.Surface((50, 50))

        game.player.asset_loader = MockAssetLoader()

        self.player = Player(100, 300)

    def tearDown(self):
        pygame.quit()

    def test_player_movement_left(self):
        """Тест движения игрока влево"""
        initial_x = self.player.rect.x

        # Создаем правильный mock для keys
        class MockKeys:
            def __getitem__(self, key):
                if key == pygame.K_LEFT:
                    return True
                return False

        keys = MockKeys()
        platforms = []  # Передаем пустой список платформ
        self.player.handle_keys(keys, platforms)

        self.assertEqual(self.player.rect.x, initial_x - self.player.speed)
        self.assertFalse(self.player.facing_right)

    def test_player_movement_right(self):
        """Тест движения игрока вправо"""
        initial_x = self.player.rect.x

        # Создаем правильный mock для keys
        class MockKeys:
            def __getitem__(self, key):
                if key == pygame.K_RIGHT:
                    return True
                return False

        keys = MockKeys()
        platforms = []  # Передаем пустой список платформ
        self.player.handle_keys(keys, platforms)

        self.assertEqual(self.player.rect.x, initial_x + self.player.speed)
        self.assertTrue(self.player.facing_right)

    def test_player_jump(self):
        """Тест прыжка игрока"""
        self.player.on_ground = True
        self.player.jump()

        self.assertEqual(self.player.velocity_y, -23)
        self.assertTrue(self.player.is_jumping)
        self.assertFalse(self.player.on_ground)


if __name__ == "__main__":
    unittest.main()
