from sqlalchemy import Text, ForeignKey, Integer, Date, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import date, datetime

class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserDict(Base):
    __tablename__ = 'user_dicts'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    matching: Mapped[str] = mapped_column()

    categories = relationship("Category", back_populates="user_dict", cascade="all, delete")


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    dict_id: Mapped[int] = mapped_column(ForeignKey('user_dicts.id'))

    user_dict = relationship("UserDict", back_populates="categories")
    items = relationship("Item", back_populates="category", cascade="all, delete")


class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    matching: Mapped[str] = mapped_column(Text)
    level_difficulty: Mapped[int] = mapped_column(Integer)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    last_date_answer: Mapped[date] = mapped_column(Date)
    is_repeating: Mapped[int] = mapped_column(Integer)
    date_for_repeat: Mapped[date] = mapped_column(Date)
    repeating_interval: Mapped[int] = mapped_column(Integer)

    category = relationship("Category", back_populates="items")


# Создает базу данных для пользователя с указанным ID
async def create_user_database(user_id: int):
    user_database_url = f"sqlite+aiosqlite:///user_databases/user_{user_id}.db"  # Формируем URL базы данных
    user_engine = create_async_engine(user_database_url)  # Создаем асинхронный движок базы данных

    # Создаем таблицы в базе данных
    async with user_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Получает сессию подключения к базе данных пользователя
async def get_user_database(user_id: int):
    user_database_url = f"sqlite+aiosqlite:///user_databases/user_{user_id}.db"  # URL базы данных пользователя

    user_engine = create_async_engine(user_database_url)  # Создаем асинхронный движок базы данных
    user_session = async_sessionmaker(user_engine)  # Создаем фабрику сессий для работы с базой данных

    return user_session  # Возвращаем фабрику сессий