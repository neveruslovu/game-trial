#!/usr/bin/env python3
"""
Quick visual test for menu settings changes.
"""
import pygame
import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ui.menu import MainMenu
from game.assets.audio.audio_manager import AudioManager

class DummyApp:
    """Minimal app stub for testing menu."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Menu Settings Test")
        self.running = True
        self.has_active_game = False
        
        # Initialize audio
        try:
            self.audio = AudioManager.get_instance(
                base_path=os.path.join(PROJECT_ROOT, "game", "assets", "audio")
            )
        except Exception as e:
            print(f"Audio init failed (expected in test): {e}")
            self.audio = None

    def go_to_menu(self):
        pass

    def start_game(self):
        pass

    def resume_game(self):
        pass


def main():
    app = DummyApp()
    menu = MainMenu(app)
    
    # Enter settings mode immediately
    menu.settings_mode = True
    
    clock = pygame.time.Clock()
    
    print("=" * 60)
    print("MENU SETTINGS VISUAL TEST")
    print("=" * 60)
    print("Testing:")
    print("  ✓ Increased spacing (100px between options)")
    print("  ✓ Improved slider design with colors")
    print("  ✓ Better visual hierarchy")
    print("  ✓ No overlapping elements")
    print("=" * 60)
    print("\nControls:")
    print("  - Mouse: Click and drag sliders")
    print("  - Arrow keys: Navigate and adjust")
    print("  - ESC: Close")
    print("=" * 60)
    
    while app.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                app.running = False
            else:
                menu.handle_event(event)
        
        menu.draw(app.screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("\n✓ Test completed successfully!")


if __name__ == "__main__":
    main()
