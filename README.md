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

Este proyecto consiste en el desarrollo, contenerización y automatización del ciclo de vida de una **Calculadora Distribuida** construida en **Python 3.12.7** con el microframework **Flask 3.1.1**, desacoplada en una arquitectura multi-contenedor e integrada con una base de datos relacional **PostgreSQL 16.6**.

La aplicación permite resolver operaciones aritméticas (`suma`, `resta`, `multiplicacion` y `division`), aplicar validaciones matemáticas robustas (control de división entre cero y validación de payloads JSON) y garantizar la persistencia transaccional del historial en PostgreSQL.

La infraestructura se encuentra declarada completamente como código mediante **Docker** y **Docker Compose**, y orquestada mediante un pipeline de Integración Continua en **Jenkins** (`Jenkinsfile`), complementado con el flujo inicial de **GitHub Actions**.

---

## 📊 2. Matriz de Progreso de Entregas Académicas

| Hito / Entrega | Semana | Estado | Tecnologías y Alcance Logrado |
|---|---|:---:|---|
| **Entrega 1: Docker con Dos Contenedores Comunicados** | Semana 3 | ✅ **COMPLETADA**<br>*(10/Nov/2026)* | • Repositorio GitHub estructurado.<br>• Contenedor 1 (`calculator-app`): Python 3.12.7-slim + Flask 3.1.1.<br>• Contenedor 2 (`calculator-db`): PostgreSQL 16.6.<br>• Red personalizada bridge `calculator-network`.<br>• Comunicación obligatoria por nombre de servicio (`DB_HOST=db`).<br>• Transacción real de ida y vuelta (`POST /calculate`).<br>• Volumen nominal persistente `postgres-data`.<br>• Seguridad: `.env`, `.env.example`, `.dockerignore`.<br>• Pipeline inicial en GitHub Actions (`docker-build.yml`).<br>• Informe formal en Normas APA 7 con evidencias. |
| **Entrega 2: Implementación de Jenkins como Gestor de Operaciones** | Semana 5 | ✅ **COMPLETADA**<br>*(24/Nov/2026)* | • Servidor **Jenkins LTS** (`jenkins/jenkins:lts-jdk21`) contenerizado con `Dockerfile.jenkins` y `docker-compose.jenkins.yml`, volumen persistente `jenkins_home` y *Docker Socket Binding* (`/var/run/docker.sock`).<br>• **Credenciales seguras** en el almacén nativo de Jenkins (`postgres-db-credentials` vía *Credentials Binding*, nunca quemadas en código).<br>• **Pipeline Declarativo como Código (`Jenkinsfile`)** con etapas de Checkout, Linter, Pruebas Unitarias, Build de Contenedores, Integración Multi-Contenedor y bloque `post`.<br>• **Disparo automático desde GitHub** mediante `githubPush()` y `pollSCM('H/5 * * * *')`.<br>• Suite de **11 pruebas unitarias** (`tests/test_calculadora.py` con `pytest` + reporte **JUnit XML**) y análisis estático con `flake8`.<br>• Construcción y verificación de **ambos servicios** (`calculator-app` y `postgres:16.6`) y prueba de integración real por nombre de servicio `db`.<br>• Evidencia del ciclo **Fail-Fast** (Build #1 fallido en rojo ➔ Build #2 corregido en verde) con **14 figuras APA 7** e informe final en PDF/DOCX. |
| **Entrega 3 y Sustentación: Integración Continua Integral** | Semanas 7 y 8 | ⚪ **PLANIFICADA** | • Integración continua ampliada y observabilidad de despliegues.<br>• Monitoreo, trazabilidad de fallos e historial consolidado.<br>• Documento final integrado y defensa técnica (Sustentación oral). |

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

El archivo [`Jenkinsfile`](./Jenkinsfile) gobierna el ciclo de vida del código y se dispara automáticamente ante cada `push` en GitHub mediante **Webhook (`githubPush()`)** y **Sondeo SCM (`pollSCM('H/5 * * * *')`)**:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ 1. Checkout SCM │ ──> │ 2. Linter       │ ──> │ 3. Unit Tests   │ ──> │ 4. Build        │ ──> │ 5. Test Integr. │
│ (GitHub Push /  │     │ (Flake8 PEP 8)  │     │ (11 Pytest +    │     │ (calculator-app │     │ (Flask ➔ db     │
│  Poll SCM)      │     │                 │     │  JUnit XML)     │     │  + postgres:16) │     │  PostgreSQL)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
                                                                                                         │
                                                                                                         ▼
                                                                                                ┌─────────────────┐
                                                                                                │ 6. Bloque Post  │
                                                                                                │ (docker down -v │
                                                                                                │  + rm .env)     │
                                                                                                └─────────────────┘
```

1. **Checkout de Código:** Descarga la revisión disparada por Webhook/Poll SCM y registra el hash y mensaje del commit.
2. **Análisis Estático (Flake8):** Audita calidad y estilo PEP 8 (`--max-line-length=120`), aplicando *Fail-Fast* ante cualquier infracción.
3. **Pruebas Unitarias (Pytest + JUnit):** Ejecuta las **11 pruebas unitarias** en `tests/test_calculadora.py` y publica los resultados XML en Jenkins mediante el plugin JUnit. Si falla una aserción (ej. Build #1), el pipeline aborta de inmediato.
4. **Build de Contenedores (Entrega 1):** Genera dinámicamente `.env` a partir de las credenciales cifradas de Jenkins (`DB_CREDS = credentials('postgres-db-credentials')`) y construye/verifica las imágenes de ambos servicios (`docker compose build --no-cache` y `docker compose pull db`).
5. **Pruebas de Integración Multi-Contenedor:** Levanta ambos servicios con `docker compose up -d`, realiza una transacción real `POST /calculate` (`25 + 75 = 100.0`) y verifica la persistencia física en PostgreSQL usando el nombre de servicio **`db`**.
6. **Bloque `post`:** Ejecuta limpieza obligatoria (`docker compose down -v`, eliminación de `.env` y `.venv_ci`) y emite diagnóstico en `success` o `failure`.

---

## 📁 5. Estructura del Repositorio

```text
calculadora-docker/
│
├── .github/workflows/             # Flujo CI complementario en GitHub Actions (docker-build.yml)
├── app/                           # Código fuente del microservicio Flask
│   ├── app.py                     # API REST Flask con lógica desacoplada procesar_calculo()
│   └── requirements.txt           # Dependencias de producción (Flask 3.1.1, psycopg 3.2.9)
│
├── tests/                         # Suite de pruebas automatizadas para CI
│   ├── __init__.py
│   └── test_calculadora.py        # 11 pruebas unitarias (lógica aritmética + endpoints Flask)
│
├── evidencias/                    # Evidencias visuales de Entrega 1 (E01-E09) y Entrega 2 (E10-E24)
│
├── .dockerignore                  # Exclusión de archivos innecesarios en la imagen Docker
├── .env.example                   # Plantilla de variables de entorno (sin secretos reales)
├── .gitignore                     # Exclusión de .env, entornos virtuales y artefactos locales
├── docker-compose.yml             # Orquestación de calculator-app y calculator-db (PostgreSQL 16.6)
├── docker-compose.jenkins.yml     # Orquestación del servidor local Jenkins CI con volumen y socket
├── Dockerfile                     # Construcción de la imagen calculator-app (python:3.12.7-slim)
├── Dockerfile.jenkins             # Imagen Jenkins LTS (JDK 21) + Docker CLI + Compose + Python 3
├── Jenkinsfile                    # Pipeline declarativo CI/CD (credenciales, triggers, stages y post)
├── requirements-dev.txt           # Dependencias de pruebas y calidad (pytest 8.3.4, flake8 7.1.1)
└── README.md                      # Documentación integral del proyecto
```

---

## 🚀 6. Guía Rápida de Despliegue Local (Docker Compose)

### Prerrequisitos
* Git 2.39+
* Docker Desktop 24+ (con WSL2 en Windows) o Docker Engine con Docker Compose v2

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

## 🧪 7. Ejecución de Pruebas Unitarias y Linter en Local

Para reproducir localmente las etapas 2 y 3 del pipeline de Jenkins:

```bash
# Crear y activar entorno virtual
python -m venv .venv
# PowerShell: .venv\Scripts\Activate.ps1 | Linux/macOS: source .venv/bin/activate

# Instalar dependencias de desarrollo y pruebas
pip install -r requirements-dev.txt

# Ejecutar análisis estático (PEP 8)
flake8 app/ tests/ --max-line-length=120 --statistics

# Ejecutar las 11 pruebas unitarias
python -m pytest tests/ -v
```

---

## 🌐 8. Catálogo de Endpoints de la API

La aplicación responde en el puerto `5000` (`http://localhost:5000`):

| Método | Endpoint | Descripción | Formato Body |
|---|---|---|---|
| `GET` | `/` | Comprobación de salud y nombre del host DB conectado (`db`). | N/A |
| `POST` | `/calculate` | Realiza operación aritmética y la persiste en PostgreSQL. | JSON: `{"numero1": 25, "numero2": 75, "operacion": "suma"}` |
| `GET` | `/history` | Retorna el historial de operaciones almacenadas. | N/A |

### Ejemplo de Prueba con `curl`:
```bash
curl -X POST http://localhost:5000/calculate \
  -H "Content-Type: application/json" \
  -d '{"numero1": 25, "numero2": 75, "operacion": "suma"}'
```

### Respuesta esperada (HTTP 201 Created):
```json
{
  "guardado_en": "db",
  "id": 1,
  "mensaje": "Operacion guardada correctamente",
  "numero1": 25.0,
  "numero2": 75.0,
  "operacion": "suma",
  "resultado": 100.0
}
```

---

## 🛠️ 9. Despliegue y Configuración de Jenkins Local (Entrega 2)

```bash
# 1. Construir e iniciar el contenedor de Jenkins LTS con Docker CLI y volumen persistente
docker compose -f docker-compose.jenkins.yml up -d --build

# 2. Obtener la contraseña inicial de desbloqueo
docker exec -it jenkins-ci cat /var/jenkins_home/secrets/initialAdminPassword

# 3. Acceder en el navegador: http://localhost:8080
```

### Configuración Inicial en Jenkins:
1. Instalar los plugins: **Pipeline**, **Git / GitHub**, **Docker Pipeline**, **Credentials Binding** y **JUnit**.
2. Crear la credencial global (*Username with password*) con ID **`postgres-db-credentials`** en *Administrar Jenkins ➔ Credentials ➔ Global credentials*.
3. Crear un Job tipo **Pipeline** llamado **`calculadora-docker-ci`** apuntando a este repositorio (`Pipeline script from SCM`, ruta `Jenkinsfile`).

---

## 🔒 10. Seguridad y Buenas Prácticas Implementadas

* **Versiones Inmutables (Sin `:latest`):** Imágenes fijadas explícitamente (`python:3.12.7-slim`, `postgres:16.6`, `jenkins/jenkins:lts-jdk21`, `docker/compose-bin:v2.29.7`).
* **Zero Hardcoded Secrets:** Ninguna contraseña escrita en código fuente ni en el `Jenkinsfile`. Uso estricto de `.env` local (ignorado en `.gitignore`) y *Jenkins Credentials Store* (`postgres-db-credentials`) en CI.
* **Aislamiento de Red:** Red Docker bridge dedicada (`calculator-network`) con resolución DNS por nombre de servicio (`DB_HOST=db`).
* **Healthchecks y Fail-Fast:** Sincronización mediante `depends_on: condition: service_healthy` y detención automática del pipeline si falla el linter, cualquiera de las 11 pruebas unitarias o la verificación en PostgreSQL.
