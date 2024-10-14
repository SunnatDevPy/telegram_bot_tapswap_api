from sqlalchemy import delete as sqlalchemy_delete, DateTime, update as sqlalchemy_update, select, func, desc
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr, sessionmaker, Mapped, mapped_column

from config import conf


class Base(AsyncAttrs, DeclarativeBase):
    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower() + "s"


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self):
        self._engine = create_async_engine(
            conf.db.db_url,
        )
        self._session = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)()

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # async def drop_all(self):
    #     async with self._session.begin() as conn:
    #         await conn.run_sync(Base.metadata.drop_all)


db = AsyncDatabaseSession()
db.init()


class AbstractClass:
    @staticmethod
    async def commit():
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    @classmethod
    async def create(cls, **kwargs):  # Create
        object_ = cls(**kwargs)
        db.add(object_)
        await cls.commit()
        return object_

    @classmethod
    async def update(cls, id_, **kwargs):
        query = (
            sqlalchemy_update(cls)
            .where(cls.id == id_)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def update_question(cls, id_, question_id, **kwargs):
        query = (
            sqlalchemy_update(cls)
            .where(cls.id == id_, cls.question_id == question_id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
            .returning(cls)
        )
        await db.execute(query)
        await cls.commit()
        return (await db.execute(query)).scalar()

    @classmethod
    async def update_event(cls, user_id, event_id, **kwargs):
        query = (
            sqlalchemy_update(cls)
            .where(cls.user_id == user_id, cls.event_id == event_id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def get_admins(cls):
        query = select(cls).where(cls.is_admin == True)
        return (await db.execute(query)).scalars()

    @classmethod
    async def get_experience_from_user(cls):
        query = select(cls).where(cls.is_admin == True)
        return (await db.execute(query)).scalars()

    @classmethod
    async def get(cls, id_):
        query = select(cls).where(cls.id == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_from_level(cls, id_):
        query = select(cls).where(cls.level == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_from_type(cls, type):
        query = select(cls).where(cls.status_id == type).order_by(desc(cls.coins)).limit(10)
        return (await db.execute(query)).scalars().all()

    @classmethod
    async def get_from_type_rank(cls, type_):
        query = select(cls).where(cls.status_id == type_).order_by(desc(cls.coins))
        return (await db.execute(query)).scalars()

    @classmethod
    async def get_from_user_id(cls, id_):
        query = select(cls).where(cls.user_id == id_).order_by(cls.id).limit(20)
        return (await db.execute(query)).scalars().all()

    @classmethod
    async def get_from_referral_id(cls, id_):
        query = select(cls).where(cls.referrer_id == id_)
        return (await db.execute(query)).scalars()

    @classmethod
    async def get_from_user_id_experience(cls, id_):
        query = select(cls).where(cls.user_id == id_).order_by(cls.experience_id)
        return (await db.execute(query)).scalars()

    @classmethod
    async def get_experience_from_users(cls, user_id, id_):
        query = select(cls).order_by(cls.experience_id).where(cls.user_id == user_id, cls.id == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_question_from_user(cls, user_id, question_id):
        query = select(cls).order_by(cls.question_id).where(cls.user_id == user_id, cls.question_id == question_id)
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_event_from_users(cls, user_id, id_):
        query = select(cls).order_by(cls.experience_id).where(cls.user_id == user_id, cls.id == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def delete(cls, id_):
        query = sqlalchemy_delete(cls).where(cls.id == id_)
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def delete_question(cls, id_):
        query = sqlalchemy_delete(cls).where(cls.user_id == id_)
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def get_all(cls):
        return (await db.execute(select(cls))).scalars().all()

    @classmethod
    async def get_alls(cls):
        query = select(cls).order_by(cls.id)
        return (await db.execute(query)).scalars()


class CreateModel(Base, AbstractClass):
    __abstract__ = True
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now())
