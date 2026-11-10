import os
import time
from flask import Flask, request, jsonify
import psycopg

app = Flask(__name__)

# Configuracion de la base de datos
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "calculadora")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


# Conexion con PostgreSQL
def get_connection():
    return psycopg.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=5432
    )


# Crear tabla automaticamente
def initialize_database():
    for attempt in range(10):
        try:
            with get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS operaciones (
                        id SERIAL PRIMARY KEY,
                        numero1 DOUBLE PRECISION NOT NULL,
                        numero2 DOUBLE PRECISION NOT NULL,
                        operacion VARCHAR(30) NOT NULL,
                        resultado DOUBLE PRECISION NOT NULL,
                        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

            print("Tabla operaciones creada correctamente")
            return

        except psycopg.OperationalError:
            print(f"Esperando PostgreSQL... intento {attempt + 1}")
            time.sleep(3)

    raise RuntimeError("No fue posible conectar con PostgreSQL")


# Ruta principal
@app.route("/", methods=["GET"])
def inicio():
    return jsonify({
        "mensaje": "Calculadora Python funcionando",
        "servicio": "calculator-app",
        "base_datos": DB_HOST
    })


# Realizar y guardar operaciones
@app.route("/calculate", methods=["POST"])
def calcular():
    datos = request.get_json(silent=True) or {}

    try:
        numero1 = float(datos["numero1"])
        numero2 = float(datos["numero2"])
        operacion = datos["operacion"].lower()

        if operacion == "suma":
            resultado = numero1 + numero2

        elif operacion == "resta":
            resultado = numero1 - numero2

        elif operacion == "multiplicacion":
            resultado = numero1 * numero2

        elif operacion == "division":
            if numero2 == 0:
                return jsonify({
                    "error": "No se puede dividir entre cero"
                }), 400

            resultado = numero1 / numero2

        else:
            return jsonify({
                "error": "Operacion no valida"
            }), 400

        # Guardar operacion en PostgreSQL
        with get_connection() as conn:
            registro = conn.execute("""
                INSERT INTO operaciones
                (numero1, numero2, operacion, resultado)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (numero1, numero2, operacion, resultado)).fetchone()

        return jsonify({
            "id": registro[0],
            "numero1": numero1,
            "numero2": numero2,
            "operacion": operacion,
            "resultado": resultado,
            "guardado_en": DB_HOST,
            "mensaje": "Operacion guardada correctamente"
        }), 201

    except (KeyError, TypeError, ValueError, AttributeError):
        return jsonify({
            "error": "Datos incorrectos o incompletos"
        }), 400

    except psycopg.Error:
        app.logger.exception("Error de comunicacion con PostgreSQL")
        return jsonify({
            "error": "No fue posible guardar la operacion"
        }), 500


# Consultar historial
@app.route("/history", methods=["GET"])
def historial():
    try:
        with get_connection() as conn:
            registros = conn.execute("""
                SELECT id, numero1, numero2,
                       operacion, resultado, fecha
                FROM operaciones
                ORDER BY id DESC
            """).fetchall()

        datos = []

        for registro in registros:
            datos.append({
                "id": registro[0],
                "numero1": registro[1],
                "numero2": registro[2],
                "operacion": registro[3],
                "resultado": registro[4],
                "fecha": registro[5].isoformat()
            })

        return jsonify(datos), 200

    except psycopg.Error:
        app.logger.exception("Error consultando el historial")
        return jsonify({
            "error": "No fue posible consultar el historial"
        }), 500


# Iniciar aplicacion
if __name__ == "__main__":
    initialize_database()

    print("Calculadora iniciada correctamente")
    print(f"Conectando con PostgreSQL mediante el servicio: {DB_HOST}")

    app.run(host="0.0.0.0", port=5000)
