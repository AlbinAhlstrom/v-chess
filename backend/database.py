from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, Boolean, Float, DateTime, func
import datetime
from typing import Optional

DATABASE_URL = "sqlite+aiosqlite:///./chess.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class GameModel(Base):
    __tablename__ = "games"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    variant: Mapped[str] = mapped_column(String)
    fen: Mapped[str] = mapped_column(String)
    move_history: Mapped[str] = mapped_column(Text) # JSON list
    time_control: Mapped[Optional[str]] = mapped_column(Text) # JSON dict
    clocks: Mapped[Optional[str]] = mapped_column(Text) # JSON dict
    last_move_at: Mapped[Optional[float]] = mapped_column(Float)
    is_over: Mapped[bool] = mapped_column(Boolean, default=False)
    winner: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
