from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Position:
    x: int | None = None
    y: int | None = None


@dataclass
class Config:
    interval_ms: int = 1000
    opacity: float = 0.88
    theme: str = "dark"
    position: Position = field(default_factory=Position)
    thresholds: dict[str, tuple[float, float]] = field(
        default_factory=lambda: {"cpu": (60.0, 80.0), "gpu": (60.0, 80.0), "ram": (70.0, 90.0)}
    )

    @property
    def path(self) -> Path:
        base = os.environ.get("APPDATA") or str(Path.home() / ".config")
        return Path(base) / "SidePulse" / "config.json"

    def save(self, path: Path | None = None) -> Path:
        target = path or self.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        return target

    @classmethod
    def load(cls, path: Path | None = None) -> "Config":
        target = path or cls().path
        if not target.exists():
            return cls()
        try:
            raw = json.loads(target.read_text(encoding="utf-8"))
            position = raw.get("position", {})
            thresholds = raw.get("thresholds", {})
            defaults = cls()
            return cls(
                interval_ms=max(250, int(raw.get("interval_ms", defaults.interval_ms))),
                opacity=min(1.0, max(0.35, float(raw.get("opacity", defaults.opacity)))),
                theme=str(raw.get("theme", defaults.theme)),
                position=Position(position.get("x"), position.get("y")),
                thresholds={
                    key: tuple(thresholds.get(key, defaults.thresholds[key]))
                    for key in defaults.thresholds
                },
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return cls()
