# game/platform.py
import pygame
from .asset_loader import asset_loader

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type="grass", is_trap=False, is_door=False):
        super().__init__()
        
        self.platform_type = platform_type
        self.is_trap = is_trap
        self.is_door = is_door
        
        # 🔥 ИСПОЛЬЗУЕМ TILESET ДЛЯ ПОЛУЧЕНИЯ ИЗОБРАЖЕНИЯ
        self.image = self.get_tile_image(platform_type)
        if self.image:
            self.image = pygame.transform.scale(self.image, (width, height))
        else:
            # Заглушка если тайл не найден
            self.image = pygame.Surface((width, height))
            self.image.fill((100, 200, 100))  # Зеленый для платформ
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.has_collision = True
        
        # 🔥 СОЗДАЕМ СПЕЦИАЛЬНЫЕ COLLISION_RECT ДЛЯ РАЗНЫХ ТИПОВ
        self.collision_rect = self.create_collision_rect()
        
        # 🔥 ДЛЯ TRIANGLE СОЗДАЕМ МАСКУ ДЛЯ ТОЧНОЙ КОЛЛИЗИИ
        if platform_type == "triangle":
            self.collision_mask = self.create_triangle_mask()
    
    def create_collision_rect(self):
        """Создает специальные collision rect для разных типов платформ"""
        if self.platform_type.startswith("semitype"):
            # 🔥 ДЛЯ SEMITYPE: урезаем в 2 раза снизу (верхняя половина)
            return pygame.Rect(
                self.rect.x,
                self.rect.y, 
                self.rect.width,
                self.rect.height // 2  # Только верхняя половина
            )
        else:
            # 🔥 ДЛЯ ОСТАЛЬНЫХ: обычный rect
            return self.rect.copy()
    
    def create_triangle_mask(self):
        """Создает маску для треугольной коллизии (правый верхний → правый нижний → левый нижний)"""
        mask_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # 🔥 ТРЕУГОЛЬНИК: правый верхний → правый нижний → левый нижний
        points = [
            (self.rect.width, 0),           # Правый верхний угол
            (self.rect.width, self.rect.height),  # Правый нижний угол  
            (0, self.rect.height)           # Левый нижний угол
        ]
        pygame.draw.polygon(mask_surface, (255, 255, 255), points)
        
        return pygame.mask.from_surface(mask_surface)
    
    def check_collision(self, other_rect):
        """🔥 УНИВЕРСАЛЬНАЯ ПРОВЕРКА КОЛЛИЗИЙ"""
        if not self.has_collision:
            return False
            
        if self.platform_type == "triangle" and hasattr(self, 'collision_mask'):
            # 🔥 ДЛЯ TRIANGLE: используем маску для точной коллизии
            return self.check_triangle_collision(other_rect)
        else:
            # 🔥 ДЛЯ ОСТАЛЬНЫХ: используем collision_rect
            return self.collision_rect.colliderect(other_rect)
    
    def check_triangle_collision(self, other_rect):
        """Проверка коллизии с треугольником с использованием маски"""
        if not hasattr(self, 'collision_mask'):
            return False
            
        # Создаем маску для объекта
        other_surface = pygame.Surface((other_rect.width, other_rect.height), pygame.SRCALPHA)
        other_surface.fill((255, 255, 255))
        other_mask = pygame.mask.from_surface(other_surface)
        
        # Вычисляем смещение
        offset_x = other_rect.x - self.rect.x
        offset_y = other_rect.y - self.rect.y
        
        # Проверяем пересечение масок
        return self.collision_mask.overlap(other_mask, (offset_x, offset_y))
    
    def get_tile_image(self, platform_type):
        """🔥 ПОЛУЧАЕМ ТАЙЛ ИЗ TILESET ПО ТИПУ"""
        type_to_gid = {
            "grass1": 1,  
            "grass_half": 2,            
            "triangle": 25,
            "semitype1": 57,
            "semitype2": 49, 
            "semitype3": 41,
            "grass2": 9,
            "grass3": 89, 
            "grass4": 97,
            "grass5": 73,
            "grass6": 17,
            "box": 341
        }
        
        gid = type_to_gid.get(platform_type, 1)
        return asset_loader.get_tile_image(gid)
    
    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))
        
        # 🔥 ОТЛАДКА: показать collision_rect
        if hasattr(self, 'collision_mask'):
             
             pygame.draw.rect(screen, (255, 0, 0), camera.apply(self.collision_rect), 2)