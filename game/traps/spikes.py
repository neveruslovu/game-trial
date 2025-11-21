# game/traps/spikes.py
import pygame
from ..asset_loader import asset_loader

class Spikes(pygame.sprite.Sprite):
    def __init__(self, x, y, width=128, height=128):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.damage = 10  # Урон от шипов

        # Create a more accurate collision area for the spikes
        # Only the bottom part of the sprite actually contains spikes
        spike_height_ratio = 0.5  # Spikes only in bottom half
        self.collision_rect = pygame.Rect(
            x, 
            y + height * (1 - spike_height_ratio),  # Start from middle
            width, 
            height * spike_height_ratio  # Only bottom half
        )

        # Загрузка спрайта
        try:
            self.image = asset_loader.load_image("tiles/spikes.png", scale=1)
            self.image = pygame.transform.scale(self.image, (width, height))
        except:
            # Заглушка
            self.image = pygame.Surface((width, height))
            self.image.fill((255, 50, 50))
            # Рисуем шипы на заглушке
            spike_height = height // 2
            for i in range(0, width, width // 4):
                points = [
                    (i, height),
                    (i + width // 8, height - spike_height),
                    (i + width // 4, height)
                ]
                pygame.draw.polygon(self.image, (200, 30, 30), points)

    def check_collision(self, player):
        """Проверка столкновения с игроком"""
        # Use the more accurate collision rect
        if self.collision_rect.colliderect(player.get_actual_hitbox()) and player.is_alive:
            return True
        return False

    def draw(self, screen, camera):
        """Отрисовка шипов"""
        screen.blit(self.image, camera.apply(self.rect))
