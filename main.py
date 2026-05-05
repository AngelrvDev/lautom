import json
import os
from datetime import datetime

from core import convert_to_excel, download_csv, remove_temp_files, send_message
from env import PATH

if __name__ == "__main__":
    try:
        with open("conf.json", "r") as f:
            data = json.load(f)

        for conf in data:
            print(conf["subject"])

            DATE = datetime.now().strftime("%d-%m-%y")
            DATE_QUERY = datetime.now().strftime("%Y-%m-%d") + " 06:00:00"
            FILES = []

            for file in conf["files"]:
                file_name = file["name"] + "_" + DATE

                QUERY = file["query"]
                QUERY = QUERY.replace("{DATE}", DATE_QUERY)

                # ----- 1 Descargar CSV --------------
                download_csv(host=file["host"], query=QUERY, file_name=file_name)

                if os.path.getsize(f"{PATH}/csv/{file_name}.csv") == 0:
                    print(f"{file_name}.csv esta vacio no se pudo convertir a xlsx")
                    continue

                # ----- 2 Convertir a EXCEL -----------
                convert_to_excel(file_name=file_name)

                FILES.append(file_name)

            if not FILES:
                print("No hay archivos que enviar.")
                continue

            # ----- 3 Enviar correo ---------------
            MESSAGE = conf["message"]
            MESSAGE = MESSAGE.replace("{DATE}", DATE)
            send_message(
                subject=conf["subject"],
                message=MESSAGE,
                address=conf["address"],
                files=FILES,
            )

            # Limpiando archivos temporales
            for file in FILES:
                remove_temp_files(file=file)

    except Exception as e:
        print(f"❌ Error: {e}")
