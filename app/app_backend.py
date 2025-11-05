import os
from flask import Flask, request, jsonify
from pydantic import ValidationError
from botocore.exceptions import ClientError

from model.character import Character
from backend.repository_factory import DatabaseFactory
from backend.db.repository_base import CharacterRepository

app = Flask(__name__)

# --- Inicialización de la Base de Datos ---
db_type = os.getenv('DB_TYPE', 'dynamodb')
try:
    db: CharacterRepository = DatabaseFactory.create(db_type)
except ValueError as e:
    raise RuntimeError(f"Error inicializando la DB: {e}") from e

# --- Manejo de CORS ---
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,x-api-key'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

# --- Manejo centralizado de errores ---
def handle_db_error(e):
    if isinstance(e, ClientError):
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code in ('AccessDeniedException', 'ValidationException'):
             return jsonify({'error': 'Error de configuración o validación', 'details': error_message}), 403
             
        return jsonify({'error': f'Error de DynamoDB ({error_code})', 'details': error_message}), 500
        
    return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500

# --- Endpoints CRUD ---

@app.route('/characters', methods=['POST'])
def create_character():
    try:
        data = request.get_json()
        character = Character(**data)
        created = db.create_character(character)
        return jsonify(created.model_dump()), 201
    except ValidationError as e:
        return jsonify({'error': 'Error de validación', 'details': e.errors()}), 400
    except Exception as e:
        return handle_db_error(e)

@app.route('/characters/<character_id>', methods=['GET'])
def get_character(character_id):
    try:
        character = db.get_character(character_id)
        if character:
            return jsonify(character.model_dump()), 200
        return jsonify({'error': 'Personaje no encontrado'}), 404
    except Exception as e:
        return handle_db_error(e)

@app.route('/characters', methods=['GET'])
def get_all_characters():
    try:
        characters = db.get_all_characters()
        return jsonify([c.model_dump() for c in characters]), 200
    except Exception as e:
        return handle_db_error(e)

@app.route('/characters/<character_id>', methods=['PUT'])
def update_character(character_id):
    try:
        # FIX para 400 Bad Request: Obtenemos el diccionario JSON directamente.
        data = request.get_json()
        
        # Eliminamos claves de control, ya que las gestiona el repositorio
        data.pop('character_id', None)
        data.pop('created_at', None) 
        data.pop('updated_at', None) # Evita que el cliente intente sobreescribir la fecha
        
        # IMPORTANTE: Llamamos al repositorio pasando el diccionario de datos (data),
        # que es lo que la función update_character del Canvas espera ahora (update_data: Dict).
        updated = db.update_character(character_id, data) 
        
        if updated:
            # updated ya es el objeto Character completo devuelto por el repositorio
            return jsonify(updated.model_dump()), 200
        # Si el repositorio devuelve None, es 404
        return jsonify({'error': 'Personaje no encontrado'}), 404
        
    except Exception as e:
        # Aquí también podemos capturar errores de tipo Pydantic si el repositorio los lanza
        if isinstance(e, ValidationError):
            return jsonify({'error': 'Error de validación', 'details': e.errors()}), 400
        return handle_db_error(e)

@app.route('/characters/<character_id>', methods=['DELETE'])
def delete_character(character_id):
    try:
        # FIX para 404 Not Found: El repositorio devuelve True si se elimina.
        if db.delete_character(character_id):
            # Si se eliminó, devolvemos 204 No Content, que es la respuesta HTTP correcta
            return '', 204
        # Si el repositorio devuelve False, significa que no lo encontró
        return jsonify({'error': 'Personaje no encontrado'}), 404
    except Exception as e:
        return handle_db_error(e)

@app.route('/health', methods=['GET'])
def health():
    """Chequeo simple de salud. Verifica que la API está corriendo y qué DB usa."""
    try:
        return jsonify({'status': 'healthy', 'db_type': db_type, 'message': 'API de Personajes OK'}), 200
    except Exception as e:
        return handle_db_error(e)

# --- Entrada para desarrollo/local ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
