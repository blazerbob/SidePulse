from __future__ import annotations

import threading
from collections.abc import Callable


def start_tray(
    show: Callable[[], None], hide: Callable[[], None], close: Callable[[], None]
) -> threading.Thread | None:
    try:
        import pystray
        from PIL import Image, ImageDraw
    except ImportError:
        return None

    image = Image.new("RGBA", (64, 64), "#10151c")
    draw = ImageDraw.Draw(image)
    draw.ellipse((12, 12, 52, 52), fill="#65d48b")
    draw.ellipse((24, 24, 40, 40), fill="#10151c")
    menu = pystray.Menu(
        pystray.MenuItem("Показать", lambda _icon, _item: show()),
        pystray.MenuItem("Скрыть", lambda _icon, _item: hide()),
        pystray.MenuItem("Выход", lambda icon, _item: (icon.stop(), close())),
    )
    icon = pystray.Icon("SidePulse", image, "SidePulse", menu)
    thread = threading.Thread(target=icon.run, daemon=True)
    thread.start()
    return thread
