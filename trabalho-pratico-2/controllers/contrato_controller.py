from typing import List
from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session

from models.models import ContratoModel, ContratoSchema
from database import get_db

contratos_controller_router = APIRouter(
    prefix="/contratos",
    tags=["Contratos"],
    dependencies=[Depends(get_db)],
    responses={404: {"description": "Not found"}}
)

@contratos_controller_router.post("", response_model=ContratoSchema)
def create_contrato(*, session: Session = Depends(get_db), contrato: ContratoSchema):
    db_contrato = ContratoModel(**contrato.dict())
    session.add(db_contrato)
    session.commit()
    session.refresh(db_contrato)
    return db_contrato

@contratos_controller_router.get("", response_model=List[ContratoSchema])
def read_contratos(*, session: Session = Depends(get_db)):
    contratos = session.query(ContratoModel).all()
    return contratos

@contratos_controller_router.get("/{item_id}", response_model=ContratoSchema)
def read_contrato(*, session: Session = Depends(get_db), item_id: int):
    contrato = session.get(ContratoModel, item_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato not found")
    return contrato

@contratos_controller_router.put("/{item_id}", response_model=ContratoSchema)
def update_contrato(*, session: Session = Depends(get_db), item_id: int, contrato: ContratoSchema):
    db_contrato = session.get(ContratoModel, item_id)
    if not db_contrato:
        raise HTTPException(status_code=404, detail="Contrato not found")
    contrato_data = contrato.dict(exclude_unset=True)
    for key, value in contrato_data.items():
        setattr(db_contrato, key, value)
    session.add(db_contrato)
    session.commit()
    session.refresh(db_contrato)
    return db_contrato

@contratos_controller_router.delete("/{item_id}", response_model=ContratoSchema)
def delete_contrato(*, session: Session = Depends(get_db), item_id: int):
    contrato = session.get(ContratoModel, item_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato not found")
    session.delete(contrato)
    session.commit()
    return contrato