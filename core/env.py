"""
Lautom - Configuración de variables de entorno

Este módulo carga las variables de entorno desde el archivo .env usando la
biblioteca python-dotenv y las hace disponibles como constantes para uso
en toda la aplicación.

Variables de entorno requeridas:
- APP_PATH: Ruta base para carpetas temporales (por defecto: './temp')
- SSH_PORT: Puerto para conexión SSH (entero)
- SSH_USER: Nombre de usuario para autenticación SSH
- SSH_PASSWORD: Contraseña para autenticación SSH
- SSH_PATH: Ruta remota en el servidor SSH donde se generan los archivos CSV
- SMTP_HOST: Servidor SMTP para envío de correos
- SMTP_PORT: Puerto del servidor SMTP (entero)
- SMTP_USER: Usuario para autenticación SMTP
- SMTP_PASSWORD: Contraseña para autenticación SMTP

Todas las variables son obligatorias excepto APP_PATH, que tiene un valor por defecto.
"""

import os

from dotenv import load_dotenv

load_dotenv()

APP_PATH = os.getenv('APP_PATH')
CSV_PATH = f"{os.getenv('APP_PATH')}/temp/csv"
EXCEL_PATH = f"{os.getenv('APP_PATH')}/temp/excel"

SSH_PORT = int(os.getenv("SSH_PORT", "22"))
SSH_USER = os.getenv("SSH_USER")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")
SSH_PATH = os.getenv("SSH_PATH")

RSA_KEY = str(os.getenv("RSA_KEY"))

SMTP_HOST = str(os.getenv("SMTP_HOST"))
SMTP_PORT = int(os.getenv("SMTP_PORT", "22"))
SMTP_USER = str(os.getenv("SMTP_USER"))
SMTP_PASSWORD = str(os.getenv("SMTP_PASSWORD"))

LOG_CONSOLE = os.getenv("LOG_CONSOLE", "false").lower()
