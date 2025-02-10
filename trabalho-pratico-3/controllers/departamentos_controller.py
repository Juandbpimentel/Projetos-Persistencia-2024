from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

from models import Departamento
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


@router.post("/", response_model=Departamento, status_code=201)
async def create_departamento(departamento: Departamento) -> dict[str, str | Departamento]:
    departamento_dict = departamento.model_dump(by_alias=True, exclude={"id"})
    novo_departamento = await db_departamentos.insert_one(departamento_dict)
    departamento_criado = await db_departamentos.find_one({"_id": novo_departamento.inserted_id})

    if not departamento_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar departamento")


    await db.empresas.update_one(
        {"_id": ObjectId(departamento_criado["empresa_id"])},
        {"$push": {"departamentos": str(departamento_criado["_id"])}}
    )
    funcionarios = []

    for funcionario_id in departamento_criado["funcionarios"]:
        funcionario = await db.funcionarios.find_one({"_id": ObjectId(funcionario_id)})
        if not funcionario:
            raise HTTPException(status_code=404, detail=f"Funcionario {funcionario_id} não encontrado")
        funcionarios.append(funcionario)

    for funcionario in funcionarios:
        funcionario = await db.funcionarios.find_one({"_id": ObjectId(funcionario["_id"])})
        if funcionario["departamento_id"] is not None:
            await db_departamentos.update_one(
                {"_id": ObjectId(funcionario["departamento_id"])},
                {"$pull": {"funcionarios": str(funcionario["_id"])}}
            )
        await db.funcionarios.update_one(
            {"_id": ObjectId(funcionario["_id"])},
            {"$set": {"departamento_id": str(departamento_criado["_id"])}}
        )

    departamento_criado["_id"] = str(departamento_criado["_id"])
    return departamento_criado

@router.put("/{departamento_id}", response_model=Departamento)
async def update_departamento(departamento_id: str, departamento: Departamento) -> Departamento:
    departamento_dict = departamento.model_dump(by_alias=True, exclude={"id"})
    departamento_antigo = await db_departamentos.find_one({"_id": ObjectId(departamento_id)})

    departamento_atualizado = await db_departamentos.find_one_and_update(
        {"_id": ObjectId(departamento_id)},
        {"$set": departamento_dict},
        return_document=True
    )

    if not departamento_atualizado:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    if departamento_antigo["funcionarios"] != departamento_dict["funcionarios"]:
        funcionarios_removidos = list(set(departamento_antigo["funcionarios"]) - set(departamento_dict["funcionarios"]))
        funcionarios_adicionados = list(set(departamento_dict["funcionarios"]) - set(departamento_antigo["funcionarios"]))

        for funcionario_id in funcionarios_removidos:
            await db.funcionarios.delete_one({"_id": ObjectId(funcionario_id)})
            await db.projetos.update_many(
                {},
                {"$pull": {"funcionarios": funcionario_id}}
            )

        for funcionario_id in funcionarios_adicionados:
            funcionario = await db.funcionarios.find_one({"_id": ObjectId(funcionario_id)})
            if not funcionario:
                raise HTTPException(status_code=404, detail=f"Funcionario {funcionario_id} não encontrado")
            if funcionario["departamento_id"] is not None:
                await db_departamentos.update_one(
                    {"_id": ObjectId(funcionario["departamento_id"])},
                    {"$pull": {"funcionarios": str(funcionario["_id"])}}
                )
            await db.funcionarios.update_one(
                {"_id": ObjectId(funcionario_id)},
                {"$set": {"departamento_id": str(departamento_atualizado["_id"])}}
            )

    departamento_atualizado["_id"] = str(departamento_atualizado["_id"])
    return departamento_atualizado

@router.delete("/{departamento_id}", response_model=Departamento)
async def delete_departamento(departamento_id: str) -> Departamento:
    departamento = await db_departamentos.find_one_and_delete({"_id": ObjectId(departamento_id)})

    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    funcionarios = departamento["funcionarios"] if "funcionarios" in departamento else []

    await db.empresas.update_one(
        {"_id": ObjectId(departamento["empresa_id"])},
        {"$pull": {"departamentos": departamento_id}}
    )

    await db.funcionarios.delete_many({"departamento_id": departamento_id})

    for funcionario_id in funcionarios:
        await db.projetos.update_many(
            {},
            {"$pull": {"funcionarios": funcionario_id}}
        )

    departamento["_id"] = str(departamento["_id"])
    return departamento
