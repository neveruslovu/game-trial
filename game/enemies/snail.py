# game/enemies/snail.py
import pygame
from ..asset_loader import asset_loader
from ..health import HealthComponent
class Snail(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Загрузка спрайта
        try:
            self.image = asset_loader.load_image("enemies/snail.png", 0.6)
        except FileNotFoundError:
            # Заглушка если спрайт не загрузился
            self.image = pygame.Surface((40, 30))
            self.image.fill((150, 75, 0))  # Коричневый цвет
        
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Физика и AI
        self.speed = 40  # Улитки медленнее слаймов
        self.direction = 1
        self.velocity = pygame.math.Vector2(0, 0)
        self.gravity = 1500
        self.facing_right = True
        
        # Состояния
        self.health_component = HealthComponent(30)
        self.is_invincible = False
        self.invincibility_timer = 0
        self.invincibility_duration = 1.0  # 1 секунда неуязвимости после получения урона
        self.is_dead = False      
        self.death_timer = 0
        self.death_duration = 1.0  # 1 секунда анимации смерти       
        # 🔥 НОВАЯ ПЕРЕМЕННАЯ: отложенная смерть
        self.will_die_after_hurt = False 
        self.is_hurt = False
        self.hurt_timer = 0
        self.hurt_duration = 0.5  # 500ms анимации получения урона

        # Хитбокс
        self.hitbox = pygame.Rect(0, 0, 30, 25)
        self.show_hitbox = True
        
        print(f"🐌 Улитка создана на позиции ({x}, {y})!")
    
    def update(self, dt, level):
        """Обновление улитки"""
        if self.is_dead:
            self.death_timer -= dt
            if self.death_timer <= 0:
                self.kill()
                print("💀 Слайм умер и удален!")
            
            return

        # 🔥 ПРОВЕРЯЕМ НУЖНО ЛИ ЗАПУСТИТЬ СМЕРТЬ ПОСЛЕ АНИМАЦИИ УДАРА
        if self.will_die_after_hurt and not self.is_hurt:
            print("💀 Запускаем смерть после завершения анимации удара")
            self.die()
            self.will_die_after_hurt = False
            return

        # ⚔️ Обновляем таймер неуязвимости
        if self.is_invincible:
            self.invincibility_timer -= dt
            if self.invincibility_timer <= 0:
                self.is_invincible = False
                print("🛡️ Неуязвимость слайма закончилась")

        # 🎨 Обновляем анимацию получения урона
        if self.is_hurt:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.is_hurt = False
                print("🎨 Анимация удара завершена")
                if self.will_die_after_hurt:
                    print("💀 Немедленно запускаем смерть после завершения анимации удара")
                    self.die()
                    self.will_die_after_hurt = False
                    return
        # Применяем гравитацию
        self.velocity.y += self.gravity * dt
    
        # Движение по горизонтали
        self.velocity.x = self.speed * self.direction
    
        
    
        # Применяем движение
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt
    
        # Обновляем направление
        if self.velocity.x > 0:
            self.facing_right = True
        elif self.velocity.x < 0:
            self.facing_right = False
    
        # Проверка выхода за границы уровня
        level_width = level.width
        if self.rect.right > level_width - 50 or self.rect.left < 50:
            self.direction *= -1

        # Обновление здоровья
        self.health_component.update(dt)

    def take_damage(self, amount):
        """Получение урона с анимацией и неуязвимостью"""
        # 🔥 ПРОВЕРЯЕМ НЕУЯЗВИМОСТЬ
        if self.is_invincible:      
            return False
        
        if self.is_dead:
            return False
            
        damaged = self.health_component.take_damage(amount)
        if damaged:
            print(f"💥 Слайм получил {amount} урона! Осталось HP: {self.health_component.current_health}")
            
            
            
            # ⚔️ Включаем неуязвимость
            self.is_invincible = True
            self.invincibility_timer = self.invincibility_duration
            
            
            
            # 💀 ПРОВЕРКА СМЕРТИ - но НЕ запускаем смерть сразу
            if self.health_component.is_dead():
                print("💀 Слайм получил смертельный урон, но сначала покажем анимацию удара")
                # 🔥 УСТАНАВЛИВАЕМ ФЛАГ ЧТО СЛАЙМ УМРЕТ ПОСЛЕ АНИМАЦИИ УДАРА
                self.will_die_after_hurt = True
            else:
                print("🎨 Слайм получил урон, но выжил")
        
        return damaged      
     
    def die(self):
        """Обрабатывает смерть слайма"""
        self.is_dead = True
        self.death_timer = self.death_duration
        self.velocity.x = 0
        self.velocity.y = 0


    def draw(self, screen, camera):
        """Отрисовка улитки"""
        screen_rect = self.rect.move(-camera.offset.x, -camera.offset.y)
        
        # Отрисовка спрайта
        if not self.facing_right:
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