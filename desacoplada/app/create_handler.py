import json
from model.character import Character 
from pydantic import ValidationError
from backend.db.repository_dynamodb import DynamoDBCharacterRepository # o tu repositorio RDS

# Inicialización (ejecutada una vez en frío)
db_repo = DynamoDBCharacterRepository() 

def create_response(status_code, body):
    """Utilidad de respuesta."""
    # (El mismo utilitario de respuesta que definimos antes)
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }

def lambda_handler(event, context):
    """Handler para POST /characters"""
    try:
        # 1. Obtener datos (asumimos que el body existe para un POST)
        data = json.loads(event['body'])
        
        # 2. Validar y crear
        character = Character(**data)
        created = db_repo.create_character(character)
        
        # 3. Devolver 201 Created
        return create_response(201, created.model_dump())

    except ValidationError as e:
        return create_response(400, {'error': 'Error de validación', 'details': e.errors()})
    except Exception as e:
        # Aquí llamarías a una función de manejo de errores más robusta
        return create_response(500, {'error': 'Error interno', 'details': str(e)})