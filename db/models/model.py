from typing import List

from sqlalchemy import BIGINT, BigInteger, String, ForeignKey, TEXT, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import CreateModel


class User(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    phone: Mapped[str] = mapped_column(String, nullable=True)
    coins: Mapped[int] = mapped_column(BigInteger, default=0)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    status_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("statusies.id", ondelete='CASCADE'))
    bonus: Mapped[int] = mapped_column(Integer, default=1)
    energy: Mapped[int] = mapped_column(Integer, default=200)
    max_energy: Mapped[int] = mapped_column(Integer, default=200)
    hour_coin: Mapped[int] = mapped_column(Integer, default=0)


class Event(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)
    timer: Mapped[int] = mapped_column(Integer)
    coin: Mapped[int] = mapped_column(Integer)
    photo: Mapped[str]


class UserAndEvent(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id", ondelete='CASCADE'), sort_order=1, index=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events.id', ondelete="CASCADE"))
    status: Mapped[bool] = mapped_column(Boolean, default=False)


class Experience(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, index=True)
    name: Mapped[str]
    photo: Mapped[str] = mapped_column(String)
    degree: Mapped[int] = mapped_column(default=1)
    price: Mapped[int] = mapped_column(BigInteger)
    hour_coin: Mapped[int] = mapped_column(BigInteger)
    description: Mapped[str] = mapped_column(TEXT)
    user_experiences: Mapped[List['UserAndExperience']] = relationship("UserAndExperience", back_populates="experience")


class UserAndExperience(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id", ondelete='CASCADE'), sort_order=1, index=True)
    experience_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("experiences.id", ondelete='CASCADE'), sort_order=1)
    degree: Mapped[int] = mapped_column(default=0)
    hour_coin: Mapped[int] = mapped_column(default=0)
    next_coin: Mapped[int] = mapped_column(BigInteger, default=0)
    price: Mapped[int] = mapped_column(BigInteger, default=0)

    experience: Mapped[Experience] = relationship("Experience", back_populates="user_experiences")


class Statusie(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, index=True)
    level: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String)
    limit_coin: Mapped[int] = mapped_column(BigInteger)


class Questions(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, index=True)
    description: Mapped[str] = mapped_column(TEXT)
    a: Mapped[str] = mapped_column(String, nullable=True)
    b: Mapped[str] = mapped_column(String, nullable=True)
    c: Mapped[str] = mapped_column(String, nullable=True)
    d: Mapped[str] = mapped_column(String, nullable=True)
    ball: Mapped[int] = mapped_column(Integer, default=0)
    answer: Mapped[str] = mapped_column(String)


class ParamQuestion(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id", ondelete='CASCADE'), sort_order=1, index=True)
    question_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('questionss.id', ondelete="CASCADE"), index=True)
    answer: Mapped[bool] = mapped_column(Boolean, default=False)


class Referral(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, index=True)
    referrer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"), index=True)
    referred_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"))
