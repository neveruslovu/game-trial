import os
import pygame
from typing import Dict, Optional


class MusicManager:
    """
    Handles background music:
    - Track registry by key
    - Lazy loading with error handling
    - Crossfade between tracks
    - Volume control hooks (driven by AudioManager)
    """

    def __init__(self, audio_manager: "AudioManager"):
        self.audio_manager = audio_manager
        self.tracks: Dict[str, str] = {}  # key -> filepath
        self.current_key: Optional[str] = None
        self.default_fade_ms = 500
        self._last_set_volume = 1.0

    # ---------- Registry ----------

    def register_track(self, key: str, path: str):
        self.tracks[key] = path

    # ---------- Core Controls ----------

    def play(self, key: str, loop: int = -1, fade_ms: int = None):
        """
        Play a registered track by key.
        loop: -1 for infinite, 0 for once, etc.
        """
        if key not in self.tracks:
            print(f"[Music] WARNING: Track '{key}' is not registered.")
            return

        if not pygame.mixer.get_init():
            return

        path = self.tracks[key]
        if not os.path.exists(path):
            print(f"[Music] WARNING: File not found for '{key}': {path}")
            return

        try:
            fade = fade_ms if fade_ms is not None else self.default_fade_ms
            # If something is already playing, fade out then load
            if pygame.mixer.music.get_busy() and self.current_key != key:
                pygame.mixer.music.fadeout(fade)

            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops=loop, fade_ms=fade)
            self.current_key = key
            # Re-apply volume after load
            pygame.mixer.music.set_volume(self._last_set_volume)
        except Exception as e:
            print(f"[Music] ERROR: Failed to play '{key}' ({path}): {e}")

    def stop(self):
        if not pygame.mixer.get_init():
            return
        try:
            pygame.mixer.music.stop()
            self.current_key = None
        except Exception as e:
            print(f"[Music] WARNING: Failed to stop music: {e}")

    def pause(self):
        if not pygame.mixer.get_init():
            return
        try:
            pygame.mixer.music.pause()
        except Exception as e:
            print(f"[Music] WARNING: Failed to pause music: {e}")

    def resume(self):
        if not pygame.mixer.get_init():
            return
        try:
            pygame.mixer.music.unpause()
        except Exception as e:
            print(f"[Music] WARNING: Failed to resume music: {e}")

    # ---------- Volume / Crossfade ----------

    def apply_volume(self, volume: float):
        """
        Set music volume [0.0, 1.0].
        """
        if not pygame.mixer.get_init():
            return
        self._last_set_volume = max(0.0, min(1.0, float(volume)))
        try:
            pygame.mixer.music.set_volume(self._last_set_volume)
        except Exception as e:
            print(f"[Music] WARNING: Failed to set volume: {e}")

    def fade_to_volume(self, target_volume: float, duration_ms: int):
        """
        Approximate fade by using pygame.mixer.music.set_volume over time.
        For now, this is a stub-friendly API; actual timed interpolation
        can be implemented via update hooks if needed.
        """
        # Simple immediate set; hook for future advanced fade implementation.
        self.apply_volume(target_volume)


__all__ = ["MusicManager"]
