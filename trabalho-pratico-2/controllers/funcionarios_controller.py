from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select

from models.models import FuncionarioModel
from database import get_session, init_db

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/funcionarios", response_model=FuncionarioModel)
def create_funcionario(*, session: Session = Depends(get_session), funcionario: FuncionarioModel):
    session.add(funcionario)
    session.commit()
    session.refresh(funcionario)
    return funcionario

@app.get("/funcionarios", response_model=List[FuncionarioModel])
def read_funcionarios(*, session: Session = Depends(get_session)):
    funcionarios = session.exec(select(FuncionarioModel)).all()
    return funcionarios

@app.get("/funcionarios/{funcionario_id}", response_model=FuncionarioModel)
def read_funcionario(*, session: Session = Depends(get_session), funcionario_id: int):
    funcionario = session.get(FuncionarioModel, funcionario_id)
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionario not found")
    return funcionario

@app.put("/funcionarios/{funcionario_id}", response_model=FuncionarioModel)
def update_funcionario(*, session: Session = Depends(get_session), funcionario_id: int, funcionario: FuncionarioModel):
    db_funcionario = session.get(FuncionarioModel, funcionario_id)
    if not db_funcionario:
        raise HTTPException(status_code=404, detail="Funcionario not found")
    funcionario_data = funcionario.dict(exclude_unset=True)
    for key, value in funcionario_data.items():
        setattr(db_funcionario, key, value)
    session.add(db_funcionario)
    session.commit()
    session.refresh(db_funcionario)
    return db_funcionario

@app.delete("/funcionarios/{funcionario_id}", response_model=FuncionarioModel)
def delete_funcionario(*, session: Session = Depends(get_session), funcionario_id: int):
    funcionario = session.get(FuncionarioModel, funcionario_id)
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionario not found")
    session.delete(funcionario)
    session.commit()
    return funcionario