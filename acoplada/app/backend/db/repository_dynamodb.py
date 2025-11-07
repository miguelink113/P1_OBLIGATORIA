import boto3
import os
import datetime # NECESARIO para manejar la marca de tiempo de la actualización
from typing import List, Optional, Dict # Importamos Dict para el PUT
from backend.db.repository_base import CharacterRepository
from model.character import Character

TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME') 

if not TABLE_NAME:
    # Lanza un error claro si la configuración de ECS falló
    raise RuntimeError("La variable de entorno DYNAMODB_TABLE_NAME no está configurada en el contenedor ECS.")

class DynamoDBCharacterRepository(CharacterRepository):
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(TABLE_NAME)
    
    def initialize(self):
        """
        Realiza la inicialización de la tabla DynamoDB.
        """
        try:
            self.table.load()  # Verifica que la tabla exista
            print(f"DynamoDB table '{TABLE_NAME}' is ready.")
        except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
            print(f"DynamoDB table '{TABLE_NAME}' does not exist. You need to create it.")

    def _to_character(self, item: dict) -> Character:
        if not item:
            return None
        valid_fields = Character.model_fields.keys()
        clean = {k: v for k, v in item.items() if k in valid_fields}
        return Character(**clean)

    def create_character(self, character: Character) -> Character:
        self.table.put_item(Item=character.model_dump())
        return character
    
    def get_character(self, character_id: str) -> Optional[Character]:
        response = self.table.get_item(Key={'character_id': character_id})
        item = response.get('Item')
        return self._to_character(item)
    
    def get_all_characters(self) -> List[Character]:
        response = self.table.scan()
        items = response.get('Items', [])
        return [self._to_character(row) for row in items]
    
    # ----------------------------------------------------
    # FIX para el 400 Bad Request
    # Cambiamos el tipo de dato de entrada a 'update_data: Dict'
    # ----------------------------------------------------
    def update_character(self, character_id: str, update_data: Dict) -> Optional[Character]:
        
        # 1. Aseguramos el campo de fecha de actualización
        update_data['updated_at'] = datetime.datetime.utcnow().isoformat()
        
        # 2. Eliminamos campos que no deben ser actualizados (claves)
        update_data.pop('character_id', None)
        update_data.pop('created_at', None) 

        if not update_data:
            return self.get_character(character_id)

        update_expression = "SET "
        expr_values = {}
        expr_names = {}

        # 3. Construimos dinámicamente la expresión de actualización para DynamoDB
        for i, (key, value) in enumerate(update_data.items()):
            # Usamos un esquema de nombres más robusto para evitar colisiones con palabras reservadas
            name = f'#key{i}'
            val = f':val{i}'
            update_expression += f"{name} = {val}"
            if i < len(update_data) - 1:
                update_expression += ", "
            expr_names[name] = key
            expr_values[val] = value

        response = self.table.update_item(
            Key={'character_id': character_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ReturnValues='ALL_NEW'
        )

        item = response.get('Attributes')
        return self._to_character(item) if item else None

    # ----------------------------------------------------
    # FIX para el 404 Not Found en DELETE
    # Se verifica si realmente se eliminó un elemento.
    # ----------------------------------------------------
    def delete_character(self, character_id: str) -> bool:
        response = self.table.delete_item(
            Key={'character_id': character_id},
            ReturnValues='ALL_OLD'
        )
        # DynamoDB retorna un diccionario con 'Attributes' si se eliminó algo.
        # Si el elemento no existe, retorna 200 OK pero sin 'Attributes'.
        # Devolvemos True solo si 'Attributes' está presente.
        return 'Attributes' in response
