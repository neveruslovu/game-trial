import pygame
from ..health import HealthComponent
from ..asset_loader import asset_loader


class Slime(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # 🎨 ЗАГРУЗКА 4 СПРАЙТОВ СЛАЙМА
        self.load_sprites()
        self.current_sprite = self.idle_sprite

        # Анимационные переменные
        self.current_state = "idle"  # idle, move, hurt, dead
        self.animation_frame = 0
        self.animation_speed = 0.15
        self.animation_timer = 0

        # Состояния
        self.is_hurt = False
        self.hurt_timer = 0
        self.hurt_duration = 0.5  # 500ms анимации получения урона

        # ⚔️ СИСТЕМА НЕУЯЗВИМОСТИ ДЛЯ ВРАГОВ
        self.is_invincible = False
        self.invincibility_timer = 0
        self.invincibility_duration = (
            1.0  # 1 секунда неуязвимости после получения урона
        )

        # 💀 СИСТЕМА СМЕРТИ
        self.is_dead = False
        self.death_timer = 0
        self.death_duration = 1.0  # 1 секунда анимации смерти

        # 🔥 НОВАЯ ПЕРЕМЕННАЯ: отложенная смерть
        self.will_die_after_hurt = False

        # Графика - используем загруженный спрайт
        if self.current_sprite:
            self.image = self.current_sprite
            self.rect = self.image.get_rect(topleft=(x, y))
            # Хитбокс относительно РЕАЛЬНОГО размера спрайта
            sprite_width, sprite_height = self.image.get_size()
            self.hitbox = pygame.Rect(
                (sprite_width - 20) // 2,  # Центрируем по горизонтали
                (sprite_height + 13) // 2,  # Центрируем по вертикали
                22,
                22,
            )
        else:
            self.image = pygame.Surface((34, 24))
            self.rect = self.image.get_rect(topleft=(x, y))
            self.hitbox = pygame.Rect(0, 0, 20, 20)

        self.show_hitbox = True

        # Базовая физика
        self.health_component = HealthComponent(30)
        self.speed = 40
        self.direction = 1
        self.velocity = pygame.math.Vector2(0, 0)
        self.gravity = 1500
        self.facing_right = True

    def load_sprites(self):
        """Загружает 4 спрайта для анимаций слайма"""
        try:
            # 🎨 4 ОСНОВНЫХ СПРАЙТА
            self.idle_sprite = asset_loader.load_image(
                "enemies/slimePurple.png", 0.6
            )  # стоит
            self.move_sprite = asset_loader.load_image(
                "enemies/slimePurple_move.png", 0.6
            )  # движется
            self.hurt_sprite = asset_loader.load_image(
                "enemies/slimePurple_hit.png", 0.6
            )  # получил урон
            self.dead_sprite = asset_loader.load_image(
                "enemies/slimePurple_dead.png", 0.6
            )  # умер

            print("🎨 4 спрайта слайма загружены успешно!")

        except Exception as e:
            print(f"❌ Ошибка загрузки спрайтов слайма: {e}")
            # Заглушки если спрайты не загрузились
            self.create_placeholder_sprites()
        self.current_sprite = self.idle_sprite if hasattr(self, "idle_sprite") else None
        if self.current_sprite is None:
            print("⚠️ ВНИМАНИЕ: current_sprite is None после загрузки!")
            self.create_placeholder_sprites()
            self.current_sprite = self.idle_sprite

    def create_placeholder_sprites(self):
        """Создает простые спрайты для тестирования"""
        self.idle_sprite = self.create_colored_surface((100, 100, 200))  # Синий - стоит
        self.move_sprite = self.create_colored_surface(
            (80, 80, 180)
        )  # Темно-синий - движется
        self.hurt_sprite = self.create_colored_surface(
            (255, 100, 100)
        )  # Красный - получил урон
        self.dead_sprite = self.create_colored_surface((50, 50, 50))  # Темный - умер
        self.current_sprite = self.idle_sprite
        self.image = self.current_sprite  # ✅ ВАЖНО!

    def create_colored_surface(self, color):
        """Создает цветную поверхность для тестирования (как у fly: всегда валидный спрайт)"""
        surf = pygame.Surface((40, 30), pygame.SRCALPHA)
        surf.fill(color)
        return surf

    def update_animation(self, dt):
        """Обновляет анимацию в зависимости от состояния"""
        previous_state = self.current_state

        # Определяем текущее состояние
        if self.is_dead:
            self.current_state = "dead"
            print(f"💀 Анимация смерти: {self.death_timer:.2f} сек осталось")
        elif self.is_hurt:
            self.current_state = "hurt"
            print(f"💥 Анимация удара: {self.hurt_timer:.2f} сек осталось")
        elif abs(self.velocity.x) > 0.1:  # Движется
            self.current_state = "move"
        else:
            self.current_state = "idle"

        # Если состояние изменилось, сбрасываем анимацию
        if previous_state != self.current_state:
            self.animation_frame = 0
            self.animation_timer = 0
            print(
                f"🔄 Смена состояния слайма: {previous_state} -> {self.current_state}"
            )

        # 🎨 ПРОСТАЯ СИСТЕМА АНИМАЦИЙ - меняем спрайты по состоянию
        if self.current_state == "idle":
            self.current_sprite = self.idle_sprite

        elif self.current_state == "move":
            # 🔥 ПРОСТАЯ ПУЛЬСАЦИЯ для движения (без дополнительных кадров)
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                # Чередуем между idle и move спрайтом для эффекта движения
                if self.current_sprite == self.idle_sprite:
                    self.current_sprite = self.move_sprite
                else:
                    self.current_sprite = self.idle_sprite
                self.animation_timer = 0

        elif self.current_state == "hurt":
            self.current_sprite = self.hurt_sprite

        elif self.current_state == "dead":
            self.current_sprite = self.dead_sprite

        # Обновляем основное изображение
        self.image = self.current_sprite

    def update(self, dt, level):
        """Обновление слайма с анимациями"""
        # 💀 Если слайм мертв, обрабатываем анимацию смерти
        if self.is_dead:
            self.death_timer -= dt
            if self.death_timer <= 0:
                self.kill()
                print("💀 Слайм умер и удален!")
            else:
                self.update_animation(dt)
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
                    print(
                        "💀 Немедленно запускаем смерть после завершения анимации удара"
                    )
                    self.die()
                    self.will_die_after_hurt = False
                    return

        # Применяем гравитацию
        self.velocity.y += self.gravity * dt

        # Движение по горизонтали
        self.velocity.x = self.speed * self.direction

        # Сохраняем старую позицию
        old_x, old_y = self.rect.x, self.rect.y

        # Движение
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt

        # Обновляем направление взгляда
        if self.velocity.x > 0:
            self.facing_right = True
        elif self.velocity.x < 0:
            self.facing_right = False

        # Обновление здоровья
        self.health_component.update(dt)

        # 🎨 Обновляем анимацию
        self.update_animation(dt)

    def take_damage(self, amount):
        """Получение урона с анимацией и неуязвимостью"""
        # 🔥 ПРОВЕРЯЕМ НЕУЯЗВИМОСТЬ
        if self.is_invincible:
            print("🛡️ Слайм неуязвим, урон заблокирован")
            return False
        if self.is_dead:
            print("💀 Слайм уже мертв, урон невозможен")
            return False

        damaged = self.health_component.take_damage(amount)
        if damaged:
            print(
                f"💥 Слайм получил {amount} урона! Осталось HP: {self.health_component.current_health}"
            )

            # 🎨 Включаем анимацию получения урона
            self.is_hurt = True
            self.hurt_timer = self.hurt_duration

            # ⚔️ Включаем неуязвимость
            self.is_invincible = True
            self.invincibility_timer = self.invincibility_duration

            # Сбрасываем анимацию для принудительного показа hurt спрайта
            self.current_state = "hurt"
            self.animation_frame = 0
            self.animation_timer = 0

            # 💀 ПРОВЕРКА СМЕРТИ - но НЕ запускаем смерть сразу
            if self.health_component.is_dead():
                print(
                    "💀 Слайм получил смертельный урон, но сначала покажем анимацию удара"
                )
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

        print(f"💀 Запущена анимация смерти на {self.death_duration} секунд")

    def draw(self, screen, camera):
        """Отрисовка слайма"""
        screen_x = self.rect.x - camera.offset.x
        screen_y = self.rect.y - camera.offset.y

        # Отрисовка спрайта
        if self.current_sprite:
            if not self.facing_right:
                flipped_sprite = pygame.transform.flip(self.current_sprite, True, False)
                screen.blit(flipped_sprite, (screen_x, screen_y))
            else:
                screen.blit(self.current_sprite, (screen_x, screen_y))
        else:
            pygame.draw.rect(screen, (255, 0, 0), (screen_x, screen_y, 40, 60))

        # Отрисовка хитбокса (для отладки)
        if self.show_hitbox:
            hitbox_rect = pygame.Rect(
                screen_x + self.hitbox.x,
                screen_y + self.hitbox.y,
                self.hitbox.width,
                self.hitbox.height,
            )
            pygame.draw.rect(screen, (255, 0, 0), hitbox_rect, 2)
