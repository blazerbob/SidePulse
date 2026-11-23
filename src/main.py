from __future__ import annotations

import tkinter as tk

from src.core.config import Config
from src.core.metrics import MetricsCollector
from src.ui.panel import SidePanel
from src.ui.tray import start_tray


def main() -> None:
    config = Config.load()
    root = tk.Tk()
    collector = MetricsCollector()
    panel: SidePanel

    def close() -> None:
        root.destroy()

    panel = SidePanel(root, collector, config, close)
    start_tray(panel.show, panel.hide, close)
    root.mainloop()


if __name__ == "__main__":
    main()
