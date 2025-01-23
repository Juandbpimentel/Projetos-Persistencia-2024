from typing import List
from fastapi import Depends, HTTPException, APIRouter, Query
from sqlmodel import Session, select
from sqlalchemy import func

from models.models import FuncionarioModel, FuncionarioSchema
from database import get_db

funcionarios_controller_router = APIRouter(
    prefix="/funcionarios",
    tags=["Funcionarios"],
    dependencies=[Depends(get_db)],
    responses={404: {"description": "Not found"}}
)

@funcionarios_controller_router.post("", response_model=FuncionarioSchema)
def create_funcionario(*, session: Session = Depends(get_db), funcionario: FuncionarioSchema):
    db_funcionario = FuncionarioModel(**funcionario.dict())
    session.add(db_funcionario)
    session.commit()
    session.refresh(db_funcionario)
    return db_funcionario

@funcionarios_controller_router.get("", response_model=List[FuncionarioSchema])
def read_funcionarios(*, session: Session = Depends(get_db), page: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
    offset = (page - 1) * limit
    funcionarios = session.query(FuncionarioModel).offset(offset).limit(limit).all()
    return funcionarios

@funcionarios_controller_router.get("/{item_id}", response_model=FuncionarioSchema)
def read_funcionario(*, session: Session = Depends(get_db), item_id: int):
    funcionario = session.get(FuncionarioModel, item_id)
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionario not found")
    return funcionario

@funcionarios_controller_router.put("/{item_id}", response_model=FuncionarioSchema)
def update_funcionario(*, session: Session = Depends(get_db), item_id: int, funcionario: FuncionarioSchema):
    db_funcionario = session.get(FuncionarioModel, item_id)
    if not db_funcionario:
        raise HTTPException(status_code=404, detail="Funcionario not found")
    funcionario_data = funcionario.dict(exclude_unset=True)
    for key, value in funcionario_data.items():
        setattr(db_funcionario, key, value)
    session.add(db_funcionario)
    session.commit()
    session.refresh(db_funcionario)
    return db_funcionario

@funcionarios_controller_router.delete("/{item_id}", response_model=FuncionarioSchema)
def delete_funcionario(*, session: Session = Depends(get_db), item_id: int):
    funcionario = session.get(FuncionarioModel, item_id)
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionario not found")
    session.delete(funcionario)
    session.commit()
    return funcionario

@funcionarios_controller_router.get("/auxiliar/count", response_model=int)
def count_funcionarios(*, session: Session = Depends(get_db)):
    count = session.execute(select(func.count(FuncionarioModel.id))).scalar()
    return count