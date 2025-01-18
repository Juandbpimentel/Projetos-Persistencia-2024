from sqlalchemy import Column, String, Integer, ForeignKey, Integer, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from enum import Enum
from database import Base
from typing import Optional

from database import get_db
from pydantic import BaseModel
from enum import Enum as PyEnum

class StatusEnum(PyEnum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    SUSPENSO = "suspenso"

class DepartamentoModel(Base):
    __tablename__ = 'departamentos'
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    nome:Mapped[String] = mapped_column(String, unique=True)
    gerente:Mapped[int] = mapped_column(String)
    orcamento:Mapped[int] = mapped_column(String)
    status: Mapped[StatusEnum] = mapped_column(SQLAlchemyEnum(StatusEnum))



class DepartamentoSchema(BaseModel):
    id: int
    nome: str
    gerente: int
    orcamento: int
    status: StatusEnum

    class Config:
        orm_mode = True


departamento_routes = SQLAlchemyCRUDRouter(
    schema = DepartamentoSchema,
    db_model=DepartamentoModel,
    db=get_db,
    prefix='departamentos'
)


# from sqlalchemy import Column, Integer, ForeignKey
# from sqlalchemy.orm import sessionmaker, relationship
# from sqlalchemy.ext.declarative import declarative_base
#
# Base = declarative_base()
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     name = Column(String(50))
#     projects = relationship("Project", secondary="user_project", backref="users")
#
# class Project(Base):
#     __tablename__ = "projects"
#     id = Column(Integer, primary_key=True)
#     title = Column(String(100))
# class UserProject(Base):
#     __tablename__ = "user_project"
#     user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
#     project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
