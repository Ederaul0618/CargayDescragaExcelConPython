""" programa que se cargan de conectarse a un servidor (FTP) donde descragar de forma masiva los exceles se instalan las bibliotecas necesarias,
 paramiko para establecer la conexión con el servidor SSH y FTP. 
 os para que python interactúe con el sistema operativo.
 ctypes y stat para otorgar permisos a la carpeta seleccionada (Necesita leer y escribir información).
 schedule y time para marcar el tiempo y programar la descarga.
 smtplib para iniciar sesión en el correo del usuario / enviar el correo  y MIMEText y MIMEMultipart para redactar el correo electrónico"""

import os
import time
import smtplib
from datetime import datetime
import ctypes
import stat
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import paramiko
import schedule

# Se establece el envío de correo electrónico como falso por defecto
correo_enviado = False

# Se otorgan los permisos correspondientes de seguridad y acceso a la carpeta en la que se van a depositar las descargas


def otorgar_permisos(path):
    try:
        path = os.path.abspath(path)
        command = f'icacls "{path}" /grant Everyone:F'
        os.system(command)
    except Exception as e:
        print(f'No se pudieron cambiar los permisos: {e}')
        exit(1)

# Se define el procedimiento para enviar el correo electrónico


def enviar_correo():
    global correo_enviado

    if correo_enviado:
        return

    # Se definen las variables involucradas en el envio del correo electrónico
    correo_enviado = True
    remitente = '****@*****' # colocar correo 
    destinatario = '*****@*****+'
    asunto = 'Carga de datos'
    cuerpo = ('Buen día estimados.\n'
              '\n'
              'No se han cargado los datos correspondientes al día de hoy, agradecería se hiciera a la brevedad.\n'
              '\n'
              'Agradezco de antemano su atención. Saludos cordiales.')

    # Se define la estructura del mensaje según MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto

    msg.attach(MIMEText(cuerpo, 'plain'))

    # Se introduce la información de inicio de sesión
    try:
        # Se añade el servicio de correo a utilizar
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.starttls()
        # Se coloca la contraseña de acceso al correo
        server.login(remitente, '*********')
        text = msg.as_string()
        # Se envía el correo a través del servidor
        server.sendmail(remitente, destinatario, text)
        server.quit()
        print(f'Correo enviado a {destinatario}')
    except Exception as e:
        print(f'No se pudo enviar el correo: {e}')

# Se define el método de descarga de archivos


def descargar_archivos():
    global correo_enviado

    # Se define la dirección IP (enmascarada por una URL de MS Azure) que da al servidor
    hostname = '**************************'
    port = '***'
    usuario = '*****'  # Se define el nombre de usuario para acceder
    contrasena = '*****'  # Se define la contraseña de acceso al servidor
    # Se obtiene la fecha del día y se almacena en una variable
    fecha_actual = datetime.now()
    # Se le da el formato correcto para la cadena de texto ruta_servidor
    fecha_formateada = fecha_actual.strftime('%Y_%B_%d')
    # Se establece la ruta de los archivos dentro del servidor
    ruta_servidor = f'/upload/Reportes/BI/BI_{fecha_formateada}/' 
    ruta_local = f'C:/Users/Eder Perez Gallardo/Downloads/Descarga_Bi/0.Bi/BI_{
        fecha_formateada}/'  # Se establece la ruta de descarga en la computadora local

    # Se crea el directorio de la ruta local en caso de no existir
    if not os.path.exists(ruta_local):
        try:
            os.makedirs(ruta_local)
            otorgar_permisos(ruta_local)
        except OSError as e:
            print(f'Ocurrió un error al crear el directorio {ruta_local}: {e}')
            return False

    # Se define una conexión SSH para conectarse al servidor
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Se inicia la conexión SSH para conectarse al servidor
        ssh.connect(hostname, port, usuario, contrasena)
        # Se inicia el protocolo FTP
        sftp = ssh.open_sftp()

        # Se descargan de manera iterativa todos los archivos listados en la ruta del servidor
        try:
            files = sftp.listdir(ruta_servidor)
            for file in files:
                remote_file_path = os.path.join(ruta_servidor, file)
                local_file_path = os.path.join(ruta_local, file)
                sftp.get(remote_file_path, local_file_path)
                print(f'Archivo {file} descargado correctamente a {
                      local_file_path}')
            # Se cierra la conexión con el protocolo de transferencia de archivos
            sftp.close()
            correo_enviado = False
            return True
        except IOError as e:
            print(f'La ruta en el servidor no existe: {e}')
            return False

    except Exception as e:
        print(f'Ocurrió un error: {e}')
        return False
    finally:
        # Se cierra la conexión con el servidor
        ssh.close()

# Se define el método para programar la descarga


def descarga_programada():
    intentos = 0
    while intentos < 3:  # Se establece un máximo de 3 intentos de descarga
        if descargar_archivos():
            break
        else:
            intentos += 1
            print(f'Intento {intentos} fallido. Quedan {
                  3 - intentos} intentos')
            if intentos == 1 and not correo_enviado and datetime.now().weekday() < 5:
                enviar_correo()
            # Se detiene 15 minutos (900 Segundos) antes de reintentar la descarga
            time.sleep(900)


# Se marca la hora de inicio de la descarga en formato de 24 horas
schedule.every().day.at("11:28").do(descarga_programada)

while True:
    schedule.run_pending()
    time.sleep(60)
