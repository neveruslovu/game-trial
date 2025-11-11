import os
import pygame
from typing import Dict, Optional, List, Tuple


class SFXManager:
    """
    Handles sound effects:
    - Registry of sound keys to file paths
    - Lazy loading and caching of pygame.mixer.Sound
    - Simple pooling via channels to avoid overlap issues
    - Volume control hooks (driven by AudioManager)
    - Graceful error handling when files are missing
    """

    def __init__(self, audio_manager: "AudioManager"):
        self.audio_manager = audio_manager
        self.sounds: Dict[str, str] = {}  # key -> filepath
        self.cache: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self._last_set_volume = 1.0

        # Basic pool: prepare a limited number of channels for SFX
        self.max_channels = 32
        self._ensure_mixer_channels()

    # ---------- Initialization ----------

    def _ensure_mixer_channels(self):
        if not pygame.mixer.get_init():
            return
        try:
            current = pygame.mixer.get_num_channels()
            if current < self.max_channels:
                pygame.mixer.set_num_channels(self.max_channels)
        except Exception as e:
            print(f"[SFX] WARNING: Failed to set channels: {e}")

    # ---------- Registry ----------

    def register_sound(self, key: str, path: str):
        self.sounds[key] = path

    # ---------- Loading ----------

    def _load_sound(self, key: str) -> Optional[pygame.mixer.Sound]:
        """
        Lazy load a sound and cache it.
        Returns None on error, but caches result to avoid repeated attempts.
        """
        if key in self.cache:
            return self.cache[key]

        if key not in self.sounds:
            print(f"[SFX] WARNING: Sound '{key}' is not registered.")
            self.cache[key] = None
            return None

        if not pygame.mixer.get_init():
            self.cache[key] = None
            return None

        path = self.sounds[key]
        if not os.path.exists(path):
            print(f"[SFX] WARNING: File not found for '{key}': {path}")
            self.cache[key] = None
            return None

        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self._last_set_volume)
            self.cache[key] = sound
            return sound
        except Exception as e:
            print(f"[SFX] ERROR: Failed to load sound '{key}' ({path}): {e}")
            self.cache[key] = None
            return None

    # ---------- Core Controls ----------

    def play(self, key: str, loops: int = 0) -> Optional[pygame.mixer.Channel]:
        """
        Play sound by key once (loops=0) or N extra times.
        Uses first available channel.
        """
        if not pygame.mixer.get_init():
            return None

        sound = self._load_sound(key)
        if sound is None:
            return None

        try:
            channel = sound.play(loops=loops)
            return channel
        except Exception as e:
            print(f"[SFX] WARNING: Failed to play sound '{key}': {e}")
            return None

    def play_at(
        self,
        key: str,
        position: Optional[Tuple[float, float]] = None,
        listener_position: Optional[Tuple[float, float]] = None,
        max_distance: float = 800.0,
    ) -> Optional[pygame.mixer.Channel]:
        """
        Simple positional audio approximation:
        - Adjusts volume and stereo panning based on relative x-position.
        - This is 2D '3D-like' behavior as per plan.
        """
        if not pygame.mixer.get_init():
            return None

        sound = self._load_sound(key)
        if sound is None:
            return None

        try:
            channel = pygame.mixer.find_channel()
            if channel is None:
                # Fallback: let Sound choose channel
                channel = sound.play()
                return channel

            base_volume = self._last_set_volume

            if position is not None and listener_position is not None:
                lx, ly = listener_position
                sx, sy = position
                dx = sx - lx
                dy = sy - ly
                distance = (dx * dx + dy * dy) ** 0.5
                distance = min(distance, max_distance)
                # Volume attenuation based on distance
                vol_scale = 1.0 - (distance / max_distance)
                vol_scale = max(0.0, min(1.0, vol_scale))

                # Simple stereo pan from dx
                if max_distance > 0:
                    pan = max(-1.0, min(1.0, dx / max_distance))
                else:
                    pan = 0.0

                left = base_volume * vol_scale * (1.0 - max(0.0, pan))
                right = base_volume * vol_scale * (1.0 + min(0.0, pan))
                channel.set_volume(left, right)
            else:
                channel.set_volume(base_volume)

            channel.play(sound)
            return channel
        except Exception as e:
            print(f"[SFX] WARNING: Failed positional play for '{key}': {e}")
            return None

    def stop_all(self):
        if not pygame.mixer.get_init():
            return
        try:
            pygame.mixer.stop()
        except Exception as e:
            print(f"[SFX] WARNING: Failed to stop all sounds: {e}")

    # ---------- Volume ----------

    def apply_volume(self, volume: float):
        """
        Apply volume [0.0, 1.0] to all cached sounds.
        """
        if not pygame.mixer.get_init():
            return

        self._last_set_volume = max(0.0, min(1.0, float(volume)))
        for key, sound in self.cache.items():
            if sound is None:
                continue
            try:
                sound.set_volume(self._last_set_volume)
            except Exception as e:
                print(f"[SFX] WARNING: Failed to set volume for '{key}': {e}")


__all__ = ["SFXManager"]
