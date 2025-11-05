import pygame

class MainMenu:
    def __init__(self, app):
        self.app = app
        self.selected_index = 0
        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 72)
        
        print("📋 MainMenu initialized")
        print(f"📱 Menu app reference: {self.app}")
    
    def get_menu_options(self):
        """Получение опций меню в зависимости от состояния игры"""
        if self.app.has_active_game:
            return ["Продолжить игру", "Новая игра", "Загрузить", "Настройки", "Выход"]
        else:
            return ["Новая игра", "Загрузить", "Настройки", "Выход"]
    
    @property
    def options(self):
        """Получение текущих опций меню"""
        return self.get_menu_options()
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            print(f"⌨️ Key pressed: {pygame.key.name(event.key)}")
            
            if event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
                print(f"🎮 Menu selection: {self.options[self.selected_index]}")
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
                print(f"🎮 Menu selection: {self.options[self.selected_index]}")
            elif event.key == pygame.K_RETURN:
                print(f"🎮 Menu selected: {self.options[self.selected_index]}")
                self.select_option()
        
        # Добавляем обработку мыши
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левая кнопка мыши
            mouse_pos = pygame.mouse.get_pos()
            print(f"🖱️ Mouse clicked at: {mouse_pos}")
            self.handle_mouse_click(mouse_pos)
        
        # Подсветка при наведении мышью
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.handle_mouse_hover(mouse_pos)
    
    def handle_mouse_click(self, mouse_pos):
        """Обработка клика мышью"""
        for i, option in enumerate(self.options):
            text = self.font.render(option, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.app.screen.get_width()//2, 250 + i * 60))
            
            print(f"🔍 Checking option '{option}' at rect: {text_rect}")
            
            if text_rect.collidepoint(mouse_pos):
                print(f"🎯 Mouse clicked on: {option}")
                self.selected_index = i
                self.select_option()
                return True
        
        print("❌ No menu option clicked")
        return False
    
    def handle_mouse_hover(self, mouse_pos):
        """Подсветка при наведении мышью"""
        for i, option in enumerate(self.options):
            text = self.font.render(option, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.app.screen.get_width()//2, 250 + i * 60))
            
            if text_rect.collidepoint(mouse_pos):
                if self.selected_index != i:
                    self.selected_index = i
                    print(f"🖱️ Mouse over: {option}")
                break
    
    def select_option(self):
        option = self.options[self.selected_index]
        print(f"🚀 Executing menu action: {option}")
        print(f"📱 App reference in select_option: {self.app}")
        
        if option == "Продолжить игру":
            print("🔄 Continuing existing game...")
            self.app.resume_game()
        elif option == "Новая игра":
            print("🎮 Starting new game...")
            self.app.start_game()
        elif option == "Загрузить":
            print("📂 Load game (not implemented)")
        elif option == "Настройки":
            print("⚙️ Settings (not implemented)")
        elif option == "Выход":
            print("👋 Exiting game...")
            self.app.running = False
    
    def update(self, dt):
        pass
    
    def draw(self, screen):
        screen.fill((30, 30, 60))
        
        # Заголовок
        title = self.title_font.render("RPG PLATFORMER", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        
        # Опции меню
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(screen.get_width()//2, 250 + i * 60))
            screen.blit(text, text_rect)
            
            # Отладочная рамка (временно)
            debug_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(screen, (255, 0, 0), debug_rect, 1)
