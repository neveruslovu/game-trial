import unittest
import sys
import os
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from game.player import Player
from game.platform import Platform
from game.camera import Camera

# Удалите эту строку:
# from mocks import MockAssetLoader, MockCamera, MockLevel, MockImage

# Вместо этого создайте моки прямо в файле:
class MockImage:
    def __init__(self, width=50, height=50):
        self._width = width
        self._height = height
    
    def get_width(self): return self._width
    def get_height(self): return self._height
    def convert_alpha(self): return self

class MockAssetLoader:
    def load_image(self, name, scale=1):
        return MockImage()

class TestPlayer(unittest.TestCase):
    def setUp(self):
        pygame.init()
        # Подменяем asset_loader на mock
        import game.player
        self.original_loader = getattr(game.player, 'asset_loader', None)
        game.player.asset_loader = MockAssetLoader()
        self.player = Player(100, 300)
    
    def tearDown(self):
        # Восстанавливаем оригинальный asset_loader
        import game.player
        if self.original_loader:
            game.player.asset_loader = self.original_loader
        pygame.quit()
    
    def test_player_initialization(self):
        """Тест инициализации игрока"""
        self.assertEqual(self.player.rect.x, 100)
        self.assertEqual(self.player.rect.y, 300)
        self.assertEqual(self.player.speed, 5)
        self.assertFalse(self.player.is_jumping)
    
    def test_player_jump(self):
        """Тест прыжка игрока"""
        self.player.on_ground = True
        self.player.jump()
        self.assertEqual(self.player.velocity_y, -23)
        self.assertTrue(self.player.is_jumping)
    
    def test_player_movement(self):
        pass

class TestPlatform(unittest.TestCase):
    def setUp(self):
        pygame.init()
    
    def tearDown(self):
        pygame.quit()
    
    def test_platform_creation(self):
        pass
    
    def test_platform_draw(self):
        pass
    
        # Создаем mock camera с правильными методами
        

class TestCamera(unittest.TestCase):
    def setUp(self):
        pygame.init()
    
    def tearDown(self):
        pygame.quit()
    
    def test_camera_initialization(self):
        """Тест инициализации камеры"""
        # Создаем mock target
        class MockTarget:
            def __init__(self):
                self.rect = pygame.Rect(100, 100, 50, 50)
        
        target = MockTarget()
        screen_size = (800, 600)
        
        try:
            camera = Camera(target, screen_size)
            self.assertEqual(camera.offset.x, 0)
            self.assertEqual(camera.offset.y, 0)
            self.assertEqual(camera.screen_size, screen_size)
            success = True
        except Exception as e:
            success = False
            print(f"Ошибка инициализации камеры: {e}")
        
        self.assertTrue(success)
    
    def test_camera_update(self):
        """Тест обновления камеры"""
        class MockTarget:
            def __init__(self):
                self.rect = pygame.Rect(500, 300, 50, 50)
        
        target = MockTarget()
        screen_size = (800, 600)
        
        try:
            camera = Camera(target, screen_size)
            camera.update()
            # Камера должна следовать за игроком
            self.assertNotEqual(camera.offset.x, 0)
            self.assertNotEqual(camera.offset.y, 0)
            success = True
        except Exception as e:
            success = False
            print(f"Ошибка обновления камеры: {e}")
        
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()