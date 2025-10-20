from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class QueryLog(Base):
    """
    Modelo para registrar las consultas de los usuarios.
    Almacena el prompt, la respuesta final y metadata de cada interacción.
    """
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String, nullable=False)
    prompt_text = Column(Text, nullable=False)
    final_answer = Column(Text, nullable=True)  # Puede ser None si falla
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<QueryLog(id={self.id}, user={self.user_name}, timestamp={self.timestamp})>"
