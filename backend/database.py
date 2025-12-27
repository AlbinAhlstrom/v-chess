from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, Boolean, Float, DateTime, func, ForeignKey
import os
import datetime
from typing import Optional

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./chess.db")
print(f"DEBUG: backend.database using DATABASE_URL={DATABASE_URL}")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    google_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    picture: Mapped[Optional[str]] = mapped_column(String)
    supporter_badge: Mapped[Optional[str]] = mapped_column(String) # e.g., 'kickstarter', 'patreon'
    default_time: Mapped[float] = mapped_column(Float, default=10.0)
    default_increment: Mapped[float] = mapped_column(Float, default=0.0)
    default_time_control_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

class Rating(Base):
    __tablename__ = "ratings"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.google_id"), index=True)
    variant: Mapped[str] = mapped_column(String, index=True)
    rating: Mapped[float] = mapped_column(Float, default=1500.0)
    rd: Mapped[float] = mapped_column(Float, default=350.0)
    volatility: Mapped[float] = mapped_column(Float, default=0.06)
    last_updated: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class GameModel(Base):
    __tablename__ = "games"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    variant: Mapped[str] = mapped_column(String)
    fen: Mapped[str] = mapped_column(String)
    move_history: Mapped[str] = mapped_column(Text) # JSON list
    uci_history: Mapped[Optional[str]] = mapped_column(Text) # JSON list
    time_control: Mapped[Optional[str]] = mapped_column(Text) # JSON dict
    clocks: Mapped[Optional[str]] = mapped_column(Text) # JSON dict
    last_move_at: Mapped[Optional[float]] = mapped_column(Float)
    is_over: Mapped[bool] = mapped_column(Boolean, default=False)
    winner: Mapped[Optional[str]] = mapped_column(String)
    white_player_id: Mapped[Optional[str]] = mapped_column(String)
    black_player_id: Mapped[Optional[str]] = mapped_column(String)
    white_rating_diff: Mapped[Optional[int]] = mapped_column(Float) # Using Float for consistency with rating types
    black_rating_diff: Mapped[Optional[int]] = mapped_column(Float)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
