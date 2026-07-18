import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from core import remove_temp_file
from core.env import CSV_PATH, EXCEL_PATH
from core.logger import setup_logging
from core.email import send_message
from core.downcsv import download_csv
from core.excel import convert_to_excel, tab_dinamica


LOGGER = logging.getLogger(__name__)


def non_negative_int(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("debe ser un número entero")

    if number < 0:
        raise argparse.ArgumentTypeError("debe ser mayor o igual a cero")
    return number


def parse_arguments(arguments=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", help="Ruta al archivo JSON de configuración")
    parser.add_argument(
        "--days-ago",
        type=non_negative_int,
        default=0,
        help="Días a restar a la fecha de consulta y del archivo (predeterminado: 0)",
    )
    return parser.parse_args(arguments)


def automatizacion(conf, days_ago=0, current_date=None):
    LOGGER.warning(f"Iniciando el proceso para:  {conf['subject']}")

    if not isinstance(conf.get("tabla_dinamica", False), bool):
        raise ValueError("tabla_dinamica debe ser true o false")

    current_date = current_date or datetime.now()
    report_date = current_date - timedelta(days=days_ago)
    DATE = report_date.strftime("%d-%m-%y")
    DATE_QUERY = report_date.strftime("%Y-%m-%d") + " 06:00:00"
    FILES = []

    for file in conf["files"]:
        file_name = file["name"] + "_" + DATE

        QUERY = file["query"]
        QUERY = QUERY.replace("{DATE}", DATE_QUERY)

        # ----- 1 Descargar CSV --------------------------
        exito = download_csv(
            host=file["host"], query=QUERY, file_name=file_name
        )

        if not exito:
            LOGGER.warning(
                f"Saltando reporte {file_name} debido a error en servidor {file['host']}"
            )
            continue

        # ----- 2 Convertir a EXCEL ---------------------
        convert_to_excel(file_name=file_name)

        excel_file = Path(f"{EXCEL_PATH}/{file_name}.xlsx")
        if conf.get("tabla_dinamica") and excel_file.is_file():
            tab_dinamica(str(excel_file))

        # ------ Eliminar el csv temporal -------------
        file = f"{file_name}.csv"
        remove_temp_file(file=file, path=CSV_PATH)

        if excel_file.is_file():
            FILES.append(file_name)

    # ----- 3 Enviar correo -----------------------------
    send_message(
        subject=conf["subject"],
        message=conf["message"],
        address=conf["address"],
        files=FILES,
    )
    print(FILES)
    # Limpiando archivos temporales
    for file in FILES:
        file = f"{file}.xlsx"
        remove_temp_file(file=file, path=EXCEL_PATH)


if __name__ == "__main__":
    setup_logging()
    try:
        arguments = parse_arguments()
        config_path = arguments.config_path

        if os.path.getsize(config_path) == 0:
            print("El archivo JSON está vacío")
            LOGGER.warning(f"El archivo {config_path} está vacío")
            sys.exit(1)

        # Leer JSON
        with open(config_path, "r", encoding="latin-1") as f:
            data = json.load(f)

        for conf in data:
            automatizacion(conf, days_ago=arguments.days_ago)

    except Exception as e:
        LOGGER.error(f"{e}")
