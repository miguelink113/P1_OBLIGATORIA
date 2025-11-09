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
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Api-Key",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        'body': json.dumps(body) # Puede ser una cadena vacía si es 204
    }

# --- Handler principal ---
def lambda_handler(event, context):
    """Handler para DELETE /characters/{id} (Eliminar)"""
    try:
        character_id = event['pathParameters']['id']
        
        # El repositorio debe devolver True si se eliminó, False si no existía
        if db_repo.delete_character(character_id):
            # 204 No Content es la respuesta HTTP correcta para un borrado exitoso
            return create_response(204, '') 
        
        return create_response(404, {'error': 'Personaje no encontrado para eliminar'})
        
    except Exception as e:
        print(f"Error al eliminar personaje {character_id}: {e}")
        return create_response(500, {'error': 'Error interno del servidor', 'details': str(e)})