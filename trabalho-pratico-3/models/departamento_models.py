from pydantic import BaseModel, Field

from typing import List, Optional


class Departamento(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    orcamento: float
    status: str
    empresa_id: str
    funcionarios_id: Optional[List[str]] = Field(default_factory=list)

class DepartamentoDetalhadoDTO(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    orcamento: float
    status: str
    empresa: 'Empresa'
    funcionarios: Optional[List['Funcionario']] = Field(default_factory=list)

DepartamentoDetalhadoDTO.model_rebuild()