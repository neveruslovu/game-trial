import pygame
from .asset_loader import asset_loader
from game.assets.audio import AudioManager


class Player:
    class HealthComponent:
        def __init__(self, max_health):
            self.max_health = max_health
            self.current_health = max_health

        def take_damage(self, damage):
            """Наносит урон и возвращает True если урон был применен"""
            if self.current_health > 0:
                self.current_health -= damage
                if self.current_health < 0:
                    self.current_health = 0
                return True
            return False

        def heal(self, amount):
            """Восстанавливает здоровье"""
            self.current_health += amount
            if self.current_health > self.max_health:
                self.current_health = self.max_health

        def is_dead(self):
            """Проверяет, мертв ли игрок"""
            return self.current_health <= 0

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 80, 100)
        self.hitbox = pygame.Rect(10, 10, 60, 90)

        self.velocity_y = 0
        self.velocity_x = 0
        self.speed = 5
        self.jump_power = -23
        self.gravity = 0.8
        self.is_jumping = False
        self.on_ground = False
        self.facing_right = True
        self.show_hitbox = True

        # Система сбора предметов
        self.coins = 0
        self.keys = 0
        self.jewels = 0

        # 🔑 КЛЮЧИ ДЛЯ ЗАМКОВ
        self.has_yellow_key = False

        # Coyote Time
        self.coyote_time = 0.15
        self.time_since_ground = 0
        self.jump_buffer = 0
        self.jump_buffer_time = 0.1

        # Анимации
        self.current_state = "idle"
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.animation_timer = 0

        # Система урона
        self.is_invincible = False
        self.invincibility_timer = 0
        self.invincibility_duration = 1.0

        # Атака прыжком
        self.bounce_power = -12

        # Отскок при уроне
        self.knockback_power = 8
        self.knockback_duration = 0.3
        self.knockback_timer = 0
        self.is_knockback = False

        # Система смерти
        self.is_alive = True
        self.respawn_timer = 0
        self.respawn_duration = 2.0
        self.respawn_position = (x, y)

        # 🔥 ДОБАВЛЕНО: Переменные для предотвращения дрожания
        self.blocked_left = False
        self.blocked_right = False
        self.on_slope = False

        # Callback, который может быть установлен уровнем для обработки удара по ящику
        self.on_box_hit = None

        # Callback, который может быть установлен уровнем для обработки респавна игрока
        self.on_respawn = None

        self.health_component = self.HealthComponent(60)
        print(f"🎯 Player created at position: ({x}, {y})")

        # Загрузка спрайтов
        self.load_sprites()
        self.current_sprite = self.idle_sprite

        # Переменные для обработки столкновений
        self.old_x = x
        self.old_y = y

    def collect_yellow_key(self):
        """Отмечает, что игрок подобрал жёлтый ключ."""
        self.has_yellow_key = True
        print("🔑 Yellow key collected")

    def load_sprites(self):
        """Загружает все спрайты для анимаций"""
        self.idle_sprite = asset_loader.load_image("player/alienPink_front.png", 0.6)
        self.run_sprites = [
            asset_loader.load_image("player/alienPink_stand.png", 0.6),
            asset_loader.load_image("player/alienPink_walk1.png", 0.6),
            asset_loader.load_image("player/alienPink_walk2.png", 0.6),
        ]
        self.jump_sprite = asset_loader.load_image("player/alienPink_jump.png", 0.6)
        self.land_sprite = asset_loader.load_image("player/alienPink_duck.png", 0.6)

    def update_animation(self, moved):
        """Обновляет анимацию в зависимости от состояния игрока"""
        if not self.is_alive:
            return

        previous_state = self.current_state

        # Определяем новое состояние
        if not self.on_ground:
            self.current_state = "jump"
        elif previous_state == "jump" and self.on_ground:
            # Мгновенный переход из прыжка в приземление
            self.current_state = "land"
        elif moved and not self.is_knockback:
            self.current_state = "run"
        else:
            self.current_state = "idle"

        # Если состояние изменилось — сбрасываем кадр/таймер
        if previous_state != self.current_state:
            self.animation_frame = 0
            self.animation_timer = 0

        # Прогресс таймера анимации
        self.animation_timer += self.animation_speed

        if self.current_state == "run":
            # Бег — циклическая анимация
            if self.animation_timer >= 1:
                self.animation_frame = (self.animation_frame + 1) % len(
                    self.run_sprites
                )
                self.animation_timer = 0
            self.current_sprite = self.run_sprites[self.animation_frame]

        elif self.current_state == "idle":
            self.current_sprite = self.idle_sprite

        elif self.current_state == "jump":
            self.current_sprite = self.jump_sprite

        elif self.current_state == "land":
            # Приземление — показываем спрайт duck на короткое время, затем возвращаемся в idle
            self.current_sprite = self.land_sprite
            if self.animation_timer >= 0.2:
                self.current_state = "idle"
                self.current_sprite = self.idle_sprite
                self.animation_frame = 0
                self.animation_timer = 0

    def handle_landing_animation(self):
        """Обрабатывает завершение анимации приземления"""
        self.current_state = "idle"
        self.current_sprite = self.idle_sprite

    def update(self, platforms, enemies, current_time, traps=None):
        """Обновление состояния игрока с системой урона"""
        if not self.is_alive:
            self.respawn_timer -= 1 / 60
            if self.respawn_timer <= 0:
                self.respawn()
            return

        # Сохраняем старые позиции
        self.old_x = self.rect.x
        self.old_y = self.rect.y

        # Смерть при падении за карту
        if self.rect.y > 3000:
            self.health_component.current_health = 0
            self.die()

        # Проверка шипов
        if traps and not self.is_invincible and self.is_alive:
            self.check_trap_collisions(traps, current_time)

        # Таймер неуязвимости
        if self.is_invincible:
            self.invincibility_timer -= 1 / 60
            if self.invincibility_timer <= 0:
                self.is_invincible = False

        # Таймер отскока
        if self.is_knockback:
            self.knockback_timer -= 1 / 60
            if self.knockback_timer <= 0:
                self.is_knockback = False
                self.velocity_x = 0

        was_on_ground = self.on_ground

        # 🔥 ИСПРАВЛЕНИЕ: Обрабатываем горизонтальные столкновения для ОБЫЧНОГО движения
        if not self.is_knockback:
            self.handle_horizontal_collisions(platforms)

        # Применяем гравитацию
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Обрабатываем вертикальные столкновения
        self.handle_vertical_collisions(platforms)

        # Coyote Time
        if self.on_ground:
            self.time_since_ground = 0
        elif was_on_ground:
            self.time_since_ground = 0
        else:
            self.time_since_ground += 1 / 60

        # Автопрыжок по буферу
        if not self.is_knockback and self.jump_buffer > 0 and self.can_jump():
            self.jump()
            self.jump_buffer = 0

        # Проверка врагов
        self.check_enemy_collisions(enemies, current_time)

    def handle_horizontal_collisions(self, platforms):
        """Обрабатывает горизонтальные столкновения для ВСЕХ типов движения"""
        # 🔥 СБРАСЫВАЕМ ФЛАГИ БЛОКИРОВКИ ПЕРЕД ПРОВЕРКОЙ
        self.blocked_left = False
        self.blocked_right = False
        self.on_slope = False

        # Сначала обрабатываем все треугольные платформы, чтобы понять, стоим ли мы на склоне
        for platform in platforms:
            if hasattr(platform, "has_collision") and not platform.has_collision:
                continue
            if getattr(platform, "platform_type", None) != "triangle":
                continue
            if not self.check_collision(platform):
                continue

            self.on_slope = True
            # For horizontal movement on slopes, check if we should continue moving up
            self.handle_triangle_collision(platform, platforms)

            # If we're on a slope and moving horizontally, adjust vertical position
            player_hitbox = self.get_actual_hitbox()
            if self.on_ground and abs(self.velocity_x) > 0:
                # Calculate the expected Y position on the slope based on X position
                relative_x = (player_hitbox.centerx - platform.rect.left) / platform.rect.width
                relative_x = max(0.0, min(1.0, relative_x))

                # Calculate slope height at this position
                slope_height = relative_x * platform.rect.height
                expected_y = platform.rect.bottom - slope_height - self.hitbox.height - self.hitbox.y

                # If we're moving right and approaching the edge, look for next slope
                if relative_x > 0.7 and self.velocity_x > 0:
                    for next_platform in platforms:
                        if (getattr(next_platform, "platform_type", None) == "triangle" and 
                            abs(next_platform.rect.left - platform.rect.right) < 5):
                            # Found adjacent slope, adjust position to transition smoothly
                            next_relative_x = (player_hitbox.centerx - next_platform.rect.left) / next_platform.rect.width
                            next_relative_x = max(0.0, min(1.0, next_relative_x))
                            next_slope_height = next_relative_x * next_platform.rect.height
                            expected_y = next_platform.rect.bottom - next_slope_height - self.hitbox.height - self.hitbox.y
                            break

                # Smoothly adjust Y position to match slope
                if abs(self.rect.y - expected_y) < 20:  # Only adjust if difference is reasonable
                    self.rect.y = expected_y

        # Теперь обрабатываем остальные платформы
        for platform in platforms:
            # Пропускаем платформы без коллизий
            if hasattr(platform, "has_collision") and not platform.has_collision:
                continue
            if getattr(platform, "platform_type", None) == "triangle":
                continue

            if self.check_collision(platform):
                # 🔥 ИСПРАВЛЕНИЕ: Используем правильные границы для разных типов платформ
                if hasattr(platform, "collision_rect"):
                    platform_left = platform.collision_rect.left
                    platform_right = platform.collision_rect.right
                    platform_top = platform.collision_rect.top
                    platform_bottom = platform.collision_rect.bottom
                else:
                    platform_left = platform.rect.left
                    platform_right = platform.rect.right
                    platform_top = platform.rect.top
                    platform_bottom = platform.rect.bottom

                player_hitbox = self.get_actual_hitbox()

                # Only handle as horizontal collision if there's significant vertical overlap
                vertical_overlap = min(player_hitbox.bottom, platform_bottom) - max(player_hitbox.top, platform_top)

                if vertical_overlap > 5:  # Only if there's meaningful overlap
                    # 🔥 УЛУЧШЕННОЕ ОПРЕДЕЛЕНИЕ НАПРАВЛЕНИЯ
                    if self.velocity_x > 0 or (self.rect.x > self.old_x):  # Движение вправо
                        # Check for step-up (allow climbing small obstacles like slope tops)
                        step_height = 16  # Max pixels to step up
                        if self.on_slope:
                            step_height = max(step_height, self.hitbox.width)
                        if (
                            self.on_ground
                            and player_hitbox.bottom > platform_top
                            and (player_hitbox.bottom - platform_top) <= step_height
                        ):
                            self.rect.bottom = platform_top
                            # Don't stop horizontal movement
                        else:
                            # 🔥 Блокируем движение только если реально упираемся боком в платформу
                            if player_hitbox.bottom > platform_top:
                                # 🔥 ИСПРАВЛЕНИЕ: Используем реальный хитбокс для расчета
                                self.rect.right = platform_left + self.hitbox.x
                                self.velocity_x = 0  # 🔥 ОБНУЛЯЕМ СКОРОСТЬ ВМЕСТО ОТСКОКА
                                # 🔥 УСТАНАВЛИВАЕМ ФЛАГ БЛОКИРОВКИ
                                self.blocked_right = True

                    elif self.velocity_x < 0 or (
                        self.rect.x < self.old_x
                    ):  # Движение влево
                        # Check for step-up (allow climbing small obstacles like slope tops)
                        step_height = 16  # Max pixels to step up
                        if self.on_slope:
                            step_height = max(step_height, self.hitbox.width)
                        if (
                            self.on_ground
                            and player_hitbox.bottom > platform_top
                            and (player_hitbox.bottom - platform_top) <= step_height
                        ):
                            self.rect.bottom = platform_top
                            # Don't stop horizontal movement
                        else:
                            # 🔥 Блокируем движение только если реально упираемся боком в платформу
                            if player_hitbox.bottom > platform_top:
                                # 🔥 ИСПРАВЛЕНИЕ: Используем реальный хитбокс ДЛЯ расчета
                                self.rect.left = platform_right - self.hitbox.x
                                self.velocity_x = 0  # 🔥 ОБНУЛЯЕМ СКОРОСТЬ ВМЕСТО ОТСКОКА
                                # 🔥 УСТАНАВЛИВАЕМ ФЛАГ БЛОКИРОВКИ
                                self.blocked_left = True
                break

    def handle_vertical_collisions(self, platforms):
        """Обрабатывает вертикальные столкновения"""
        self.on_ground = False

        for platform in platforms:
            # Пропускаем платформы без коллизий
            if hasattr(platform, "has_collision") and not platform.has_collision:
                continue

            if self.check_collision(platform):
                # 🔥 ОСОБАЯ ОБРАБОТКА ДЛЯ ТРЕУГОЛЬНИКОВ
                if platform.platform_type == "triangle":
                    self.handle_triangle_collision(platform, platforms)
                    continue

                # 🔥 ИСПРАВЛЕНИЕ: Используем правильные границы для разных типов платформ
                if hasattr(platform, "collision_rect"):
                    platform_top = platform.collision_rect.top
                    platform_bottom = platform.collision_rect.bottom
                else:
                    platform_top = platform.rect.top
                    platform_bottom = platform.rect.bottom

                # 🔥 УЛУЧШЕННОЕ ОПРЕДЕЛЕНИЕ НАПРАВЛЕНИЯ
                if self.velocity_y > 0:  # Падение вниз
                    self.rect.bottom = platform_top
                    self.on_ground = True
                    self.is_jumping = False
                    self.velocity_y = 0
                    self.time_since_ground = 0

                elif self.velocity_y < 0:  # Движение вверх
                    # Ударились головой о нижнюю часть платформы
                    if getattr(platform, "platform_type", None) == "box" and callable(
                        getattr(self, "on_box_hit", None)
                    ):
                        try:
                            self.on_box_hit(platform)
                        except Exception as e:
                            print(f"[Player] on_box_hit callback failed: {e}")
                    self.rect.top = platform_bottom
                    self.velocity_y = 0
                break

    def handle_triangle_collision(self, triangle, platforms=None):
        """Обрабатывает столкновение с треугольной платформой (правый треугольник, подъём слева направо)"""
        self.on_slope = True
        player_hitbox = self.get_actual_hitbox()

        # Горизонтальная проекция игрока должна быть над треугольником
        player_center_x = player_hitbox.centerx
        triangle_left = triangle.rect.left
        triangle_right = triangle.rect.right
        triangle_bottom = triangle.rect.bottom

        # 🔥 FIX: More lenient bounds checking for smooth transitions
        # Increased tolerance when moving horizontally to allow smooth tile transitions
        bounds_tolerance = 10 if abs(self.velocity_x) > 0 else 5
        if player_center_x < triangle_left - bounds_tolerance or player_center_x > triangle_right + bounds_tolerance:
            return

        # Нормализованная позиция по X (0.0 - левая точка, 1.0 - правая)
        triangle_width = triangle.rect.width
        triangle_height = triangle.rect.height

        # Use center_x but clamp it to triangle bounds for calculation
        clamped_x = max(triangle_left, min(triangle_right, player_center_x))
        relative_x = (clamped_x - triangle_left) / triangle_width
        relative_x = max(0.0, min(1.0, relative_x))

        # Для тайла 'triangle' наклон поднимается слева направо:
        #   при x = left  → высота = 0   (у самого низа)
        #   при x = right → высота = H   (у самого верха)
        # ⇒ высота поверхности над нижней точкой:
        slope_height = relative_x * triangle_height
        surface_y = triangle_bottom - slope_height

        player_bottom = player_hitbox.bottom

        # 🔥 NEW: Check for adjacent slope tiles when near edges
        # This helps with smooth transitions between slope tiles
        look_ahead_distance = 20  # pixels to look ahead

        # Check if we're near the right edge and moving right
        if (relative_x > 0.8 and self.velocity_x > 0 and platforms):
            # Look for next triangle tile to the right
            next_tile_x = triangle_right
            next_tile_y = triangle_bottom

            # Find any triangle tile at this position
            for platform in platforms:
                if (platform.platform_type == "triangle" and 
                    abs(platform.rect.left - next_tile_x) < 5 and 
                    abs(platform.rect.bottom - next_tile_y) < 5):
                    # Found adjacent triangle tile, increase tolerance
                    look_ahead_distance = 30
                    break

        # 🔥 FIX: Adaptive tolerance at slope peak for smooth transition
        if relative_x > 0.85:
            tolerance = look_ahead_distance  # Use larger tolerance at peak or when transitioning
        else:
            tolerance = 5

        # 🔥 FIX: Only apply collision when falling (not jumping up)
        if player_bottom > surface_y - tolerance and self.velocity_y >= 0:
            # Don't snap if player is jumping high above the slope
            if player_bottom - surface_y > 30:
                return

            correction = player_bottom - surface_y
            # Сдвигаем прямоугольник игрока так, чтобы дно хитбокса легло на склон
            self.rect.y -= correction

            self.on_ground = True
            self.is_jumping = False
            self.velocity_y = 0
            self.time_since_ground = 0

    def get_actual_hitbox(self):
        """Возвращает актуальный хитбокс в мировых координатах"""
        return pygame.Rect(
            self.rect.x + self.hitbox.x,
            self.rect.y + self.hitbox.y,
            self.hitbox.width,
            self.hitbox.height,
        )

    def check_enemy_collisions(self, enemies, current_time):
        """Проверяет столкновения с врагами"""
        for enemy in enemies.sprites():
            if hasattr(enemy, "is_dead") and enemy.is_dead:
                continue
            if hasattr(enemy, "is_hurt") and enemy.is_hurt:
                continue

            if self.check_collision_with_enemy(enemy):
                collision_type = self.get_collision_type(enemy)

                if collision_type == "top":
                    self.kill_enemy(enemy)
                elif not self.is_invincible and self.is_alive:
                    self.take_damage(10, enemy)

    def get_collision_type(self, enemy):
        """Определяет тип столкновения с врагом"""
        if (
            self.velocity_y > 0
            and self.rect.bottom < enemy.rect.centery
            and self.rect.bottom > enemy.rect.top
        ):
            return "top"
        return "side"

    def kill_enemy(self, enemy):
        """Убивает врага"""
        enemy.take_damage(30)
        self.velocity_y = self.bounce_power

    def take_damage(self, damage, enemy):
        """Наносит урон игроку"""
        if not self.is_invincible and self.is_alive:
            damage_taken = self.health_component.take_damage(damage)

            if damage_taken:
                # Звук получения урона
                try:
                    AudioManager.get_instance().sfx.play("player_take_damage")
                except Exception as e:
                    print(f"[Audio][Player] take_damage sfx failed: {e}")

                self.is_invincible = True
                self.invincibility_timer = self.invincibility_duration
                self.apply_knockback(enemy)

                if self.health_component.current_health <= 0:
                    self.die()

    def apply_knockback(self, enemy):
        """Применяет отскок от врага"""
        if self.rect.centerx < enemy.rect.centerx:
            self.velocity_x = -self.knockback_power
        else:
            self.velocity_x = self.knockback_power

        self.velocity_y = -self.knockback_power * 0.7
        self.is_knockback = True
        self.knockback_timer = self.knockback_duration

    def die(self):
        """Обрабатывает смерть игрока"""
        # Звук смерти
        try:
            AudioManager.get_instance().sfx.play("player_death")
        except Exception as e:
            print(f"[Audio][Player] death sfx failed: {e}")

        self.is_alive = False
        self.respawn_timer = self.respawn_duration
        self.velocity_y = 0
        self.velocity_x = 0
        self.is_knockback = False
        self.is_invincible = False

    def respawn(self):
        """Возрождает игрока"""
        self.is_alive = True
        self.health_component.current_health = self.health_component.max_health
        self.rect.x = self.respawn_position[0]
        self.rect.y = self.respawn_position[1]
        self.velocity_y = 0
        self.velocity_x = 0
        self.is_invincible = True
        self.invincibility_timer = 3.0
        self.current_state = "idle"
        self.current_sprite = self.idle_sprite

        # Вызываем callback респавна, если он установлен (для возрождения врагов и т.д.)
        if callable(self.on_respawn):
            try:
                self.on_respawn()
            except Exception as e:
                print(f"[Player] on_respawn callback failed: {e}")

    def check_collision_with_enemy(self, enemy):
        """Проверка коллизии с врагом"""
        if hasattr(enemy, "is_dead") and enemy.is_dead:
            return False
        if hasattr(enemy, "is_hurt") and enemy.is_hurt:
            return False

        return self.get_actual_hitbox().colliderect(enemy.rect)

    def handle_event(self, event):
        """Обработка событий"""
        if not self.is_alive:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.is_knockback:
                self.jump_buffer = self.jump_buffer_time
        elif event.type == pygame.USEREVENT + 1:
            self.handle_landing_animation()
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)

    def handle_keys(self, keys, platforms):
        """🔥 ИСПРАВЛЕНИЕ: Теперь принимает platforms как параметр"""
        if not self.is_alive or self.is_knockback:
            return

        moved = False

        # 🔥 ИСПРАВЛЕНИЕ: ПРОВЕРЯЕМ БЛОКИРОВКУ ПЕРЕД ДВИЖЕНИЕМ
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not self.blocked_left:
            self.rect.x -= self.speed
            self.facing_right = False
            moved = True
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not self.blocked_right:
            self.rect.x += self.speed
            self.facing_right = True
            moved = True

        # 🔥 ВАЖНОЕ ИСПРАВЛЕНИЕ: Проверяем горизонтальные столкновения сразу после движения
        if moved:
            self.handle_horizontal_collisions(platforms)

        self.update_animation(moved)

    def can_jump(self):
        return (
            self.on_ground or self.time_since_ground < self.coyote_time
        ) and not self.is_jumping

    def jump(self):
        if self.can_jump():
            self.velocity_y = self.jump_power
            self.is_jumping = True
            self.on_ground = False
            self.time_since_ground = self.coyote_time
            # Звук прыжка
            try:
                AudioManager.get_instance().sfx.play("player_jump")
            except Exception as e:
                print(f"[Audio][Player] jump sfx failed: {e}")

    def check_collision(self, platform):
        """Проверка коллизии с платформой"""
        # Проверяем имеет ли платформа коллизии
        if hasattr(platform, "has_collision") and not platform.has_collision:
            return False

        # 🔥 ИСПОЛЬЗУЕМ НОВУЮ СИСТЕМУ КОЛЛИЗИЙ
        if hasattr(platform, "check_collision"):
            return platform.check_collision(self.get_actual_hitbox())
        else:
            # Фолбэк на старую систему
            return self.get_actual_hitbox().colliderect(platform.rect)

    def check_trap_collisions(self, traps, current_time):
        """Проверка столкновений с ловушками"""
        for trap in traps:
            if hasattr(trap, "check_collision") and trap.check_collision(self):
                self.take_damage_from_trap(trap.damage)

    def take_damage_from_trap(self, damage):
        """Получение урона от ловушки"""
        if not self.is_invincible and self.is_alive:
            damage_taken = self.health_component.take_damage(damage)

            if damage_taken:
                # Звук получения урона от ловушки (тот же, что и при ударе врага)
                try:
                    AudioManager.get_instance().sfx.play("player_take_damage")
                except Exception as e:
                    print(f"[Audio][Player] trap damage sfx failed: {e}")

                self.is_invincible = True
                self.invincibility_timer = self.invincibility_duration
                self.velocity_y = -8

                if self.health_component.current_health <= 0:
                    self.die()

    def draw(self, screen, camera):
        """Отрисовка игрока"""
        if not self.is_alive:
            return

        screen_x = self.rect.x - camera.offset.x
        screen_y = self.rect.y - camera.offset.y

        if self.is_invincible and int(self.invincibility_timer * 10) % 2 == 0:
            return

        if self.current_sprite:
            if not self.facing_right:
                flipped_sprite = pygame.transform.flip(self.current_sprite, True, False)
                screen.blit(flipped_sprite, (screen_x, screen_y))
            else:
                screen.blit(self.current_sprite, (screen_x, screen_y))
