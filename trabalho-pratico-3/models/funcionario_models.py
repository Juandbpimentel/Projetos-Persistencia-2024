from pydantic import BaseModel, Field
from typing import List, Optional

class Funcionario(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: str
    nome: str
    cargo: str
    salario: float
    telefone: str
    departamento_id: str
    projetos_id: Optional[List[str]] = Field(default_factory=list)

class FuncionarioDetalhadoDTO(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: str
    nome: str
    cargo: str
    salario: float
    telefone: str
    departamento: 'Departamento'
    projetos: Optional[List['Projeto']] = Field(default_factory=list)

FuncionarioDetalhadoDTO.model_rebuild()