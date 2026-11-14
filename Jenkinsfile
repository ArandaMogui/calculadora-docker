pipeline {
    agent any

    environment {
        APP_NAME          = "calculator-app"
        DB_NAME           = "calculator-db"
        POSTGRES_DB       = "calculadora"
        POSTGRES_USER     = "admin"
        POSTGRES_PASSWORD = "admin_secure_password"
        DB_HOST           = "db"
    }

    options {
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }

    stages {

        stage('1. Checkout de Codigo') {
            steps {
                echo '📥 Descargando codigo fuente del repositorio...'
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

        stage('4. Construccion de Imagenes Docker') {
            steps {
                echo '🐳 Compilando imagen de aplicacion con Dockerfile y Docker Compose...'
                sh '''
                    cp .env.example .env
                    docker compose build calculator-app
                '''
            }
        }

        stage('5. Pruebas de Integracion Multi-Contenedor') {
            steps {
                echo '🌐 Levantando ambiente multi-contenedor (Flask + PostgreSQL)...'
                sh '''
                    # Asegurar existencia de volumen externo
                    docker volume create postgres-data || true

                    # Iniciar servicios en segundo plano
                    docker compose up -d

                    # Esperar inicializacion de Flask
                    echo "Esperando que calculator-app responda en puerto 5000..."
                    for i in $(seq 1 30); do
                        if curl -fsS http://localhost:5000/ > /dev/null 2>&1; then
                            echo "Aplicacion disponible en el intento $i"
                            break
                        fi
                        echo "Intento $i/30: esperando..."
                        sleep 2
                    done

                    # Prueba de transaccion real ida y vuelta: POST /calculate
                    echo "Ejecutando operacion de prueba POST /calculate..."
                    RESPONSE=$(curl -fsS -X POST http://localhost:5000/calculate \
                        -H "Content-Type: application/json" \
                        -d '{"numero1": 25, "numero2": 75, "operacion": "suma"}')

                    echo "Respuesta recibida: $RESPONSE"

                    # Validar resultado en el cuerpo JSON
                    echo "$RESPONSE" | grep -q '"resultado":100' || echo "$RESPONSE" | grep -q '"resultado": 100'
                    echo "$RESPONSE" | grep -q '"guardado_en":"db"' || echo "$RESPONSE" | grep -q '"guardado_en": "db"'

                    # Validar persistencia real en PostgreSQL
                    echo "Consultando tabla operaciones en PostgreSQL..."
                    docker compose exec -T db psql -U admin -d calculadora -c "SELECT * FROM operaciones ORDER BY id DESC LIMIT 1;"
                '''
            }
        }
    }

    post {
        always {
            echo '🧹 Limpiando ambiente de prueba y liberando recursos...'
            sh '''
                docker compose down -v || true
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
