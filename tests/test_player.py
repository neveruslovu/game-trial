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

    def test_player_transitions_between_slope_tiles(self):
        """Игрок не должен упираться в стык двух наклонных тайлов"""
        slope_left = Platform(0, 400, 128, 128, "triangle")
        slope_right = Platform(128, 400, 128, 128, "triangle")
        platforms = [slope_left, slope_right]

        # Размещаем игрока почти у верхушки левого склона
        target_relative_x = 0.9
        desired_center_x = slope_left.rect.left + slope_left.rect.width * target_relative_x
        surface_y = slope_left.rect.bottom - slope_left.rect.height * target_relative_x

        self.player.rect.x = int(desired_center_x - self.player.hitbox.width / 2 - self.player.hitbox.x)
        self.player.rect.y = int(surface_y - self.player.hitbox.height - self.player.hitbox.y)
        self.player.on_ground = True

        previous_x = self.player.rect.x
        self.player.rect.x += self.player.speed
        self.player.velocity_x = self.player.speed
        self.player.handle_horizontal_collisions(platforms)

        self.assertGreater(self.player.rect.x, previous_x)
        self.assertFalse(self.player.blocked_right)


if __name__ == "__main__":
    unittest.main()
