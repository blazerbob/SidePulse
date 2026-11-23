from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import psutil


@dataclass(frozen=True)
class Sample:
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    cpu_temp_c: float | None
    gpu_temp_c: float | None


class TemperatureProvider:
    """Best-effort temperature reader with optional hardware dependencies."""

    def __init__(self) -> None:
        self._lhm_reader = self._load_lhm()
        self._nvml_reader = self._load_nvml()

    @staticmethod
    def _load_lhm() -> Callable[[str], float | None] | None:
        try:
            from pathlib import Path

            import clr  # type: ignore[import-not-found]

            dll = Path(__file__).resolve().parents[1] / "lib" / "LibreHardwareMonitorLib.dll"
            if not dll.exists():
                return None
            clr.AddReference(str(dll))
            from LibreHardwareMonitor.Hardware import Computer  # type: ignore[import-not-found]

            computer = Computer()
            computer.IsCpuEnabled = True
            computer.IsGpuEnabled = True
            computer.Open()

            def read(kind: str) -> float | None:
                values: list[float] = []
                for hardware in computer.Hardware:
                    hardware.Update()
                    is_cpu = kind == "cpu" and hardware.HardwareType.ToString() == "Cpu"
                    is_gpu = kind == "gpu" and "Gpu" in hardware.HardwareType.ToString()
                    if not (is_cpu or is_gpu):
                        continue
                    for sensor in hardware.Sensors:
                        if (
                            sensor.SensorType.ToString() == "Temperature"
                            and sensor.Value is not None
                        ):
                            values.append(float(sensor.Value))
                return min(values) if values else None

            return read
        except Exception:
            return None

    @staticmethod
    def _load_nvml() -> Callable[[], float | None] | None:
        try:
            import pynvml  # type: ignore[import-not-found]

            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)

            def read() -> float | None:
                try:
                    return float(
                        pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    )
                except Exception:
                    return None

            return read
        except Exception:
            return None

    def read(self, kind: str) -> float | None:
        if self._lhm_reader:
            value = self._lhm_reader(kind)
            if value is not None:
                return value
        if kind == "gpu" and self._nvml_reader:
            return self._nvml_reader()
        return None


class MetricsCollector:
    def __init__(self, provider: TemperatureProvider | None = None) -> None:
        self.provider = provider or TemperatureProvider()

    def read(self) -> Sample:
        memory = psutil.virtual_memory()
        return Sample(
            ram_percent=float(memory.percent),
            ram_used_gb=memory.used / (1024**3),
            ram_total_gb=memory.total / (1024**3),
            cpu_temp_c=self.provider.read("cpu"),
            gpu_temp_c=self.provider.read("gpu"),
        )


def level(value: float | None, thresholds: tuple[float, float]) -> str:
    if value is None:
        return "unknown"
    if value < thresholds[0]:
        return "good"
    if value < thresholds[1]:
        return "warn"
    return "danger"
