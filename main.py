import pygame
import sys
import os

# Добавляем путь для импортов
sys.path.append(os.path.dirname(__file__))

from game.player import Player
from game.camera import Camera
from game.levels.level1 import Level
from ui.menu import MainMenu
from ui.hud import HUD
from game.assets.audio import AudioManager


class RPGPlatformer:
    def __init__(self):
        pygame.init()
        # Настройки экрана
        self.SCREEN_WIDTH = 1400
        self.SCREEN_HEIGHT = 800
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("2D PLATFORMER")

        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"  # menu, game, settings

        # Инициализация систем
        # Аудиосистема (глобальный синглтон, базовый путь укажем на каталог audio)
        self.audio = AudioManager.get_instance(
            base_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "game",
                "assets",
                "audio",
            )
        )
        self.audio.apply_volumes()

        self.menu = MainMenu(self)
        self.player = None
        self.level = None
        self.camera = None
        self.hud = None

        # ⏰ ДОБАВЛЕНО: Переменная для отслеживания времени игры
        self.game_start_time = 0

        # 🔄 НОВОЕ: Флаг для отслеживания активной игровой сессии
        self.has_active_game = False

        print("🎮 RPG Platformer инициализирован!")
        # Вход в меню — включаем меню-музыку
        self.audio.on_menu_enter()

    def start_game(self):
        """Запуск новой игры"""
        print("🚀 Запуск новой игры...")
        self.state = "game"
        # Музыка для игрового уровня
        self.audio.on_game_start("level1")
        self.game_start_time = pygame.time.get_ticks()

        try:
            # 🔥 Сначала создаем уровень, потом игрока
            self.level = Level("level1")

            # Игрок создаётся и затем привязывается к уровню
            self.player = Player(0, 0)
            self.level.set_player(self.player)
            self.camera = Camera(self.player, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self.hud = HUD(self.player)
            print(f"📷 Камера создана:")
            print(f"  - Позиция игрока: ({self.player.rect.x}, {self.player.rect.y})")
            print(
                f"  - Offset камеры: ({self.camera.offset.x}, {self.camera.offset.y})"
            )
            self.camera.update()
            print(
                f"  - Offset после update: ({self.camera.offset.x}, {self.camera.offset.y})"
            )

            # Подключаем завершение уровня к МЕНЮ (экран выбора действия после победы)
            def on_level_complete(level_name: str):
                print(f"🏁 Level '{level_name}' completed, opening level-complete menu")
                # Переключаемся в состояние "menu", но меню будет показывать опции завершения уровня
                self.state = "menu"
                # Обновляем меню на режим завершения уровня
                if isinstance(self.menu, MainMenu):
                    self.menu.set_level_completed(level_name)

            self.level.on_level_complete = on_level_complete

            # 🔄 Флаг активной игры
            self.has_active_game = True

            print("✅ Игра запущена!")

        except Exception as e:
            print(f"❌ Ошибка при запуске игры: {e}")
            import traceback

            traceback.print_exc()

    def resume_game(self):
        """Продолжение существующей игры"""
        print("🔄 Продолжение игры...")
        if self.has_active_game and self.player and self.level:
            self.state = "game"
            print("✅ Игра восстановлена!")
        else:
            print("❌ Нет активной игры для продолжения")

    def go_to_menu(self):
        """Переход в меню с сохранением игровой сессии"""
        print("🏠 Переход в меню...")
        self.state = "menu"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                # Корректно выключаем аудио
                self.audio.shutdown()
                return

            # Состояние: меню
            if self.state == "menu":
                self.menu.handle_event(event)
                continue

            # Состояние: игра
            if self.state == "game" and self.player and self.level:
                # Обычный игровой ввод
                self.player.handle_event(event)

                # ESC → переход в меню
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.go_to_menu()

    def update(self):
        dt = self.clock.get_time() / 1000.0  # Delta time в секундах

        # Обновление в зависимости от состояния
        if self.state == "game" and self.player and self.level:
            # ⏰ ДОБАВЛЕНО: Получаем текущее время игры
            current_time = (pygame.time.get_ticks() - self.game_start_time) / 1000.0

            # 🔧 ВАЖНО: Обрабатываем непрерывный ввод клавиш
            keys = pygame.key.get_pressed()
            # 🔥 ИСПРАВЛЕНИЕ: Передаем platforms в handle_keys
            self.player.handle_keys(
                keys, self.level.platforms
            )  # 🔥 ДОБАВЛЕНО platforms

            # 🔧 Обновляем игрока
            self.player.update(
                platforms=self.level.platforms,
                enemies=self.level.enemies,
                current_time=current_time,
                traps=self.level.traps,
            )

            # Обновление уровня
            self.level.update(dt)

            # Обновление камеры
            self.camera.update()

    def draw(self):
        # Отрисовка в зависимости от состояния
        if self.state == "menu":
            self.menu.draw(self.screen)
        elif self.state == "game":
            # Отрисовка игры
            self.level.draw(self.screen, self.camera)
            self.player.draw(self.screen, self.camera)
            self.hud.draw(self.screen)

        pygame.display.flip()

    def run(self):
        # Сброс первого dt, чтобы избежать гигантского шага физики
        self.clock.tick(60)
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = RPGPlatformer()
    game.run()
