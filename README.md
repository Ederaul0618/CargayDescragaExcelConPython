# Automatización de Descargas y Actualización de Bases de Datos con Python

Este proyecto implementa un sistema de automatización en Python que conecta de forma segura a servidores FTP (mediante FileZilla) y a plataformas web para la descarga y procesamiento automático de archivos Excel. Su propósito es **reducir el trabajo manual, optimizar tiempos operativos y mantener actualizadas las bases de datos y reportes empresariales** de forma eficiente y programada.

## 🚀 Funcionalidad Principal

### 1. **Conexión FTP automática**
El sistema se conecta de forma automática a un servidor FTP utilizando FileZilla y credenciales seguras, navega al directorio deseado y descarga los archivos relevantes sin intervención del usuario. Esta funcionalidad es especialmente útil para entornos donde los archivos se actualizan diariamente o en intervalos regulares.

### 2. **Ingesta automatizada a SQL Server**
Una vez descargados, los archivos son procesados mediante scripts en Python que realizan limpieza de datos, validación estructural y carga directa a una base de datos en **SQL Server**, asegurando integridad y actualización inmediata de la información.

### 3. **Extracción desde portales web**
Además del canal FTP, el sistema también automatiza la descarga de reportes en Excel directamente desde plataformas web autenticadas, mediante técnicas de web scraping o automatización con Selenium. Esto permite consolidar reportes provenientes de múltiples fuentes con un solo flujo de trabajo.

## 🧠 Beneficios clave

- 🔄 **Actualización en tiempo real** de reportes y bases de datos.
- ⏱️ **Reducción significativa del tiempo operativo** invertido en tareas repetitivas.
- ⚙️ **Automatización escalable**, adaptable a múltiples orígenes de datos.
- 🛡️ **Seguridad en la transferencia y manejo de datos**.
- 🧩 Integración nativa con **SQL Server** para análisis posterior o visualización.

## 🛠️ Tecnologías empleadas

- **Python 3**
- **pandas**, **pyodbc**, **openpyxl**
- **Selenium** (para automatización web)
- **FileZilla / FTP** (descarga programada)
- **SQL Server** (motor de base de datos)




