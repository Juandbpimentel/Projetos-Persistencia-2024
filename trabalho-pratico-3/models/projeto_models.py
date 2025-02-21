from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Projeto(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    funcionarios_id: Optional[List[str]] = Field(default_factory=list)
    contrato_id: Optional[str] = Field(None)
    cliente_id: str
    nome: str
    descricao: str
    data_inicio: str
    data_fim: Optional[str] = Field(None)
    status: str

class ProjetoDetalhadoDTO(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    funcionarios: Optional[List['Funcionario']] = Field(default_factory=list)
    contrato: Optional['Contrato'] = Field(None)
    cliente: 'Cliente'
    nome: str
    descricao: str
    data_inicio: str
    data_fim: Optional[str] = Field(None)
    status: str

    @classmethod
    def resolve_refs(cls):
        from models.cliente_models import Cliente
        from models.funcionario_models import Funcionario
        from models.contrato_models import Contrato
        cls.model_rebuild(_types_namespace={"Cliente": Cliente, "Funcionario": Funcionario, "Contrato": Contrato})


