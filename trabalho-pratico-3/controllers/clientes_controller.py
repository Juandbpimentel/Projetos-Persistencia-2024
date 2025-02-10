from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

from models import Cliente
from config import db

db_clientes = db.clientes

router = APIRouter(
    prefix="/clientes",
    tags=["clientes"],
    responses={
        404: {"description": "Não encontrado"},
        200: {"description": "Sucesso"},
        201: {"description": "Criado com sucesso"},
        500: {"description": "Erro interno"},
        400: {"description": "Requisição inválida"}},
)

@router.get("/", response_model=List[Cliente])
async def get_clientes(skip: int = 0, limit: int = 10) -> List[Cliente]:
    clientes = await db_clientes.find().skip(skip).limit(limit).to_list(length=limit)
    for cliente in clientes:
        cliente["_id"] = str(cliente["_id"])
        if "projetos" in cliente and isinstance(cliente["projetos"], list):
            cliente["projetos"] = [str(projeto_id) if isinstance(projeto_id, ObjectId) else projeto_id for projeto_id in cliente["projetos"]]

    return clientes

@router.get("/{cliente_id}", response_model=Cliente)
async def get_cliente(cliente_id: str) -> Cliente:
    cliente = await db_clientes.find_one({"_id": ObjectId(cliente_id)})

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    cliente["_id"] = str(cliente["_id"])
    if "projetos" in cliente and isinstance(cliente["projetos"], list):
        cliente["projetos"] = [str(projeto_id) if isinstance(projeto_id, ObjectId) else projeto_id for projeto_id in cliente["projetos"]]

    return cliente


@router.post("/", response_model=Cliente)
async def create_cliente(cliente: Cliente) -> Cliente:
    cliente_dict = cliente.model_dump(by_alias=True, exclude={"id"})
    novo_cliente = await db_clientes.insert_one(cliente_dict)
    cliente_criado = await db_clientes.find_one({"_id": novo_cliente.inserted_id})

    if not cliente_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar cliente")

    projetos = []

    for projeto_id in cliente_criado["projetos"]:
        projeto = await db.projetos.find_one({"_id": ObjectId(projeto_id)})
        if not projeto:
            raise HTTPException(status_code=404, detail=f"Projeto {projeto_id} não encontrado")

        projetos.append(projeto)

    for projeto in projetos:
        if projeto["cliente_id"] != cliente_criado["_id"]:
            db.projetos.update_one(
                {"_id": ObjectId(projeto["_id"])},
                {"$set": {"cliente_id": cliente_criado["_id"]}}
            )
            db.clientes.update_one(
                {"_id": cliente_criado["_id"]},
                {"$push": {"projetos": str(projeto["_id"])}}
            )
            db.clientes.update_one(
                {"_id": ObjectId(projeto["cliente_id"])},
                {"$pull": {"projetos": str(projeto["_id"])}}
            )

    cliente_criado["_id"] = str(cliente_criado["_id"])
    return cliente_criado


@router.put("/{cliente_id}", response_model=Cliente)
async def update_cliente(cliente_id: str, cliente: Cliente) -> Cliente:
    cliente_dict = cliente.model_dump(by_alias=True, exclude={"id"})
    cliente_antigo = await db_clientes.find_one({"_id": ObjectId(cliente_id)})

    if not cliente_antigo:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    cliente_atualizado = await db_clientes.find_one_and_update(
        {"_id": ObjectId(cliente_id)},
        {"$set": cliente_dict},
        return_document=True
    )

    if not cliente_atualizado:
        raise HTTPException(status_code=400, detail="Falha ao atualizar cliente")

    if cliente_antigo["projetos"] != cliente_dict["projetos"]:
        projetos_removidos = list(set(cliente_antigo["projetos"]) - set(cliente_dict["projetos"]))
        projetos_adicionados = list(set(cliente_dict["projetos"]) - set(cliente_antigo["projetos"]))
        for projeto_id in projetos_removidos:
            await db.funcionarios.update_many(
                {},
                {"$pull": {"projetos": projeto_id}}
            )
            await db.contratos.delete_one({"projeto_id": projeto_id})
            await db.projetos.delete_one({"_id": ObjectId(projeto_id)})

        for projeto_id in projetos_adicionados:
            projeto = await db.projetos.find_one({"_id": ObjectId(projeto_id)})
            await db.projetos.update_one(
                {"_id": ObjectId(projeto_id)},
                {"$set": {"cliente_id": cliente_atualizado["_id"]}}
            )
            await db.clientes.update_one(
                {"_id": cliente_atualizado["_id"]},
                {"$push": {"projetos": str(projeto_id)}}
            )
            await db.clientes.update_one(
                {"_id": ObjectId(projeto["cliente_id"])},
                {"$pull": {"projetos": str(projeto_id)}}
            )

    cliente_atualizado["_id"] = str(cliente_atualizado["_id"])
    return cliente_atualizado


@router.delete("/{cliente_id}", response_model=dict[str, str | Cliente])
async def delete_cliente(cliente_id: str) -> dict[str, str | Cliente]:
    cliente_deletado = await db_clientes.find_one_and_delete({"_id": ObjectId(cliente_id)})

    if not cliente_deletado:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    for projeto_id in cliente_deletado["projetos"]:
        await db.funcionarios.update_many(
            {},
            {"$pull": {"projetos": projeto_id}}
        )
        await db.contratos.delete_one({"projeto_id": projeto_id})
        await db.projetos.delete_one({"_id": ObjectId(projeto_id)})

    cliente_deletado["_id"] = str(cliente_deletado["_id"])
    return {"message": "Cliente deletado com sucesso!", "cliente": cliente_deletado}
