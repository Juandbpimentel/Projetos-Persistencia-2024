from bson import ObjectId
from pydantic import BaseModel, Field

from typing import List, Optional

class ClienteSchema(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome_cliente: str
    cnpj_cpf: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str
    projeto: Optional[str]

class FuncionarioSchema(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: str
    nome: str
    cargo: str
    salario: str
    telefone: str
    departamento: str
    projetos: List[str] = Field(default_factory=list)

class ProjetoSchema(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    descricao: str
    funcionarios: List[str]= Field(default_factory=list)
    contrato: Optional[str]
    cliente: str

class ContratoSchema(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: str
    nome: str
    condicoes_de_servico: str
    vigecia: str
    qtd_max: int
    projeto: str

class DepartamentoSchema(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    orcamento: int
    status: str
    empresa: str
    funcionarios: List[str] = Field(default_factory=list)

class EmpresaSchema(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome_empresa: str
    CNPJ: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str
    departamentos: List[str] = Field(default_factory=list)

    class Config:
        json_encoders = {
            ObjectId: str
        }