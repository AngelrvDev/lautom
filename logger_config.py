import logging
import os


def setup_logging():
    # Evita duplicar handlers si se llama más de una vez
    root = logging.getLogger()
    if root.handlers:
        return

    handlers = [logging.FileHandler("app.log")]

    # Activar consola con variable de entorno
    if os.getenv("LOG_CONSOLE", "false").lower() == "true":
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
