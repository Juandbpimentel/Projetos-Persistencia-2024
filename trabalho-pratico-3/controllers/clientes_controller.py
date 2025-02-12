from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

from models.cliente_models import Cliente, ClienteDetalhadoDTO

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

async def buscar_cliente_por_id(cliente_id: str) -> ClienteDetalhadoDTO:
    cliente = await db_clientes.aggregate([
        {"$match": {"_id": ObjectId(cliente_id)}},
        {"$lookup": {
            "from": "projetos",
            "localField": "projetos_id",
            "foreignField": "_id",
            "as": "projetos"
        }}
    ]).to_list()
    if cliente:
        cliente = cliente[0]
        converte_ids_para_string(cliente)
    return cliente


async def buscar_clientes_com_page_e_limit(page: int, limit: int) -> List[ClienteDetalhadoDTO]:
    clientes = await db_clientes.aggregate([
        {"$lookup": {
            "from": "projetos",
            "localField": "projetos_id",
            "foreignField": "_id",
            "as": "projetos"
        }},
        {"$sort": {"_id": 1}},
        {"$skip": max(0, page) * limit},
        {"$limit": limit}
    ]).to_list()
    for cliente in clientes:
        converte_ids_para_string(cliente)
    return clientes


def converte_ids_para_string(cliente):
    cliente["_id"] = str(cliente["_id"])
    if cliente["projetos"]:
        for projeto in cliente["projetos"]:
            projeto["_id"] = str(projeto["_id"])
            if projeto["cliente_id"]:
                projeto["cliente_id"] = str(projeto["cliente_id"])
            if projeto["funcionarios_id"]:
                projeto["funcionarios_id"] = [str(funcionario_id) for funcionario_id in projeto["funcionarios_id"]]
            if projeto["contrato_id"]:
                projeto["contrato_id"] = str(projeto["contrato_id"])

async def trata_cliente_dict(cliente):
    cliente = cliente.model_dump(by_alias=True, exclude={"id"})
    cliente["projetos_id"] = [
        ObjectId(projeto_id) for projeto_id in cliente["projetos_id"]
        if await db.projetos.find_one({"_id": ObjectId(projeto_id)})
    ]
    return cliente

@router.get("/", response_model=List[ClienteDetalhadoDTO])
async def get_clientes(page: int = 0, limit: int = 10) -> List[ClienteDetalhadoDTO]:
    return await buscar_clientes_com_page_e_limit(page, limit)

@router.get("/{cliente_id}", response_model=ClienteDetalhadoDTO)
async def get_cliente(cliente_id: str) -> ClienteDetalhadoDTO:
    cliente = await buscar_cliente_por_id(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    return cliente


@router.post("/", response_model=ClienteDetalhadoDTO)
async def create_cliente(cliente: Cliente) -> ClienteDetalhadoDTO:
    cliente_dict = await trata_cliente_dict(cliente)
    novo_cliente = await db_clientes.insert_one(cliente_dict)
    cliente_criado = await buscar_cliente_por_id(str(novo_cliente.inserted_id))

    if not cliente_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar cliente")

    if cliente_criado["projetos"]:
        for projeto in cliente_criado["projetos"]:
            if not projeto:
                raise HTTPException(status_code=404, detail=f"Projeto {projeto["_id"]} não encontrado")
            if projeto["cliente_id"] != cliente_criado["_id"]:
                db.projetos.update_one(
                    {"_id": ObjectId(projeto["_id"])},
                    {"$set": {"cliente_id": ObjectId(cliente_criado["_id"])}}
                )
                db.clientes.update_one(
                    {"_id": ObjectId(projeto["cliente_id"])},
                    {"$pull": {"projetos_id": ObjectId(projeto["_id"])}}
                )


    cliente_criado = await buscar_cliente_por_id(str(novo_cliente.inserted_id))
    return cliente_criado


@router.put("/{cliente_id}", response_model=ClienteDetalhadoDTO)
async def update_cliente(cliente_id: str, cliente: Cliente) -> ClienteDetalhadoDTO:
    cliente_dict = await trata_cliente_dict(cliente)
    cliente_antigo = await buscar_cliente_por_id(cliente_id)

    if not cliente_antigo:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    await db_clientes.update_one({"_id": ObjectId(cliente_id)}, {"$set": cliente_dict})
    cliente_atualizado = await buscar_cliente_por_id(cliente_id)

    if not cliente_atualizado:
        raise HTTPException(status_code=400, detail="Falha ao atualizar cliente")

    if cliente_antigo["projetos"] != cliente_atualizado["projetos"]:
        antigos = {projeto["_id"]: projeto for projeto in cliente_antigo["projetos"]}
        novos = {projeto["_id"]: projeto for projeto in cliente_atualizado["projetos"]}
        removidos = [antigos[_id] for _id in set(antigos) - set(novos)]
        adicionados = [novos[_id] for _id in set(novos) - set(antigos)]
        for projeto in removidos:
            await db.funcionarios.update_many(
                {},
                {"$pull": {"projetos_id": ObjectId(projeto["_id"])}}
            )
            await db.contratos.delete_one({"projeto_id":  ObjectId(projeto["_id"])})
            await db.projetos.delete_one({"_id":  ObjectId(projeto["_id"])})

        for projeto in adicionados:
            projeto = await db.projetos.find_one({"_id":  ObjectId(projeto["_id"])})
            await db.projetos.update_one(
                {"_id":  ObjectId(projeto["_id"])},
                {"$set": {"cliente_id": ObjectId(cliente_atualizado["_id"])}}
            )
            await db.clientes.update_one(
                {"_id": ObjectId(projeto["cliente_id"])},
                {"$pull": {"projetos_id":  ObjectId(projeto["_id"])}}
            )

    cliente_atualizado = await buscar_cliente_por_id(cliente_id)
    return cliente_atualizado


@router.delete("/{cliente_id}", response_model=ClienteDetalhadoDTO)
async def delete_cliente(cliente_id: str) ->ClienteDetalhadoDTO:
    cliente = await buscar_cliente_por_id(cliente_id)

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    cliente_deletado = await db_clientes.delete_one({"_id": ObjectId(cliente_id)})
    if not cliente_deletado:
        raise HTTPException(status_code=400, detail="Erro ao deletar cliente")

    for projeto in cliente["projetos"]:
        await db.funcionarios.update_many(
            {},
            {"$pull": {"projetos_id":ObjectId(projeto["_id"])}}
        )
        await db.contratos.delete_one({"projeto_id": ObjectId(projeto["_id"])})
        await db.projetos.delete_one({"_id": ObjectId(projeto["_id"])})

    return cliente
