from abc import ABC, abstractmethod
from typing import List, Optional
from app.model.character import Character

class CharacterRepository(ABC):
    """
    Define la interfaz abstracta para interactuar con la capa de persistencia 
    (Base de Datos) para los objetos Character.
    """
    
    @abstractmethod
    def initialize(self):
        """
        Realiza la inicialización necesaria de la conexión o recursos de la DB 
        (ej. crear la tabla si no existe, o establecer la conexión con RDS).
        """
        pass
    
    # 1. CREATE (Crear un nuevo personaje)
    @abstractmethod
    def create_character(self, character: Character) -> Character:
        """
        Inserta un nuevo personaje en la base de datos.
        Retorna el objeto Character con su ID asignado por la DB.
        """
        pass
    
    # 2. READ por ID (Obtener un personaje específico)
    @abstractmethod
    def get_character(self, character_id: str) -> Optional[Character]:
        """
        Busca y retorna un personaje por su ID único.
        Retorna None si el ID no existe.
        """
        pass
    
    # 3. READ All (Obtener todos los personajes)
    @abstractmethod
    def get_all_characters(self) -> List[Character]:
        """
        Retorna una lista de todos los personajes almacenados.
        """
        pass
    
    # 4. UPDATE (Actualizar un personaje existente)
    @abstractmethod
    def update_character(self, character_id: str, character: Character) -> Optional[Character]:
        """
        Actualiza un personaje existente por ID con los nuevos datos.
        Retorna el objeto Character actualizado o None si el ID no existe.
        """
        pass
    
    # 5. DELETE (Eliminar un personaje)
    @abstractmethod
    def delete_character(self, character_id: str) -> bool:
        """
        Elimina el personaje por su ID.
        Retorna True si la eliminación fue exitosa, False si el personaje no fue encontrado.
        """
        pass