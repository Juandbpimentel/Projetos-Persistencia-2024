from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

from models.funcionario_models import Funcionario
from config import db

db_funcionarios = db.funcionarios

router = APIRouter(
    prefix="/funcionarios",
    tags=["funcionarios"],
    responses={
        404: {"description": "Não encontrado"},
        200: {"description": "Sucesso"},
        201: {"description": "Criado com sucesso"},
        500: {"description": "Erro interno"},
        400: {"description": "Requisição inválida"}},
)

@router.get("/", response_model=List[Funcionario])
async def get_funcionarios(skip: int = 0, limit: int = 10) -> List[Funcionario]:
    funcionarios = await db_funcionarios.find().skip(skip).limit(limit).to_list(length=limit)
    for funcionario in funcionarios:
        funcionario["_id"] = str(funcionario["_id"])
        if "projetos" in funcionario and isinstance(funcionario["projetos"], list):
            funcionario["projetos"] = [str(projeto_id) if isinstance(projeto_id, ObjectId) else projeto_id for projeto_id in funcionario["projetos"]]

    return funcionarios


@router.get("/{funcionario_id}", response_model=Funcionario)
async def get_funcionario(funcionario_id: str) -> Funcionario:
    funcionario = await db_funcionarios.find_one({"_id": ObjectId(funcionario_id)})

    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionario não encontrado")

    funcionario["_id"] = str(funcionario["_id"])
    if "projetos" in funcionario and isinstance(funcionario["projetos"], list):
        funcionario["projetos"] = [str(projeto_id) if isinstance(projeto_id, ObjectId) else projeto_id for projeto_id in funcionario["projetos"]]

    return funcionario


@router.post("/", response_model=Funcionario)
async def create_funcionario(funcionario: Funcionario) -> Funcionario:
    funcionario_dict = funcionario.model_dump(by_alias=True, exclude={"id"})
    novo_funcionario = await db_funcionarios.insert_one(funcionario_dict)
    funcionario_criado = await db_funcionarios.find_one({"_id": novo_funcionario.inserted_id})

    if not funcionario_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar funcionario")

    projetos = []

    for projeto_id in funcionario_criado["projetos"]:
        projeto = await db.projetos.find_one({"_id": ObjectId(projeto_id)})
        if not projeto:
            raise HTTPException(status_code=404, detail=f"Projeto {projeto_id} não encontrado")
        projetos.append(projeto)

    for projeto in projetos:
        await db.projetos.update_one(
            {"_id": ObjectId(projeto["_id"])},
            {"$push": {"funcionarios": funcionario_criado["_id"]}}
        )

    await db.departamentos.update_one(
        {"_id": ObjectId(funcionario_criado["departamento_id"])},
        {"$push": {"funcionarios": str(funcionario_criado["_id"])}}
    )

    funcionario_criado["_id"] = str(funcionario_criado["_id"])
    return funcionario_criado


@router.put("/{funcionario_id}", response_model=Funcionario)
async def update_funcionario(funcionario_id: str, funcionario: Funcionario) -> Funcionario:
    funcionario_dict = funcionario.model_dump(by_alias=True, exclude={"id"})
    funcionario_antigo = await db_funcionarios.find_one({"_id": ObjectId(funcionario_id)})

    if not funcionario_antigo:
        raise HTTPException(status_code=404, detail="Funcionario não encontrado")

    funcionario_atualizado = await db_funcionarios.find_one_and_update(
        {"_id": ObjectId(funcionario_id)},
        {"$set": funcionario_dict},
        return_document=True
    )

    if not funcionario_atualizado:
        raise HTTPException(status_code=400, detail="Falha ao atualizar funcionario")

    if funcionario_antigo["projetos"] != funcionario_dict["projetos"]:
        projetos_removidos = list(set(funcionario_antigo["projetos"]) - set(funcionario_dict["projetos"]))
        projetos_adicionados = list(set(funcionario_dict["projetos"]) - set(funcionario_antigo["projetos"]))

        for projeto_id in projetos_removidos:
            await db.projetos.update_one(
                {"_id": ObjectId(projeto_id)},
                {"$pull": {"funcionarios": funcionario_id}}
            )

        for projeto_id in projetos_adicionados:
            await db.projetos.update_one(
                {"_id": ObjectId(projeto_id)},
                {"$push": {"funcionarios": funcionario_id}}
            )

    if funcionario_antigo["departamento_id"] != funcionario_dict["departamento_id"]:
        await db.departamentos.update_one(
            {"_id": ObjectId(funcionario_antigo["departamento_id"])},
            {"$pull": {"funcionarios": funcionario_id}}
        )

        await db.departamentos.update_one(
            {"_id": ObjectId(funcionario_dict["departamento_id"])},
            {"$push": {"funcionarios": funcionario_id}}
        )

    funcionario_atualizado["_id"] = str(funcionario_atualizado["_id"])
    return funcionario_atualizado


@router.delete("/{funcionario_id}", response_model=Funcionario)
async def delete_funcionario(funcionario_id: str) -> Funcionario:
    funcionario_deletado = await db_funcionarios.delete_one({"_id": ObjectId(funcionario_id)})

    if not funcionario_deletado:
        raise HTTPException(status_code=404, detail="Funcionario não encontrado")

    await db.projetos.update_many(
        {},
        {"$pull": {"funcionarios": funcionario_id}}
    )

    await db.departamentos.update_one(
        {"_id": ObjectId(funcionario_deletado["departamento_id"])},
        {"$pull": {"funcionarios": funcionario_id}}
    )

    funcionario_deletado["_id"] = str(funcionario_deletado["_id"])
    return funcionario_deletado

