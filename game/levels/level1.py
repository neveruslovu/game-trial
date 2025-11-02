# game/levels/level1.py
import pygame
import base64
import zlib
import os
from ..platform import Platform
from ..enemies.slime import Slime
from ..enemies.snail import Snail
from ..enemies.fly import Fly
from ..items.items import Item
from ..decorations import Decoration
from ..asset_loader import asset_loader
from ..traps.saw import Saw
from ..traps.spikes import Spikes

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
        
        # Загрузка фона
        original_bg = asset_loader.load_image("backgrounds/colored_grass.png", 1)
        self.background = pygame.transform.scale(original_bg, (1400, 800))       
        self.player = None
        self.player_spawn_point = (0, 1280)  # Из TMX объекта
        self.width = 30 * 128  # 3840
        self.height = 20 * 128  # 2560
        
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
            ("Spritesheets/spritesheet_hud.png", 522, 128, 128)
        ]
        
        for path, firstgid, tilewidth, tileheight in tilesets_data:
            asset_loader.load_tileset(path, firstgid, tilewidth, tileheight)
    
    def set_player(self, player):
        """Установить ссылку на игрока"""
        self.player = player
        if self.player:
            self.player.rect.x = self.player_spawn_point[0]
            self.player.rect.y = self.player_spawn_point[1]
            self.player.respawn_position = self.player_spawn_point
    
    def decode_layer_data(self, encoded_data):
        """Декодирование данных слоя тайлов из base64+zlib"""
        try:
            encoded_data = encoded_data.strip().replace('\n', '').replace('\r', '')
            decoded = base64.b64decode(encoded_data)
            decompressed = zlib.decompress(decoded)
            
            tile_data = []
            for i in range(0, len(decompressed), 4):
                tile_gid = int.from_bytes(decompressed[i:i+4], byteorder='little')
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
        semiground_data = "eJxjYBjawBKIDYFYc6AdQgKAuZnaamkJKAnnoRJHtHAnPf0+VMJ5FIyCUTAKRgIAAN5vBEc="
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
        traps_layer_data = "eJxjYBgFQxHMYqSvvlEwCsgFuNLcaFocGgAUT+hxNRp3o2AUEAYA+iEEPg=="
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
        decoration_layer_data = "eJxjYBgFo2DkgGjGgXYBdUHKAPknZ5iFI7mgZIDCoQZob+wgiIPhlp9GwSigJgAA5dUC2w=="
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
            (898, 1268-128, 128, 128, "slime"),
            # snail (GID 459 = 417 + 42)  
            (1790, 1264-128, 128, 128, "snail"),
            # saw (GID 481 = 417 + 64)
            (2684, 1788-128, 128, 128, "saw"),
            # fly (GID 475 = 417 + 58)
            (2308, 1648-128, 128, 128, "fly")
        ]
        
        for x, y, w, h, enemy_type in enemies_data:
            try:
                if enemy_type == "slime":
                    enemy = Slime(x, y)
                elif enemy_type == "snail":
                    enemy = Snail(x, y)
                elif enemy_type == "fly":
                    enemy = Fly(x, y)
                elif enemy_type == "saw":
                    saw = Saw(x, y)
                    self.traps.add(saw)
                
                self.enemies.add(enemy)
                print(f"✅ Враг {enemy_type} создан на позиции ({x}, {y})")
                
            except Exception as e:
                print(f"❌ Ошибка создания врага {enemy_type}: {e}")
    
        # 🔥 ПРЕДМЕТЫ ИЗ OBJECTGROUP
        items_data = [
            # Ключ (GID 572 = 522 + 50)
            (440, 364-128, 128, 128, "key_yellow"),
            # Рубин (GID 522)
            (2432, 128-128, 128, 128, "jewel_blue"),
            # Монеты (GID 158 = 129 + 29)
            (384, 1024-128, 128, 128, "coin"),
            (512, 1024-128, 128, 128, "coin"),
            (640, 1024-128, 128, 128, "coin"),
            (2560, 1280-128, 128, 128, "coin"),
            (2816, 1664-128, 128, 128, "coin"),
            (2048, 768-128, 128, 128, "coin"),
            (1852, 368-128, 128, 128, "coin"),
        ]
        
        for x, y, w, h, item_type in items_data:
            item = Item(x, y, w, h, item_type)
            self.items.add(item)
        
        # 🔥 ДЕКОРАЦИИ ИЗ OBJECTGROUP
        decorations_data = [
            
            # Замок (GID 363 = 289 + 74)
            (840, 1590-32, 32, 32, "lock_yellow"),
        ]
        
        for x, y, w, h, deco_type in decorations_data:
            decoration = Decoration(x, y, w, h, deco_type)
            self.decorations.add(decoration)

        box_data = [  
            # Ящики (GID 341 = 289 + 52)
            (1792, 1664-128, 128, 128, "box"),
            (1920, 1664-128, 128, 128, "box"),

            ]
        for x, y, w, h,platform_type in box_data:
            platform= Platform(x, y, w, h, platform_type)
            self.platforms.add(platform)

        print(f"✅ Objects loaded: {len(self.enemies)} врагов, {len(self.items)} предметов, {len(self.decorations)} декораций")
    
    def get_platform_type_by_gid(self, gid):
        """Определяет тип платформы по GID"""
        # 🔥 СООТВЕТСТВИЕ GID ТИПАМ ПЛАТФОРМ ИЗ spritesheet_ground
        platform_types = {
            # spritesheet_ground (GID 1-128)
            1: "grass1", 
            2: "grass_half", 
            25: "triangle", 57: "semitype1", 49: "semitype2", 41: "semitype3", 9: "grass2", 89: "grass3", 97: "grass4", 73:"grass5", 17: "grass6"
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
            349: "dec6"
            # Добавьте другие GID по мере необходимости
        }
        return decoration_types.get(gid,"f" )
        
    
    
    def update(self, dt):
        """Обновление уровня"""
        for enemy in self.enemies:
            enemy.update(dt, self)
            if hasattr(enemy, 'gravity') and not hasattr(enemy, 'rotation_speed'):
                enemy.velocity.y += enemy.gravity * dt
            self.check_enemy_collisions(enemy)
        
        if self.player:
            self.check_item_collection()
    
    def check_item_collection(self):
        """Проверка сбора предметов игроком"""
        for item in self.items.sprites():
            if not item.collected and self.player.rect.colliderect(item.rect):
                item_type = item.collect()
                if item_type:
                    print(f"🎁 Собран предмет: {item_type}")
                    if item_type == "coin":
                        self.player.coins += 1
                    elif item_type == "key_yellow":
                        self.player.keys += 1
                    elif item_type == "jewel_blue":
                        self.player.jewels += 1

    def check_enemy_collisions(self, enemy):
        """Проверка столкновений врага с платформами"""
        for platform in self.platforms:
            if not platform.has_collision:
                continue
            
            if hasattr(platform, 'check_collision') and platform.check_collision(enemy.rect):
                # Столкновение сверху
                if (enemy.velocity.y > 0 and 
                    enemy.rect.bottom > platform.rect.top and
                    enemy.rect.top < platform.rect.top and
                    abs(enemy.rect.bottom - platform.rect.top) < 20):
                
                    enemy.rect.bottom = platform.rect.top
                    enemy.velocity.y = 0
                    return True
            
                # Столкновение снизу
                elif (enemy.velocity.y < 0 and 
                    enemy.rect.top < platform.rect.bottom and
                    enemy.rect.bottom > platform.rect.bottom and
                    abs(enemy.rect.top - platform.rect.bottom) < 20):
                
                    enemy.rect.top = platform.rect.bottom
                    enemy.velocity.y = 0
                    return True
            
                # Столкновение сбоку
                elif (enemy.velocity.x != 0 and
                    ((enemy.rect.right > platform.rect.left and enemy.direction > 0) or
                    (enemy.rect.left < platform.rect.right and enemy.direction < 0))):
                
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