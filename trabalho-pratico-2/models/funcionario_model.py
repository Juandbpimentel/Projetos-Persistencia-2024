from sqlalchemy import Column, String, Integer, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from database import Base
from typing import Optional

from database import get_db
from pydantic import BaseModel

# class Parent(Base):
#     __tablename__ = "parent_table"
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     children: Mapped[List["Child"]] = relationship(back_populates="parent")
#
#
# class Child(Base):
#     __tablename__ = "child_table"
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
#     parent: Mapped["Parent"] = relationship(back_populates="children")


class FuncionarioModel(Base):
    __tablename__ = 'funcionarios'
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    email:Mapped[String] = mapped_column(String, unique=True)
    nome:Mapped[String] = mapped_column(String)
    cargo:Mapped[String] = mapped_column(String)
    salario:Mapped[String] = mapped_column(String)
    telefone:Mapped[String] = mapped_column(String)

class FuncionarioSchema(BaseModel):
    id: int
    email: str
    nome: str
    cargo: str
    salario: str
    telefone: str
    class Config:
        orm_mode = True


funcionario_routes = SQLAlchemyCRUDRouter(
    schema = FuncionarioSchema,
    db_model=FuncionarioModel,
    db=get_db,
    prefix='funcionarios'
)

