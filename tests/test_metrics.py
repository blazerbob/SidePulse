from types import SimpleNamespace

import src.core.metrics as metrics


class Provider:
    def read(self, kind: str) -> float | None:
        return {"cpu": 55.0, "gpu": None}[kind]


def test_collector_converts_memory(monkeypatch):
    monkeypatch.setattr(
        metrics.psutil,
        "virtual_memory",
        lambda: SimpleNamespace(percent=62.5, used=4 * 1024**3, total=16 * 1024**3),
    )
    sample = metrics.MetricsCollector(Provider()).read()
    assert sample.ram_percent == 62.5
    assert sample.ram_used_gb == 4
    assert sample.ram_total_gb == 16
    assert sample.cpu_temp_c == 55
    assert sample.gpu_temp_c is None


def test_level_thresholds():
    assert metrics.level(None, (60, 80)) == "unknown"
    assert metrics.level(59.9, (60, 80)) == "good"
    assert metrics.level(60, (60, 80)) == "warn"
    assert metrics.level(80, (60, 80)) == "danger"
