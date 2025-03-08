from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Call(Base):
    __tablename__ = "calls"
    
    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String(50), unique=True, index=True)
    from_number = Column(String(20))
    to_number = Column(String(20))
    status = Column(String(20))
    duration = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with messages
    messages = relationship("Message", back_populates="call")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"))
    content = Column(Text)
    role = Column(String(20))  # 'user' or 'assistant'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with call
    call = relationship("Call", back_populates="messages")

# Database initialization
def init_db(database_url: str):
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine 