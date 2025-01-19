import decimal
from typing import Optional

from fastapi_crudrouter import SQLAlchemyCRUDRouter
from pydantic.types import Decimal

from database import Base, get_db
from pydantic import BaseModel

from models.models import ClienteModel, FuncionarioModel, ProjetoModel, ContratoModel, StatusEnum, EmpresaModel, \
    DepartamentoModel

#Schemas para o uso do CrudRouter
class ClienteSchema(BaseModel):
    id: int
    nome_cliente: str
    cnpj_cpf: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str

    class Config:
        orm_mode = True


class FuncionarioSchema(BaseModel):
    id: int
    email: str
    nome: str
    cargo: str
    salario: str
    telefone: str
    class Config:
        orm_mode = True

class ProjetoSchema(BaseModel):
    id: int
    nome_cliente: str
    decricao: str

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ContratoSchema(BaseModel):
    id: int
    nome: str
    condicoes_de_servico: str
    vigencia: StatusEnum
    qtd_max: int

    class Config:
        orm_mode = True

class EmpresaSchema(BaseModel):
    id: int
    nome_empresa: str
    CNPJ: str
    razao_social: str
    nome_fantasa: str
    email_de_contato: str
    class Config:
        orm_mode = True


class DepartamentoSchema(BaseModel):
    id: int
    nome: str
    orcamento: int
    status: StatusEnum
    gerente_id: int

    class Config:
        orm_mode = True



#Rotas para o uso do CrudRouter
departamentos_routes = SQLAlchemyCRUDRouter(
    schema = DepartamentoSchema,
    db_model=DepartamentoModel,
    db=get_db,
    prefix='departamentos'
)

empresas_routes = SQLAlchemyCRUDRouter(
    schema = EmpresaSchema,
    db_model=EmpresaModel,
    db=get_db,
    prefix='empresas'
)

contratos_routes = SQLAlchemyCRUDRouter(
    schema = ContratoSchema,
    db_model=ContratoModel,
    db=get_db,
    prefix='contratos'
)


projetos_routes = SQLAlchemyCRUDRouter(
    schema=ProjetoSchema,
    db_model=ProjetoModel,
    db=get_db,
    prefix='projetos'
)

clientes_routes = SQLAlchemyCRUDRouter(
    schema=ClienteSchema,
    db_model=ClienteModel,
    db=get_db,
    prefix='clientes'
)

funcionarios_routes = SQLAlchemyCRUDRouter(
    schema = FuncionarioSchema,
    db_model=FuncionarioModel,
    db=get_db,
    prefix='funcionarios'
)
