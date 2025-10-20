import contextlib
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from google.genai import types as genai_types

from database import async_engine, AsyncSessionLocal, Base
from models import QueryLog
from llm_service import get_gemini_model
from tool_caller import call_search_web


# ========== Esquemas Pydantic ==========

class QueryRequest(BaseModel):
    """Schema para recibir consultas del usuario"""
    user_name: str
    prompt: str


class QueryResponse(BaseModel):
    """Schema para devolver la respuesta del orquestador"""
    final_answer: str


# ========== Gestor de Vida (Lifespan) ==========

async def init_db():
    """
    Inicializa la base de datos creando todas las tablas definidas en los modelos.
    Se ejecuta al iniciar la aplicación.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Base de datos inicializada correctamente")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor del ciclo de vida de la aplicación.
    Se ejecuta al inicio (antes del yield) y al apagado (después del yield).
    """
    # Startup: Inicializar base de datos
    await init_db()
    yield
    # Shutdown: Aquí se pueden agregar tareas de limpieza si es necesario
    print("🔴 Apagando aplicación...")


# ========== Instancia de FastAPI ==========

app = FastAPI(
    title="Orquestador de Agente IA",
    description="API para gestionar consultas y coordinar herramientas con n8n",
    version="1.0.0",
    lifespan=lifespan
)


# ========== Middleware de CORS ==========

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== Dependencia de Base de Datos ==========

async def get_db():
    """
    Dependency para inyectar la sesión de base de datos en los endpoints.
    Asegura que la sesión se cierre correctamente después de cada request.
    """
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


# ========== Endpoints ==========

@app.get("/")
async def root():
    """Endpoint de verificación de estado del servicio"""
    return {
        "status": "Orquestador en línea",
        "version": "1.0.0",
        "message": "API funcionando correctamente"
    }


@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint principal para procesar consultas del usuario con agente IA real.
    
    Args:
        request: QueryRequest con user_name y prompt
        db: Sesión de base de datos (inyectada automáticamente)
    
    Returns:
        QueryResponse con la respuesta final del agente
    
    Flujo del agente:
        1. Recibe la consulta del usuario
        2. Envía el prompt a Gemini con herramientas disponibles
        3. Si Gemini necesita buscar en la web, ejecuta la función
        4. Envía los resultados de vuelta a Gemini
        5. Obtiene la respuesta final
        6. Guarda el log en la base de datos
        7. Devuelve la respuesta
    """
    try:
        # Paso 1: Obtener el cliente Gemini configurado
        result = get_gemini_model()
        print(f"🔧 Resultado de get_gemini_model: {type(result)}")
        client, tools = result
        print(f"🔧 Cliente: {type(client)}, Tools: {type(tools)}")
        
        # Paso 2: Primero preguntar a Gemini si necesita buscar información en la web
        print(f"📤 Analizando prompt: {request.prompt}")
        analysis_prompt = f"""Analiza la siguiente consulta del usuario y determina si necesitas buscar información actualizada en la web para responderla correctamente.

Consulta del usuario: "{request.prompt}"

Responde ÚNICAMENTE con una de estas dos opciones:
- Si necesitas buscar en la web (noticias, eventos actuales, información reciente): Responde solo "BUSCAR: <query optimizada para búsqueda>"
- Si puedes responder con tu conocimiento actual: Responde solo "RESPONDER"

Tu respuesta:"""
        
        analysis_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=analysis_prompt,
        )
        
        analysis_text = analysis_response.text.strip()
        print(f"🤔 Análisis de Gemini: {analysis_text}")
        
        final_answer = None
        
        # Paso 3: Verificar si Gemini decidió buscar en la web
        if analysis_text.startswith("BUSCAR:"):
            # Gemini decidió usar búsqueda web
            query = analysis_text.replace("BUSCAR:", "").strip()
            print(f"🔍 Ejecutando búsqueda web con query: {query}")
            
            # Paso 4: Llamar a nuestra herramienta real (webhook n8n)
            tool_results_dict = await call_search_web(query=query)
            print(f"✅ Resultados de búsqueda obtenidos")
            
            # Paso 5: Enviar los resultados a Gemini para que genere la respuesta final
            final_prompt = f"""El usuario preguntó: "{request.prompt}"

Encontré esta información actualizada en la web:
{tool_results_dict}

Por favor, genera una respuesta completa y útil para el usuario basándote en esta información. Sé específico y cita datos relevantes."""
            
            print("📤 Enviando resultados a Gemini para generar respuesta final...")
            final_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=final_prompt,
            )
            
            final_answer = final_response.text
            print(f"✅ Respuesta final del agente (con búsqueda web)")
        else:
            # Gemini decidió responder directamente
            print("💬 Generando respuesta directa sin búsqueda web...")
            direct_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=request.prompt,
            )
            final_answer = direct_response.text
            print(f"✅ Respuesta directa del agente (sin búsqueda web)")
        
        # Paso 7: Guardar el log en la base de datos
        db_log = QueryLog(
            user_name=request.user_name,
            prompt_text=request.prompt,
            final_answer=final_answer
        )
        
        db.add(db_log)
        await db.commit()
        await db.refresh(db_log)
        
        print(f"💾 Log guardado con ID: {db_log.id}")
        
        # Paso 8: Devolver la respuesta al cliente
        return QueryResponse(final_answer=final_answer)
    
    except Exception as e:
        # En caso de error, hacer rollback y devolver error
        await db.rollback()
        print(f"❌ Error procesando query: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la consulta: {str(e)}"
        )


@app.get("/api/v1/logs")
async def get_logs(db: AsyncSession = Depends(get_db)):
    """
    Endpoint para obtener todos los logs de consultas.
    Útil para debugging y monitoreo.
    """
    from sqlalchemy import select
    
    try:
        result = await db.execute(select(QueryLog).order_by(QueryLog.timestamp.desc()))
        logs = result.scalars().all()
        
        return {
            "total": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "user_name": log.user_name,
                    "prompt_text": log.prompt_text,
                    "final_answer": log.final_answer,
                    "timestamp": log.timestamp.isoformat()
                }
                for log in logs
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo logs: {str(e)}"
        )
