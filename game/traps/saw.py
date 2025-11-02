# game/enemies/saw.py
import pygame
from ..asset_loader import asset_loader

class Saw(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Загрузка спрайта
        try:
            self.image = asset_loader.load_image("enemies/sawHalf.png", 1)
        except:
            # Заглушка если спрайт не загрузился
            self.image = pygame.Surface((50, 50))
            self.image.fill((100, 100, 100))  # Серый цвет
            pygame.draw.circle(self.image, (200, 200, 200), (25, 25), 20)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Физика и AI
        self.speed = 60
        self.direction = 1
        self.velocity = pygame.math.Vector2(0, 0)
        self.rotation_angle = 0
        self.rotation_speed = 360  # градусов в секунду
        
        # Хитбокс
        self.hitbox = pygame.Rect(10, 10, 30, 30)
        self.show_hitbox = True
        print(f"🔄 Пила создана на позиции ({x}, {y})!")
    
    def update(self, dt, level):
        """Обновление пилы"""

    
    def draw(self, screen, camera):
        """Отрисовка пилы с вращением"""
        screen_rect = self.rect.move(-camera.offset.x, -camera.offset.y)
        
        # Вращаем спрайт
        rotated_sprite = pygame.transform.rotate(self.image, self.rotation_angle)
        rotated_rect = rotated_sprite.get_rect(center=screen_rect.center)
        
        screen.blit(rotated_sprite, rotated_rect)
        
        # Отрисовка хитбокса (для отладки)
        if self.show_hitbox:
            hitbox_rect = pygame.Rect(
                screen_rect.x + self.hitbox.x,
                screen_rect.y + self.hitbox.y,
                self.hitbox.width,
                self.hitbox.height
            )
            pygame.draw.rect(screen, (255, 0, 0), hitbox_rect, 2)