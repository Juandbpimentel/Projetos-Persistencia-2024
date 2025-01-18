from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from database import Base, get_db
from pydantic import BaseModel

from models.funcionario_model import FuncionarioModel


class ProjetoModel(Base):
    __tablename__ = 'projetos'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String)
    descricao: Mapped[str] = mapped_column(String)

class ProjetoSchema(BaseModel):
    id: int
    nome_cliente: str
    decricao: str
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
projeto_routes = SQLAlchemyCRUDRouter(
    schema=ProjetoSchema,
    db_model=ProjetoModel,
    db=get_db,
    prefix='projetos'
)