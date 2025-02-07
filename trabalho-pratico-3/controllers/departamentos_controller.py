from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List, Any, Coroutine

from fastapi.params import Depends
from motor.motor_asyncio import AsyncIOMotorCollection

from models.models import Departamento
from config import db

db_departamentos = db.departamentos

router = APIRouter(
    prefix="/departamentos",
    tags=["departamentos"],
    responses={
        404: {"description": "Não encontrado"},
        200: {"description": "Sucesso"},
        201: {"description": "Criado com sucesso"},
        500: {"description": "Erro interno"},
        400: {"description": "Requisição inválida"}},
)


@router.get("/", response_model=List[Departamento])
async def get_departamentos(skip: int = 0, limit: int = 10) -> List[Departamento]:
    departamentos = await db_departamentos.find().skip(skip).limit(limit).to_list(length=limit)
    for departamento in departamentos:
        departamento["_id"] = str(departamento["_id"])
        if "funcionarios" in departamento and isinstance(departamento["funcionarios"], list):
            departamento["funcionarios"] = [
                str(funcionario_id) if isinstance(funcionario_id, ObjectId) else funcionario_id for funcionario_id in
                departamento["funcionarios"]]

    return departamentos

@router.get("/{departamento_id}", response_model=Departamento)
async def get_departamento(departamento_id: str) -> Departamento:
    departamento = await db_departamentos.find_one({"_id": ObjectId(departamento_id)})

    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    departamento["_id"] = str(departamento["_id"])
    if "funcionarios" in departamento and isinstance(departamento["funcionarios"], list):
        departamento["funcionarios"] = [
            str(funcionario_id) if isinstance(funcionario_id, ObjectId) else funcionario_id for funcionario_id in
            departamento["funcionarios"]]

    return departamento


@router.post("/", response_model=dict[str, str | Departamento])
async def create_departamento(departamento: Departamento) -> dict[str, str | Departamento]:
    departamento_dict = departamento.model_dump(by_alias=True, exclude={"id"})
    novo_departamento = await db_departamentos.insert_one(departamento_dict)
    departamento_criado = await db_departamentos.find_one({"_id": novo_departamento.inserted_id})

    if not departamento_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar departamento")

    departamento_criado["_id"] = str(departamento_criado["_id"])

    await db.empresas.update_one(
        {"_id": ObjectId(departamento_criado["empresa_id"])},
        {"$push": {"departamentos": str(departamento_criado["_id"])}}
    )
    return {"message": "Departamento criado com sucesso!", "departamento": departamento_criado}

@router.put("/{departamento_id}", response_model=Departamento)
async def update_departamento(departamento_id: str, departamento: Departamento) -> Departamento:
    departamento_dict = departamento.model_dump(by_alias=True, exclude={"id"})
    departamento_atualizado = await db_departamentos.find_one_and_update(
        {"_id": ObjectId(departamento_id)},
        {"$set": departamento_dict},
        return_document=True
    )

    if not departamento_atualizado:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    funcionarios = await db.funcionarios.find({"departamento_id": ObjectId(departamento_id)}).to_list(length=None)
    await db.funcionarios.delete_many({"departamento_id": ObjectId(departamento_id)})
    for funcionario in funcionarios:
        await db.projetos.update_many(
            {},
            {"$pull": {"funcionarios": funcionario["_id"]}}
        )

    departamento_atualizado["_id"] = str(departamento_atualizado["_id"])
    return departamento_atualizado

@router.delete("/{departamento_id}", response_model=dict[str, str | Departamento])
async def delete_departamento(departamento_id: str) -> dict[str, str | Departamento]:
    departamento = await db_departamentos.find_one({"_id": ObjectId(departamento_id)})
    funcionarios = []

    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")


    await db.empresas.update_one(
        {"_id": ObjectId(departamento["empresa_id"])},
        {"$pull": {"departamentos": departamento_id}}
    )

    funcionarios.extend(
        await db.funcionarios.find(
            {"departamento_id": ObjectId(departamento_id)}
        ).to_list()
    )

    await db_departamentos.delete_one({"_id": ObjectId(departamento_id)})

    for funcionario in funcionarios:
        await db.projetos.update_many(
            {},
            {"$pull": {"funcionarios": funcionario["_id"]}}
        )
        await db.funcionarios.delete_one({"_id": ObjectId(funcionario["_id"])})


    departamento["_id"] = str(departamento["_id"])
    return {"message": "Departamento deletado com sucesso!", "departamento": departamento}
