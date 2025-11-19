import os
import pygame

from .music_manager import MusicManager
from .sfx_manager import SFXManager
from .settings import AudioSettings


class AudioManager:
    """
    Central audio system facade.

    Responsibilities:
    - Initialize pygame.mixer with safe defaults
    - Hold global AudioSettings
    - Provide access to MusicManager and SFXManager
    - Apply settings (volume, mute) globally
    - Simple API for game states to interact with audio
    """

    _instance = None

    @classmethod
    def get_instance(cls, base_path: str = None) -> "AudioManager":
        """
        Singleton accessor.

        base_path:
            Root path used to resolve audio assets. If None,
            defaults to directory containing this file.
        """
        if cls._instance is None:
            cls._instance = AudioManager(base_path=base_path)
        return cls._instance

    def __init__(self, base_path: str = None):
        if AudioManager._instance is not None:
            raise RuntimeError(
                "Use AudioManager.get_instance() instead of direct instantiation."
            )

        # Resolve audio root
        module_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = base_path or module_dir

        # Settings
        # Загружаем сохранённые значения, если файл настроек уже существует
        self.settings = AudioSettings.load()

        # Initialize pygame.mixer safely
        self._init_mixer()

        # Managers
        self.music = MusicManager(self)
        self.sfx = SFXManager(self)

        # Load core assets (lazy where possible, but we can preload essentials)
        self._register_default_assets()

        # Применяем уровни громкости к микшеру сразу после инициализации
        self.apply_volumes()

    # ---------- Initialization ----------

    def _init_mixer(self):
        """
        Initialize pygame.mixer with error handling.
        If initialization fails, audio methods degrade gracefully.
        """
        self.mixer_initialized = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.mixer_initialized = True
        except Exception as e:
            print(f"[Audio] WARNING: Failed to initialize mixer: {e}")
            self.mixer_initialized = False

    def _register_default_assets(self):
        """
        Register known music and SFX asset paths in managers.
        Actual loading is lazy with error handling.
        """
        # Music
        self.music.register_track(
            "menu",
            os.path.join(self.base_path, "music", "menu_theme.mp3"),
        )
        self.music.register_track(
            "level1",
            os.path.join(self.base_path, "music", "game_level1.mp3"),
        )
        self.music.register_track(
            "victory",
            os.path.join(self.base_path, "music", "victory_theme.mp3"),
        )

        # SFX: organized by category
        sfx_root = os.path.join(self.base_path, "sfx")

        # Player SFX
        self.sfx.register_sound(
            "player_jump", os.path.join(sfx_root, "player", "jump.wav")
        )
        self.sfx.register_sound(
            "player_walk", os.path.join(sfx_root, "player", "walk.wav")
        )
        self.sfx.register_sound(
            "player_collect_coin", os.path.join(sfx_root, "player", "collect_coin.wav")
        )
        self.sfx.register_sound(
            "player_take_damage", os.path.join(sfx_root, "player", "take_damage.wav")
        )
        self.sfx.register_sound(
            "player_death", os.path.join(sfx_root, "player", "death.wav")
        )

        # Enemy SFX
        self.sfx.register_sound(
            "enemy_slime_move", os.path.join(sfx_root, "enemies", "slime_move.wav")
        )
        self.sfx.register_sound(
            "enemy_death", os.path.join(sfx_root, "enemies", "enemy_death.wav")
        )
        self.sfx.register_sound(
            "enemy_hit", os.path.join(sfx_root, "enemies", "enemy_hit.wav")
        )
        self.sfx.register_sound(
            "fly_buzz", os.path.join(sfx_root, "enemies", "fly_buzz.wav")
        )

        # UI SFX
        self.sfx.register_sound(
            "ui_button_click", os.path.join(sfx_root, "ui", "button_click.wav")
        )
        self.sfx.register_sound(
            "ui_menu_move", os.path.join(sfx_root, "ui", "menu_move.wav")
        )

    # ---------- Global Controls ----------

    def set_master_volume(self, volume: float):
        """
        Set global master volume [0.0, 1.0].
        Adjusts music + sfx volumes according to settings.
        """
        self.settings.set_master_volume(volume)
        self.apply_volumes()

    def set_music_volume(self, volume: float):
        self.settings.set_music_volume(volume)
        self.apply_volumes()

    def set_sfx_volume(self, volume: float):
        self.settings.set_sfx_volume(volume)
        self.apply_volumes()

    def mute_all(self):
        self.settings.muted = True
        self.apply_volumes()

    def unmute_all(self):
        self.settings.muted = False
        self.apply_volumes()

    def toggle_mute(self):
        self.settings.muted = not self.settings.muted
        self.apply_volumes()

    def apply_volumes(self):
        """
        Apply current settings to pygame.mixer + managers.
        """
        if not self.mixer_initialized:
            return

        effective_music = self.settings.get_effective_music_volume()
        effective_sfx = self.settings.get_effective_sfx_volume()

        print(
            "[Audio] apply_volumes: "
            f"master={self.settings.master_volume:.2f} "
            f"music={self.settings.music_volume:.2f} "
            f"sfx={self.settings.sfx_volume:.2f} "
            f"muted={self.settings.muted} -> "
            f"eff_music={effective_music:.2f} eff_sfx={effective_sfx:.2f}"
        )

        # Music volume (pygame.mixer.music is global)
        self.music.apply_volume(effective_music)

        # SFX volume (per sound / channel)
        self.sfx.apply_volume(effective_sfx)

    # ---------- State helpers (for game integration) ----------

    def on_menu_enter(self):
        """
        Call when switching to menu state.
        """
        if not self.mixer_initialized:
            return
        self.music.play("menu", loop=-1, fade_ms=500)

    def on_game_start(self, level_name: str = "level1"):
        """
        Call when entering gameplay.
        """
        if not self.mixer_initialized:
            return
        # Dynamic music selection by level name
        track_key = f"level_{level_name}"
        if track_key not in self.music.tracks:
            track_key = "level1"
        self.music.play(track_key, loop=-1, fade_ms=500)

    def on_level_complete(self):
        """
        Call on victory / level completion.
        """
        if not self.mixer_initialized:
            return
        self.music.play("victory", loop=0, fade_ms=300)

    def on_pause(self):
        """
        Optional: Muffle or pause music when pausing.
        """
        if not self.mixer_initialized:
            return
        self.music.fade_to_volume(0.3, duration_ms=300)

    def on_resume(self):
        """
        Restore volume after pause.
        """
        if not self.mixer_initialized:
            return
        self.apply_volumes()

    # ---------- Shutdown ----------

    def shutdown(self):
        """
        Stop all sounds and quit mixer gracefully.
        """
        if not self.mixer_initialized:
            return
        try:
            self.music.stop()
            self.sfx.stop_all()
            pygame.mixer.quit()
        except Exception as e:
            print(f"[Audio] WARNING: error during shutdown: {e}")


__all__ = ["AudioManager"]
