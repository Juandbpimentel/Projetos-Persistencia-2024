from __future__ import annotations
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

    @classmethod
    def resolve_refs(cls):
        from models.funcionario_models import Funcionario
        from models.empresa_models import Empresa
        cls.model_rebuild(_types_namespace={"Funcionario": Funcionario, "Empresa": Empresa})