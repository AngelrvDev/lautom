import logging
import os


LOGGER = logging.getLogger(__name__)


def remove_temp_file(file: str, path: str):
    try:
        os.remove(f"{path}/{file}")
        LOGGER.info(f"Archivo temporal eliminado: {path}/{file}")
    except FileNotFoundError:
        LOGGER.warning(f"El archivo temporal no fue encontrado: {path}/{file}")
    except PermissionError:
        LOGGER.error(f"Sin permisos para eliminar el archivo temporal: {path}/{file}")
