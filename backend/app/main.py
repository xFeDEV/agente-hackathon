import contextlib
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_engine, AsyncSessionLocal, Base
from models import QueryLog


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
    Endpoint principal para procesar consultas del usuario.
    
    Args:
        request: QueryRequest con user_name y prompt
        db: Sesión de base de datos (inyectada automáticamente)
    
    Returns:
        QueryResponse con la respuesta final
    
    Flujo actual (MVP):
        1. Recibe la consulta del usuario
        2. Genera una respuesta simulada
        3. Guarda el log en la base de datos
        4. Devuelve la respuesta
    
    Flujo futuro:
        1. Recibe la consulta del usuario
        2. Analiza el prompt con el LLM
        3. Determina qué herramientas invocar
        4. Ejecuta las herramientas vía n8n
        5. Construye la respuesta final
        6. Guarda el log completo
    """
    try:
        # ===== LÓGICA MVP: RESPUESTA SIMULADA =====
        simulated_answer = f"Esta es una respuesta simulada. El prompt fue: {request.prompt}"
        
        # Guardar el log en la base de datos
        db_log = QueryLog(
            user_name=request.user_name,
            prompt_text=request.prompt,
            final_answer=simulated_answer
        )
        
        db.add(db_log)
        await db.commit()
        await db.refresh(db_log)  # Obtener el ID generado
        
        print(f"✅ Log guardado con ID: {db_log.id}")
        
        # Devolver la respuesta
        return QueryResponse(final_answer=simulated_answer)
    
    except Exception as e:
        # En caso de error, hacer rollback y devolver error
        await db.rollback()
        print(f"❌ Error procesando query: {str(e)}")
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
