from datetime import datetime
from core import download_csv, convert_to_excel, send_message

def main():
    try:
        # ------ Config ------------
        HOST = ""
        NAME = ""
        FILE_NAME = f"{NAME}-" + datetime.now().strftime("%d-%m-%y")
        DATE = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        QUERY = f""

        # ----- 1 Descargar CSV --------------
        download_csv(HOST, QUERY, FILE_NAME)

        # ----- 2 Convertir a EXCEL -----------
        convert_to_excel(FILE_NAME)

        # ----- 3 Enviar correo ---------------
        subject = f"Reporte {NAME} {DATE}"
        message = f"Buenos noches, les cormparto el reporte de {NAME} del dia de hoy {DATE}. \n \n Saludos cordiales."
        address = []
        files = [FILE_NAME]
        send_message(subject, message, files, address)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()