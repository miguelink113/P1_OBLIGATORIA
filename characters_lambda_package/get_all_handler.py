import json
from backend.db.repository_dynamodb import DynamoDBCharacterRepository # Ajusta el import si es necesario
from model.character import Character # Usado para el mapeo si es necesario

# --- Inicialización y utilidades (repetir o importar) ---
db_repo = DynamoDBCharacterRepository() 

def create_response(status_code, body):
    """Utilidad de respuesta."""
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
    """Handler para GET /characters (Obtener todos)"""
    try:
        # Llama a la función del repositorio para obtener todos los elementos
        characters = db_repo.get_all_characters()
        
        # Mapea y devuelve la lista de personajes
        return create_response(200, [c.model_dump() for c in characters])

    except Exception as e:
        print(f"Error al obtener todos los personajes: {e}")
        return create_response(500, {'error': 'Error interno del servidor', 'details': str(e)})