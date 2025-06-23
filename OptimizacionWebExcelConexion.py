# -------------------------------------------------------------
# Script de automatización con Selenium usando Firefox (geckodriver)
# para ingresar al portal admin.callmed.mx, filtrar solicitudes y
# descargar un archivo Excel al directorio de descargas.
# -------------------------------------------------------------

import os # crear, eliminar y renombrar archivos y directorios; obtener información del sistema operativo; ejecutar comandos del sistema; y trabajar con rutas de archivos y directorios
import time
from datetime import datetime, timedelta # manipular fechas y horas objetivo es poder extraer campos de forma eficiente para su posterior manipulación o formateo
from selenium import webdriver #  controla el navegador web, permitiendo la interacción con páginas web y sus elementos como lo haría un usuario humano
from selenium.webdriver.firefox.options import Options # configurar y personalizar el comportamiento del navegador Firefox cuando se automatiza con Selenium WebDriver.
from selenium.webdriver.common.by import By # especificar cómo encontrar elementos web dentro de una página web. Permite utilizar diferentes estrategias de localización, como por ID, nombre de clase, XPATH, enlace de texto, etc.
from selenium.webdriver.support.ui import WebDriverWait, Select #espera de condiciones específicas en la automatización web, como la aparición de elementos, la visibilidad de elementos,
from selenium.webdriver.support import expected_conditions as EC # especialmente para la gestión de esperas y la manipulación de elementos web. Facilita la espera de condiciones específicas antes de interactuar con elementos, evitando errores por tiempos de carga
from selenium.webdriver.common.keys import Keys # enviar acciones de teclado (como teclas especiales, como Ctrl, Shift, Enter, etc.) a elementos web

# Ruta donde se descargará el archivo
ruta_descargas = "C:/Users/Eder Perez Gallardo/Downloads"

# Configurar Firefox para permitir descargas  automáticas archivo Excel directamente y en silencio, al lugar que tú especificaste, sin pedir confirmación al usuario.
options = Options() # Crea una instancia de configuración
options.set_preference("browser.download.folderList", 2) # use una carpeta personalizada para las descargas numero 2 es Carpeta definida manualmente (como en browser.download.dir)
options.set_preference("browser.download.dir", ruta_descargas) # Especifica dónde se guardarán los archivos descargados
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") #  Le indica a Firefox que no muestre un cuadro de diálogo de descarga para archivos con ese tipo MIME (.xlsx), y que los descargue automáticamente.
options.set_preference("pdfjs.disabled", True) # Desactiva el visor interno de PDF de Firefox
options.set_preference("browser.download.manager.showWhenStarting", False) #  Evita que Firefox muestre la ventana del gestor de descargas al comenzar una descarga
 
# Iniciar WebDriver con Firefox
driver = webdriver.Firefox(options=options)

try:
    driver.get("https://admin.callmed.mx/Buzon.aspx")

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "aref"))).click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txtUser"))).send_keys("EPEREZGEYE")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txtPassword"))).send_keys("Angelitai$22")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnEntrar"))).click()

    WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.ID, "dialogLoadingGral")))

    for intento in range(3): #for = Inicia un BUCLE de 3 intentos. Esto es útil si la página no carga de inmediato o hay retrasos por el servidor
        try:
            WebDriverWait(driver, 20).until(EC.invisibility_of_element_located((By.ID, "dialogLoadingGral")))
            autorizaciones = WebDriverWait(driver, 20).until( # Espera hasta 20 segundos a que desaparezca el cuadro de carga general (ID dialogLoadingGral), lo que indica que la página está lista para interactuar.
                EC.element_to_be_clickable((By.XPATH, "//div[@id='sidebar']//span[text()='Autorizaciones']/parent::a")) #Espera que el botón “Autorizaciones” esté presente y clickeable.
            ) 
            autorizaciones.click()
            break
        except Exception as e: #Si falla (por ejemplo, el botón no está listo), muestra el error e intenta de nuevo tras 2 segundos.
            print(f"⚠ Intento {intento+1} fallido: {e}")
            time.sleep(2)
    else: # Si ningún intento tuvo éxito, lanza una excepción crítica deteniendo el script.
        raise Exception("❌ No se pudo hacer clic en 'Autorizaciones' tras 3 intentos.")

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='Buzon.aspx']"))
    ).click()

    WebDriverWait(driver, 30).until(EC.invisibility_of_element_located((By.ID, "dialogLoadingGral")))
    time.sleep(1)

    fecha_inicial = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "txtFechaInicial")))
    driver.execute_script("arguments[0].removeAttribute('readonly')", fecha_inicial)
    fecha_inicial.clear()
    fecha_inicial.send_keys("01/01/2022")

    ayer = datetime.now() - timedelta(days=1)
    fecha_final_texto = ayer.strftime("%d/%m/%Y")

    fecha_final = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "txtFechaFinal")))
    driver.execute_script("arguments[0].removeAttribute('readonly')", fecha_final)
    fecha_final.clear()
    fecha_final.send_keys(fecha_final_texto)
    fecha_final.send_keys(Keys.TAB)
    time.sleep(1)

    WebDriverWait(driver, 30).until(EC.invisibility_of_element_located((By.ID, "dialogLoadingGral")))
    time.sleep(1)

    Select(WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "dblEstatus")))).select_by_visible_text("--Seleccione--")
    time.sleep(1)
    Select(WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "dblBuzon")))).select_by_visible_text("--Todos--")

    driver.find_element(By.ID, "btnBuscar").click()

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "lblProcessLoading")))
        WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.ID, "lblProcessLoading")))
    except:
        print("ℹ️ 'lblProcessLoading' no apareció, se continúa con el flujo.")

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dialogLoadingGral")))
        WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.ID, "dialogLoadingGral")))
    except:
        pass

    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//table//tbody/tr")))

    for intento in range(3):
        try:
            WebDriverWait(driver, 60).until(
                EC.invisibility_of_element_located((By.ID, "dialogLoadingGral"))
            )
            btn_excel = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, "btnExcel"))
            )
            time.sleep(0.5)
            btn_excel.click()
            break
        except Exception as e:
            print(f"⚠ Exportación fallida en intento {intento+1}: {e}")
            time.sleep(3)
    else:
        raise Exception("❌ No se pudo hacer clic en Exportar después de 3 intentos.")

   # Nombre esperado por el sistema
    nombre_esperado = f"Buzón_{datetime.now().strftime('%d_%m_%Y')}.xlsx"
    ruta_archivo = os.path.join(ruta_descargas, nombre_esperado)
    archivo_temporal = ruta_archivo + ".part"  # Firefox usa este sufijo durante la descarga

    print(f"⏳ Esperando que finalice la descarga de: {nombre_esperado}")

    # Esperar hasta 120 segundos a que se termine de descargar (sin .part)
    tiempo_espera = 180  # 3 minutos por si es archivo grande
    for _ in range(tiempo_espera):
        if os.path.exists(ruta_archivo) and not os.path.exists(archivo_temporal):
            print(f"✅ Archivo descargado exitosamente: {ruta_archivo}")
            break
        time.sleep(1)
    else:
        print(f"⚠ Descarga no finalizó en {tiempo_espera} segundos.")
finally:
    #driver.quit()
     pass
