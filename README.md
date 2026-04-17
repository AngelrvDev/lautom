# Lautom - Sistema de Reporte Automatizado

Sistema automatizado para generar reportes de llamadas desde una base de datos MySQL, convertir los resultados a formato Excel y enviarlos por correo electrónico.

## Descripción

Lautom es un proyecto Python que automatiza el proceso de:
1. Consultar una base de datos MySQL para obtener registros de llamadas
2. Descargar los resultados en formato CSV
3. Convertir el CSV a formato Excel (.xlsx)
4. Enviar el archivo generado por correo electrónico a los destinatarios especificados

## Requisitos

- Python 3.x
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clona este repositorio
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Copia el archivo `.env.example` a `.env` y configura las variables de entorno necesarias

## Uso

Ejecuta el script de prueba principal:
```bash
python main.py
```

El script realizará automáticamente:
- Consulta a la base de datos MySQL
- Descarga de resultados en CSV
- Conversión a formato Excel
- Envío por correo electrónico

## Estructura del Proyecto

- `main.py`: Script principal de pureba que ejecuta el flujo completo
- `core.py`: Contiene las funciones principales (descargar_csv, convert_to_excel, send_message)
- `env.py`: Manejo de variables de entorno
- `requirements.txt`: Lista de dependencias de Python
- `.env`: Archivo de configuración de variables de entorno (no incluido en git)
- `.env.example`: Ejemplo de configuración de variables de entorno

## Configuración

El proyecto requiere configurar las siguientes variables en el archivo `.env`:
- Credenciales de la base de datos MySQL
- Configuración del servidor SMTP para envío de correos
- Destinatarios de correo

Consulta `.env.example` para ver el formato esperado.

## Funcionalidades

- Conexión segura a base de datos MySQL
- Generación de nombres de archivo basados en fecha y hora
- Conversión de CSV a Excel con formato adecuado
- Envío de correos con adjuntos
- Manejo de errores y logging básico

## Notas

- Los archivos temporales se almacenan en la carpeta `temp/`
- Los registros de prueba se encuentran en la carpeta `test/`
- El proyecto utiliza bibliotecas estándar de Python como pandas, openpyxl, paramiko, entre otros

## Licencia

Este proyecto está bajo licencia MIT.