from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from src.core.config import Config
from src.core.metrics import MetricsCollector, Sample, level

COLORS = {"good": "#65d48b", "warn": "#f5c451", "danger": "#ff6b6b", "unknown": "#a9b4c2"}


class SidePanel:
    def __init__(
        self, root: tk.Tk, collector: MetricsCollector, config: Config, on_close: Callable[[], None]
    ) -> None:
        self.root = root
        self.collector = collector
        self.config = config
        self.on_close = on_close
        self.drag_offset: tuple[int, int] | None = None
        self.labels: dict[str, tk.Label] = {}

        root.title("SidePulse")
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", config.opacity)
        root.configure(bg="#10151c")
        root.geometry(self._geometry())

        frame = tk.Frame(root, bg="#10151c", padx=14, pady=12)
        frame.pack(fill="both", expand=True)
        title = tk.Label(
            frame, text="SIDEPULSE", fg="#8da2ba", bg="#10151c", font=("Segoe UI", 9, "bold")
        )
        title.pack(anchor="w", pady=(0, 8))
        title.bind("<ButtonPress-1>", self._start_drag)
        title.bind("<B1-Motion>", self._drag)

        for key, caption in (("ram", "ОЗУ"), ("cpu", "CPU"), ("gpu", "GPU")):
            row = tk.Frame(frame, bg="#10151c")
            row.pack(fill="x", pady=3)
            tk.Label(row, text=caption, fg="#8da2ba", bg="#10151c", font=("Segoe UI", 9)).pack(
                anchor="w"
            )
            label = tk.Label(
                row, text="...", fg="#a9b4c2", bg="#10151c", font=("Segoe UI", 16, "bold")
            )
            label.pack(anchor="w")
            label.bind("<ButtonPress-1>", self._start_drag)
            label.bind("<B1-Motion>", self._drag)
            self.labels[key] = label

        hint = tk.Label(
            frame,
            text="ПКМ — скрыть   Esc — выход",
            fg="#596879",
            bg="#10151c",
            font=("Segoe UI", 8),
        )
        hint.pack(anchor="w", pady=(9, 0))
        root.bind("<Button-3>", lambda _event: self.hide())
        root.bind("<Escape>", lambda _event: self.close())
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.update()

    def _geometry(self) -> str:
        x = self.config.position.x
        y = self.config.position.y
        if x is None or y is None:
            self.root.update_idletasks()
            screen_w = self.root.winfo_screenwidth()
            x, y = screen_w - 190, 180
        return f"180x205+{x}+{y}"

    def _start_drag(self, event: tk.Event) -> None:
        self.drag_offset = (event.x_root - self.root.winfo_x(), event.y_root - self.root.winfo_y())

    def _drag(self, event: tk.Event) -> None:
        if self.drag_offset:
            x = event.x_root - self.drag_offset[0]
            y = event.y_root - self.drag_offset[1]
            self.root.geometry(f"+{x}+{y}")

    def update(self) -> None:
        try:
            sample = self.collector.read()
            self._render(sample)
        except Exception:
            for label in self.labels.values():
                label.configure(text="n/a", fg=COLORS["unknown"])
        self.root.after(self.config.interval_ms, self.update)

    def _render(self, sample: Sample) -> None:
        self.labels["ram"].configure(
            text=f"{sample.ram_percent:.0f}%  {sample.ram_used_gb:.1f}/{sample.ram_total_gb:.1f} ГБ",
            fg=COLORS[level(sample.ram_percent, self.config.thresholds["ram"])],
        )
        for key, value in (("cpu", sample.cpu_temp_c), ("gpu", sample.gpu_temp_c)):
            text = "n/a" if value is None else f"{value:.0f}°C"
            self.labels[key].configure(
                text=text, fg=COLORS[level(value, self.config.thresholds[key])]
            )

    def hide(self) -> None:
        self.root.withdraw()

    def show(self) -> None:
        self.root.deiconify()
        self.root.attributes("-topmost", True)

    def close(self) -> None:
        self.config.position.x = self.root.winfo_x()
        self.config.position.y = self.root.winfo_y()
        self.config.save()
        self.on_close()
