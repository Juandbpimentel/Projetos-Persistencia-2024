from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

from models.models import Projeto
from config import db

db_projetos = db.projetos

router = APIRouter(
    prefix="/projetos",
    tags=["projetos"],
    responses={
        404: {"description": "Não encontrado"},
        200: {"description": "Sucesso"},
        201: {"description": "Criado com sucesso"},
        500: {"description": "Erro interno"},
        400: {"description": "Requisição inválida"}},
)

@router.get("/", response_model=List[Projeto])
async def get_projetos(skip: int = 0, limit: int = 10) -> List[Projeto]:
    projetos = await db_projetos.find().skip(skip).limit(limit).to_list(length=limit)
    for projeto in projetos:
        projeto["_id"] = str(projeto["_id"])
        if "funcionarios" in projeto and isinstance(projeto["funcionarios"], list):
            projeto["funcionarios"] = [str(funcionario_id) if isinstance(funcionario_id, ObjectId) else funcionario_id for funcionario_id in projeto["funcionarios"]]

    return projetos

@router.get("/{projeto_id}", response_model=Projeto)
async def get_projeto(projeto_id: str) -> Projeto:
    projeto = await db_projetos.find_one({"_id": ObjectId(projeto_id)})

    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    projeto["_id"] = str(projeto["_id"])
    if "funcionarios" in projeto and isinstance(projeto["funcionarios"], list):
        projeto["funcionarios"] = [str(funcionario_id) if isinstance(funcionario_id, ObjectId) else funcionario_id for funcionario_id in projeto["funcionarios"]]

    return projeto

@router.put("/{projeto_id}", response_model=Projeto)
async def update_projeto(projeto_id: str, projeto: Projeto) -> Projeto:
    projeto_dict = projeto.model_dump(by_alias=True, exclude={"id"})
    projeto_atualizado = await db_projetos.find_one_and_update(
        {"_id": ObjectId(projeto_id)},
        {"$set": projeto_dict},
        return_document=True
    )

    if not projeto_atualizado:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    projeto_atualizado["_id"] = str(projeto_atualizado["_id"])
    return projeto_atualizado

@router.delete("/{projeto_id}", response_model=dict[str, str | Projeto])
async def delete_projeto(projeto_id: str) -> dict[str, str | Projeto]:
    projeto_deletado = await db_projetos.find_one({"_id": ObjectId(projeto_id)})

    if not projeto_deletado:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    await db_projetos.delete_one({"_id": ObjectId(projeto_id)})
    projeto_deletado["_id"] = str(projeto_deletado["_id"])
    return {"message": "Projeto deletado com sucesso!", "projeto": projeto_deletado}

@router.post("/", response_model=Projeto)
async def create_projeto(projeto: Projeto) -> Projeto:
    projeto_dict = projeto.model_dump(by_alias=True, exclude={"id"})
    novo_projeto = await db_projetos.insert_one(projeto_dict)
    projeto_criado = await db_projetos.find_one({"_id": novo_projeto.inserted_id})

    if not projeto_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar projeto")

    projeto_criado["_id"] = str(projeto_criado["_id"])
    return projeto_criado