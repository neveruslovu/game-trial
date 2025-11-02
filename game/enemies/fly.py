# game/enemies/fly.py
import pygame
from ..asset_loader import asset_loader
from ..health import HealthComponent

class Fly(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Загрузка спрайта
        try:
            self.image = asset_loader.load_image("enemies/fly.png", 0.6)
        except FileNotFoundError:
            # Заглушка если спрайт не загрузился
            self.image = pygame.Surface((40, 30))
            self.image.fill((200, 100, 200))  # Фиолетовый цвет
        
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Физика и AI
        self.speed = 80
        self.direction = 1
        self.velocity = pygame.math.Vector2(0, 0)
        self.facing_right = False
        self.start_x = x
        self.move_range = 600
        
        # Состояния
        self.health_component = HealthComponent(20) # У мух меньше здоровья
        self.is_invincible = False
        self.invincibility_timer = 0
        self.invincibility_duration = 0.5
        self.is_dead = False      
        self.death_timer = 0
        self.death_duration = 0.5
        self.will_die_after_hurt = False 
        self.is_hurt = False
        self.hurt_timer = 0
        self.hurt_duration = 0.3

        # Хитбокс
        self.hitbox = pygame.Rect(0, 0, 30, 25)
        self.show_hitbox = True
        
        print(f"🪰 Муха создана на позиции ({x}, {y})!")
    
    def update(self, dt, level):
        """Обновление мухи"""
        if self.is_dead:
            self.death_timer -= dt
            if self.death_timer <= 0:
                self.kill()
            return

        if self.will_die_after_hurt and not self.is_hurt:
            self.die()
            self.will_die_after_hurt = False
            return

        if self.is_invincible:
            self.invincibility_timer -= dt
            if self.invincibility_timer <= 0:
                self.is_invincible = False

        if self.is_hurt:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.is_hurt = False
                if self.will_die_after_hurt:
                    self.die()
                    self.will_die_after_hurt = False
                    return

        # Движение по горизонтали
        self.velocity.x = self.speed * self.direction
    
        # Применяем движение
        self.rect.x += self.velocity.x * dt

        # Обновляем направление
        if self.velocity.x > 0:
            self.facing_right = True
        elif self.velocity.x < 0:
            self.facing_right = False
    
        # Проверка выхода за границы диапазона
        if self.rect.x > self.start_x + self.move_range or self.rect.x < self.start_x:
            self.direction *= -1

    def take_damage(self, amount):
        """Получение урона с анимацией и неуязвимостью"""
        if self.is_invincible:      
            return False
        
        if self.is_dead:
            return False
            
        damaged = self.health_component.take_damage(amount)
        if damaged:
            self.is_hurt = True
            self.hurt_timer = self.hurt_duration
            
            self.is_invincible = True
            self.invincibility_timer = self.invincibility_duration
            
            if self.health_component.is_dead():
                self.will_die_after_hurt = True
        
        return damaged      
     
    def die(self):
        """Обрабатывает смерть мухи"""
        self.is_dead = True
        self.death_timer = self.death_duration
        self.velocity.x = 0
        # Загрузка спрайта смерти
        try:
            self.image = asset_loader.load_image("enemies/fly_dead.png", 0.6)
        except FileNotFoundError:
            pass # Если спрайт не найден, останется старый


    def draw(self, screen, camera):
        """Отрисовка мухи"""
        screen_rect = self.rect.move(-camera.offset.x, -camera.offset.y)
        
        # Отрисовка спрайта
        if self.facing_right:
            flipped_sprite = pygame.transform.flip(self.image, True, False)
            screen.blit(flipped_sprite, screen_rect)
        else:
            screen.blit(self.image, screen_rect)
        
        # Отрисовка хитбокса (для отладки)
        if self.show_hitbox:
            hitbox_rect = pygame.Rect(
                screen_rect.x + self.hitbox.x,
                screen_rect.y + self.hitbox.y,
                self.hitbox.width,
                self.hitbox.height
            )
            pygame.draw.rect(screen, (255, 0, 0), hitbox_rect, 2)