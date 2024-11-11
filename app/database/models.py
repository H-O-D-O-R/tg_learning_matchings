from sqlalchemy import BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

main_engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
main_async_session = async_sessionmaker(main_engine)



class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(BigInteger)

async def async_main():
    async with main_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



