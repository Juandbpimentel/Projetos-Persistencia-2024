from typing import Optional, List

from pydantic import BaseModel, Field


class Empresa(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome_empresa: str
    CNPJ: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str
    departamentos_id: Optional[List[str]] = Field(default_factory=list)

class EmpresaDetalhadaDTO(BaseModel):
    iid: Optional[str] = Field(None, alias="_id")
    nome_empresa: str
    CNPJ: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str
    departamentos: Optional[List['Departamento']] = Field(default_factory=list)

EmpresaDetalhadaDTO.model_rebuild()