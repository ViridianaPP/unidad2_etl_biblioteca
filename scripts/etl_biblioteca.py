import pandas as pd
import mysql.connector

print("Leyendo archivo...")

df = pd.read_csv("data/prestamos_biblioteca_100.csv")

print("\nRealizando limpieza de datos...")

# Estandarizar nombres de columnas
df.columns = df.columns.str.strip().str.lower()

# Quitar espacios en columnas de texto
columnas_texto = ["alumno", "carrera", "libro", "categoria", "sede"]

for columna in columnas_texto:
    df[columna] = df[columna].str.strip()

# Convertir fecha
df["fecha_prestamo"] = pd.to_datetime(df["fecha_prestamo"])

# Convertir columnas numéricas
columnas_numericas = [
    "dias_prestamo",
    "multa_diaria",
    "total_multa"
]

for columna in columnas_numericas:
    df[columna] = pd.to_numeric(df[columna])

# Verificar valores nulos
print("\nValores nulos por columna:")
print(df.isnull().sum())

print("\nLimpieza terminada.")

print("\nConectando a MySQL...")

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="biblioteca_dw"
)

cursor = conexion.cursor()

print("Conexión realizada correctamente.")

print("\nCreando tablas...")

# ==========================
# Tabla dim_alumno
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS dim_alumno(
    id_alumno INT AUTO_INCREMENT PRIMARY KEY,
    alumno VARCHAR(100) UNIQUE
)
""")

# ==========================
# Tabla dim_carrera
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS dim_carrera(
    id_carrera INT AUTO_INCREMENT PRIMARY KEY,
    carrera VARCHAR(100) UNIQUE
)
""")

# ==========================
# Tabla dim_libro
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS dim_libro(
    id_libro INT AUTO_INCREMENT PRIMARY KEY,
    libro VARCHAR(150),
    categoria VARCHAR(100),
    UNIQUE(libro, categoria)
)
""")

# ==========================
# Tabla dim_sede
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS dim_sede(
    id_sede INT AUTO_INCREMENT PRIMARY KEY,
    sede VARCHAR(100) UNIQUE
)
""")

# ==========================
# Tabla dim_fecha
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS dim_fecha(
    id_fecha INT PRIMARY KEY,
    fecha DATE UNIQUE,
    anio INT,
    mes INT,
    dia INT
)
""")

# ==========================
# Tabla fact_prestamos
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS fact_prestamos(
    id_prestamo INT PRIMARY KEY,
    id_fecha INT,
    id_alumno INT,
    id_carrera INT,
    id_libro INT,
    id_sede INT,
    dias_prestamo INT,
    multa_diaria DECIMAL(10,2),
    total_multa DECIMAL(10,2),

    FOREIGN KEY (id_fecha) REFERENCES dim_fecha(id_fecha),
    FOREIGN KEY (id_alumno) REFERENCES dim_alumno(id_alumno),
    FOREIGN KEY (id_carrera) REFERENCES dim_carrera(id_carrera),
    FOREIGN KEY (id_libro) REFERENCES dim_libro(id_libro),
    FOREIGN KEY (id_sede) REFERENCES dim_sede(id_sede)
)
""")

# ==========================
# Tabla etl_errores
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS etl_errores(
    id_error INT AUTO_INCREMENT PRIMARY KEY,
    fecha_error DATETIME,
    archivo_origen VARCHAR(100),
    fila_csv INT,
    id_registro INT,
    descripcion_error VARCHAR(255),
    datos_originales TEXT
)
""")

# ==========================
# Tabla etl_log
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS etl_log(
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    fecha_ejecucion DATETIME,
    archivo_origen VARCHAR(100),
    filas_leidas INT,
    filas_cargadas INT,
    filas_rechazadas INT,
    estado VARCHAR(50)
)
""")

conexion.commit()

print("Tablas creadas correctamente.")

print("\nLimpiando tablas...")

cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

cursor.execute("DELETE FROM fact_prestamos")
cursor.execute("DELETE FROM dim_alumno")
cursor.execute("DELETE FROM dim_carrera")
cursor.execute("DELETE FROM dim_libro")
cursor.execute("DELETE FROM dim_sede")
cursor.execute("DELETE FROM dim_fecha")
cursor.execute("DELETE FROM etl_errores")

cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

conexion.commit()

print("Tablas limpiadas correctamente.")

print("\nValidando registros...")

prestamos_validos = []
prestamos_error = []

ids_prestamos = []

for indice, fila in df.iterrows():

    tiene_error = False
    descripcion_error = ""

    # ==========================
    # Validar id_prestamo duplicado
    # ==========================
    if fila["id_prestamo"] in ids_prestamos:
        tiene_error = True
        descripcion_error = "id_prestamo duplicado"

    # ==========================
    # Validar total_multa
    # ==========================
    elif fila["dias_prestamo"] * fila["multa_diaria"] != fila["total_multa"]:
        tiene_error = True
        descripcion_error = "total_multa incorrecto"

    # ==========================
    # Registro válido
    # ==========================
    if tiene_error == False:

        prestamos_validos.append(fila)
        ids_prestamos.append(fila["id_prestamo"])

    # ==========================
    # Registro con error
    # ==========================
    else:

        prestamos_error.append(fila)

        cursor.execute(
            """
            INSERT INTO etl_errores(
                fecha_error,
                archivo_origen,
                fila_csv,
                id_registro,
                descripcion_error,
                datos_originales
            )
            VALUES(NOW(), %s, %s, %s, %s, %s)
            """,
            (
                "prestamos_biblioteca_100.csv",
                indice + 2,
                fila["id_prestamo"],
                descripcion_error,
                str(fila.to_dict())
            )
        )

conexion.commit()

# Trabajar únicamente con registros válidos
df = pd.DataFrame(prestamos_validos)

print("Registros válidos:", len(prestamos_validos))
print("Registros con error:", len(prestamos_error))

print("\nCargando dimensiones...")

# ==========================
# dim_alumno
# ==========================
alumnos = df[["alumno"]].drop_duplicates()

for _, fila in alumnos.iterrows():
    cursor.execute(
        "INSERT INTO dim_alumno(alumno) VALUES(%s)",
        (fila["alumno"],)
    )

# ==========================
# dim_carrera
# ==========================
carreras = df[["carrera"]].drop_duplicates()

for _, fila in carreras.iterrows():
    cursor.execute(
        "INSERT INTO dim_carrera(carrera) VALUES(%s)",
        (fila["carrera"],)
    )

# ==========================
# dim_libro
# ==========================
libros = df[["libro", "categoria"]].drop_duplicates()

for _, fila in libros.iterrows():
    cursor.execute(
        "INSERT INTO dim_libro(libro,categoria) VALUES(%s,%s)",
        (
            fila["libro"],
            fila["categoria"]
        )
    )

# ==========================
# dim_sede
# ==========================
sedes = df[["sede"]].drop_duplicates()

for _, fila in sedes.iterrows():
    cursor.execute(
        "INSERT INTO dim_sede(sede) VALUES(%s)",
        (fila["sede"],)
    )

# ==========================
# dim_fecha
# ==========================
fechas = df[["fecha_prestamo"]].drop_duplicates()

for _, fila in fechas.iterrows():

    fecha = fila["fecha_prestamo"]
    id_fecha = int(fecha.strftime("%Y%m%d"))

    cursor.execute(
        """
        INSERT INTO dim_fecha
        VALUES(%s,%s,%s,%s,%s)
        """,
        (
            id_fecha,
            fecha.date(),
            fecha.year,
            fecha.month,
            fecha.day
        )
    )

conexion.commit()

print("Dimensiones cargadas correctamente.")
print("\nCargando tabla de hechos...")

for _, fila in df.iterrows():

    fecha = fila["fecha_prestamo"]
    id_fecha = int(fecha.strftime("%Y%m%d"))

    # Obtener id_alumno
    cursor.execute(
        "SELECT id_alumno FROM dim_alumno WHERE alumno = %s",
        (fila["alumno"],)
    )
    id_alumno = cursor.fetchone()[0]

    # Obtener id_carrera
    cursor.execute(
        "SELECT id_carrera FROM dim_carrera WHERE carrera = %s",
        (fila["carrera"],)
    )
    id_carrera = cursor.fetchone()[0]

    # Obtener id_libro
    cursor.execute(
        """
        SELECT id_libro
        FROM dim_libro
        WHERE libro = %s
        AND categoria = %s
        """,
        (
            fila["libro"],
            fila["categoria"]
        )
    )
    id_libro = cursor.fetchone()[0]

    # Obtener id_sede
    cursor.execute(
        "SELECT id_sede FROM dim_sede WHERE sede = %s",
        (fila["sede"],)
    )
    id_sede = cursor.fetchone()[0]

    # Insertar en la tabla de hechos
    cursor.execute(
        """
        INSERT INTO fact_prestamos
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            fila["id_prestamo"],
            id_fecha,
            id_alumno,
            id_carrera,
            id_libro,
            id_sede,
            fila["dias_prestamo"],
            fila["multa_diaria"],
            fila["total_multa"]
        )
    )

conexion.commit()

print("Tabla de hechos cargada correctamente.")

from datetime import datetime

estado = "FINALIZADO_CON_ERRORES" if len(prestamos_error) > 0 else "FINALIZADO_OK"

cursor.execute("""
INSERT INTO etl_log(
    fecha_ejecucion,
    archivo_origen,
    filas_leidas,
    filas_cargadas,
    filas_rechazadas,
    estado
)
VALUES (%s, %s, %s, %s, %s, %s)
""", (
    datetime.now(),
    "prestamos_biblioteca_100.csv",
    len(df) + len(prestamos_error),
    len(prestamos_validos),
    len(prestamos_error),
    estado
))

conexion.commit()

import os

os.makedirs("evidencias", exist_ok=True)

with open("evidencias/reporte_ejecucion.txt", "w", encoding="utf-8") as f:
    f.write("REPORTE DE EJECUCIÓN ETL\n")
    f.write("========================\n\n")
    f.write("Nombre del alumno: Viridiana Portilla Palestina\n")
    f.write(f"Fecha y hora: {datetime.now()}\n")
    f.write("Archivo procesado: prestamos_biblioteca_100.csv\n\n")

    f.write(f"Filas leídas: {len(df) + len(prestamos_error)}\n")
    f.write(f"Filas cargadas: {len(prestamos_validos)}\n")
    f.write(f"Filas rechazadas: {len(prestamos_error)}\n")
    f.write(f"Estado final: {estado}\n\n")

    f.write("ERRORES DETECTADOS:\n")

    for error in prestamos_error:
        f.write(f"- id_prestamo {error['id_prestamo']} -> ")
        if error["id_prestamo"] in ids_prestamos:
            f.write("id_prestamo duplicado\n")
        else:
            f.write("total_multa incorrecto\n")

cursor.close()
conexion.close()

print("\n========================")
print("RESUMEN FINAL DEL ETL")
print("========================")
print("Filas leídas:", len(df) + len(prestamos_error))
print("Filas cargadas:", len(prestamos_validos))
print("Filas rechazadas:", len(prestamos_error))
print("Estado:", estado)
print("========================\n")