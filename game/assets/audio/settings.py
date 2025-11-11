import json
import os
from dataclasses import dataclass, asdict


DEFAULT_SETTINGS = {
    "master_volume": 0.8,
    "music_volume": 0.8,
    "sfx_volume": 0.8,
    "muted": False,
}


@dataclass
class AudioSettings:
    master_volume: float = DEFAULT_SETTINGS["master_volume"]
    music_volume: float = DEFAULT_SETTINGS["music_volume"]
    sfx_volume: float = DEFAULT_SETTINGS["sfx_volume"]
    muted: bool = DEFAULT_SETTINGS["muted"]

    def clamp(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    # Volume setters with clamping

    def set_master_volume(self, value: float):
        self.master_volume = self.clamp(value)

    def set_music_volume(self, value: float):
        self.music_volume = self.clamp(value)

    def set_sfx_volume(self, value: float):
        self.sfx_volume = self.clamp(value)

    # Effective volumes (respecting mute)

    def get_effective_music_volume(self) -> float:
        if self.muted:
            return 0.0
        return self.clamp(self.master_volume * self.music_volume)

    def get_effective_sfx_volume(self) -> float:
        if self.muted:
            return 0.0
        return self.clamp(self.master_volume * self.sfx_volume)

    # Persistence helpers

    @staticmethod
    def get_save_path() -> str:
        """
        Store settings JSON in same directory as this module.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "audio_settings.json")

    def save(self):
        try:
            path = self.get_save_path()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=2)
        except Exception as e:
            print(f"[Audio] WARNING: Failed to save audio settings: {e}")

    @classmethod
    def load(cls) -> "AudioSettings":
        path = cls.get_save_path()
        if not os.path.exists(path):
            return cls()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(
                master_volume=float(
                    data.get("master_volume", DEFAULT_SETTINGS["master_volume"])
                ),
                music_volume=float(
                    data.get("music_volume", DEFAULT_SETTINGS["music_volume"])
                ),
                sfx_volume=float(
                    data.get("sfx_volume", DEFAULT_SETTINGS["sfx_volume"])
                ),
                muted=bool(data.get("muted", DEFAULT_SETTINGS["muted"])),
            )
        except Exception as e:
            print(
                f"[Audio] WARNING: Failed to load audio settings, using defaults: {e}"
            )
            return cls()


__all__ = ["AudioSettings"]
