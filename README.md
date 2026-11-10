Calculadora Python con Docker

1. Descripción del proyecto

Este proyecto consiste en el desarrollo de una calculadora utilizando Python y Flask, desplegada mediante contenedores Docker.

La aplicación permite realizar operaciones matemáticas básicas y almacenar los resultados en una base de datos PostgreSQL.

El proyecto utiliza Docker Compose para administrar los servicios y establecer la comunicación entre los contenedores mediante una red propia de Docker.

2. Tecnologías utilizadas

Python 3.12.7
Flask 3.1.1
Psycopg 3.2.9
PostgreSQL 16.6
Docker
Docker Compose
Git y GitHub
Visual Studio Code
3. Arquitectura del proyecto

El proyecto está compuesto por dos servicios:

Servicio 1: calculator-app

Aplicación desarrollada en Python.
Framework Flask.
Puerto: 5000.
Permite realizar operaciones matemáticas.
Guarda y consulta los resultados en PostgreSQL.

Servicio 2: db

Base de datos PostgreSQL 16.6.
Puerto interno: 5432.
Almacena el historial de operaciones.
Utiliza un volumen persistente llamado postgres-data.

Ambos servicios se comunican mediante la red Docker calculator-network.

La aplicación utiliza el nombre del servicio db como dirección del servidor de base de datos, en lugar de utilizar localhost o una dirección IP fija.

4. Estructura del proyecto
text
calculadora-docker/
│
├── app/
│   ├── app.py
│   └── requirements.txt
│
├── evidencias/
│
├── .dockerignore
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
└── README.md


Nota: el archivo .env contiene credenciales privadas y no debe subirse a GitHub.

5. Requisitos previos

Para ejecutar el proyecto se necesita:

Windows 11, Linux o macOS.
Docker Desktop instalado.
Docker Compose.
Git (opcional, para clonar el repositorio).
6. Configuración inicial

Clonar el repositorio:

bash
git clone https://github.com/ArandaMogui/calculadora-docker.git


Entrar en la carpeta:

bash
cd calculadora-docker


Crear el archivo .env a partir del ejemplo:

En PowerShell:

powershell
Copy-Item .env.example .env


Editar el archivo .env y configurar las credenciales:

dotenv
POSTGRES_DB=calculadora
POSTGRES_USER=admin
POSTGRES_PASSWORD=CAMBIAR_POR_UNA_PASSWORD_SEGURA
DB_HOST=db


No compartir ni subir el archivo .env.

7. Construcción de las imágenes Docker

Para construir la imagen de la aplicación:

bash
docker compose build


Este comando utiliza el Dockerfile para construir la imagen de Python e instalar las dependencias.

8. Levantar los contenedores

Para iniciar los dos servicios:

bash
docker compose up -d


Este comando realiza las siguientes acciones:

Construye la aplicación si es necesario.
Crea la red de Docker.
Inicia PostgreSQL.
Espera a que PostgreSQL esté saludable.
Inicia la aplicación Flask.
9. Verificar los contenedores

Consultar los servicios:

bash
docker compose ps


Consultar los contenedores activos:

bash
docker ps


Consultar los registros:

bash
docker compose logs


Consultar únicamente los registros de la aplicación:

bash
docker compose logs calculator-app


Consultar los registros de PostgreSQL:

bash
docker compose logs db

10. Acceder a la calculadora

Abrir en el navegador:

http://localhost:5000/

La aplicación dispone de los siguientes endpoints:

Método	Endpoint	Función
GET	/	Información de la aplicación
POST	/calculate	Realizar y guardar operaciones
GET	/history	Consultar el historial
11. Prueba de operaciones matemáticas

Ejemplo de una suma utilizando PowerShell:

powershell
Invoke-RestMethod `
-Uri http://localhost:5000/calculate `
-Method POST `
-ContentType "application/json" `
-Body '{"numero1":20,"numero2":30,"operacion":"suma"}'


Resultado esperado:

text
numero1     : 20
numero2     : 30
operacion   : suma
resultado   : 50
guardado_en : db

12. Consultar el historial

Para consultar las operaciones almacenadas:

powershell
Invoke-RestMethod -Uri http://localhost:5000/history

13. Verificar los datos directamente en PostgreSQL

Ejecutar:

bash
docker compose exec db psql -U admin -d calculadora


Consultar las operaciones:

sql
SELECT * FROM operaciones;


Salir de PostgreSQL:

sql
\q

14. Verificar la red Docker

Listar las redes:

bash
docker network ls


Inspeccionar la red:

bash
docker network inspect calculadora-docker_calculator-network


La red conecta los servicios calculator-app y db.

15. Detener los contenedores

Para detener los servicios:

bash
docker compose stop


Para detener y eliminar los contenedores y la red:

bash
docker compose down


Los datos de PostgreSQL permanecen en el volumen persistente.

Para eliminar también el volumen y sus datos:

bash
docker compose down -v


Advertencia: el último comando elimina permanentemente los datos almacenados en el volumen de PostgreSQL.

16. Seguridad y buenas prácticas
Se utiliza una imagen oficial de Python con versión fija.
Se utiliza PostgreSQL con versión fija.
Las credenciales se configuran mediante variables de entorno.
El archivo .env está excluido del repositorio.
Se proporciona un archivo .env.example.
Se utiliza .dockerignore para excluir archivos innecesarios.
Los datos se conservan mediante un volumen Docker.
La aplicación se comunica con PostgreSQL mediante el nombre de servicio db.
17. Autor

Proyecto académico: Calculadora Python con Docker.

Desarrollado utilizando Python, Flask, PostgreSQL, Docker y Docker Compose.