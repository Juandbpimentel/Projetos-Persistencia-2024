from typing import List
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlmodel import Session, select

from models.crud_router_models import EmpresaModel, EmpresaSchema
from models.models import EmpresaModel
from database import get_db

empresas_controller_router = APIRouter(prefix="/empresas", tags=["Empresas"], dependencies=[Depends(get_db)], responses={404: {"description": "Not found"}})


@empresas_controller_router.post("", response_model=EmpresaSchema)
def create_empresa(*, session: Session = Depends(get_db), empresa: EmpresaSchema):
        session.add(empresa)
        session.commit()
        session.refresh(empresa)
        return empresa

@empresas_controller_router.get("", response_model=List[EmpresaSchema])
def read_empresas(*, session: Session = Depends(get_db)):
    empresas = session.exec(select(EmpresaSchema)).all()
    return empresas

@empresas_controller_router.get("/{item_id}", response_model=EmpresaSchema)
def read_empresa(*, session: Session = Depends(get_db), item_id: int):
    empresa = session.get(EmpresaSchema, item_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa not found")
    return empresa

@empresas_controller_router.put("/{item_id}", response_model=EmpresaSchema)
def update_empresa(*, session: Session = Depends(get_db), item_id: int, empresa: EmpresaSchema):
    db_empresa = session.get(EmpresaSchema, item_id)
    if not db_empresa:
        raise HTTPException(status_code=404, detail="Empresa not found")
    empresa_data = empresa.dict(exclude_unset=True)
    for key, value in empresa_data.items():
        setattr(db_empresa, key, value)
    session.add(db_empresa)
    session.commit()
    session.refresh(db_empresa)
    return db_empresa

@empresas_controller_router.delete("/{item_id}", response_model=EmpresaSchema)
def delete_empresa(*, session: Session = Depends(get_db), item_id: int):
    empresa = session.get(EmpresaSchema, item_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa not found")
    session.delete(empresa)
    session.commit()
    return empresa