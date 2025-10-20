import httpx


async def call_search_web(query: str) -> dict:
    """
    Llama al webhook de n8n para realizar una búsqueda web.
    
    Args:
        query: El término de búsqueda a enviar al webhook.
        
    Returns:
        dict: La respuesta del webhook en formato JSON, o un diccionario de error si falla.
    """
    # URL del webhook de n8n (usando el nombre del servicio Docker)
    webhook_url = "http://n8n-mcp:5678/webhook/search-web"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json={"query": query},
                timeout=30.0  # Timeout de 30 segundos
            )
            response.raise_for_status()  # Lanza excepción si el status code es 4xx o 5xx
            return response.json()
    except httpx.RequestError as e:
        return {
            "error": "Request failed",
            "message": str(e),
            "query": query
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "query": query
        }
