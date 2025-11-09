import json
from backend.db.repository_dynamodb import DynamoDBCharacterRepository # Ajusta el import si es necesario

# --- Inicialización y utilidades (repetir o importar) ---
db_repo = DynamoDBCharacterRepository() 

def create_response(status_code, body):
    """Utilidad de respuesta."""
    # ... (cuerpo de la función create_response)
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }

# --- Handler principal ---
def lambda_handler(event, context):
    """Handler para GET /characters/{id} (Obtener por ID)"""
    try:
        # API Gateway coloca los parámetros de ruta en 'pathParameters'
        # Asegúrate de que tu YAML de despliegue define la ruta con {id}
        character_id = event['pathParameters']['id']
        
        character = db_repo.get_character(character_id)
        
        if character:
            return create_response(200, character.model_dump())
        
        # 404 Not Found si el repositorio devuelve None
        return create_response(404, {'error': 'Personaje no encontrado'})

    except Exception as e:
        print(f"Error al obtener personaje {character_id}: {e}")
        return create_response(500, {'error': 'Error interno del servidor', 'details': str(e)})