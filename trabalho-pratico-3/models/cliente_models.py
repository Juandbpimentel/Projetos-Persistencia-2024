from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List



class Cliente(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome_cliente: str
    cnpj_cpf: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str
    projetos_id: Optional[List[str]] = Field(default_factory=list)


class ClienteDetalhadoDTO(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome_cliente: str
    cnpj_cpf: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str
    projetos: Optional[List['Projeto']] = Field(default_factory=list)
    @classmethod
    def resolve_refs(cls):
        from models.projeto_models import Projeto
        cls.model_rebuild(_types_namespace={"Projeto": Projeto})
