# ☁️ PRÁCTICA ENTREGABLE: DISEÑO DE APLICACIONES EN LA NUBE

Este repositorio contiene la aplicación desarrollada para la Práctica Obligatoria, diseñada para ser desplegada como un servicio monolítico no desacoplado en la arquitectura **AWS ECS Fargate + API Gateway + NLB**.

## 🎯 Objetivo

Proporcionar una estructura de código y configuración que permita la automatización completa del despliegue de la infraestructura (Infraestructura como Código, IaC) y la aplicación (mediante contenedorización Docker) utilizando **AWS CloudFormation** y la **AWS CLI**.

---

## 📂 Estructura del Proyecto

El proyecto está organizado para separar claramente la lógica de la aplicación, las configuraciones de despliegue y los recursos auxiliares.

| Directorio/Archivo | Contenido Principal | Propósito |
| :--- | :--- | :--- |
| **`app/backend/`** | Lógica de la API, módulos de base de datos. | Contiene el núcleo del servidor, incluyendo la definición de la API (`app_backend.py`) y la gestión de la persistencia (`db/`). |
| **`app/frontend/`** | Archivos de interfaz de usuario. | Aloja el archivo `frontend.html` para la interacción básica del usuario. |
| **`app/model/`** | Clases de datos. | Define la estructura de los objetos de la aplicación (e.g., `character.py`). |
| **`app/test/`** | Scripts de pruebas. | Contiene pruebas de unidad y/o integración (e.g., `test_api_cycle.py`). |
| **`config/`** | Plantillas de CloudFormation (YAML). | Define la infraestructura. Incluye `bd_dynamodb.yml` (base de datos) y `main.yml` (ECS, NLB, API Gateway). |
| **`Dockerfile`** | Definición del contenedor. | Contiene las instrucciones para construir la imagen de Docker de la aplicación. |
| **`ecs-params.json`** | Archivo de parámetros. | Proporciona variables clave (URI de ECR, IDs de VPC/Subredes, Nombre de Tabla DynamoDB) para la plantilla `main.yml` de CloudFormation. |
| **`requirements.txt`** | Dependencias de Python. | Lista de librerías Python requeridas por la aplicación. |
| **`venv/`** | Entorno virtual de Python. | Entorno de desarrollo aislado para gestionar las dependencias localmente. |

---

## ⚙️ Proceso de Despliegue Detallado (AWS CLI)

### FASE 0: Prerrequisitos y Configuración Inicial

1.  **Verificación de Archivos:** Confirme que `bd_dynamodb.yml`, `main.yml`, `Dockerfile` y `ecs-params.json` están actualizados y son correctos.
2.  **Configuración de AWS CLI:** Obtenga las credenciales temporales (`aws_access_key_id`, `aws_secret_access_key`, `aws_session_token`) y configure la CLI.
    ```bash
    aws configure
    export REGION='{TU_REGION}'
    export ACCOUNT_ID='{TU_ID_DE_CUENTA_AWS}'
    aws sts get-caller-identity # Comprobación
    ```
3.  **Docker Desktop:** Asegúrese de que Docker Desktop está en ejecución para la fase de contenedorización.

### FASE 1: Base de Datos (DynamoDB)

Despliega el recurso de base de datos NoSQL.

1.  **Desplegar la Pila de BDD (CloudFormation):**
    ```bash
    aws cloudformation create-stack \
      --stack-name BDD-Stack-P1 \
      --template-body file://config/bd_dynamodb.yml \
      --region $REGION \
      --capabilities CAPABILITY_IAM
    aws cloudformation wait stack-create-complete --stack-name BDD-Stack-P1 --region $REGION
    ```
2.  **Obtener el Nombre de la Tabla:** (Actualizar `ecs-params.json` con este valor).
    ```bash
    aws cloudformation describe-stacks \
      --stack-name BDD-Stack-P1 \
      --query "Stacks[0].Outputs[?OutputKey=='DynamoDBTableName'].OutputValue" \
      --output text
    ```

### FASE 2: Contenedorización y Registro (ECR)

Construcción de la imagen Docker y subida al repositorio de AWS.

1.  **Crear el Repositorio ECR:**
    ```bash
    aws ecr create-repository \
      --repository-name p1-app-repo \
      --region $REGION \
      --image-scanning-configuration scanOnPush=true
    export ECR_URI="$ACCOUNT_ID.dkr.ecr.$[REGION.amazonaws.com/p1-app-repo](https://REGION.amazonaws.com/p1-app-repo)"
    ```
2.  **Login en ECR:**
    ```bash
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI
    ```
3.  **Construir y Subir la Imagen:**
    ```bash
    docker build -t p1-app-repo .
    docker tag p1-app-repo:latest $ECR_URI:latest
    docker push $ECR_URI:latest
    ```

### FASE 3: Despliegue de Infraestructura y Servicios (ECS & API Gateway)

Despliegue de los recursos de computación (ECS Fargate), balanceo de carga (NLB) y la capa de exposición pública (API Gateway, VPC Link).

1.  **Desplegar la Pila Completa (CloudFormation):**
    ```bash
    aws cloudformation create-stack \
      --stack-name ECS-Stack-P1 \
      --template-body file://config/main.yml \
      --parameters file://ecs-params.json \
      --region $REGION \
      --capabilities CAPABILITY_NAMED_IAM
    aws cloudformation wait stack-create-complete --stack-name ECS-Stack-P1 --region $REGION
    ```
2.  **Obtener los Endpoints de Acceso (Outputs):**
    * **A. URL Base de la API Gateway:** (URL pública para testing)
        ```bash
        aws cloudformation describe-stacks \
          --stack-name ECS-Stack-P1 \
          --query "Stacks[0].Outputs[?OutputKey=='CharacterApiUrl'].OutputValue" \
          --output text
        ```
    * **B. ID de la API Key:** (Necesario para obtener el valor secreto en la Consola)
        ```bash
        aws cloudformation describe-stacks \
          --stack-name ECS-Stack-P1 \
          --query "Stacks[0].Outputs[?OutputKey=='ApiKeyId'].OutputValue" \
          --output text
        ```
    * **C. DNS del Load Balancer (Interno):** (Para verificación interna, opcional)
        ```bash
        aws cloudformation describe-stacks \
          --stack-name ECS-Stack-P1 \
          --query "Stacks[0].Outputs[?OutputKey=='CharacterNlbDnsName'].OutputValue" \
          --output text
        ```

### FASE 4: Pruebas Funcionales (CRUD)

Utilice la **CharacterApiUrl** y el valor secreto de la **API Key** (en el header `x-api-key`) para verificar el correcto funcionamiento de las operaciones CRUD (POST, GET, PUT, DELETE) mediante herramientas como Postman o cURL.

### FASE 5: Limpieza de Recursos

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
    aws ecr delete-repository --repository-name p1-app-repo --force --region $REGION
    ```
4.  **Verificación Final:** Confirme que no quedan stacks activos en CloudFormation.