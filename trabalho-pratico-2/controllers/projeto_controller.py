from typing import List
from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session

from models.models import ProjetoModel, ProjetoSchema
from database import get_db

projetos_controller_router = APIRouter(
    prefix="/projetos",
    tags=["Projetos"],
    dependencies=[Depends(get_db)],
    responses={404: {"description": "Not found"}}
)

@projetos_controller_router.post("", response_model=ProjetoSchema)
def create_projeto(*, session: Session = Depends(get_db), projeto: ProjetoSchema):
    db_projeto = ProjetoModel(**projeto.dict())
    session.add(db_projeto)
    session.commit()
    session.refresh(db_projeto)
    return db_projeto

@projetos_controller_router.get("", response_model=List[ProjetoSchema])
def read_projetos(*, session: Session = Depends(get_db)):
    projetos = session.query(ProjetoModel).all()
    return projetos

@projetos_controller_router.get("/{item_id}", response_model=ProjetoSchema)
def read_projeto(*, session: Session = Depends(get_db), item_id: int):
    projeto = session.get(ProjetoModel, item_id)
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto not found")
    return projeto

@projetos_controller_router.put("/{item_id}", response_model=ProjetoSchema)
def update_projeto(*, session: Session = Depends(get_db), item_id: int, projeto: ProjetoSchema):
    db_projeto = session.get(ProjetoModel, item_id)
    if not db_projeto:
        raise HTTPException(status_code=404, detail="Projeto not found")
    projeto_data = projeto.dict(exclude_unset=True)
    for key, value in projeto_data.items():
        setattr(db_projeto, key, value)
    session.add(db_projeto)
    session.commit()
    session.refresh(db_projeto)
    return db_projeto

@projetos_controller_router.delete("/{item_id}", response_model=ProjetoSchema)
def delete_projeto(*, session: Session = Depends(get_db), item_id: int):
    projeto = session.get(ProjetoModel, item_id)
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto not found")
    session.delete(projeto)
    session.commit()
    return projeto