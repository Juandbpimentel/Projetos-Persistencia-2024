from sqlalchemy import Column, String, Integer, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from database import Base
from typing import Optional

from database import get_db
from pydantic import BaseModel


class EmpresaModel(Base):
    __tablename__ = 'empresas'
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    nome_empresa:Mapped[String] = mapped_column(String)
    CNPJ:Mapped[String] = mapped_column(String)
    razao_social:Mapped[String] = mapped_column(String)
    nome_fantasia:Mapped[String] = mapped_column(String)
    email_de_contato:Mapped[String] = mapped_column(String)


class EmpresaSchema(BaseModel):
    id: int
    nome_empresa: str
    CNPJ: str
    razao_social: str
    nome_fantasa: str
    email_de_contato: str
    class Config:
        orm_mode = True


funcionario_routes = SQLAlchemyCRUDRouter(
    schema = EmpresaSchema,
    db_model=EmpresaModel,
    db=get_db,
    prefix='empresas'
)
