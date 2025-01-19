import decimal
from typing import Optional

from pydantic.types import Decimal
from sqlalchemy import Column, String, Integer, Enum as SQLAlchemyEnum, ForeignKey
from enum import Enum as PyEnum, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base, get_db

class ClienteModel(Base):
    __tablename__ = 'clientes'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome_cliente: Mapped[str] = mapped_column(String)
    cnpj_cpf: Mapped[str] = mapped_column(String, unique=True)
    razao_social: Mapped[str] = mapped_column(String)
    nome_fantasia: Mapped[str] = mapped_column(String)
    email_de_contato: Mapped[str] = mapped_column(String)

class FuncionarioModel(Base):
    __tablename__ = 'funcionarios'
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    email:Mapped[String] = mapped_column(String, unique=True)
    nome:Mapped[String] = mapped_column(String)
    cargo:Mapped[String] = mapped_column(String)
    salario:Mapped[String] = mapped_column(String)
    telefone:Mapped[String] = mapped_column(String)

class ProjetoModel(Base):
    __tablename__ = 'projetos'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String)
    descricao: Mapped[str] = mapped_column(String)

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

class DepartamentoModel(Base):
    __tablename__ = 'departamentos'
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    nome:Mapped[String] = mapped_column(String, unique=True)
    orcamento:Mapped[int] = mapped_column(String)
    status: Mapped[StatusEnum] = mapped_column(SQLAlchemyEnum(StatusEnum))
    gerente_id:Mapped[int] = mapped_column(Integer, ForeignKey('funcionarios.id'), nullable=True)

class EmpresaModel(Base):
    __tablename__ = 'empresas'
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    nome_empresa:Mapped[String] = mapped_column(String)
    CNPJ:Mapped[String] = mapped_column(String)
    razao_social:Mapped[String] = mapped_column(String)
    nome_fantasia:Mapped[String] = mapped_column(String)
    email_de_contato:Mapped[String] = mapped_column(String)