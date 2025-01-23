from typing import List
from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session

from models.models import DepartamentoModel, DepartamentoSchema
from database import get_db

departamentos_controller_router = APIRouter(
    prefix="/departamentos",
    tags=["Departamentos"],
    dependencies=[Depends(get_db)],
    responses={404: {"description": "Not found"}}
)

@departamentos_controller_router.post("", response_model=DepartamentoSchema)
def create_departamento(*, session: Session = Depends(get_db), departamento: DepartamentoSchema):
    db_departamento = DepartamentoModel(**departamento.dict())
    session.add(db_departamento)
    session.commit()
    session.refresh(db_departamento)
    return db_departamento

@departamentos_controller_router.get("", response_model=List[DepartamentoSchema])
def read_departamentos(*, session: Session = Depends(get_db)):
    departamentos = session.query(DepartamentoModel).all()
    return departamentos

@departamentos_controller_router.get("/{item_id}", response_model=DepartamentoSchema)
def read_departamento(*, session: Session = Depends(get_db), item_id: int):
    departamento = session.get(DepartamentoModel, item_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento not found")
    return departamento

@departamentos_controller_router.put("/{item_id}", response_model=DepartamentoSchema)
def update_departamento(*, session: Session = Depends(get_db), item_id: int, departamento: DepartamentoSchema):
    db_departamento = session.get(DepartamentoModel, item_id)
    if not db_departamento:
        raise HTTPException(status_code=404, detail="Departamento not found")
    departamento_data = departamento.dict(exclude_unset=True)
    for key, value in departamento_data.items():
        setattr(db_departamento, key, value)
    session.add(db_departamento)
    session.commit()
    session.refresh(db_departamento)
    return db_departamento

@departamentos_controller_router.delete("/{item_id}", response_model=DepartamentoSchema)
def delete_departamento(*, session: Session = Depends(get_db), item_id: int):
    departamento = session.get(DepartamentoModel, item_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento not found")
    session.delete(departamento)
    session.commit()
    return departamento