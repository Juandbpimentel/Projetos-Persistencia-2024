from typing import Optional, List

from pydantic import BaseModel, Field

from models import Departamento


class EmpresaDetalhadaDTO(BaseModel):
    id: str = Field(None, alias="_id")
    nome_empresa: str
    CNPJ: str
    razao_social: str
    nome_fantasia: str
    email_de_contato: str
    departamentos: Optional[List[Departamento]] = Field(default_factory=list)