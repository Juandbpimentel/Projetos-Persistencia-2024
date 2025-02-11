from __future__ import annotations
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
    @classmethod
    def resolve_refs(cls):
        from models.cliente_models import Cliente
        from models.funcionario_models import Funcionario
        from models.contrato_models import Contrato
        cls.model_rebuild(_types_namespace={"Cliente": Cliente, "Funcionario": Funcionario, "Contrato": Contrato})