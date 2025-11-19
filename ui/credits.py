import pygame


class Credits:
    """Simple credits screen implementation."""

    def __init__(self, app):
        self.app = app
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.credits_text = [
            "2D PLATFORMER",
            "",
            "Разработано с любовью",
            "",
            "Программирование: neveruslovu",
            "",
            "Нажмите ESC для возврата в меню",
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.go_to_menu()

    def draw(self, screen):
        # Draw background
        if hasattr(self.app.menu, "background") and self.app.menu.background:
            screen.blit(self.app.menu.background, (0, 0))
        else:
            screen.fill((30, 30, 60))

        # Create a semi-transparent overlay for better text visibility
        overlay = pygame.Surface(
            (screen.get_width(), screen.get_height()), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 80))  # Semi-transparent black overlay
        screen.blit(overlay, (0, 0))

        # Draw credits text
        y_offset = 150
        for line in self.credits_text:
            if line == "2D PLATFORMER":
                text = self.title_font.render(line, True, (255, 255, 255))
            else:
                text = self.font.render(line, True, (255, 255, 255))

            text_rect = text.get_rect(center=(screen.get_width() // 2, y_offset))
            screen.blit(text, text_rect)

            y_offset += 50
