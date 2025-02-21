import decimal
from typing import Optional, List

from pydantic.types import Decimal
from enum import Enum as PyEnum
from sqlalchemy import (
    Column,
    String,
    Integer,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from pydantic import BaseModel, Field

projeto_funcionario_association = Table(
    "projeto_funcionario",
    Base.metadata,
    Column("projeto_id", Integer, ForeignKey("projetos.id")),
    Column("funcionario_id", Integer, ForeignKey("funcionarios.id")),
)


class ProjetoModel(Base):
    __tablename__ = "projetos"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String)
    descricao: Mapped[str] = mapped_column(String)
    contrato: Mapped["ContratoModel"] = relationship(
        "ContratoModel", back_populates="projeto", uselist=False
    )
    funcionarios: Mapped[List["FuncionarioModel"]] = relationship(
        "FuncionarioModel",
        secondary=projeto_funcionario_association,
        back_populates="projetos",
    )
    cliente: Mapped["ClienteModel"] = relationship(
        "ClienteModel", back_populates="projeto", uselist=False
    )


class ClienteModel(Base):
    __tablename__ = "clientes"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String)
    cnpj_cpf: Mapped[str] = mapped_column(String, unique=True)
    razao_social: Mapped[str] = mapped_column(String)
    nome_fantasia: Mapped[str] = mapped_column(String)
    email_de_contato: Mapped[str] = mapped_column(String)
    projeto_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("projetos.id"), nullable=True
    )
    projeto: Mapped[Optional["ProjetoModel"]] = relationship(
        "ProjetoModel", back_populates="cliente"
    )


class ContratoModel(Base):
    __tablename__ = "contratos"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    nome: Mapped[str] = mapped_column(String)
    condicoes_de_servico: Mapped[str] = mapped_column(String)
    vigecia: Mapped[str] = mapped_column(String)
    qtd_max: Mapped[int] = mapped_column(Integer)
    projeto_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("projetos.id"), nullable=True
    )
    projeto: Mapped[Optional["ProjetoModel"]] = relationship(
        "ProjetoModel", back_populates="contrato"
    )


class FuncionarioModel(Base):
    __tablename__ = "funcionarios"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    nome: Mapped[str] = mapped_column(String)
    cargo: Mapped[str] = mapped_column(String)
    salario: Mapped[str] = mapped_column(String)
    telefone: Mapped[str] = mapped_column(String)
    departamento_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departamentos.id")
    )
    projetos: Mapped[List["ProjetoModel"]] = relationship(
        "ProjetoModel",
        secondary=projeto_funcionario_association,
        back_populates="funcionarios",
    )
    departamento: Mapped["DepartamentoModel"] = relationship(
        "DepartamentoModel", back_populates="funcionarios"
    )


# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html


class DepartamentoModel(Base):
    __tablename__ = "departamentos"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String, unique=True)
    orcamento: Mapped[int] = mapped_column(Integer)
    status: Mapped[String] = mapped_column(String)
    funcionarios: Mapped[List["FuncionarioModel"]] = relationship(
        "FuncionarioModel", back_populates="departamento"
    )
    empresa_id: Mapped[int] = mapped_column(Integer, ForeignKey("empresas.id"))


class EmpresaModel(Base):
    __tablename__ = "empresas"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[String] = mapped_column(String)
    CNPJ: Mapped[String] = mapped_column(String)
    razao_social: Mapped[String] = mapped_column(String)
    nome_fantasia: Mapped[String] = mapped_column(String)
    email_de_contato: Mapped[String] = mapped_column(String)
    departamentos: Mapped[List["DepartamentoModel"]] = relationship("DepartamentoModel")


class ClienteSchema(BaseModel):
    id: int
    nome: str
    cnpj_cpf: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str
    projeto_id: Optional[int] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class FuncionarioSchema(BaseModel):
    id: int
    email: str
    nome: str
    cargo: str
    salario: str
    telefone: str
    departamento_id: int
    projeto_id: Optional[int] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class ProjetoSchema(BaseModel):
    id: int
    nome: str
    descricao: str
    funcionarios: Optional[List[FuncionarioSchema]] = Field(default_factory=list)
    contrato: Optional["ContratoSchema"] = None
    cliente: Optional["ClienteSchema"] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class ContratoSchema(BaseModel):
    id: int
    email: str
    nome: str
    condicoes_de_servico: str
    vigecia: str
    qtd_max: int
    projeto_id: Optional[int] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class DepartamentoSchema(BaseModel):
    id: int
    nome: str
    orcamento: int
    status: str
    empresa_id: int
    funcionarios: Optional[List[FuncionarioSchema]] = Field(default_factory=list)

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class EmpresaSchema(BaseModel):
    id: int
    nome: str
    CNPJ: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str
    departamentos: Optional[List[DepartamentoSchema]] = Field(default_factory=list)

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
