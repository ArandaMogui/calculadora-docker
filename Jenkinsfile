pipeline {
    agent any

    environment {
        APP_NAME    = "calculator-app"
        DB_NAME     = "calculator-db"
        POSTGRES_DB = "calculadora"
        DB_HOST     = "db"
        // Seguridad: Credenciales inyectadas desde el gestor nativo de Jenkins (Credentials Binding)
        // Nunca quemadas en texto plano en el codigo ni en el repositorio (Criterio 2 de la rubrica)
        DB_CREDS    = credentials('postgres-db-credentials')
    }

    triggers {
        // Disparo automatico ante cambios en el repositorio GitHub (Criterio 4 de la rubrica)
        githubPush()
        pollSCM('H/5 * * * *')
    }

    options {
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }

    stages {

        stage('1. Checkout de Codigo') {
            steps {
                echo '📥 Descargando codigo fuente del repositorio GitHub...'
                checkout scm
                sh 'git log -1 --pretty=format:"Commit: %h - %an: %s (%ci)"'
            }
        }

        stage('2. Analisis Estatico y Calidad (Linter)') {
            steps {
                echo '🔍 Verificando calidad y estilo de codigo con Flake8...'
                sh '''
                    python3 -m venv .venv_ci
                    . .venv_ci/bin/activate
                    pip install --upgrade pip
                    pip install flake8
                    flake8 app/ tests/ --max-line-length=120 --statistics
                '''
            }
        }

        stage('3. Pruebas Unitarias Automatizadas') {
            steps {
                echo '🧪 Ejecutando suite de pruebas unitarias con Pytest...'
                sh '''
                    . .venv_ci/bin/activate
                    pip install -r requirements-dev.txt
                    mkdir -p reports
                    python -m pytest tests/ -v --junitxml=reports/unit-tests-report.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/unit-tests-report.xml'
                }
            }
        }

        stage('4. Build de Contenedores de la Entrega 1') {
            steps {
                echo '🐳 Compilando y empaquetando imagenes Docker de los servicios (Entrega 1)...'
                sh '''
                    # Generacion dinamica y segura del entorno desde credenciales de Jenkins
                    echo "POSTGRES_USER=${DB_CREDS_USR}" > .env
                    echo "POSTGRES_PASSWORD=${DB_CREDS_PSW}" >> .env
                    echo "POSTGRES_DB=${POSTGRES_DB}" >> .env
                    echo "DB_HOST=${DB_HOST}" >> .env
                    echo "PORT=5000" >> .env

                    # Construccion y verificacion de los dos contenedores (calculator-app y db)
                    docker compose build --no-cache
                    docker compose pull db
                    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep -E "calculadora|postgres" || true
                '''
            }
        }

        stage('5. Pruebas de Integracion Multi-Contenedor') {
            steps {
                echo '🌐 Levantando ambiente multi-contenedor (Flask + PostgreSQL en red bridge)...'
                sh '''
                    # Asegurar existencia de volumen persistente externo
                    docker volume create postgres-data || true

                    # Iniciar servicios en segundo plano
                    docker compose up -d

                    # Esperar disponibilidad del servicio web en el puerto 5000
                    echo "Esperando que calculator-app responda en http://localhost:5000/ ..."
                    for i in $(seq 1 30); do
                        if curl -fsS http://localhost:5000/ > /dev/null 2>&1; then
                            echo "Aplicacion disponible en el intento $i"
                            break
                        fi
                        echo "Intento $i/30: esperando respuesta del contenedor..."
                        sleep 2
                    done

                    # Prueba de transaccion real ida y vuelta: POST /calculate
                    echo "Ejecutando transaccion de prueba POST /calculate..."
                    RESPONSE=$(curl -fsS -X POST http://localhost:5000/calculate \
                        -H "Content-Type: application/json" \
                        -d '{"numero1": 25, "numero2": 75, "operacion": "suma"}')

                    echo "Respuesta recibida: $RESPONSE"

                    # Validar resultado aritmetico y origen del almacenamiento
                    echo "$RESPONSE" | grep -q '"resultado":100' || echo "$RESPONSE" | grep -q '"resultado": 100'
                    echo "$RESPONSE" | grep -q '"guardado_en":"db"' || echo "$RESPONSE" | grep -q '"guardado_en": "db"'

                    # Validar persistencia real en PostgreSQL usando el nombre de servicio 'db'
                    echo "Consultando tabla de operaciones directamente en PostgreSQL..."
                    docker compose exec -T db psql -U ${DB_CREDS_USR} -d ${POSTGRES_DB} -c "SELECT * FROM operaciones ORDER BY id DESC LIMIT 1;"
                '''
            }
        }
    }

    post {
        always {
            echo '🧹 Limpiando ambiente de prueba y liberando recursos de contenedores...'
            sh '''
                docker compose down -v || true
                rm -f .env
                rm -rf .venv_ci
            '''
        }
        success {
            echo '✅ [EXITO] El pipeline de Jenkins finalizo exitosamente. Integracion Continua validada.'
        }
        failure {
            echo '❌ [FALLO] El pipeline fallo en alguna etapa. Inspeccionar logs de diagnostico.'
            sh '''
                docker compose logs || true
            '''
        }
    }
}
