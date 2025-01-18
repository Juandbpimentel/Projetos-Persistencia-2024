from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from database import Base, get_db
from pydantic import BaseModel

class ClienteModel(Base):
    __tablename__ = 'clientes'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome_cliente: Mapped[str] = mapped_column(String)
    cnpj_cpf: Mapped[str] = mapped_column(String, unique=True)
    razao_social: Mapped[str] = mapped_column(String)
    nome_fantasia: Mapped[str] = mapped_column(String)
    email_de_contato: Mapped[str] = mapped_column(String)

class ClienteSchema(BaseModel):
    id: int
    nome_cliente: str
    cnpj_cpf: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str

    class Config:
        orm_mode = True

cliente_routes = SQLAlchemyCRUDRouter(
    schema=ClienteSchema,
    db_model=ClienteModel,
    db=get_db,
    prefix='clientes'
)