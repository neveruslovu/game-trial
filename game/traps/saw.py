# game/enemies/saw.py
import pygame
from ..asset_loader import asset_loader


class Saw(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Загрузка анимации
        self.animation_frames = []
        try:
            # Загружаем оба кадра анимации
            frame1 = asset_loader.load_image("enemies/sawHalf.png", 1)
            frame2 = asset_loader.load_image("enemies/sawHalf_move.png", 1)
            self.animation_frames.append(frame1)
            self.animation_frames.append(frame2)
            print(f"✅ Загружено {len(self.animation_frames)} кадров анимации пилы")
        except FileNotFoundError as e:
            print(f"❌ Ошибка загрузки спрайтов пилы: {e}")
            # Заглушка если спрайты не загрузились
            fallback_surface = pygame.Surface((50, 50))
            fallback_surface.fill((100, 100, 100))
            pygame.draw.circle(fallback_surface, (200, 200, 200), (25, 25), 20)
            self.animation_frames.append(fallback_surface)
            self.animation_frames.append(fallback_surface)

        self.current_frame = 0
        self.image = self.animation_frames[self.current_frame]
        self.image_rect = self.image.get_rect(topleft=(x, y))

        # Создаем уменьшенный хитбокс - в 2 раза меньше, центрированный и опущенный
        smaller_size = (self.image_rect.width // 2, self.image_rect.height // 2)
        offset_x = (self.image_rect.width - smaller_size[0]) // 2
        offset_y = (self.image_rect.height - smaller_size[1]) // 2
        # Опускаем хитбокс на 10 пикселей вниз
        vertical_offset = 40
        self.rect = pygame.Rect(
            x + offset_x,
            y + offset_y + vertical_offset,
            smaller_size[0],
            smaller_size[1],
        )

        # Анимация
        self.animation_speed = 0.1  # время между кадрами
        self.animation_timer = 0

        # Физика и AI (без вращения)
        self.speed = 60
        self.direction = 1
        self.velocity = pygame.math.Vector2(0, 0)
        self.damage = 10  # Урон пилы

        # Хитбокс
        self.hitbox = pygame.Rect(10, 40, 30, 30)
        self.show_hitbox = True
        print(f"🔄 Пила создана на позиции ({x}, {y})!")

    def update(self, dt, level):
        """Обновление пилы"""
        # Обновление анимации
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            print(f"🔄 Смена кадра пилы: {self.current_frame}")  # Отладка

        # Обновляем изображение с текущим кадром
        self.image = self.animation_frames[self.current_frame]

    def check_collision(self, player):
        """Проверка столкновения с игроком"""
        if self.rect.colliderect(player.rect) and player.is_alive:
            return True
        return False

    def draw(self, screen, camera):
        """Отрисовка пилы"""
        # Отрисовка изображения по его оригинальному rect
        image_screen_rect = self.image_rect.move(-camera.offset.x, -camera.offset.y)
        screen.blit(self.image, image_screen_rect)

        # Отрисовка уменьшенного хитбокса (для отладки)
        if self.show_hitbox:
            hitbox_screen_rect = self.rect.move(-camera.offset.x, -camera.offset.y)
            pygame.draw.rect(screen, (255, 0, 0), hitbox_screen_rect, 2)
