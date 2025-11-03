from typing import Dict, Type
from app.backend.db.repository_base import CharacterRepository
from app.backend.db.repository_dynamodb import DynamoDBCharacterRepository

class DatabaseFactory:
    """
    Fábrica para instanciar la implementación de CharacterRepository según DB_TYPE.
    Ahora solo soporta 'dynamodb'.
    """

    _databases: Dict[str, Type[CharacterRepository]] = {
        # Mantenemos 'dynamodb' como la única opción válida
        'dynamodb': DynamoDBCharacterRepository,
    }

    @classmethod
    def create(cls, db_type: str) -> CharacterRepository:
        if not db_type:
            raise ValueError("Se debe pasar el tipo de base de datos a 'create()'.")
        
        db_type = db_type.lower()
        database_class = cls._databases.get(db_type)

        if not database_class:
            available = ', '.join(cls._databases.keys())
            # Si se pasa un tipo no válido, el error ahora solo mencionará 'dynamodb'
            raise ValueError(f"DB_TYPE '{db_type}' no válido. Opciones: {available}")
        
        return database_class()

    @classmethod
    def get_available_databases(cls) -> list:
        return list(cls._databases.keys())
