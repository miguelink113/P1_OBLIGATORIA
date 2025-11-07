import requests
import json
import sys

# --- CONFIGURACIÓN CRÍTICA ---
# ⚠️ IMPORTANTE: REEMPLAZA LOS VALORES CON LOS OUTPUTS DE TU STACK DE CLOUDFORMATION.

# 1. URL BASE de la API Gateway (Ej: https://abcdef123.execute-api.us-east-1.amazonaws.com/prod)
BASE_URL = "https://6wh6fxb8be.execute-api.us-east-1.amazonaws.com/prod" 

# 2. HEADER: La clave de API para autenticar la petición.
API_KEY_VALUE = "dkKi8GK9zh1OdmTiY3L7596MGMNMmviI5evznWS4"

# 3. ENDPOINT/RECURSO: La ruta base que definiste en tu OpenAPI (ej. /characters).
# **NO** incluyas el nombre del stack ni el stage.
ENDPOINT = "/characters"

# Define el encabezado de autenticación
HEADERS = {
    "x-api-key": API_KEY_VALUE,
    "Content-Type": "application/json"
}

# --- DATOS DE PRUEBA ---
INITIAL_CHARACTER_DATA = {
    "nombre": "TestSubject",
    "raza": "Mediano",
    "clase": "Pícaro",
    "nivel": 3
}

# Variable para almacenar el ID creado durante la prueba
CREATED_ID = None
# -------------------------

def check_config():
    """Verifica que la configuración crítica se ha actualizado."""
    if BASE_URL.startswith("INSÉRTA") or API_KEY_VALUE.startswith("INSÉRTA"):
        print("🛑 ERROR DE CONFIGURACIÓN: Debes reemplazar BASE_URL y API_KEY_VALUE.")
        sys.exit(1)

def create_character():
    """Tests the POST method and captures the created ID."""
    print("--- 1. POST: Creando nuevo personaje ---")
    global CREATED_ID
    
    try:
        # Usa el encabezado de autenticación
        response = requests.post(f"{BASE_URL}{ENDPOINT}", json=INITIAL_CHARACTER_DATA, headers=HEADERS)
        response.raise_for_status() # Lanza excepción para códigos 4xx o 5xx
        
        data = response.json()
        # **NOTA: Asume que el ID se devuelve con la clave 'id' o 'character_id'.
        # Ajusta esta clave si tu API usa otra (ej. 'ID' o 'id').**
        CREATED_ID = data.get('id') or data.get('character_id')
        
        if CREATED_ID:
            print(f"✅ ÉXITO: Personaje creado con ID: {CREATED_ID}")
            return True
        else:
            print(f"❌ FALLO: Creado, pero no se encontró la clave 'id'/'character_id' en la respuesta.")
            print("Respuesta:", data)
            return False
            
    except requests.exceptions.RequestException as e:
        if response is not None:
            print(f"❌ ERROR en POST (Status {response.status_code}): {e}")
            try:
                print(f"Detalles del Servidor: {response.json()}")
            except:
                print(f"Respuesta Raw: {response.text}")
        else:
            print(f"❌ ERROR en POST: {e}")
        return False

def get_all_characters():
    """Tests the GET All method."""
    print("\n--- 2. GET: Listando todos los personajes ---")
    try:
        response = requests.get(f"{BASE_URL}{ENDPOINT}", headers=HEADERS)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ ÉXITO: Encontrados {len(data)} personajes en total.")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR en GET All: {e}")

def update_character():
    """Tests the PUT method on the created character."""
    if not CREATED_ID:
        print("🛑 SALTANDO UPDATE: No hay ID para actualizar.")
        return
        
    print(f"\n--- 3. PUT: Actualizando personaje {CREATED_ID} ---")
    update_payload = {
        "nivel": 10,  # Sube de nivel!
        "clase": "Bardo" # Cambio de clase
    }
    
    try:
        response = requests.put(f"{BASE_URL}{ENDPOINT}/{CREATED_ID}", json=update_payload, headers=HEADERS)
        response.raise_for_status()
        
        data = response.json()
        
        # Verificar la actualización
        if data.get('nivel') == 10 and data.get('clase') == "Bardo":
            print(f"✅ ÉXITO: Personaje actualizado. Nuevo nivel: {data.get('nivel')}.")
        else:
            print(f"❌ FALLO: Solicitud de actualización exitosa, pero los cambios no se reflejan.")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR en PUT: {e}")

def get_single_character():
    """Tests the GET Single method."""
    if not CREATED_ID:
        print("🛑 SALTANDO GET INDIVIDUAL: No hay ID para buscar.")
        return
        
    print(f"\n--- 4. GET: Buscando personaje {CREATED_ID} ---")
    try:
        response = requests.get(f"{BASE_URL}{ENDPOINT}/{CREATED_ID}", headers=HEADERS)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ ÉXITO: Encontrado: {data.get('nombre')}, Nivel: {data.get('nivel')}.")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR en GET Individual: {e}")

def delete_character():
    """Tests the DELETE method and cleans up the created data."""
    if not CREATED_ID:
        print("🛑 SALTANDO DELETE: No hay ID para eliminar.")
        return
        
    print(f"\n--- 5. DELETE: Eliminando personaje {CREATED_ID} ---")
    try:
        response = requests.delete(f"{BASE_URL}{ENDPOINT}/{CREATED_ID}", headers=HEADERS)
        response.raise_for_status()
        
        if response.status_code in [200, 204]:
            print(f"✅ ÉXITO: Personaje {CREATED_ID} eliminado correctamente.")
        
        # Comprobación final
        check_response = requests.get(f"{BASE_URL}{ENDPOINT}/{CREATED_ID}", headers=HEADERS)
        if check_response.status_code == 404:
             print("✅ LIMPIEZA CONFIRMADA: Personaje ya no existe (404).")
        else:
             print(f"❌ FALLO DE LIMPIEZA: Personaje aún accesible (Status: {check_response.status_code}).")

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR en DELETE: {e}")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    check_config()
    if create_character():
        get_all_characters()
        update_character()
        get_single_character()
        delete_character()
    
    print("\n--- CICLO DE PRUEBAS CRUD COMPLETADO ---")