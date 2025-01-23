from typing import List
from fastapi import Depends, HTTPException, APIRouter, Query
from sqlmodel import Session, select
from sqlalchemy import func

from models.models import ClienteModel, ClienteSchema
from database import get_db

clientes_controller_router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    dependencies=[Depends(get_db)],
    responses={404: {"description": "Not found"}}
)

@clientes_controller_router.post("", response_model=ClienteSchema)
def create_cliente(*, session: Session = Depends(get_db), cliente: ClienteSchema):
    db_cliente = ClienteModel(**cliente.dict())
    session.add(db_cliente)
    session.commit()
    session.refresh(db_cliente)
    return db_cliente

@clientes_controller_router.get("", response_model=List[ClienteSchema])
def read_clientes(*, session: Session = Depends(get_db), page: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
    offset = (page - 1) * limit
    clientes = session.query(ClienteModel).offset(offset).limit(limit).all()
    return clientes

@clientes_controller_router.get("/{item_id}", response_model=ClienteSchema)
def read_cliente(*, session: Session = Depends(get_db), item_id: int):
    cliente = session.get(ClienteModel, item_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    return cliente

@clientes_controller_router.put("/{item_id}", response_model=ClienteSchema)
def update_cliente(*, session: Session = Depends(get_db), item_id: int, cliente: ClienteSchema):
    db_cliente = session.get(ClienteModel, item_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    cliente_data = cliente.dict(exclude_unset=True)
    for key, value in cliente_data.items():
        setattr(db_cliente, key, value)
    session.add(db_cliente)
    session.commit()
    session.refresh(db_cliente)
    return db_cliente

@clientes_controller_router.delete("/{item_id}", response_model=ClienteSchema)
def delete_cliente(*, session: Session = Depends(get_db), item_id: int):
    cliente = session.get(ClienteModel, item_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    session.delete(cliente)
    session.commit()
    return cliente

@clientes_controller_router.get("/auxiliar/count", response_model=int)
def count_clientes(*, session: Session = Depends(get_db)):
    count = session.execute(select(func.count(ClienteModel.id))).scalar()
    return count