from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

from models.models import Cliente
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

@router.put("/{cliente_id}", response_model=Cliente)
async def update_cliente(cliente_id: str, cliente: Cliente) -> Cliente:
    cliente_dict = cliente.model_dump(by_alias=True, exclude={"id"})
    cliente_atualizado = await db_clientes.find_one_and_update(
        {"_id": ObjectId(cliente_id)},
        {"$set": cliente_dict},
        return_document=True
    )

    if not cliente_atualizado:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    cliente_atualizado["_id"] = str(cliente_atualizado["_id"])
    return cliente_atualizado

@router.delete("/{cliente_id}", response_model=dict[str, str | Cliente])
async def delete_cliente(cliente_id: str) -> dict[str, str | Cliente]:
    cliente_deletado = await db_clientes.find_one({"_id": ObjectId(cliente_id)})

    if not cliente_deletado:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    await db_clientes.delete_one({"_id": ObjectId(cliente_id)})
    cliente_deletado["_id"] = str(cliente_deletado["_id"])
    return {"message": "Cliente deletado com sucesso!", "cliente": cliente_deletado}

@router.post("/", response_model=Cliente)
async def create_cliente(cliente: Cliente) -> Cliente:
    cliente_dict = cliente.model_dump(by_alias=True, exclude={"id"})
    novo_cliente = await db_clientes.insert_one(cliente_dict)
    cliente_criado = await db_clientes.find_one({"_id": novo_cliente.inserted_id})

    if not cliente_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar cliente")

    cliente_criado["_id"] = str(cliente_criado["_id"])
    return cliente_criado