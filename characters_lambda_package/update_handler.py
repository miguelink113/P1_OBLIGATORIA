import json
from pydantic import ValidationError
from backend.db.repository_dynamodb import DynamoDBCharacterRepository # Ajusta el import si es necesario

# --- Inicialización y utilidades (repetir o importar) ---
db_repo = DynamoDBCharacterRepository() 

def create_response(status_code, body):
    """Utilidad de respuesta."""
    # ... (cuerpo de la función create_response)
    return {
        'statusCode': status_code,
        'headers': {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Api-Key",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        'body': json.dumps(body)
    }

# --- Handler principal ---
def lambda_handler(event, context):
    """Handler para PUT /characters/{id} (Actualizar)"""
    try:
        character_id = event['pathParameters']['id']
        data = json.loads(event['body'])
        
        # Eliminar claves de control para evitar sobreescritura accidental
        data.pop('character_id', None)
        data.pop('created_at', None) 
        data.pop('updated_at', None) 
        
        # El repositorio maneja el update con el ID y los datos
        updated = db_repo.update_character(character_id, data) 
        
        if updated:
            return create_response(200, updated.model_dump())
        
        return create_response(404, {'error': 'Personaje no encontrado para actualizar'})
        
    except ValidationError as e:
        return create_response(400, {'error': 'Error de validación', 'details': e.errors()})
    except Exception as e:
        print(f"Error al actualizar personaje {character_id}: {e}")
        return create_response(500, {'error': 'Error interno del servidor', 'details': str(e)})