import logging
import smtplib
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from typing import List

from .env import EXCEL_PATH, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER
from .logger import setup_logging

setup_logging()
LOGGER = logging.getLogger(__name__)


def send_message(subject: str, message: str, files: List[str], address: List[str]):
    """
    Envía un correo electrónico con adjuntos usando SMTP seguro.

    Crea y envía un correo electrónico con el asunto y mensaje especificados,
    adjuntando los archivos indicados y enviándolo a la lista de destinatarios
    mediante conexión SSL al servidor SMTP configurado.

    Args:
        subject (str): Asunto del correo electrónico
        message (str): Cuerpo del mensaje de correo
        files (List[str]): Lista de nombres de archivos (sin extensión)
                          que se adjuntarán desde la carpeta excel/
        address (List[str]): Lista de direcciones de correo electrónico destinatarias

    Returns:
        None

    Raises:
        Exception: Si ocurre algún error durante la autenticación SMTP,
                  envío del mensaje o procesamiento de adjuntos

    Example:
        >>> send_message(
        ...     "Reporte diario",
        ...     "Adjunto el reporte de hoy",
        ...     ["reporte_diario"],
        ...     ["usuario@ejemplo.com"]
        ... )
        # Envía un correo con reporte_diario.xlsx adjunto

    Note:
        Requiere que las variables de entorno SMTP_HOST, SMTP_PORT,
        SMTP_USER y SMTP_PASSWORD estén configuradas correctamente.
        Los archivos deben existir en la subcarpeta excel/ con extensión .xlsx.
    """

    if not files:
        LOGGER.warning("No hay archivos que enviar.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"Luzware <{SMTP_USER}>"
    msg["To"] = address

    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="luzware.com")
    msg.set_content(message)

    for file in files:
        add_attachment(msg, file)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(msg)
    LOGGER.info(f"Enviando correo {subject}")


def add_attachment(msg: EmailMessage, file: str):
    """
    Adjunta un archivo Excel a un mensaje de correo electrónico.

    Lee un archivo Excel desde el sistema de archivos y lo adjunta al mensaje
    de correo proporcionado con el tipo MIME apropiado para archivos de Excel.

    Args:
        msg (EmailMessage): Objeto de mensaje de correo al que se adjuntará el archivo
        file (str): Nombre base del archivo Excel (sin extensión) ubicado en la carpeta excel/

    Returns:
        None

    Raises:
        FileNotFoundError: Si el archivo especificado no existe en la ruta esperada
        Exception: Si ocurre algún error al leer el archivo o adjuntarlo al mensaje

    Example:
        >>> msg = EmailMessage()
        >>> add_attachment(msg, "reporte_diario")
        # Adjunta: temp/excel/reporte_diario.xlsx al mensaje msg

    Note:
        Requiere que la variable de entorno PATH esté configurada correctamente
        y que el archivo exista en la subcarpeta excel/ con extensión .xlsx.
    """
    with open(f"{EXCEL_PATH}/{file}.xlsx", "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"{file}.xlsx",
        )
