import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

# Leer la URL de conexión a la base de datos desde variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear el motor asíncrono de SQLAlchemy
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Logs de SQL en consola (útil para desarrollo)
    future=True
)

# Crear el session maker asíncrono
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Evita que los objetos expiren después del commit
    autocommit=False,
    autoflush=False
)

# Clase base para los modelos ORM
Base = declarative_base()
