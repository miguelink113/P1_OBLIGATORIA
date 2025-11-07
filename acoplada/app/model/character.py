from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime
import uuid

class Character(BaseModel):
    """
    Representa un personaje de rol con validación de tipos y campos por defecto.
    """
    # Clave Primaria
    character_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        description="ID único y universal del personaje (similar a un UUID)."
    )
    
    # Atributoss
    nombre: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Nombre del personaje (Atributo 1)."
    )
    raza: Literal['Humano', 'Elfo', 'Enano', 'Orco', 'Mediano'] = Field(
        ..., 
        description="Raza del personaje (Atributo 2)."
    )
    clase: Literal['Guerrero', 'Mago', 'Pícaro', 'Clérigo', 'Bardo'] = Field(
        ..., 
        description="Clase del personaje (Atributo 3)."
    )
    nivel: int = Field(
        1, 
        ge=1, 
        le=20, 
        description="Nivel actual del personaje, debe ser entre 1 y 20."
    )
    
    # Atributos de Gestión/Metadata (Similar a created_at, updated_at)
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp de creación en formato ISO 8601."
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp de la última actualización en formato ISO 8601."
    )
    
    # Configuración de Pydantic y Ejemplo de API
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Aerion",
                "raza": "Elfo",
                "clase": "Mago",
                "nivel": 5,
            }
        }
        
    def update_timestamp(self):
        """
        Actualiza el timestamp de modificación del personaje. 
        Útil antes de guardar en la DB (Update).
        """
        self.updated_at = datetime.utcnow().isoformat()
        
    @field_validator('nivel', mode='before')
    @classmethod
    def check_level_is_int(cls, value):
        """
        Validador para convertir el nivel a entero si es una cadena y verificar rango.
        """
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                raise ValueError("El nivel debe ser un número entero.")
        return value

    def to_dict(self) -> dict:
        """
        Convierte el objeto Character a un dict listo para DynamoDB,
        excluyendo valores None y garantizando tipos válidos.
        """
        return self.model_dump(
            exclude_none=True,      # No incluir campos que no tienen valor
            by_alias=False          # DynamoDB usa los nombres reales del modelo
        )
