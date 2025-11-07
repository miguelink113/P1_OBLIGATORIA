# ☁️ PRÁCTICA ENTREGABLE: DISEÑO DE APLICACIONES EN LA NUBE

Este repositorio contiene la aplicación desarrollada para la Práctica Obligatoria 1 de Computación en la Nube, diseñada para ser desplegada como un servicio monolítico no desacoplado en la arquitectura **AWS ECS Fargate + API Gateway + NLB**.

## 📂 Estructura del Proyecto

El proyecto está organizado para separar claramente la lógica de la aplicación, las configuraciones de despliegue y los recursos auxiliares.

| Directorio / Archivo | Contenido Principal | Propósito |
| :--- | :--- | :--- |
| **`acoplada/app/backend/`** | Lógica de la API, módulos de base de datos. | Contiene el núcleo del servidor, incluyendo la definición de la API (`app_backend.py`) y la gestión de la persistencia (`db/`). |
| **`acoplada/app/backend/model/`** | Clases de datos. | Define la estructura de los objetos de la aplicación (`character.py`). |
| **`frontend/`** | Archivos de interfaz de usuario. | Contiene el archivo `frontend.html` para la interacción básica del usuario. |
| **`acoplada/config/`** | Plantillas de CloudFormation (YAML). | Define la infraestructura. Incluye `bd_dynamodb.yml` (base de datos), `ecr.yml` (Repositorio Docker) y `ecs.yml` (ECS, NLB, API Gateway). |
| **`desacoplada/`** | Base para la versión desacoplada. | Espacio reservado para una versión con Lambdas + API Gateway + DynamoDB. |
| **`test/`** | Scripts de pruebas. | Incluye `AWS API Characters.postman_collection.json` (colección Postman) y `test_api_cycle.py` (test automático de CRUD). |
| **`Dockerfile`** | Definición del contenedor. | Instrucciones para construir la imagen Docker de la aplicación monolítica. |
| **`acoplada/config/ecs-params.json`** | Archivo de parámetros. | Contiene variables clave (URI de ECR, IDs de VPC/Subredes, Nombre de Tabla DynamoDB). |
| **`requirements.txt`** | Dependencias de Python. | Lista de librerías requeridas por la aplicación. |
| **`venv/`** | Entorno virtual de Python. | Entorno de desarrollo aislado para dependencias locales. |

---

## ⚙️ Proceso de Despliegue Detallado (AWS CLI)

### SECCIÓN 0: Prerrequisitos y Configuración Inicial

1.  **Verificación de Archivos:** Confirme que `bd_dynamodb.yml`, `ecr.yml`, `ecs.yml`, `Dockerfile` y `ecs-params.json` están actualizados y son correctos.
2.  **Configuración de AWS CLI:** Obtenga las credenciales temporales (`aws_access_key_id`, `aws_secret_access_key`, `aws_session_token`) y configure la CLI.
    ```bash
    aws configure
    export REGION='{TU_REGION}'
    export ACCOUNT_ID='{TU_ID_DE_CUENTA_AWS}'
    aws sts get-caller-identity # Comprobación de la autenticación
    ```
3.  **Docker Desktop:** Asegúrese de que Docker Desktop está en ejecución para la fase de contenedorización.

### SECCIÓN 1: Base de Datos (DynamoDB)

Despliega el recurso de base de datos.

1.  **Desplegar la Pila de BDD (CloudFormation):**
    ```bash
    aws cloudformation create-stack 
      --stack-name bdd-stack-p1 
      --template-body file://config/bd_dynamodb.yml
      --region $REGION 
    aws cloudformation wait stack-create-complete --stack-name BDD-Stack-P1 --region $REGION
    ```
2.  **Obtener el Nombre de la Tabla:** (Actualizar `ecs-params.json` con este valor).
    ```bash
    aws cloudformation describe-stacks 
      --stack-name bdd-stack-p1 
      --query "Stacks[0].Outputs[?OutputKey=='TableName'].OutputValue" 
      --output text
    ```

### SECCIÓN 2: Contenedorización y Registro (ECR)

Construcción de la imagen Docker y subida al repositorio de AWS.

1.  **Crear el Repositorio ECR:**
    ```bash
    aws cloudformation create-stack 
    --stack-name ecr-stack-p1 
    --template-body file://config/ecr.yml 
    --region $REGION
    aws cloudformation wait stack-create-complete --stack-name ECR-Stack-P1 --region $REGION
2. **Obtener la URI de ECR y exportar la variable:**
    ```bash
    export ECR_URI="$ACCOUNT_ID.dkr.ecr.$[REGION.amazonaws.com/p1-app-repo](https://REGION.amazonaws.com/p1-app-repo)"
    ```
3.  **Login en ECR:**
    ```bash
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI
    ```
4.  **Construir y Subir la Imagen:**

    IMPORTANTE HABER INICIADO DOCKER DESKTOP

    ```bash
    docker build -t p1-app-repo .
    docker tag p1-app-repo:latest $ECR_URI:latest
    docker push $ECR_URI:latest
    ```

### SECCIÓN 3: Despliegue de Infraestructura y Servicios (ECS & API Gateway)

Despliegue de los recursos de computación (ECS Fargate), balanceo de carga (NLB) y la capa de exposición pública (API Gateway, VPC Link).

1.  **Desplegar la Pila Completa (CloudFormation):**
    ```bash
    aws cloudformation create-stack 
      --stack-name ecs-stack-p1 
      --template-body file://config/ecs.yml 
      --parameters file://config/ecs-params.json 
      --region $REGION 
    aws cloudformation wait stack-create-complete --stack-name ECS-Stack-P1 --region $REGION
    ```
2.  **Obtener los Endpoints de Acceso (Outputs):**
    * **2.1. URL Base de la API Gateway:** (URL pública para testing)
        ```bash
        aws cloudformation describe-stacks 
          --stack-name ecs-stack-p1 
          --query "Stacks[0].Outputs[?OutputKey=='CharacterApiUrl'].OutputValue"
          --output text
        ```
    * **2.2. ID de la API Key:** (Necesario para obtener el valor secreto en la Consola)
        ```bash
        aws cloudformation describe-stacks 
          --stack-name ecs-stack-p1 
          --query "Stacks[0].Outputs[?OutputKey=='ApiKeyId'].OutputValue" 
          --output text
        ```
    * **2.3. Valor secreto de la API Key:** (x-api-key)
        ```bash
        aws apigateway get-api-key
        --api-key a1b2c3d4e5
        --include-value
        --query 'value'
        --output text
        ```
    * **2.4. DNS del Load Balancer (Interno):** (Para verificación interna, opcional)
        ```bash
        aws cloudformation describe-stacks 
          --stack-name ecs-stack-p1 
          --query "Stacks[0].Outputs[?OutputKey=='CharacterNlbDnsName'].OutputValue" 
          --output text
        ```

### SECCIÓN 4: Pruebas Funcionales (CRUD)

Utilice la **CharacterApiUrl** y el valor secreto de la **API Key secreta** (en el header `x-api-key`) para verificar el correcto funcionamiento de las operaciones CRUD (POST, GET, PUT, DELETE) mediante el script de `test/test_api_cycle.py` (prueba los 5 endpoints establecidos de manera automática) o mediante la interfaz gráfica y a mano tras conectar con la API `frontend/frontend.html`

### SECCIÓN 5: Limpieza de Recursos

**Importante:** Elimine todos los recursos para evitar cargos inesperados.

1.  **Eliminar la Pila Principal (ECS/NLB/APIGW):**
    ```bash
    aws cloudformation delete-stack --stack-name ECS-Stack-P1 --region $REGION
    aws cloudformation wait stack-delete-complete --stack-name ECS-Stack-P1 --region $REGION
    ```
2.  **Eliminar la Pila de la Base de Datos (DynamoDB):**
    ```bash
    aws cloudformation delete-stack --stack-name BDD-Stack-P1 --region $REGION
    aws cloudformation wait stack-delete-complete --stack-name BDD-Stack-P1 --region $REGION
    ```
3.  **Vaciar y Eliminar el Repositorio ECR:**
    ```bash
    # Eliminar todas las imágenes
    aws ecr batch-delete-image \
        --repository-name p1-app-repo \
        --image-ids "$(aws ecr list-images --repository-name p1-app-repo --query 'imageIds[*]' --output json --region $REGION)" \
        --region $REGION || true
    # Eliminar el repositorio
    aws cloudformation delete-stack --stack-name ECR-Stack-P1 --region $REGION
    aws cloudformation wait stack-delete-complete --stack-name ECR-Stack-P1 --region $REGION
    ```
4.  **Verificación Final:** Confirme que no quedan stacks activos en CloudFormation.
    ```bash
    aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --region $REGION
    ```

## 💰 Análisis del Costo

| Servicio | Descripción | Costo mensual estimado | Costo anual estimado |
| :--- | :--- | ---: | ---: |
| **Amazon DynamoDB (On-Demand)** | Almacén NoSQL para los personajes, con modo pago por solicitud para 100 mil lecturas y escrituras. | USD 0.32 | USD 3.84 |
| **Amazon ECR (Elastic Container Registry)** | Almacenamiento de las imágenes Docker del servicio de Characters, unos 0.65 GB por mes debido a las dos imágenes de Docker que almacena. | USD 0.07 | USD 0.84 |
| **Amazon ECS (Fargate)** | Ejecución del contenedor con 2 tareas activas (0.25 vCPU, 0.5 GB RAM). | USD 18.02 | USD 216.24 |
| **Amazon API Gateway (REST API)** | Interfaz de acceso HTTP a la API Characters. Costos por llamadas (100 mil llamadas ≈ USD 3.50). | USD 0.35 | USD 4.20 |
| **AWS Network Load Balancer (NLB)** | Balanceo interno del tráfico entre tareas ECS. | USD 16.47 | USD 197.64 |
| **Total estimado** | Se ha considerado un entorno de desarrollo o de bajo tráfico | **USD 35.23** | **USD 422.76** |
