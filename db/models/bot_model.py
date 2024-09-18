from sqlalchemy import BIGINT, String, TEXT
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from db.base import CreateModel


class Network(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str]
    link: Mapped[str]


class Phone(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str] = mapped_column(TEXT)


class About(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str] = mapped_column(TEXT)


class Channel(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    url: Mapped[str] = mapped_column(String())
    title: Mapped[str] = mapped_column(String())
