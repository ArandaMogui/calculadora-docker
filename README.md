# Calculadora Python con Docker y Orquestación CI/CD con Jenkins

> **Institución Universitaria Politécnico Grancolombiano**  
> **Facultad de Ingeniería, Diseño e Innovación**  
> **Módulo:** Énfasis Profesional I (Integración Continua) - Grupo 2  
> **Docente:** Ing. John Alirio Olarte Ramos  

### 👥 Equipo de Trabajo (Autores)
* **Alex Camilo Hernández Piragauta**
* **Juan Osorio Zapata**
* **Cristian Mauricio Ricardo Rojas**
* **Valentina Yepes Arteaga**
* **Maira Alexandra Morales Guio**

---

## 📌 1. Descripción del Proyecto

Este proyecto consiste en el desarrollo, contenerización y automatización de ciclo de vida de una **Calculadora Distribuida** desarrollada en **Python** con el microframework **Flask**, desacoplada en una arquitectura de microservicios e integrada con un motor de base de datos relacional **PostgreSQL 16.6**.

La aplicación permite resolver operaciones aritméticas (`suma`, `resta`, `multiplicacion` y `division`), aplicar validaciones matemáticas robustas (control de división entre cero) y garantizar la persistencia transaccional del historial en base de datos.

La infraestructura se encuentra completamente declarada como código mediante **Docker** y **Docker Compose**, y orquestada a través de un pipeline de Integración Continua en **Jenkins** y **GitHub Actions**.

---

## 📊 2. Matriz de Progreso de Entregas Académicas

| Hito / Entrega | Semana | Estado | Tecnologías y Alcance Logrado |
|---|---|:---:|---|
| **Entrega 1: Docker con Dos Contenedores Comunicados** | Semana 3 | ✅ **COMPLETADA**<br>*(10/Nov/2026)* | • Repositorio GitHub estructurado.<br>• Contenedor 1 (`calculator-app`): Python 3.12.7 + Flask.<br>• Contenedor 2 (`calculator-db`): PostgreSQL 16.6.<br>• Red personalizada bridge `calculator-network`.<br>• Comunicación obligatoria por nombre de host (`DB_HOST=db`).<br>• Transacción real de ida y vuelta (`POST /calculate`).<br>• Volumen nominal persistente `postgres-data`.<br>• Seguridad: `.env`, `.env.example`, `.dockerignore`.<br>• Pipeline inicial en GitHub Actions (`docker-build.yml`).<br>• Informe formal en Normas APA 7 con capturas de evidencia. |
| **Entrega 2: Implementación de Jenkins como Gestor de Operaciones** | Semana 5 | 🚀 **EN CURSO / LISTA PARA REVISIÓN** | • Incorporación de **Jenkins** como servidor de CI centralizado.<br>• Pipeline Declarativo como Código (`Jenkinsfile`) con 6 etapas.<br>• Suite de pruebas unitarias automatizadas (`tests/` con `pytest`).<br>• Linter y análisis estático de código (`flake8`).<br>• Construcción automatizada de imágenes con tags dinámicos.<br>• Prueba de integración multi-contenedor efímera (App + DB).<br>• Despliegue de servidor Jenkins local con `docker-compose.jenkins.yml`.<br>• Documento técnico de especificaciones de Jenkins en Normas APA. |
| **Entrega 3 y Sustentación: Integración Continua Integral** | Semanas 7 y 8 | ⚪ **PLANIFICADA** | • Integración completa con pipelines en la nube (Travis CI / Cloud).<br>• Monitoreo, trazabilidad de fallos e historial de incidentes.<br>• Documento final consolidado y defensa técnica (Sustentación oral). |

---

## 🏗️ 3. Arquitectura del Sistema

```
+-----------------------------------------------------------------------------------------+
|                                    DOCKER HOST                                          |
|                                                                                         |
|   +─────────────────────────────────────────────────────────────────────────────────+   |
|   │                  Red Bridge Personalizada: calculator-network                   │   |
|   │                                                                                 │   |
|   │   +────────────────────────────+          +────────────────────────────+        │   |
|   │   │  Servicio 1:               │          │  Servicio 2:               │        │   |
|   │   │  calculator-app            │          │  calculator-db (db)        │        │   |
|   │   │  - Python 3.12.7-slim      │   TCP    │  - PostgreSQL 16.6         │        │   |
|   │   │  - Flask 3.1.1             │ ───────> │  - Puerto interno 5432     │        │   |
|   │   │  - Puerto interno 5000     │  5432    │  - Healthcheck pg_isready  │        │   |
|   │   │  - DB_HOST=db              │          │                            │        │   |
|   │   +─────────────┬──────────────+          +─────────────┬──────────────+        │   |
|   +─────────────────┼───────────────────────────────────────┼───────────────────────+   |
|                     │ Mapeo puerto                          │ Volumen persistente       |
|                     ▼                                       ▼                           |
|              localhost:5000                         postgres-data                       |
|        (POST /calculate con JSON)             (/var/lib/postgresql/data)                |
+-----------------------------------------------------------------------------------------+
```

---

## 🔄 4. Pipeline de Integración Continua con Jenkins

El archivo [`Jenkinsfile`](./Jenkinsfile) gobierna el ciclo de vida del código ante cada cambio o Pull Request:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ 1. Checkout SCM │ ──> │ 2. Linter       │ ──> │ 3. Unit Tests   │ ──> │ 4. Docker Build │ ──> │ 5. Test Integr. │
│ (Git pull)      │     │ (Flake8)        │     │ (Pytest + JUnit)│     │ (Compose build) │     │ (Flask ➔ Postgres│
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
                                                                                                         │
                                                                                                         ▼
                                                                                                ┌─────────────────┐
                                                                                                │ 6. Cleanup Post │
                                                                                                │ (docker down -v)│
                                                                                                └─────────────────┘
```

1. **Checkout:** Descarga el código y muestra metadatos del commit (`hash`, autor, mensaje).
2. **Linter:** Audita la calidad de sintaxis con `flake8` deteniendo el pipeline de inmediato si hay errores (*Fail-Fast*).
3. **Unit Tests:** Ejecuta pruebas unitarias aisladas sin dependencias externas y exporta resultados a formato JUnit XML (`reports/unit-tests-report.xml`).
4. **Docker Build:** Compila la imagen `calculator-app` a partir del `Dockerfile` oficial.
5. **Pruebas de Integración:** Levanta el ambiente multi-contenedor con `docker compose`, espera a que PostgreSQL y Flask estén listos, efectúa una transacción matemática de prueba vía HTTP y valida la persistencia directa en la base de datos.
6. **Limpieza:** Destruye los contenedores de prueba y libera memoria de forma automática.

---

## 📁 5. Estructura del Repositorio

```text
calculadora-docker/
│
├── 📁 .github/workflows/          # Flujo CI para GitHub Actions (docker-build.yml)
├── 📁 app/                        # Código fuente del microservicio
│   ├── app.py                     # API REST Flask con endpoints y conexión DB
│   └── requirements.txt           # Dependencias de producción (Flask, psycopg)
│
├── 📁 tests/                      # Suite de pruebas automatizadas para CI
│   ├── __init__.py
│   └── test_calculadora.py        # Pruebas unitarias de cálculo y endpoints
│
├── 📁 evidencias/                 # Capturas oficiales de verificación y pruebas
│
├── .dockerignore                  # Exclusión de archivos innecesarios en la imagen
├── .env.example                   # Plantilla de variables de entorno seguras
├── .gitignore                     # Exclusión de credenciales (.env) y venv
├── docker-compose.yml             # Orquestación de la aplicación y PostgreSQL
├── docker-compose.jenkins.yml     # Orquestación del servidor local Jenkins CI
├── Dockerfile                     # Manifiesto de construcción de la imagen Python
├── Jenkinsfile                    # Pipeline declarativo CI/CD para Jenkins
├── requirements-dev.txt           # Dependencias de testing (pytest, flake8)
└── README.md                      # Documentación integral del proyecto
```

---

## 🚀 6. Guía Rápida de Despliegue Local (Docker Compose)

### Prerrequisitos
* Git 2.28+
* Docker Desktop 24+ con soporte para Docker Compose

### Paso 1: Configurar Variables de Entorno
Crea tu archivo local `.env` a partir de la plantilla:
```bash
cp .env.example .env
```
*(En Windows PowerShell: `Copy-Item .env.example .env`)*

### Paso 2: Crear el Volumen Persistente
```bash
docker volume create postgres-data
```

### Paso 3: Construir y Levantar los Servicios
```bash
docker compose up -d --build
```

### Paso 4: Validar el Estado de los Contenedores
```bash
docker compose ps
```
Ambos servicios (`calculator-app` y `calculator-db`) deben figurar en estado `Up` / `healthy`.

---

## 🧪 7. Ejecución de Pruebas Unitarias Locales

Para ejecutar las mismas pruebas que realiza Jenkins en su etapa de CI:

```bash
# Crear entorno virtual
python -m venv .venv
# Activar entorno (PowerShell: .venv\Scripts\Activate.ps1 / Linux: source .venv/bin/activate)

# Instalar dependencias de desarrollo y test
pip install -r requirements-dev.txt

# Ejecutar linter
flake8 app/ tests/

# Ejecutar pruebas unitarias
pytest tests/ -v
```

---

## 🌐 8. Catálogo de Endpoints de la API

La aplicación responde en el puerto `5000` (`http://localhost:5000`):

| Método | Endpoint | Descripción | Formato Body |
|---|---|---|---|
| `GET` | `/` | Comprobación de salud y nombre del host DB conectado. | N/A |
| `POST` | `/calculate` | Realiza operación aritmética y la guarda en PostgreSQL. | JSON: `{"numero1": 20, "numero2": 30, "operacion": "suma"}` |
| `GET` | `/history` | Retorna el historial de operaciones almacenadas. | N/A |

### Ejemplo de Prueba con `curl`:
```bash
curl -X POST http://localhost:5000/calculate \
  -H "Content-Type: application/json" \
  -d '{"numero1": 40, "numero2": 10, "operacion": "resta"}'
```

### Respuesta esperada (HTTP 201 Created):
```json
{
  "guardado_en": "db",
  "id": 1,
  "mensaje": "Operacion guardada correctamente",
  "numero1": 40.0,
  "numero2": 10.0,
  "operacion": "resta",
  "resultado": 30.0
}
```

---

## 🛠️ 9. Despliegue de Jenkins Local

Para levantar el servidor de Jenkins y probar el pipeline:

```bash
# 1. Iniciar contenedor de Jenkins con acceso a Docker
docker compose -f docker-compose.jenkins.yml up -d

# 2. Obtener la contraseña inicial de administrador
docker exec -it jenkins-ci cat /var/jenkins_home/secrets/initialAdminPassword

# 3. Acceder en el navegador
# URL: http://localhost:8080
```

---

## 🔒 10. Seguridad y Buenas Prácticas Implementadas

* **Principio de Versión Inmutable:** Imágenes base con tags fijados explícitamente (`python:3.12.7-slim` y `postgres:16.6`), prohibiendo el uso del antipatrón `:latest`.
* **Zero Hardcoded Secrets:** Ninguna credencial quemada en el código. Uso estricto de `.env` para secretos locales y *Jenkins Credentials* para CI.
* **Aislamiento de Red:** Red Docker bridge dedicada que impide la exposición innecesaria de la base de datos hacia redes públicas.
* **Healthchecks Automáticos:** Sincronización precisa entre servicios mediante `depends_on: condition: service_healthy` antes del arranque del cliente web.
