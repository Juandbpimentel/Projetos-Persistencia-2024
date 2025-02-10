from pydantic import BaseModel, Field

from typing import List, Optional


class Projeto(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    descricao: str
    funcionarios_id: Optional[List[str]] = Field(default_factory=list)
    contrato_id: Optional[str]
    cliente_id: str


class ProjetoDetalhadoDTO(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    descricao: str
    cliente: 'Cliente'
    funcionarios: Optional[List['Funcionario']] = Field(default_factory=list)
    contrato: 'Contrato'

ProjetoDetalhadoDTO.model_rebuild()