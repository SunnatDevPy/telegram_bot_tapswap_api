from sqlalchemy import BIGINT, BigInteger, String, ForeignKey, TEXT
from sqlalchemy.orm import Mapped, mapped_column

from db.base import CreateModel


class User(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column(nullable=True)
    coins: Mapped[int] = mapped_column(BigInteger, default=0)
    is_admin: Mapped[bool] = mapped_column(default=False)
    status_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("statusies.id", ondelete='CASCADE'), default=1)
    bonus: Mapped[int] = mapped_column(default=1)
    energy: Mapped[int] = mapped_column(default=200)
    max_energy: Mapped[int] = mapped_column(default=200)


class Experience(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str]
    photo: Mapped[str] = mapped_column(String)
    degree: Mapped[int] = mapped_column(default=1)
    price: Mapped[int] = mapped_column(BigInteger)
    hour_coin: Mapped[int] = mapped_column(BigInteger)
    description: Mapped[str] = mapped_column(TEXT)


class UserAndExperience(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id", ondelete='CASCADE'), sort_order=1)
    experience_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("experiences.id", ondelete='CASCADE'), sort_order=1)
    degree: Mapped[int] = mapped_column(default=0)
    hour_coin: Mapped[int] = mapped_column(default=0)
    price: Mapped[int] = mapped_column(BigInteger, default=0)


class Statusie(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    level: Mapped[int]
    name: Mapped[str]
    limit_coin: Mapped[int] = mapped_column(BigInteger)


class Questions(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    description: Mapped[str] = mapped_column(TEXT)
    answer: Mapped[str] = mapped_column(String)


class Referral(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    referrer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"))
    referred_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"))
