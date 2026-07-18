import logging
import os

import paramiko

from .env import RSA_KEY, SSH_PATH, SSH_PORT, SSH_USER, CSV_PATH
from .logger import setup_logging

setup_logging()
LOGGER = logging.getLogger(__name__)


def download_csv(host: str, query: str, file_name: str):
    """
    Descarga resultados de una consulta MySQL mediante SSH y los guarda como CSV.

    Establece una conexión SSH al servidor especificado, ejecuta una consulta SQL
    para obtener datos de llamadas, guarda los resultados como archivo CSV en el
    servidor remoto, descarga el archivo localmente y luego lo elimina del servidor.

    Args:
        host (str): Dirección IP o hostname del servidor SSH
        query (str): Consulta SQL completa a ejecutar en la base de datos
        file_name (str): Nombre base para los archivos CSV (sin extensión)

    Returns:
        None

    Raises:
        Exception: Si ocurre algún error durante la conexión SSH,
                  ejecución de la consulta o transferencia de archivos

    Example:
        >>> descargar_csv("172.0.0.1",
                         "SELECT * FROM llamadas LIMIT 10",
                         "reporte_diario")
        # Genera y descarga: reporte_diario.csv

    Note:
        Requiere que las variables de entorno SSH_PORT, SSH_USER, SSH_PASSWORD,
        SSH_PATH y PATH estén configuradas correctamente.
    """
    ssh = None
    try:
        # ----- 1 Conexion SSH ------
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key_rsa = paramiko.RSAKey.from_private_key_file(os.path.expanduser(RSA_KEY))
        ssh.connect(
            hostname=host,
            port=SSH_PORT,
            username=SSH_USER,
            pkey=key_rsa,
            timeout=15,
        )
        LOGGER.info(f"[{host}] Conexión exitosa con el servidor")

        # Ejecutar query y generar CSV
        stdin, stdout, stderr = ssh.exec_command(
            query + " > " + f"{SSH_PATH}/{file_name}.csv"
        )
        # Esperar a que termine la ejecución del query
        stdout.channel.recv_exit_status()
        # Excepcion
        error = stderr.read().decode()
        if error:
            raise Exception(f"[{host}] Error al generar CSV: {error}")

        LOGGER.info(f"[{host}] Generado con exito el archivo: {file_name}.csv")

        # Descargar el archivo CSV
        sftp = ssh.open_sftp()
        sftp.get(f"{SSH_PATH}/{file_name}.csv", f"{CSV_PATH}/{file_name}.csv")
        sftp.close()
        LOGGER.info(f"[{host}] Archivo descargado con exito")
        # Borrar el archivo CSV generado en el servidor
        ssh.exec_command(f"rm -f {SSH_PATH}/{file_name}.csv")
        return True
    except Exception as e:
        LOGGER.error(f"[{host}] Error crítico en descarga: {e}")
        return False  # Indica que este reporte falló
    finally:
        if ssh:
            ssh.close()
