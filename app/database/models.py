from sqlalchemy import Text, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)



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

    category = relationship("Category", back_populates="items")



async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)