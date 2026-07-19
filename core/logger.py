from datetime import datetime
from pathlib import Path
from .env import APP_PATH, LOG_CONSOLE
import logging

def setup_logging():
    LOG_PATH = f"{APP_PATH}/log"
    # Crea la carpela log si no existe
    log_path = Path(LOG_PATH)
    log_path.mkdir(parents=True, exist_ok=True)

    # Evita duplicar handlers si se llama más de una vez
    root = logging.getLogger()
    if root.handlers:
        return

    LOG_DATE = datetime.now().strftime("%y-%m-%d")
    handlers: list[logging.Handler] = [
        logging.FileHandler(f"{LOG_PATH}/report-{LOG_DATE}.log")
    ]

    # Activar consola con variable de entorno
    if LOG_CONSOLE == "true":
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
