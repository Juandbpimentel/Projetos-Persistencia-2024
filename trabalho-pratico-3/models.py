from bson import ObjectId
from pydantic import BaseModel, Field

from typing import List, Optional

class Cliente(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome_cliente: str
    cnpj_cpf: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str
    projetos: Optional[List[str]] = Field(default_factory=list)

class Funcionario(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: str
    nome: str
    cargo: str
    salario: float
    telefone: str
    departamento_id: str
    projetos: Optional[List[str]] = Field(default_factory=list)

class Projeto(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    descricao: str
    funcionarios: Optional[List[str]] = Field(default_factory=list)
    contrato_id: Optional[str]
    cliente_id: str

class Contrato(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    descricao: str
    condicoes_servico: str
    data_inicio: str
    data_termino: Optional[str]
    status: str = "ativo"
    valor_total: float
    moeda: str = "BRL"
    projeto_id: str

class Departamento(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    orcamento: float
    status: str
    empresa_id: str
    funcionarios: Optional[List[str]] = Field(default_factory=list)

class Empresa(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome_empresa: str
    CNPJ: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str
    departamentos: Optional[List[str]] = Field(default_factory=list)