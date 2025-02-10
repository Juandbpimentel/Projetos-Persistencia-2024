from typing import Optional, List

from pydantic import BaseModel, Field


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

ClienteDetalhadoDTO.model_rebuild()
