import json
import logging
import os
import sys
from datetime import datetime

from core import convert_to_excel, download_csv, remove_temp_file, send_message
from env import CSV_PATH, EXCEL_PATH
from logger_config import setup_logging

if __name__ == "__main__":
    setup_logging()
    LOGGER = logging.getLogger(__name__)
    try:
        # Verificar que se envió el argumento
        if len(sys.argv) < 2:
            print("Uso: python main.py <ruta_config.json>")
            LOGGER.warning("[USE] python main.py <ruta_config.json>")
            sys.exit(1)

        config_path = sys.argv[1]

        # Leer JSON
        with open(config_path, "r") as f:
            data = json.load(f)

        # Validar que no este vacio en json
        if os.path.getsize(config_path) == 0:
            print("El archivo JSON está vacío")
            LOGGER.warning(f"El archivo {config_path} está vacío")
            exit(1)

        for conf in data:
            LOGGER.warning(f"Iniciando el proceso para:  {conf['subject']}")

            DATE = datetime.now().strftime("%d-%m-%y")
            DATE_QUERY = datetime.now().strftime("%Y-%m-%d") + " 06:00:00"
            FILES = []

            for file in conf["files"]:
                file_name = file["name"] + "_" + DATE

                QUERY = file["query"]
                QUERY = QUERY.replace("{DATE}", DATE_QUERY)

                # ----- 1 Descargar CSV --------------------------
                download_csv(host=file["host"], query=QUERY, file_name=file_name)

                # ----- 2 Convertir a EXCEL ---------------------
                convert_to_excel(file_name=file_name)

                # ------ Eliminar el csv temporal -------------
                file = f"{file_name}.csv"
                remove_temp_file(file=file, path=CSV_PATH)

                FILES.append(file_name)

            # ----- 3 Enviar correo -----------------------------
            send_message(
                subject=conf["subject"],
                message=conf["message"],
                address=conf["address"],
                files=FILES,
            )

            # Limpiando archivos temporales
            for file in FILES:
                file = f"{file}.xlsx"
                remove_temp_file(file=file, path=CSV_PATH)

    except Exception as e:
        LOGGER.error(f"{e}")
