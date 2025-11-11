import pygame


class MainMenu:
    """
    Главное меню + режим 'меню завершения уровня'.

    Обычный режим:
      - Продолжить игру (если есть активная)
      - Новая игра
      - Загрузить
      - Настройки
      - Выход

    Режим завершения уровня (level_completed_mode=True):
      - Уровень пройден (заголовок)
      - В МЕНЮ
      - ВЫБОР УРОВНЯ
      - СЛЕДУЮЩИЙ УРОВЕНЬ
    """

    def __init__(self, app):
        self.app = app
        self.selected_index = 0
        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 72)

        # Флаг и данные для экрана завершения уровня
        self.level_completed_mode = False
        self.completed_level_name = None

        # Режим настроек аудио
        self.settings_mode = False
        self.settings_selected_index = 0
        # Порядок опций в меню настроек
        self.settings_options = [
            "Громкость MASTER",
            "Громкость MUSIC",
            "Громкость SFX",
            "Mute / Unmute",
            "Назад",
        ]

        print("📋 MainMenu initialized")
        print(f"📱 Menu app reference: {self.app}")

    def get_menu_options(self):
        """Получение опций меню в зависимости от состояния игры."""
        if self.level_completed_mode:
            return ["В МЕНЮ", "ВЫБОР УРОВНЯ", "СЛЕДУЮЩИЙ УРОВЕНЬ"]
        if self.app.has_active_game:
            return ["Продолжить игру", "Новая игра", "Загрузить", "Настройки", "Выход"]
        else:
            return ["Новая игра", "Загрузить", "Настройки", "Выход"]

    @property
    def options(self):
        """Получение текущих опций меню"""
        return self.get_menu_options()

    def handle_event(self, event):
        # Режим настроек аудио обрабатывается отдельно
        if self.settings_mode:
            self.handle_settings_event(event)
            return

        if event.type == pygame.KEYDOWN:
            print(f"⌨️ Key pressed: {pygame.key.name(event.key)}")

            if event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
                print(f"🎮 Menu selection: {self.options[self.selected_index]}")
                self.play_ui_sound("ui_menu_move")
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
                print(f"🎮 Menu selection: {self.options[self.selected_index]}")
                self.play_ui_sound("ui_menu_move")
            elif event.key == pygame.K_RETURN:
                print(f"🎮 Menu selected: {self.options[self.selected_index]}")
                self.play_ui_sound("ui_button_click")
                self.select_option()

        # Добавляем обработку мыши (только для обычного меню)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            print(f"🖱️ Mouse clicked at: {mouse_pos}")
            self.handle_mouse_click(mouse_pos)

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.handle_mouse_hover(mouse_pos)

    def handle_mouse_click(self, mouse_pos):
        """Обработка клика мышью"""
        for i, option in enumerate(self.options):
            text = self.font.render(option, True, (255, 255, 255))
            text_rect = text.get_rect(
                center=(self.app.screen.get_width() // 2, 250 + i * 60)
            )

            print(f"🔍 Checking option '{option}' at rect: {text_rect}")

            if text_rect.collidepoint(mouse_pos):
                print(f"🎯 Mouse clicked on: {option}")
                self.selected_index = i
                self.play_ui_sound("ui_button_click")
                self.select_option()
                return True

        print("❌ No menu option clicked")
        return False

    def handle_mouse_hover(self, mouse_pos):
        """Подсветка при наведении мышью"""
        for i, option in enumerate(self.options):
            text = self.font.render(option, True, (255, 255, 255))
            text_rect = text.get_rect(
                center=(self.app.screen.get_width() // 2, 250 + i * 60)
            )

            if text_rect.collidepoint(mouse_pos):
                if self.selected_index != i:
                    self.selected_index = i
                    print(f"🖱️ Mouse over: {option}")
                break

    def select_option(self):
        option = self.options[self.selected_index]
        print(f"🚀 Executing menu action: {option}")
        print(f"📱 App reference in select_option: {self.app}")

        # Режим завершения уровня
        if self.level_completed_mode:
            if option == "В МЕНЮ":
                print("🏠 Returning to main menu from level-complete screen")
                self.level_completed_mode = False
                # После завершения уровня запрещаем продолжение старой игры
                self.app.has_active_game = False
                self.app.go_to_menu()
            elif option == "ВЫБОР УРОВНЯ":
                print("📜 Level select requested (stub) from level-complete screen")
                self.level_completed_mode = False
                # После завершения уровня запрещаем продолжение старой игры
                self.app.has_active_game = False
                # Здесь можно открыть экран выбора уровней; пока возвращаемся в обычное меню
                self.app.go_to_menu()
            elif option == "СЛЕДУЮЩИЙ УРОВЕНЬ":
                print("⏭ Next level requested from level-complete screen")
                self.level_completed_mode = False
                # После завершения уровня запрещаем продолжение старой игры,
                # следующая игра всегда стартует заново/на новом уровне
                self.app.has_active_game = False
                # Заглушка: перезапуск level1; заменить на загрузку следующего уровня
                self.app.start_game()
            return

        # Обычное главное меню
        if option == "Продолжить игру":
            print("🔄 Continuing existing game...")
            self.app.resume_game()
        elif option == "Новая игра":
            print("🎮 Starting new game...")
            self.app.start_game()
        elif option == "Загрузить":
            print("📂 Load game (not implemented)")
        elif option == "Настройки":
            print("⚙️ Open audio settings menu")
            self.settings_mode = True
            self.settings_selected_index = 0
        elif option == "Выход":
            print("👋 Exiting game...")
            self.app.running = False

    def set_level_completed(self, level_name: str | None = None):
        """
        Переключает меню в режим завершения уровня.
        Вызывается из main.py через level.on_level_complete.
        """
        self.level_completed_mode = True
        self.completed_level_name = level_name
        self.selected_index = 0
        print(
            f"🏁 MainMenu: level '{level_name}' completed, showing completion options"
        )

    def handle_settings_event(self, event):
        """Обработка ввода в меню настроек аудио."""
        audio = getattr(self.app, "audio", None)
        if audio is None:
            # Если по какой-то причине аудио недоступно — выходим из настроек
            self.settings_mode = False
            return

        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            print(f"⌨️ Settings key: {key_name}")

            if event.key == pygame.K_ESCAPE:
                # Выход из настроек
                self.settings_mode = False
                return

            if event.key == pygame.K_DOWN:
                self.settings_selected_index = (self.settings_selected_index + 1) % len(
                    self.settings_options
                )
            elif event.key == pygame.K_UP:
                self.settings_selected_index = (self.settings_selected_index - 1) % len(
                    self.settings_options
                )

            # Регулировка значений стрелками влево/вправо и Enter для mute/назад
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RETURN):
                opt = self.settings_options[self.settings_selected_index]
                step = -0.1 if event.key == pygame.K_LEFT else 0.1
                if opt == "Громкость MASTER" and event.key != pygame.K_RETURN:
                    audio.set_master_volume(audio.settings.master_volume + step)
                elif opt == "Громкость MUSIC" and event.key != pygame.K_RETURN:
                    audio.set_music_volume(audio.settings.music_volume + step)
                elif opt == "Громкость SFX" and event.key != pygame.K_RETURN:
                    audio.set_sfx_volume(audio.settings.sfx_volume + step)
                elif opt == "Mute / Unmute" and event.key == pygame.K_RETURN:
                    audio.toggle_mute()
                elif opt == "Назад" and event.key == pygame.K_RETURN:
                    self.settings_mode = False

                # Применяем и сохраняем настройки
                audio.apply_volumes()
                try:
                    audio.settings.save()
                except Exception as e:
                    print(f"[Audio] WARNING: cannot save settings from menu: {e}")

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((30, 30, 60))

        # Если включен режим настроек аудио — рисуем его отдельно
        if self.settings_mode:
            self.draw_settings(screen)
            return

        # Заголовок
        if self.level_completed_mode:
            title_text = "УРОВЕНЬ ПРОЙДЕН"
            if self.completed_level_name:
                title_text += f" ({self.completed_level_name})"
            title = self.title_font.render(title_text, True, (255, 255, 0))
        else:
            title = self.title_font.render("RPG PLATFORMER", True, (255, 255, 255))

        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))

        # Опции меню
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, 250 + i * 60))
            screen.blit(text, text_rect)

            debug_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(screen, (255, 0, 0), debug_rect, 1)

    def play_ui_sound(self, key: str):
        """Воспроизведение UI-звуков через глобальный AudioManager."""
        audio = getattr(self.app, "audio", None)
        if audio is None or not hasattr(audio, "sfx"):
            return
        try:
            audio.sfx.play(key)
        except Exception as e:
            print(f"[Audio][UI] WARNING: failed to play '{key}': {e}")

    def draw_settings(self, screen):
        """Отрисовка простого меню аудио-настроек."""
        screen.fill((20, 20, 40))
        title = self.title_font.render("НАСТРОЙКИ ЗВУКА", True, (255, 255, 255))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 80))

        audio = getattr(self.app, "audio", None)
        if audio is None:
            info = self.font.render("Аудиосистема недоступна", True, (255, 100, 100))
            screen.blit(
                info,
                (screen.get_width() // 2 - info.get_width() // 2, 200),
            )
            return

        values = {
            "Громкость MASTER": f"{audio.settings.master_volume:.1f}",
            "Громкость MUSIC": f"{audio.settings.music_volume:.1f}",
            "Громкость SFX": f"{audio.settings.sfx_volume:.1f}",
            "Mute / Unmute": "ON" if audio.settings.muted else "OFF",
            "Назад": "",
        }

        base_y = 220
        for i, opt in enumerate(self.settings_options):
            is_selected = i == self.settings_selected_index
            color = (255, 255, 0) if is_selected else (220, 220, 220)
            label = opt
            if values[opt]:
                label = f"{opt}: {values[opt]}"
            text = self.font.render(label, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, base_y + i * 60))
            screen.blit(text, text_rect)

            if is_selected:
                pygame.draw.rect(
                    screen,
                    (255, 255, 0),
                    text_rect.inflate(20, 10),
                    2,
                )
