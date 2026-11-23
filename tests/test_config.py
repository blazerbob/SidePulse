from pathlib import Path

from src.core.config import Config


def test_config_round_trip(tmp_path: Path):
    path = tmp_path / "config.json"
    original = Config(interval_ms=750, opacity=0.7)
    original.position.x = 42
    original.position.y = 99
    original.save(path)

    loaded = Config.load(path)
    assert loaded.interval_ms == 750
    assert loaded.opacity == 0.7
    assert loaded.position.x == 42
    assert loaded.position.y == 99


def test_invalid_config_uses_defaults(tmp_path: Path):
    path = tmp_path / "config.json"
    path.write_text("not json", encoding="utf-8")
    assert Config.load(path).interval_ms == 1000
