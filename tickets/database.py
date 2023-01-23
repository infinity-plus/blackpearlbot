from os import getenv

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import (
    relationship,
    declarative_base,
    scoped_session,
    sessionmaker,
)

BASE = declarative_base()

DB_URI = getenv("DATABASE_URL", "sqlite:///database.db")


class Panel(BASE):
    __tablename__ = "panel"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(500))
    guild_id = Column(String)
    forms = relationship("Form", back_populates="panel")


class Form(BASE):
    __tablename__ = "form"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(500))
    panel_id = Column(Integer, ForeignKey("panel.id"))
    panel = relationship("Panel", back_populates="forms")
    fields = relationship("Field", back_populates="form")


class Field(BASE):
    __tablename__ = "field"
    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    form_id = Column(Integer, ForeignKey("form.id"))
    form = relationship("Form", back_populates="fields")
    response = Column(String(500))


def start() -> scoped_session:
    """Create engine and return a scoped session instance"""
    engine = create_engine(DB_URI, client_encoding="utf8")
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


SESSION = start()
