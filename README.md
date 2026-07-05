# Unidad 2 - ETL Biblioteca

## 1. Objetivo del proyecto

Desarrollar un proceso ETL (Extract, Transform, Load) para un dataset de préstamos de biblioteca. El proyecto realiza la lectura de un archivo CSV, la limpieza y validación de los datos, la carga de la información en un mini Data Warehouse en MySQL, el registro de errores detectados y la generación de un reporte de ejecución.

---

## 2. Requisitos para ejecutarlo

Antes de ejecutar el proyecto es necesario contar con:

* Python 3.10 o superior.
* MySQL Server.
* Una base de datos llamada `biblioteca_dw`.
* El archivo `prestamos_biblioteca_100.csv` dentro de la carpeta `data`.

---

## 3. Cómo crear la base de datos

Abrir MySQL o DataGrip y ejecutar la siguiente sentencia:

```sql
CREATE DATABASE biblioteca_dw;
```

El script se encargará de crear automáticamente las tablas necesarias si aún no existen.

---

## 4. Cómo instalar librerías

Instalar las dependencias con el siguiente comando:

```bash
pip install pandas mysql-connector-python
```

---

## 5. Cómo ejecutar el script

Desde la carpeta principal del proyecto ejecutar:

```bash
python scripts/etl_biblioteca.py
```

Al finalizar la ejecución se crearán las tablas del Data Warehouse, se cargarán los registros válidos, se almacenarán los registros con error en `etl_errores`, se registrará la ejecución en `etl_log` y se generará automáticamente el archivo `evidencias/reporte_ejecucion.txt`.

---

## 6. Resultado esperado

Al ejecutar correctamente el proyecto se debe obtener el siguiente resultado:

* Filas leídas: **100**
* Filas cargadas: **98**
* Filas rechazadas: **2**
* Estado: **FINALIZADO_CON_ERRORES**

Además:

* La tabla `fact_prestamos` debe contener **98 registros**.
* La tabla `etl_errores` debe contener **2 registros**.
* Los errores registrados deben corresponder a:

  * **id_prestamo 5099:** `total_multa incorrecto`.
  * **id_prestamo 5002:** `id_prestamo duplicado`.
* El archivo `evidencias/reporte_ejecucion.txt` debe generarse automáticamente con el resumen de la ejecución.
