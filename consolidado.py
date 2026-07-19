import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from core import remove_temp_file
from core.downcsv import download_csv
from core.email import send_message
from core.env import CSV_PATH, EXCEL_PATH
from core.excel import merge_csv_to_excel
from core.logger import setup_logging


LOGGER = logging.getLogger(__name__)
SAFE_FILE_NAME = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_config(conf):
    required_fields = ("subject", "message", "address", "output_name", "files")
    missing_fields = [field for field in required_fields if field not in conf]
    if missing_fields:
        raise ValueError(f"Faltan campos requeridos: {', '.join(missing_fields)}")

    if not isinstance(conf["address"], list) or not conf["address"]:
        raise ValueError("address debe ser una lista con al menos un destinatario")
    if not isinstance(conf["files"], list) or not conf["files"]:
        raise ValueError("files debe ser una lista con al menos un origen")
    if not SAFE_FILE_NAME.fullmatch(conf["output_name"]):
        raise ValueError("output_name solo puede contener letras, números, guiones y guiones bajos")

    source_names = []
    for source in conf["files"]:
        if not all(field in source for field in ("host", "name", "query")):
            raise ValueError("Cada elemento de files requiere host, name y query")
        if not SAFE_FILE_NAME.fullmatch(source["name"]):
            raise ValueError("El nombre de cada CSV solo puede contener letras, números y guiones")
        source_names.append(source["name"])

    if len(source_names) != len(set(source_names)):
        raise ValueError("Los nombres de los CSV deben ser únicos")


def automatizacion_consolidada(conf):
    validate_config(conf)
    LOGGER.warning(f"Iniciando proceso consolidado para: {conf['subject']}")

    date = datetime.now().strftime("%d-%m-%y")
    date_query = datetime.now().strftime("%Y-%m-%d") + " 06:00:00"
    output_name = f"{conf['output_name']}_{date}"
    downloaded_files = []

    for source in conf["files"]:
        file_name = f"{source['name']}_{date}"
        query = source["query"].replace("{DATE}", date_query)

        if download_csv(host=source["host"], query=query, file_name=file_name):
            downloaded_files.append(file_name)

    if not merge_csv_to_excel(downloaded_files, output_name):
        return False

    output_file = Path(f"{EXCEL_PATH}/{output_name}.xlsx")
    if not output_file.is_file():
        LOGGER.error(f"No se encontró el Excel consolidado: {output_file}")
        return False

    send_message(
        subject=conf["subject"],
        message=conf["message"],
        address=conf["address"],
        files=[output_name],
    )
    print(output_name)

    for file_name in downloaded_files:
        remove_temp_file(file=f"{file_name}.csv", path=CSV_PATH)
    remove_temp_file(file=f"{output_name}.xlsx", path=EXCEL_PATH)
    return True


def main(config_path):
    if os.path.getsize(config_path) == 0:
        raise ValueError("El archivo JSON está vacío")

    with open(config_path, "r", encoding="latin-1") as config_file:
        configurations = json.load(config_file)

    if not isinstance(configurations, list):
        raise ValueError("El JSON debe contener una lista de configuraciones")

    for conf in configurations:
        try:
            automatizacion_consolidada(conf)
        except Exception as error:
            LOGGER.exception(f"Error en el proceso consolidado: {error}")


if __name__ == "__main__":
    setup_logging()
    if len(sys.argv) < 2:
        print("Uso: python consolidado.py <ruta_config.json>")
        sys.exit(1)

    try:
        main(sys.argv[1])
    except Exception as error:
        LOGGER.error(error)
        sys.exit(1)
