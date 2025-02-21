from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List


class Empresa(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    CNPJ: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str
    departamentos_id: Optional[List[str]] = Field(default_factory=list)


class EmpresaDetalhadaDTO(BaseModel):
    iid: Optional[str] = Field(None, alias="_id")
    nome: str
    CNPJ: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str
    departamentos: Optional[List["Departamento"]] = Field(default_factory=list)

    @classmethod
    def resolve_refs(cls):
        from models.departamento_models import Departamento

        cls.model_rebuild(_types_namespace={"Departamento": Departamento})
