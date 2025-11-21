import unittest
import sys
import os
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from game.player import Player


class MockImage:
    def __init__(self, width=50, height=50):
        self._width = width
        self._height = height
    
    def get_width(self):
        return self._width
    
    def get_height(self):
        return self._height
    
    def get_size(self):
        return (self._width, self._height)
    
    def convert_alpha(self):
        return self


class MockAssetLoader:
    def load_image(self, name, scale=1):
        return MockImage()


class TestEnemyRespawn(unittest.TestCase):
    def setUp(self):
        pygame.init()
        import game.player
        self.original_loader = getattr(game.player, 'asset_loader', None)
        game.player.asset_loader = MockAssetLoader()
    
    def tearDown(self):
        import game.player
        if self.original_loader:
            game.player.asset_loader = self.original_loader
        pygame.quit()
    
    def test_player_has_respawn_callback(self):
        """Тест что у игрока есть колбэк для респавна"""
        player = Player(100, 300)
        self.assertTrue(hasattr(player, 'on_respawn'))
        self.assertIsNone(player.on_respawn)
    
    def test_player_respawn_calls_callback(self):
        """Тест что респавн игрока вызывает колбэк"""
        player = Player(100, 300)
        
        # Устанавливаем флаг для проверки что callback был вызван
        callback_called = {'value': False}
        
        def mock_respawn_callback():
            callback_called['value'] = True
        
        player.on_respawn = mock_respawn_callback
        
        # Убиваем игрока
        player.die()
        self.assertFalse(player.is_alive)
        
        # Воскрешаем игрока
        player.respawn()
        self.assertTrue(player.is_alive)
        
        # Проверяем что callback был вызван
        self.assertTrue(callback_called['value'])
    
    def test_player_respawn_without_callback(self):
        """Тест что респавн работает без установленного колбэка"""
        player = Player(100, 300)
        
        # Убиваем игрока
        player.die()
        self.assertFalse(player.is_alive)
        
        # Воскрешаем игрока без callback - не должно быть ошибки
        player.respawn()
        self.assertTrue(player.is_alive)


if __name__ == '__main__':
    unittest.main()
