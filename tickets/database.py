from os import getenv

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import (
    relationship,
    declarative_base,
    sessionmaker,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
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


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self):
        self._engine = create_async_engine(
            DB_URI,
            future=True,
            query_cache_size=1200,
        )
        self._session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )()

    async def create_all(self):
        async with self._engine.begin() as conn:  # type: ignore
            await conn.run_sync(BASE.metadata.create_all)


SESSION = AsyncDatabaseSession()
SESSION.init()
