"""
Lautom - Módulo de operaciones core

Este módulo contiene las funciones principales para la automatización del proceso de reporte:
1. Conexión SSH y descarga de datos desde base de datos MySQL
2. Conversión de archivos CSV a formato Excel
3. Envío de correos electrónicos con adjuntos
"""

import paramiko
import pandas as pd
import smtplib
from email.message import EmailMessage
from typing import List
from env import *

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
    # ----- 1 Conexion SSH ------
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=host, 
        port=SSH_PORT, 
        username=SSH_USER, 
        password=SSH_PASSWORD
    )
    print(f"Conexion exitosa con el servidor {host}")

    # Ejecutar query y generar CSV
    stdin, stdout, stderr = ssh.exec_command(query + ' > ' + f"{SSH_PATH}/{file_name}.csv")
    # Esperar a que termine la ejecución del query
    stdout.channel.recv_exit_status()
    # Excepcion
    error = stderr.read().decode()
    if error:
        raise Exception(f"Error al generar CSV: {error}")
    print(f" ✅ Generado con exito el archivo: {file_name}.csv")

    # Descargar el archivo CSV 
    sftp = ssh.open_sftp()
    sftp.get(f"{SSH_PATH}/{file_name}.csv", F"{PATH}/csv/{file_name}.csv")
    sftp.close()
    print(f" ✅ Archivo descargado con exito")
    # Borrar el archivo CSV generado en el servidor
    ssh.exec_command(f"rm -f {SSH_PATH}/{file_name}.csv")
    ssh.close()


def convert_to_excel(file_name: str):
    """
    Convierte un archivo CSV a formato Excel con ajuste automático de ancho de columnas.
    
    Lee un archivo CSV separado por tabulaciones, lo convierte a formato Excel (.xlsx)
    y ajusta automáticamente el ancho de las columnas según el contenido.
    
    Args:
        file_name (str): Nombre base del archivo (sin extensión) ubicado en las carpetas
                        csv/ y que se guardará en excel/
        
    Returns:
        None
        
    Raises:
        Exception: Si ocurre algún error al leer el archivo CSV o escribir el archivo Excel
                  (por ejemplo, archivo no encontrado o problemas de permisos)
                  
    Example:
        >>> convert_to_excel("reporte_diario")
        # Lee: temp/csv/reporte_diario.csv
        # Guarda: temp/excel/reporte_diario.xlsx
        
    Note:
        Requiere que la variable de entorno PATH esté configurada correctamente
        y que exista el archivo CSV en la subcarpeta csv/.
    """
    df = pd.read_csv(f"{PATH}/csv/{file_name}.csv", sep="\t")

    with pd.ExcelWriter(f"{PATH}/excel/{file_name}.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Reporte")
        worksheet = writer.sheets["Reporte"]

        # Ajustar ancho automático
        for col in worksheet.columns:
            max_length = 0
            col_letter = col[0].column_letter  # letra de columna (A, B, C...)

            for cell in col:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass

            adjusted_width = max_length + 2
            worksheet.column_dimensions[col_letter].width = adjusted_width
    
    print(" ✅ Excel generado exitosamente")


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
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = address

    msg.set_content(message)

    for file in files:
        add_attachment(msg, file)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(msg)

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
    with open(f"{PATH}/excel/{file}.xlsx", 'rb') as f:
        msg.add_attachment(
            f.read(), 
            maintype='application', 
            subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
            filename=f"{file}.xlsx"
        )
