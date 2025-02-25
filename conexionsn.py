
""" Se importan las librerias necesarias para realizar la carga de datos os
para que python pueda,interactuar con el sistema operativo, numpy, parse y datetime
para manejar los tipos de datos,pandas para manejar la estructura de los datos, 
pyodbc para realizar la conexión con las base de datos, schedule y time para programar,
el horario de carga """

import os
import time
from datetime import datetime  # , timedelta
import numpy as np
import pandas as pd
import pyodbc
import schedule
from dateutil.parser import parse

# Se crea la cadena de conexión a la base de datos:
# DATABASE indica la base a la que se apunta
# UID el usuario y PWD la contraseña

connection_string = r'DRIVER={SQL Server};SERVER=LAPTOP-S7GS2OGI\SQLEXPRESS;DATABASE=BASE_BI;UID=sa;PWD=abc123'

# Se definen las variables;
# carpeta, la ruta donde se encuentran almacenados los archivos;
# tabla, la tabla de la base de datos a la que se apunta la carga

fecha_actual = datetime.now()
# Se obtiene la fecha del día y se almacena en una variable
fecha_corregida = fecha_actual  # + timedelta(days=1)
# Se le da el formato correcto para la cadena de texto ruta_servidor
fecha_formateada = fecha_corregida.strftime('%Y_%B_%d')
carpeta = f'C:/Users/Eder Perez Gallardo/Downloads/Descarga_Bi/0.Bi/BI_{
    fecha_formateada}/'
tabla = 'base_bi_2'
# Se establece un valor de fecha nula para evitar errores al momento de realizar carga
fecha_nula = datetime(1900, 1, 1)

# Se mapean las en las que no coincide el encabezado de origen y el de destino
mapeado_columnas = {
    'Num. Afiliado': 'Num# Afiliado',
    'Num. Sucursal': 'Num# Sucursal',
}

'''Se define el metódo para eliminar la notación científica en los folios'''


def remover_notacion_cientifica(value):
    # Se evalua si el tipo de dato es una fecha, en cuyo caso lo devolverá sin cambios
    try:
        parse(value)
        return value
    except (ValueError, TypeError):
        pass
    # Se evalua si el tipo de dato es numérico de punto flotante
    # en cuyo caso se mostrará como un entero sin puntos decimales
    try:
        float_value = float(value)
        if not pd.isnull(float_value):
            if float_value == 0:
                return None
            elif float_value > 1e+20:
                return '{:.0f}'.format(float_value).replace('.0', '')
            else:
                return '{:.0f}'.format(float_value)
    except (ValueError, TypeError, OverflowError):
        pass

    return value


# Se define el metódo para cargar la base


def carga_base():
    """ Se inicia la conexión con la base de datos """
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            # Se da la instrucción de truncar la tabla a la que el script está apuntado
            cursor.execute(f"TRUNCATE TABLE {tabla}")
            conn.commit()
            print("Tabla truncada correctamente.")
            # Se establece el ciclo de carga
            # de archivos para todos los elementos listados de la carpeta de origen
            for file_name in os.listdir(carpeta):
                if file_name.endswith('.xlsx'):
                    file_path = os.path.join(carpeta, file_name)
                    df = pd.read_excel(file_path)
                    df = df.where(pd.notnull(df), None)
                    # Se establece que las columnas que involucren
                    #  fechas nulas se reemplacen por el valor asignado a la variable fecha nula
                    for column in df.select_dtypes(include=['datetime64[ns]']).columns:
                        df[column] = df[column].fillna(fecha_nula)
                    # Se establece que las columnas que involucren números decimales nulos
                    # se reemplacen por 0.0, referido al tipo de dato de la columna
                    for column in df.select_dtypes(include=[np.float64, np.float32]).columns:
                        df[column] = df[column].fillna('')
                    # Se aplica el metódo para remover la notación científica
                    # a las columnas que involucren folios
                    df['Folio'] = df['Folio'].apply(
                        remover_notacion_cientifica)
                    df['FolioNC'] = df['FolioNC'].apply(
                        remover_notacion_cientifica)
                    # Se aplica una conversión de tipo de dato
                    # a las columnas especificas que deben contener números en la tabla de destino
                    try:
                        df['CostoNC'] = pd.to_numeric(
                            df['CostoNC'], errors='coerce').fillna('')
                        df['IVANC'] = pd.to_numeric(
                            df['IVANC'], errors='coerce').fillna('')
                        df['ImporteNC'] = pd.to_numeric(
                            df['ImporteNC'], errors='coerce').fillna('')
                    except KeyError as e:
                        print(f"Error: {e}. Columna no encontrada.")
                    # Se aplica el mapeado de columnas definido al inicio del código
                    df.rename(columns=mapeado_columnas, inplace=True)
                    # Se define un ciclo para la inserción de filas
                    # en la tabla de destino de SQL Server
                    for index, row in df.iterrows():
                        placeholders = ', '.join(['?'] * len(row))
                        columns = ', '.join([f'[{col}]' for col in row.index])
                        sql = f"INSERT INTO {tabla} ({columns}) VALUES ({
                            placeholders})"
                        cursor.execute(sql, tuple(row))
                    conn.commit()
                    print(f"Archivo {file_name} cargado correctamente.")
    except Exception as e:
        print(f"Error: {e}")


# Se establece la hora programada para hacer la carga de la base
schedule.every().day.at("11:36").do(carga_base)

while True:
    schedule.run_pending()
    time.sleep(1)
