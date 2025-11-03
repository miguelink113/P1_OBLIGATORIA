import os
import boto3
from botocore.exceptions import ClientError

# --- CONFIGURACIÓN (SOLO DYNAMODB LOCAL) ---
DYNAMO_TABLE = os.getenv("DYNAMODB_TABLE_NAME", "Characters")
DYNAMO_ENDPOINT = os.getenv("DYNAMODB_LOCAL_URL", "http://localhost:8000")  # DynamoDB Local
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")  # Necesario para boto3

def initialize_dynamodb():
    print("Inicializando DynamoDB local...")

    # Conectarse a DynamoDB Local
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=AWS_REGION,
        endpoint_url=DYNAMO_ENDPOINT  # Muy importante para usar local
    )

    try:
        # Verifica si la tabla ya existe
        existing_tables = dynamodb.meta.client.list_tables()['TableNames']

        if DYNAMO_TABLE in existing_tables:
            print(f"✅ Tabla DynamoDB local '{DYNAMO_TABLE}' ya existe")
            return

        # Crear tabla si no existe
        table = dynamodb.create_table(
            TableName=DYNAMO_TABLE,
            KeySchema=[{'AttributeName': 'character_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'character_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'  # Ideal para desarrollo local
        )

        print(f"Creando tabla DynamoDB local '{DYNAMO_TABLE}'...")
        table.wait_until_exists()
        print(f"✅ Tabla DynamoDB local '{DYNAMO_TABLE}' creada exitosamente")

    except ClientError as e:
        print(f"Error al inicializar DynamoDB local: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"Error inesperado durante la inicialización de DynamoDB local: {e}")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    initialize_dynamodb()
    print("Inicialización de DynamoDB local completada")
