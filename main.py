"""
Culto do Infinito — ponto de entrada (menu → jogo → game over).
"""

from __future__ import annotations

import logging
import sys

from core.game_app import GameApp
from core.game_logging import get_logger, setup_logging


def _global_excepthook(exc_type, exc, tb) -> None:
    logging.getLogger("uncaught").critical(
        "Exceção não tratada", exc_info=(exc_type, exc, tb)
    )


def main() -> None:
    setup_logging()
    sys.excepthook = _global_excepthook
    log = get_logger("main")
    log.info("Jogo iniciado (Culto do Infinito)")
    try:
        app = GameApp()
        app.run()
    except Exception:
        get_logger("main").exception("Falha fatal ao executar o jogo")
        raise
    log.info("Jogo terminado")


if __name__ == "__main__":
    main()
