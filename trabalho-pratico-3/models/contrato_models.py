from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional



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


class ContratoDetalhadoDTO(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    descricao: str
    condicoes_servico: str
    data_inicio: str
    data_termino: Optional[str]
    status: str = "ativo"
    valor_total: float
    moeda: str = "BRL"
    projeto: 'Projeto'

    @classmethod
    def resolve_refs(cls):
        from models.projeto_models import Projeto
        cls.model_rebuild(_types_namespace={"Projeto": Projeto})