import os
from google import genai
from google.genai.types import HttpOptions


def search_web(query: str):
    """
    Busca en la web información reciente o en tiempo real sobre un tema.
    
    Úsalo para noticias, eventos actuales, datos meteorológicos, resultados deportivos,
    cotizaciones de mercado, o cualquier información que el modelo no conozca o que
    pueda estar desactualizada.
    
    Args:
        query: El término de búsqueda o pregunta que se quiere investigar en la web.
    
    Returns:
        Resultados de la búsqueda web en tiempo real.
    """
    pass


def get_gemini_model():
    """
    Configura y devuelve el modelo Gemini con la herramienta de búsqueda web.
    
    Soporta dos métodos de autenticación:
    1. Vertex AI con ADC (Application Default Credentials) - Recomendado para producción
    2. API Key - Fallback o desarrollo
    
    La configuración se controla mediante variables de entorno:
    - GOOGLE_GENAI_USE_VERTEXAI: Si es "True", usa Vertex AI
    - GOOGLE_APPLICATION_CREDENTIALS: Ruta al archivo JSON de credenciales (para Vertex AI)
    - GOOGLE_CLOUD_PROJECT: ID del proyecto de Google Cloud (para Vertex AI)
    - GOOGLE_CLOUD_LOCATION: Ubicación del servicio (para Vertex AI, ej: us-central1)
    - GOOGLE_API_KEY: API Key de Gemini (fallback)
    
    Returns:
        Tupla (client, tools): Cliente de Gemini configurado y lista de herramientas.
    """
    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
    
    if use_vertex:
        # Modo Vertex AI con ADC
        # Las credenciales se cargan automáticamente desde GOOGLE_APPLICATION_CREDENTIALS
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        if not project:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT no está configurado. "
                "Es requerido cuando se usa Vertex AI."
            )
        
        print(f"🔐 Usando Vertex AI con ADC - Proyecto: {project}, Ubicación: {location}")
        
        # El cliente se autentica automáticamente usando ADC
        client = genai.Client(
            http_options=HttpOptions(api_version="v1")
        )
    else:
        # Modo API Key (fallback)
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError(
                "No se encontró GOOGLE_API_KEY. "
                "Asegúrate de configurarla en el archivo docker-compose.yml "
                "o habilita Vertex AI con GOOGLE_GENAI_USE_VERTEXAI=True"
            )
        
        print("🔑 Usando API Key de Gemini")
        
        # Crear el cliente con la API key
        client = genai.Client(
            api_key=api_key,
            http_options=HttpOptions(api_version="v1")
        )
    
    # Definir las herramientas disponibles para el modelo
    tools = [search_web]
    
    return client, tools


def generate_with_tools(client, tools, user_message: str):
    """
    Genera una respuesta usando el modelo Gemini con herramientas.
    
    Args:
        client: Cliente de Gemini configurado.
        tools: Lista de herramientas disponibles.
        user_message: Mensaje del usuario.
        
    Returns:
        Respuesta generada por el modelo.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        config={
            "tools": tools,
            "response_modalities": ["TEXT"],
        }
    )
    
    return response
