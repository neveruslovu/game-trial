import pygame
import os


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

        # Load background image
        self.background = self.load_background_image()

        # Menu options for standard mode
        self.standard_menu_options = ["Новая игра", "Настройки", "Кредиты", "Выход"]

        # Menu options when there's an active game
        self.active_game_menu_options = ["Продолжить игру", "Новая игра", "Настройки", "Кредиты", "Выход"]

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

        # Добавляем переменные для отслеживания состояния мыши в настройках
        self.dragging_slider = None  # Какой слайдер перетаскивается (master, music, sfx)
        self.slider_width = 400  # Ширина слайдера в пикселях
        self.slider_height = 20  # Высота слайдера в пикселях
        self.option_spacing = 100  # Увеличенное расстояние между опциями

        print("📋 MainMenu initialized")
        print(f"📱 Menu app reference: {self.app}")

    def get_menu_options(self):
        """Получение опций меню в зависимости от состояния игры."""
        if self.level_completed_mode:
            return ["В МЕНЮ", "ВЫБОР УРОВНЯ", "СЛЕДУЮЩИЙ УРОВЕНЬ"]
        if self.app.has_active_game:
            return self.active_game_menu_options
        else:
            return self.standard_menu_options

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
            # Button background rectangle
            button_width = 300
            button_height = 50
            button_x = self.app.screen.get_width() // 2 - button_width // 2
            button_y = 250 + i * 70
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            print(f"🔍 Checking option '{option}' at rect: {button_rect}")

            if button_rect.collidepoint(mouse_pos):
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
            # Button background rectangle
            button_width = 300
            button_height = 50
            button_x = self.app.screen.get_width() // 2 - button_width // 2
            button_y = 250 + i * 70
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            if button_rect.collidepoint(mouse_pos):
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
        elif option == "Настройки":
            print("⚙️ Open audio settings menu")
            self.settings_mode = True
            self.settings_selected_index = 0
        elif option == "Кредиты":
            print("📝 Show credits")
            self.app.go_to_credits()
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

        # Обработка событий мыши для слайдеров
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_settings_mouse_down(event.pos, audio)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_slider:
                self.dragging_slider = None
        elif event.type == pygame.MOUSEMOTION:
            self.handle_settings_mouse_motion(event.pos, audio)
        elif event.type == pygame.KEYDOWN:
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
                self.play_ui_sound("ui_menu_move")  # Добавляем звук при навигации
            elif event.key == pygame.K_UP:
                self.settings_selected_index = (self.settings_selected_index - 1) % len(
                    self.settings_options
                )
                self.play_ui_sound("ui_menu_move")  # Добавляем звук при навигации

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
                    self.play_ui_sound("ui_button_click")  # Добавляем звук при переключении
                elif opt == "Назад" and event.key == pygame.K_RETURN:
                    self.settings_mode = False
                    self.play_ui_sound("ui_button_click")  # Добавляем звук при выходе

                # Применяем и сохраняем настройки
                audio.apply_volumes()
                try:
                    audio.settings.save()
                except Exception as e:
                    print(f"[Audio] WARNING: cannot save settings from menu: {e}")

    def update(self, dt):
        pass

    def draw(self, screen):
        # Draw the background image if available, otherwise use fallback color
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((30, 30, 60))

        # Если включен режим настроек аудио — рисуем его отдельно
        if self.settings_mode:
            self.draw_settings(screen)
            return

        # Create a semi-transparent overlay for better text visibility
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))  # Semi-transparent black overlay
        screen.blit(overlay, (0, 0))

        # Заголовок
        if self.level_completed_mode:
            title_text = "УРОВЕНЬ ПРОЙДЕН"
            if self.completed_level_name:
                title_text += f" ({self.completed_level_name})"
            title = self.title_font.render(title_text, True, (255, 255, 0))
        else:
            title = self.title_font.render("MUSHROOM ADVENTURE", True, (255, 255, 255))

        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))

        # Опции меню
        for i, option in enumerate(self.options):
            # Button background rectangle
            button_width = 300
            button_height = 50
            button_x = screen.get_width() // 2 - button_width // 2
            button_y = 250 + i * 70
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            # Draw button background with highlight for selected item
            if i == self.selected_index:
                pygame.draw.rect(screen, (100, 100, 100, 180), button_rect, border_radius=10)
                pygame.draw.rect(screen, (255, 255, 255), button_rect, 3, border_radius=10)
            else:
                pygame.draw.rect(screen, (50, 50, 50, 180), button_rect, border_radius=10)
                pygame.draw.rect(screen, (200, 200, 200), button_rect, 2, border_radius=10)

            # Draw text
            color = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)

    def load_background_image(self):
        """Загрузка фонового изображения для меню."""
        try:
            # Get the path to the background image
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            background_path = os.path.join(base_path, "game", "assets", "Backgrounds", "colored_shroom.png")

            # Load and scale the image to fit the screen
            background = pygame.image.load(background_path).convert()
            background = pygame.transform.scale(background, (self.app.SCREEN_WIDTH, self.app.SCREEN_HEIGHT))
            return background
        except Exception as e:
            print(f"[Menu] WARNING: Could not load background image: {e}")
            return None

    def play_ui_sound(self, key: str):
        """Воспроизведение UI-звуков через глобальный AudioManager."""
        audio = getattr(self.app, "audio", None)
        if audio is None or not hasattr(audio, "sfx"):
            return
        try:
            audio.sfx.play(key)
        except Exception as e:
            print(f"[Audio][UI] WARNING: failed to play '{key}': {e}")

    def handle_settings_mouse_down(self, mouse_pos, audio):
        """Обработка нажатия мыши в меню настроек."""
        # Проверяем, нажал ли пользователь на один из слайдеров громкости
        base_y = 180
        slider_x = self.app.screen.get_width() // 2 - self.slider_width // 2

        # Проверяем каждый слайдер
        for i, opt in enumerate(self.settings_options):
            if opt in ["Громкость MASTER", "Громкость MUSIC", "Громкость SFX"]:
                slider_y = base_y + i * self.option_spacing + 35
                # Увеличиваем область взаимодействия для удобства
                slider_rect = pygame.Rect(slider_x - 10, slider_y - 10, self.slider_width + 20, self.slider_height + 20)

                if slider_rect.collidepoint(mouse_pos):
                    # Определяем, какой слайдер перетаскиваем
                    self.dragging_slider = opt.split()[1].lower()  # "master", "music" или "sfx"
                    # Вычисляем новое значение громкости на основе позиции мыши
                    relative_x = mouse_pos[0] - slider_x
                    new_volume = max(0.0, min(1.0, relative_x / self.slider_width))

                    # Применяем новое значение
                    if self.dragging_slider == "master":
                        audio.set_master_volume(new_volume)
                    elif self.dragging_slider == "music":
                        audio.set_music_volume(new_volume)
                    elif self.dragging_slider == "sfx":
                        audio.set_sfx_volume(new_volume)

                    # Применяем и сохраняем настройки
                    audio.apply_volumes()
                    try:
                        audio.settings.save()
                    except Exception as e:
                        print(f"[Audio] WARNING: cannot save settings from menu: {e}")

                    # Воспроизводим звук при изменении громкости
                    self.play_ui_sound("ui_menu_move")
                    return

            # Обработка клика на другие опции (Mute/Unmute и Назад)
            elif opt in ["Mute / Unmute", "Назад"]:
                # Используем тот же размер кнопок, что и в отрисовке
                button_width = 300
                button_height = 50
                button_x = self.app.screen.get_width() // 2 - button_width // 2
                button_y = base_y + i * self.option_spacing - 25
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

                if button_rect.collidepoint(mouse_pos):
                    if opt == "Mute / Unmute":
                        audio.toggle_mute()
                    else:  # Назад
                        self.settings_mode = False

                    # Применяем и сохраняем настройки
                    audio.apply_volumes()
                    try:
                        audio.settings.save()
                    except Exception as e:
                        print(f"[Audio] WARNING: cannot save settings from menu: {e}")

                    # Воспроизводим звук при клике
                    self.play_ui_sound("ui_button_click")
                    return

    def handle_settings_mouse_motion(self, mouse_pos, audio):
        """Обработка движения мыши при перетаскивании слайдера."""
        if self.dragging_slider is None:
            # Просто подсвечиваем опцию при наведении
            base_y = 180
            for i, opt in enumerate(self.settings_options):
                # Для слайдеров используем увеличенную область взаимодействия
                if opt in ["Громкость MASTER", "Громкость MUSIC", "Громкость SFX"]:
                    slider_x = self.app.screen.get_width() // 2 - self.slider_width // 2
                    slider_y = base_y + i * self.option_spacing + 25
                    # Увеличиваем область взаимодействия для удобства
                    slider_rect = pygame.Rect(slider_x - 10, slider_y - 10, self.slider_width + 20, self.slider_height + 20)

                    if slider_rect.collidepoint(mouse_pos):
                        if self.settings_selected_index != i:
                            self.settings_selected_index = i
                            # Воспроизводим звук при наведении на новую опцию
                            self.play_ui_sound("ui_menu_move")
                        return
                else:
                    # Для кнопок используем тот же размер, что и в отрисовке
                    button_width = 300
                    button_height = 50
                    button_x = self.app.screen.get_width() // 2 - button_width // 2
                    button_y = base_y + i * 60 - 25
                    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

                    if button_rect.collidepoint(mouse_pos):
                        if self.settings_selected_index != i:
                            self.settings_selected_index = i
                            # Воспроизводим звук при наведении на новую опцию
                            self.play_ui_sound("ui_menu_move")
                        return
            return

        # Обработка перетаскивания слайдера
        slider_x = self.app.screen.get_width() // 2 - self.slider_width // 2

        # Вычисляем новое значение громкости на основе позиции мыши
        # Добавляем небольшой зазор для более точного управления
        relative_x = mouse_pos[0] - slider_x
        new_volume = max(0.0, min(1.0, relative_x / self.slider_width))

        # Применяем новое значение
        if self.dragging_slider == "master":
            audio.set_master_volume(new_volume)
        elif self.dragging_slider == "music":
            audio.set_music_volume(new_volume)
        elif self.dragging_slider == "sfx":
            audio.set_sfx_volume(new_volume)

        # Применяем и сохраняем настройки
        audio.apply_volumes()
        try:
            audio.settings.save()
        except Exception as e:
            print(f"[Audio] WARNING: cannot save settings from menu: {e}")

    def draw_settings(self, screen):
        """Отрисовка простого меню аудио-настроек."""
        # Draw the background image if available, otherwise use fallback color
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((20, 20, 40))

        # Create a semi-transparent overlay for better text visibility
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))  # Semi-transparent black overlay
        screen.blit(overlay, (0, 0))

        title = self.title_font.render("НАСТРОЙКИ ЗВУКА", True, (255, 255, 255))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 60))

        audio = getattr(self.app, "audio", None)
        if audio is None:
            info = self.font.render("Аудиосистема недоступна", True, (255, 100, 100))
            screen.blit(
                info,
                (screen.get_width() // 2 - info.get_width() // 2, 200),
            )
            return

        base_y = 180
        slider_x = screen.get_width() // 2 - self.slider_width // 2

        for i, opt in enumerate(self.settings_options):
            is_selected = i == self.settings_selected_index
            color = (255, 255, 0) if is_selected else (220, 220, 220)

            # Рисуем текст опции
            if opt in ["Громкость MASTER", "Громкость MUSIC", "Громкость SFX"]:
                # Для опций громкости рисуем текст и слайдер
                volume_value = 0.0
                if opt == "Громкость MASTER":
                    volume_value = audio.settings.master_volume
                elif opt == "Громкость MUSIC":
                    volume_value = audio.settings.music_volume
                elif opt == "Громкость SFX":
                    volume_value = audio.settings.sfx_volume

                # Рисуем название опции
                label_text = opt.replace("Громкость ", "")
                text = self.font.render(f"{label_text}: {int(volume_value * 100)}%", True, color)
                text_rect = text.get_rect(center=(screen.get_width() // 2, base_y + i * self.option_spacing))
                screen.blit(text, text_rect)

                # Рисуем слайдер
                slider_y = base_y + i * self.option_spacing + 35
                
                # Тень слайдера
                shadow_rect = pygame.Rect(slider_x + 2, slider_y + 2, self.slider_width, self.slider_height)
                pygame.draw.rect(screen, (10, 10, 20), shadow_rect, border_radius=10)
                
                # Фон слайдера с закругленными углами
                bg_rect = pygame.Rect(slider_x, slider_y, self.slider_width, self.slider_height)
                pygame.draw.rect(screen, (60, 60, 80), bg_rect, border_radius=10)
                
                # Заполненная часть слайдера с градиентом
                fill_width = int(self.slider_width * volume_value)
                if fill_width > 0:
                    fill_rect = pygame.Rect(slider_x, slider_y, fill_width, self.slider_height)
                    # Цвет в зависимости от типа
                    if "MASTER" in opt:
                        fill_color = (100, 200, 255)  # Голубой
                    elif "MUSIC" in opt:
                        fill_color = (100, 255, 150)  # Зеленый
                    else:  # SFX
                        fill_color = (255, 150, 100)  # Оранжевый
                    pygame.draw.rect(screen, fill_color, fill_rect, border_radius=10)
                
                # Ручка слайдера с обводкой
                handle_x = slider_x + fill_width
                handle_size = 28
                handle_rect = pygame.Rect(handle_x - handle_size // 2, slider_y - 4, handle_size, self.slider_height + 8)
                
                # Тень ручки
                shadow_handle = pygame.Rect(handle_rect.x + 2, handle_rect.y + 2, handle_rect.width, handle_rect.height)
                pygame.draw.rect(screen, (10, 10, 20), shadow_handle, border_radius=handle_size // 2)
                
                # Основная ручка
                pygame.draw.rect(screen, (240, 240, 240), handle_rect, border_radius=handle_size // 2)
                
                # Обводка ручки
                if is_selected:
                    pygame.draw.rect(screen, (255, 255, 0), handle_rect, 3, border_radius=handle_size // 2)
                else:
                    pygame.draw.rect(screen, (180, 180, 200), handle_rect, 2, border_radius=handle_size // 2)

                # Подсветка при выборе - рамка вокруг всего элемента
                if is_selected:
                    selection_rect = pygame.Rect(slider_x - 15, base_y + i * self.option_spacing - 15, 
                                                  self.slider_width + 30, 65)
                    pygame.draw.rect(screen, (255, 255, 0), selection_rect, 2, border_radius=10)
            else:
                # Для других опций рисуем кнопки как в главном меню
                button_width = 300
                button_height = 50
                button_x = screen.get_width() // 2 - button_width // 2
                button_y = base_y + i * 60 - 25
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

                # Draw button background with highlight for selected item
                if is_selected:
                    pygame.draw.rect(screen, (100, 100, 100, 180), button_rect, border_radius=10)
                    pygame.draw.rect(screen, (255, 255, 255), button_rect, 3, border_radius=10)
                else:
                    pygame.draw.rect(screen, (50, 50, 50, 180), button_rect, border_radius=10)
                    pygame.draw.rect(screen, (200, 200, 200), button_rect, 2, border_radius=10)

                # Draw text
                label = opt
                if opt == "Mute / Unmute":
                    label = f"{opt}: {'ON' if audio.settings.muted else 'OFF'}"
                text = self.font.render(label, True, color)
                text_rect = text.get_rect(center=(screen.get_width() // 2, base_y + i * self.option_spacing))
                screen.blit(text, text_rect)

                # Подсветка при выборе
                if is_selected:
                    pygame.draw.rect(
                        screen,
                        (255, 255, 0),
                        text_rect.inflate(20, 10),
                        2,
                        border_radius=5,
                    )
