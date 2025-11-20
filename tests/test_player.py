import unittest
import sys
import os
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from game.player import Player
from game.platform import Platform


class TestPlayer(unittest.TestCase):
    """Тесты для класса Player"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        pygame.init()
        self.player = Player(100, 300)

    def tearDown(self):
        """Очистка после каждого теста"""
        pygame.quit()

    def test_player_initialization(self):
        """Тест инициализации игрока"""
        self.assertEqual(self.player.rect.x, 100)
        self.assertEqual(self.player.rect.y, 300)
        self.assertEqual(self.player.speed, 5)
        self.assertEqual(self.player.jump_power, -23)
        self.assertFalse(self.player.is_jumping)
        self.assertFalse(self.player.on_ground)
        self.assertTrue(self.player.facing_right)

    def test_player_jump(self):
        """Тест прыжка игрока"""
        self.player.on_ground = True
        self.player.jump()

        self.assertEqual(self.player.velocity_y, -23)
        self.assertTrue(self.player.is_jumping)
        self.assertFalse(self.player.on_ground)

    def test_player_movement(self):
        """Тест движения игрока"""
        # Создаем платформу под игроком
        platforms = [Platform(0, 400, 800, 50)]

        # Игрок должен падать из-за гравитации
        initial_y = self.player.rect.y
        self.player.update(platforms, [], 0)  # enemies=[], current_time=0

        # Проверяем что гравитация применяется
        self.assertGreater(self.player.velocity_y, 0)
        self.assertGreater(self.player.rect.y, initial_y)

    def test_player_collision(self):
        """Тест коллизии игрока с платформой"""
        # Платформа прямо под игроком
        platforms = [Platform(95, 360, 50, 20)]

        # Даем игроку упасть на платформу
        self.player.rect.y = 300
        for _ in range(10):  # Несколько обновлений для падения
            self.player.update(platforms, [], 0)  # enemies=[], current_time=0

        # Игрок должен быть на платформе
        self.assertTrue(self.player.on_ground)
        self.assertEqual(self.player.velocity_y, 0)

    def test_player_input_handling(self):
        """Тест обработки ввода игрока"""
        # Создаем mock для keys с достаточным размером
        keys = [0] * 512  # Создаем список "ненажатых" клавиш (достаточно большой)
        keys[pygame.K_LEFT] = 1  # Симулируем нажатие LEFT

        platforms = []  # Пустой список платформ для тестов
        self.player.handle_keys(keys, platforms)
        self.assertFalse(self.player.facing_right)

        # Тест движения вправо
        keys[pygame.K_LEFT] = 0
        keys[pygame.K_RIGHT] = 1

        self.player.handle_keys(keys, platforms)
        self.assertTrue(self.player.facing_right)


if __name__ == "__main__":
    unittest.main()
