# game/levels/level1.py
import pygame
import base64
import zlib
import os
from ..platform import Platform
from game.assets.audio import AudioManager
from ..enemies.slime import Slime
from ..enemies.snail import Snail
from ..enemies.fly import Fly
from ..items.items import Item
from ..decorations import Decoration, ExitDoor
from ..asset_loader import asset_loader
from ..traps.saw import Saw
from ..traps.spikes import Spikes


def default_level_complete_handler(level_name):
    """Простой обработчик завершения уровня (можно заменить снаружи)."""
    print(f"✅ Level '{level_name}' completed (default handler).")


class Level:
    def __init__(self, name):
        print(f"🗺️ Creating level: {name}")

        self.name = name
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
        self.traps = pygame.sprite.Group()
        self.decorations = pygame.sprite.Group()
        self.exit_doors = pygame.sprite.Group()

        # Флаг завершения уровня и callback
        self.completed = False
        self.on_level_complete = default_level_complete_handler

        # Загрузка фона
        original_bg = asset_loader.load_image("backgrounds/colored_grass.png", 1)
        self.background = pygame.transform.scale(original_bg, (1400, 800))
        self.player = None
        self.player_spawn_point = (0, 1280)  # Из TMX объекта
        self.width = 30 * 128  # 3840
        self.height = 20 * 128  # 2560

        # 🔄 НОВОЕ: Хранение начальных данных врагов для респавна
        self.initial_enemy_data = []

        # 🔥 ЗАГРУЗКА TILESETS - ОБНОВЛЕННЫЕ ПУТИ
        self.load_tilesets()
        self.load_from_xml()
        print(f"🗺️ Уровень '{name}' создан! Спавн игрока: {self.player_spawn_point}")

    def load_tilesets(self):
        """Загрузка всех tilesets из TMX"""
        print("🔄 Загрузка tilesets...")

        # 🔥 ОБНОВЛЕННЫЕ ПУТИ - БЕЗ ldesign/
        tilesets_data = [
            ("Spritesheets/spritesheet_ground.png", 1, 128, 128),
            ("Spritesheets/spritesheet_items.png", 129, 128, 128),
            ("Spritesheets/spritesheet_players.png", 161, 128, 128),
            ("Spritesheets/spritesheet_tiles.png", 289, 128, 128),
            ("Spritesheets/spritesheet_enemies.png", 417, 128, 128),
            ("Spritesheets/spritesheet_hud.png", 522, 128, 128),
        ]

        for path, firstgid, tilewidth, tileheight in tilesets_data:
            asset_loader.load_tileset(path, firstgid, tilewidth, tileheight)

    def set_player(self, player):
        """Установить ссылку на игрока и сбросить состояние врагов при новом запуске уровня"""
        self.player = player
        if self.player:
            # Позиция и респаун игрока
            self.player.rect.x = self.player_spawn_point[0]
            self.player.rect.y = self.player_spawn_point[1]
            self.player.respawn_position = self.player_spawn_point

            # Callback для удара игроком по ящику box (спавн монеты)
            if hasattr(self.player, "on_box_hit"):
                self.player.on_box_hit = self.spawn_coin_from_box

            # Callback для респавна игрока (возрождение врагов)
            if hasattr(self.player, "on_respawn"):
                self.player.on_respawn = self.respawn_killed_enemies

            # Жёсткий сброс состояния всех врагов при каждом New Game
            for enemy in self.enemies:
                # Сброс скоростей
                if hasattr(enemy, "velocity"):
                    enemy.velocity.x = 0
                    enemy.velocity.y = 0

                # Сброс флагов состояния (если есть)
                for attr in (
                    "is_dead",
                    "is_hurt",
                    "is_invincible",
                    "will_die_after_hurt",
                ):
                    if hasattr(enemy, attr):
                        setattr(enemy, attr, False)

                if hasattr(enemy, "invincibility_timer"):
                    enemy.invincibility_timer = 0
                if hasattr(enemy, "hurt_timer"):
                    enemy.hurt_timer = 0
                if hasattr(enemy, "death_timer"):
                    enemy.death_timer = 0

                # Специфические настройки для типов
                from ..enemies.slime import Slime as _SlimeType
                from ..enemies.snail import Snail as _SnailType

                if isinstance(enemy, _SlimeType):
                    enemy.direction = 1
                    enemy.facing_right = True
                    enemy.current_state = "idle"
                    if hasattr(enemy, "idle_sprite"):
                        enemy.current_sprite = enemy.idle_sprite
                        enemy.image = enemy.current_sprite

                elif isinstance(enemy, _SnailType):
                    enemy.direction = 1
                    enemy.facing_right = False

                # 🔥 FIX: Force image refresh and validate
                if (
                    hasattr(enemy, "current_sprite")
                    and enemy.current_sprite is not None
                ):
                    enemy.image = enemy.current_sprite

                # Убедимся что у врага есть изображение
                if not hasattr(enemy, "image") or enemy.image is None:
                    print(
                        f"⚠️ У врага {enemy.__class__.__name__} нет изображения! Создаём placeholder..."
                    )
                    if hasattr(enemy, "create_placeholder_sprites"):
                        enemy.create_placeholder_sprites()
                        enemy.current_sprite = enemy.idle_sprite
                        enemy.image = enemy.current_sprite

            # Обновим анимации после сброса
            for enemy in self.enemies:
                if hasattr(enemy, "update_animation"):
                    enemy.update_animation(0)

    def spawn_coin_from_box(self, box_platform):
        """При ударе по ящику box создаёт монету, уничтожает ящик и заставляет монету падать на землю."""
        if not box_platform or getattr(box_platform, "platform_type", None) != "box":
            return

        # Каждый ящик должен выдавать монету только один раз, пока уровень не будет пересоздан
        if getattr(box_platform, "coin_spawned", False):
            return

        box_rect = box_platform.rect

        # Найдём первую твёрдую платформу под ящиком, чтобы знать, где монета должна приземлиться
        ground_y = None
        for platform in self.platforms:
            if platform is box_platform:
                continue
            if not getattr(platform, "has_collision", True):
                continue

            # Горизонтальное пересечение
            if (
                platform.rect.right <= box_rect.left
                or platform.rect.left >= box_rect.right
            ):
                continue

            # Платформа должна находиться ниже низа ящика
            if platform.rect.top >= box_rect.bottom:
                if ground_y is None or platform.rect.top < ground_y:
                    ground_y = platform.rect.top

        # На всякий случай, если не нашли платформу (не должно случиться на нормальной карте)
        if ground_y is None:
            ground_y = box_rect.bottom + 5 * 128

        coin = Item(
            box_rect.x,
            box_rect.y,
            box_rect.width,
            box_rect.height,
            "coin",
        )

        # Стартуем монету снизу ящика и даём ей цель падения до земли
        coin.rect.bottom = box_rect.bottom
        coin.fall_to_ground_y = ground_y
        coin.fall_speed = 0.0

        self.items.add(coin)
        box_platform.coin_spawned = True

        # Удаляем ящик: он считается разрушенным и больше не блокирует движение
        try:
            self.platforms.remove(box_platform)
        except ValueError:
            # Если ящик уже удалён из группы — просто игнорируем
            pass

        # Небольшой звуковой эффект (используем тот же, что и для сбора монеты)
        try:
            audio = AudioManager.get_instance()
            if audio:
                audio.sfx.play("player_collect_coin")
        except Exception as e:
            print(f"[Audio][Level1] spawn_coin_from_box sfx failed: {e}")

    def decode_layer_data(self, encoded_data):
        """Декодирование данных слоя тайлов из base64+zlib"""
        try:
            encoded_data = encoded_data.strip().replace("\n", "").replace("\r", "")
            decoded = base64.b64decode(encoded_data)
            decompressed = zlib.decompress(decoded)

            tile_data = []
            for i in range(0, len(decompressed), 4):
                tile_gid = int.from_bytes(decompressed[i : i + 4], byteorder="little")
                tile_data.append(tile_gid)

            return tile_data
        except Exception as e:
            print(f"❌ Ошибка декодирования слоя: {e}")
            return []

    def load_from_xml(self):
        """Загрузка уровня из XML данных TMX"""
        try:
            # 🔥 ЗАГРУЗКА ВСЕХ СЛОЕВ ИЗ TMX
            self.load_ground_layer()
            self.load_semiground_layer()
            self.load_triangleleft_layer()
            self.load_traps_layer()
            self.load_decoration_layer()
            self.load_objects_from_xml()

            print("✅ Все слои TMX загружены!")

        except Exception as e:
            print(f"❌ Ошибка загрузки уровня: {e}")
            import traceback

            traceback.print_exc()
            self.create_fallback_level()

    def load_ground_layer(self):
        """Загрузка основного слоя земли"""
        print("🔄 Загрузка ground layer...")
        ground_layer_data = "eJxjYBgFo2AUjHTASWdzYeJMJJqXCNWLD3tCzcUmx4RGg3AkiW4YqUCQARJejFA+OWmGkbASOIDFNRMSRo87YjGp6WwUjAJqAAC+IgLF"
        tile_data = self.decode_layer_data(ground_layer_data)

        for y in range(20):
            for x in range(30):
                tile_index = y * 30 + x
                if tile_index < len(tile_data):
                    tile_gid = tile_data[tile_index]

                    if tile_gid != 0:  # Есть тайл
                        platform_type = self.get_platform_type_by_gid(tile_gid)

                        platform = Platform(x * 128, y * 128, 128, 128, platform_type)
                        self.platforms.add(platform)

        print(f"✅ Ground layer: {len(self.platforms)} платформ")

    def load_semiground_layer(self):
        """Загрузка слоя semiground"""
        print("🔄 Загрузка semiground layer...")
        semiground_data = (
            "eJxjYBjawBKIDYFYc6AdQgKAuZnaamkJKAnnoRJHtHAnPf0+VMJ5FIyCUTAKRgIAAN5vBEc="
        )
        tile_data = self.decode_layer_data(semiground_data)

        for y in range(20):
            for x in range(30):
                tile_index = y * 30 + x
                if tile_index < len(tile_data):
                    tile_gid = tile_data[tile_index]

                    if tile_gid != 0:
                        platform_type = self.get_platform_type_by_gid(tile_gid)
                        platform = Platform(x * 128, y * 128, 128, 128, platform_type)
                        self.platforms.add(platform)

    def load_triangleleft_layer(self):
        """Загрузка слоя triangleleft"""
        print("🔄 Загрузка triangleleft layer...")
        triangleleft_data = "eJxjYBgFo2AUjALqA8mBdsAoGAWjYBQMIAAAhsQAGg=="
        tile_data = self.decode_layer_data(triangleleft_data)

        for y in range(20):
            for x in range(30):
                tile_index = y * 30 + x
                if tile_index < len(tile_data):
                    tile_gid = tile_data[tile_index]

                    if tile_gid != 0:
                        platform_type = self.get_platform_type_by_gid(tile_gid)
                        platform = Platform(x * 128, y * 128, 128, 128, platform_type)
                        self.platforms.add(platform)

    def load_traps_layer(self):
        """Загрузка слоя ловушек"""
        print("🔄 Загрузка traps layer...")
        traps_layer_data = (
            "eJxjYBgFQxHMYqSvvlEwCsgFuNLcaFocGgAUT+hxNRp3o2AUEAYA+iEEPg=="
        )
        tile_data = self.decode_layer_data(traps_layer_data)

        for y in range(20):
            for x in range(30):
                tile_index = y * 30 + x
                if tile_index < len(tile_data):
                    tile_gid = tile_data[tile_index]

                    if tile_gid != 0:  # Есть ловушка
                        spike = Spikes(x * 128, y * 128, 128, 128)
                        self.traps.add(spike)

        print(f"✅ Traps layer: {len(self.traps)} ловушек")

    def load_decoration_layer(self):
        """Загрузка слоя декораций"""
        print("🔄 Загрузка decoration layer...")
        decoration_layer_data = (
            "eJxjYBgFo2DkgGjGgXYBdUHKAPknZ5iFI7mgZIDCoQZob+wgiIPhlp9GwSigJgAA5dUC2w=="
        )
        tile_data = self.decode_layer_data(decoration_layer_data)

        for y in range(20):
            for x in range(30):
                tile_index = y * 30 + x
                if tile_index < len(tile_data):
                    tile_gid = tile_data[tile_index]

                    if tile_gid != 0:
                        deco_type = self.get_decoration_type_by_gid(tile_gid)
                        decoration = Decoration(x * 128, y * 128, 128, 128, deco_type)
                        self.decorations.add(decoration)

        print(f"✅ Decoration layer: {len(self.decorations)} декораций")

    def load_objects_from_xml(self):
        """Загрузка объектов из objectgroups"""
        print("🔄 Загрузка объектов из TMX...")

        # 🔥 ВРАГИ ИЗ OBJECTGROUP (GID из spritesheet_enemies)
        enemies_data = [
            # slime (GID 418 = 417 + 1)
            (898, 1268 - 128, 128, 128, "slime"),
            # snail (GID 459 = 417 + 42)
            (1790, 1264 - 128, 128, 128, "snail"),
            # saw (GID 481 = 417 + 64)
            (2684, 1788 - 128, 128, 128, "saw"),
            # fly (GID 475 = 417 + 58)
            (2308, 1648 - 128, 128, 128, "fly"),
        ]

        # 🔄 НОВОЕ: Сохраняем начальные данные врагов для респавна после смерти игрока
        self.initial_enemy_data = enemies_data

        # При каждом создании уровня гарантированно создаём НОВЫЕ инстансы врагов.
        # Это важно: если где-то старый Level не был очищен, мы не переиспользуем "улетевших" врагов.
        self.enemies.empty()

        for x, y, w, h, enemy_type in enemies_data:
            enemy = None
            try:
                print(f"🔄 Попытка создания врага {enemy_type} на позиции ({x}, {y})")
                if enemy_type == "slime":
                    enemy = Slime(x, y)
                    # 🔥 FIX: Validate image is set
                    if enemy.image is None:
                        print(f"❌ Slime создан но image is None! Исправляем...")
                        enemy.create_placeholder_sprites()
                        enemy.image = enemy.idle_sprite
                    print(f"✅ Slime создан успешно с image: {enemy.image}")
                elif enemy_type == "snail":
                    enemy = Snail(x, y)
                    print(f"✅ Snail создан успешно: {enemy}")
                elif enemy_type == "fly":
                    enemy = Fly(x, y)
                    print(f"✅ Fly создан успешно: {enemy}")
                elif enemy_type == "saw":
                    saw = Saw(x, y)
                    self.traps.add(saw)
                    print(f"✅ Saw добавлен в ловушки")
                    continue  # Skip adding to enemies group

                # 🔥 FIX: Double-check image before adding to group
                if enemy is not None:
                    if not hasattr(enemy, "image") or enemy.image is None:
                        print(f"⚠️ {enemy_type} missing image before add, fixing...")
                        if hasattr(enemy, "idle_sprite"):
                            enemy.image = enemy.idle_sprite
                        elif hasattr(enemy, "create_placeholder_sprites"):
                            enemy.create_placeholder_sprites()
                            enemy.image = enemy.idle_sprite

                    self.enemies.add(enemy)
                    print(
                        f"✅ Враг {enemy_type} добавлен в группу врагов. Всего врагов: {len(self.enemies)}"
                    )
                else:
                    print(
                        f"⚠️ ВНИМАНИЕ: Враг {enemy_type} не был создан (enemy is None)"
                    )

            except Exception as e:
                print(f"❌ Ошибка создания врага {enemy_type}: {e}")
                import traceback

                traceback.print_exc()

        # 🔥 ПРЕДМЕТЫ ИЗ OBJECTGROUP
        items_data = [
            # Ключ (GID 572 = 522 + 50)
            (440, 364 - 128, 128, 128, "key_yellow"),
            # Рубин (GID 522)
            (2432, 128 - 128, 128, 128, "jewel_blue"),
            # Монеты (GID 158 = 129 + 29)
            (384, 1024 - 128, 128, 128, "coin"),
            (512, 1024 - 128, 128, 128, "coin"),
            (640, 1024 - 128, 128, 128, "coin"),
            (2560, 1280 - 128, 128, 128, "coin"),
            (2816, 1664 - 128, 128, 128, "coin"),
            (2048, 768 - 128, 128, 128, "coin"),
            (1852, 368 - 128, 128, 128, "coin"),
        ]

        for x, y, w, h, item_type in items_data:
            item = Item(x, y, w, h, item_type)
            self.items.add(item)

        # 🔥 ДЕКОРАЦИИ ИЗ OBJECTGROUP
        decorations_data = [
            # Замок (GID 363 = 289 + 74) — визуальный замок над дверью
            (840, 1590 - 32, 32, 32, "lock_yellow"),
        ]

        for x, y, w, h, deco_type in decorations_data:
            decoration = Decoration(x, y, w, h, deco_type)
            self.decorations.add(decoration)

        box_data = [
            # Ящики (GID 341 = 289 + 52)
            (1792, 1664 - 128, 128, 128, "box"),
            (1920, 1664 - 128, 128, 128, "box"),
        ]
        for x, y, w, h, platform_type in box_data:
            platform = Platform(x, y, w, h, platform_type)
            self.platforms.add(platform)

        print(
            f"✅ Objects loaded: {len(self.enemies)} врагов, {len(self.items)} предметов, {len(self.decorations)} декораций"
        )

    def respawn_killed_enemies(self):
        """Возрождает всех убитых врагов при респавне игрока"""
        print("🔄 Проверка убитых врагов для респавна...")
        
        # Подсчитываем текущих живых врагов по типам
        alive_enemy_count = {}
        for enemy in self.enemies.sprites():
            enemy_type = enemy.__class__.__name__.lower()
            alive_enemy_count[enemy_type] = alive_enemy_count.get(enemy_type, 0) + 1
        
        # Подсчитываем начальное количество врагов по типам
        initial_enemy_count = {}
        for x, y, w, h, enemy_type in self.initial_enemy_data:
            if enemy_type == "saw":  # Пропускаем saw - они не враги, а ловушки
                continue
            initial_enemy_count[enemy_type] = initial_enemy_count.get(enemy_type, 0) + 1
        
        # Возрождаем недостающих врагов
        for x, y, w, h, enemy_type in self.initial_enemy_data:
            # Пропускаем saw - они не враги, а ловушки
            if enemy_type == "saw":
                continue
            
            # Проверяем, нужно ли возродить врага этого типа
            current_count = alive_enemy_count.get(enemy_type, 0)
            initial_count = initial_enemy_count.get(enemy_type, 0)
            
            if current_count < initial_count:
                # Есть убитые враги этого типа, возрождаем одного
                enemy = None
                try:
                    print(f"🔄 Возрождение врага {enemy_type} на позиции ({x}, {y})")
                    if enemy_type == "slime":
                        enemy = Slime(x, y)
                        if enemy.image is None:
                            enemy.create_placeholder_sprites()
                            enemy.image = enemy.idle_sprite
                    elif enemy_type == "snail":
                        enemy = Snail(x, y)
                    elif enemy_type == "fly":
                        enemy = Fly(x, y)
                    
                    if enemy is not None:
                        if not hasattr(enemy, "image") or enemy.image is None:
                            if hasattr(enemy, "idle_sprite"):
                                enemy.image = enemy.idle_sprite
                            elif hasattr(enemy, "create_placeholder_sprites"):
                                enemy.create_placeholder_sprites()
                                enemy.image = enemy.idle_sprite
                        
                        self.enemies.add(enemy)
                        # Обновляем счетчик чтобы не создавать дубликаты
                        alive_enemy_count[enemy_type] = alive_enemy_count.get(enemy_type, 0) + 1
                        print(f"✅ Враг {enemy_type} возрожден успешно")
                except Exception as e:
                    print(f"❌ Ошибка возрождения врага {enemy_type}: {e}")
                    import traceback
                    traceback.print_exc()
        
        print(f"✅ Респавн врагов завершен. Всего врагов: {len(self.enemies)}")

    def check_exit_door_collision(self):
        """
        Проверяет столкновение игрока с дверью выхода.
        Условие завершения уровня:
        - игрок касается двери выхода
        - дверь имеет жёлтый замок
        - у игрока есть жёлтый ключ (player.has_yellow_key == True)
        Если ключа нет — выводит сообщение в консоль (можно заменить на HUD).
        """
        if not self.player:
            return

        player_rect = (
            self.player.get_actual_hitbox()
            if hasattr(self.player, "get_actual_hitbox")
            else self.player.rect
        )

        for decoration in self.decorations:
            if player_rect.colliderect(decoration.rect):
                # Ожидаем жёлтый замок
                if decoration.decoration_type == "lock_yellow":
                    if getattr(self.player, "has_yellow_key", False):
                        if not self.completed:
                            print(
                                "✅ Условие выхода выполнено: есть жёлтый ключ и столкновение с дверью."
                            )
                            self.completed = True
                            # Вызываем обработчик завершения уровня
                            if callable(self.on_level_complete):
                                self.on_level_complete(self.name)
                    else:
                        # Нет ключа — сообщение (можно интегрировать с HUD)
                        print("🚪 You need a yellow key to open this door")

                # если будут двери других цветов — можно расширить здесь

    def get_platform_type_by_gid(self, gid):
        """Определяет тип платформы по GID"""
        # 🔥 СООТВЕТСТВИЕ GID ТИПАМ ПЛАТФОРМ ИЗ spritesheet_ground
        platform_types = {
            # spritesheet_ground (GID 1-128)
            1: "grass1",
            2: "grass_half",
            25: "triangle",
            57: "semitype1",
            49: "semitype2",
            41: "semitype3",
            9: "grass2",
            89: "grass3",
            97: "grass4",
            73: "grass5",
            17: "grass6",
            # Добавьте другие GID по мере необходимости
        }
        return platform_types.get(gid, "grass")

    def get_decoration_type_by_gid(self, gid):
        """Определяет тип декорации по GID"""
        # 🔥 СООТВЕТСТВИЕ GID ТИПАМ ДЕКОРАЦИЙ ИЗ spritesheet_tiles
        decoration_types = {
            # spritesheet_tiles (GID 289-416)
            347: "dec1",
            356: "dec2",
            364: "dec3",
            372: "dec4",
            380: "dec5",
            349: "dec6",
            363: "lock_yellow",
            # Добавьте другие GID по мере необходимости
        }
        return decoration_types.get(gid, "f")

    def _compute_update_rect(self) -> pygame.Rect:
        """Вычисляет область, в которой нужно обновлять объекты (окрестность игрока).

        Если игрока нет (например, при ошибке инициализации), обновляем весь уровень.
        """
        if not self.player:
            return pygame.Rect(0, 0, self.width, self.height)

        half_w, half_h = 700, 400
        margin = 400
        cx, cy = self.player.rect.center
        return pygame.Rect(
            cx - half_w - margin,
            cy - half_h - margin,
            2 * (half_w + margin),
            2 * (half_h + margin),
        )

    def update(self, dt):
        """Обновление уровня с локализованными апдейтами."""
        update_rect = self._compute_update_rect()

        for enemy in self.enemies:
            if enemy.rect.colliderect(update_rect):
                enemy.update(dt, self)
                self.check_enemy_collisions(enemy)

        for trap in self.traps:
            if hasattr(trap, "rect") and trap.rect.colliderect(update_rect):
                trap.update(dt, self)

        if self.player:
            # Обновляем анимацию для динамических предметов (например, монет из ящиков)
            for item in self.items:
                if hasattr(item, "update"):
                    item.update(dt)

            self.check_item_collection()
            self.check_exit_door_collision()

    def check_item_collection(self):
        """Проверка сбора предметов игроком"""
        for item in self.items.sprites():
            if not item.collected and self.player.rect.colliderect(item.rect):
                item_type = item.collect()
                if item_type:
                    print(f"🎁 Собран предмет: {item_type}")
                    try:
                        audio = AudioManager.get_instance()
                    except Exception as e:
                        audio = None
                        print(f"[Audio][Level1] Failed to get AudioManager: {e}")
                    if item_type == "coin":
                        self.player.coins += 1
                        if audio:
                            try:
                                audio.sfx.play("player_collect_coin")
                            except Exception as e:
                                print(f"[Audio][Level1] coin sfx failed: {e}")
                    elif item_type == "jewel_blue":
                        self.player.coins += 10
                        if audio:
                            try:
                                audio.sfx.play("player_collect_coin")
                            except Exception as e:
                                print(f"[Audio][Level1] jewel sfx failed: {e}")
                    elif item_type == "key_yellow":
                        # логический флаг ключа для замка
                        self.player.collect_yellow_key()
                        self.player.keys += 1
                        if audio:
                            try:
                                audio.sfx.play("player_collect_coin")
                            except Exception as e:
                                print(f"[Audio][Level1] key sfx failed: {e}")

    def check_enemy_collisions(self, enemy):
        """Проверка столкновений врага с платформами"""
        for platform in self.platforms:
            if not platform.has_collision:
                continue

            if hasattr(platform, "check_collision") and platform.check_collision(
                enemy.rect
            ):
                # Столкновение сверху
                if (
                    enemy.velocity.y > 0
                    and enemy.rect.bottom > platform.rect.top
                    and enemy.rect.top < platform.rect.top
                    and abs(enemy.rect.bottom - platform.rect.top) < 20
                ):

                    enemy.rect.bottom = platform.rect.top
                    enemy.velocity.y = 0
                    return True

                # Столкновение снизу
                elif (
                    enemy.velocity.y < 0
                    and enemy.rect.top < platform.rect.bottom
                    and enemy.rect.bottom > platform.rect.bottom
                    and abs(enemy.rect.top - platform.rect.bottom) < 20
                ):

                    enemy.rect.top = platform.rect.bottom
                    enemy.velocity.y = 0
                    return True

                # Столкновение сбоку
                elif enemy.velocity.x != 0 and (
                    (enemy.rect.right > platform.rect.left and enemy.direction > 0)
                    or (enemy.rect.left < platform.rect.right and enemy.direction < 0)
                ):

                    enemy.direction *= -1
                    return True

        return False

    def draw(self, screen, camera):
        """Отрисовка уровня в правильном порядке"""
        screen.blit(self.background, (0, 0))

        # 1. Основные платформы
        for platform in self.platforms:
            platform.draw(screen, camera)

        # 2. Декорации
        for decoration in self.decorations:
            decoration.draw(screen, camera)

        # 3. Ловушки
        for trap in self.traps:
            trap.draw(screen, camera)

        # 4. Враги
        for enemy in self.enemies:
            enemy.draw(screen, camera)

        # 5. Предметы
        for item in self.items:
            item.draw(screen, camera)
