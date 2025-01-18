from sqlalchemy import Column, String, Integer, ForeignKey, Integer, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from database import Base
from typing import Optional

from database import get_db
from pydantic import BaseModel

from enum import Enum as PyEnum, Enum


class StatusEnum(PyEnum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    SUSPENSO = "suspenso"


class ContratoModel(Base):
    __tablename__ = 'contratos'
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    email:Mapped[String] = mapped_column(String, unique=True)
    nome:Mapped[String] = mapped_column(String)
    condicoes_de_servico:Mapped[String] = mapped_column(String)
    vigecia: Mapped[StatusEnum] = mapped_column(SQLAlchemyEnum(StatusEnum))
    qtd_max:Mapped[int] = mapped_column(Integer)

class ContratoSchema(BaseModel):
    id: int
    nome: str
    condicoes_de_servico: str
    vigencia: StatusEnum
    qtd_max: int

    class Config:
        orm_mode = True


funcionario_routes = SQLAlchemyCRUDRouter(
    schema = ContratoSchema,
    db_model=ContratoModel,
    db=get_db,
    prefix='contratos'
)

