from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

from models.contrato_models import Contrato, ContratoDetalhadoDTO
from config import db

db_contratos = db.contratos

router = APIRouter(
    prefix="/contratos",
    tags=["contratos"],
    responses={
        404: {"description": "Não encontrado"},
        200: {"description": "Sucesso"},
        201: {"description": "Criado com sucesso"},
        500: {"description": "Erro interno"},
        400: {"description": "Requisição inválida"}},
)

async def buscar_contrato_por_id(contrato_id: str) -> ContratoDetalhadoDTO:
    contrato = await db_contratos.aggregate([
        {"$match": {"_id": ObjectId(contrato_id)}},
        {"$lookup": {
            "from": "projetos",
            "localField": "projeto_id",
            "foreignField": "_id",
            "as": "projeto"
        }}
    ]).to_list()
    if contrato:
        contrato = contrato[0]
        converte_ids_para_string(contrato)
    return contrato

async def buscar_contratos_com_page_e_limit(page: int, limit: int) -> List[ContratoDetalhadoDTO]:
    contratos = await db_contratos.aggregate([
        {"$lookup": {
            "from": "projetos",
            "localField": "projeto_id",
            "foreignField": "_id",
            "as": "projeto"
        }},
        {"$sort": {"_id": 1}},
        {"$skip": max(0, page) * limit},
        {"$limit": limit}
    ]).to_list()
    for contrato in contratos:
        converte_ids_para_string(contrato)
    return contratos

def converte_ids_para_string(contrato):
    contrato["_id"] = str(contrato["_id"])
    if contrato["projeto"]:
        contrato["projeto"] = contrato["projeto"][0]
        contrato["projeto"]["_id"] = str(contrato["projeto"]["_id"])
        if contrato["projeto"]["cliente_id"]:
            contrato["projeto"]["cliente_id"] = str(contrato["projeto"]["cliente_id"])
        if contrato["projeto"]["funcionarios_id"]:
            contrato["projeto"]["funcionarios_id"] = [str(funcionario_id) for funcionario_id in contrato["projeto"]["funcionarios_id"]]
        if contrato["projeto"]["contrato_id"]:
            contrato["projeto"]["contrato_id"] = str(contrato["projeto"]["contrato_id"])

async def trata_contrato_dict(contrato):
    contrato_dict = contrato.model_dump(by_alias=True, exclude={"id"})
    contrato_dict["projeto_id"] = ObjectId(contrato_dict["projeto_id"])
    if not await db.projetos.find_one({"_id": contrato_dict["projeto_id"]}):
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return contrato_dict

@router.get("/", response_model=List[ContratoDetalhadoDTO])
async def get_contratos(page: int = 0, limit: int = 10) -> List[ContratoDetalhadoDTO]:
    return await buscar_contratos_com_page_e_limit(page, limit)

@router.get("/{contrato_id}", response_model=ContratoDetalhadoDTO)
async def get_contrato(contrato_id: str) -> ContratoDetalhadoDTO:
    contrato = await buscar_contrato_por_id(contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return contrato

@router.post("/", response_model=ContratoDetalhadoDTO)
async def create_contrato(contrato: Contrato) -> ContratoDetalhadoDTO:
    contrato_dict = await trata_contrato_dict(contrato)
    novo_contrato = await db_contratos.insert_one(contrato_dict)
    contrato_criado = await buscar_contrato_por_id(str(novo_contrato.inserted_id))

    if not contrato_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar contrato")

    await db.projetos.update_one(
        {"_id": ObjectId(contrato_criado["projeto_id"])},
        {"$set": {"contrato_id": ObjectId(contrato_criado["_id"])}}
    )

    contrato_criado = await buscar_contrato_por_id(str(novo_contrato.inserted_id))
    return contrato_criado

@router.put("/{contrato_id}", response_model=ContratoDetalhadoDTO)
async def update_contrato(contrato_id: str, contrato: Contrato) -> ContratoDetalhadoDTO:
    contrato_dict = await trata_contrato_dict(contrato)
    contrato_antigo = await buscar_contrato_por_id(contrato_id)

    if not contrato_antigo:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    await db_contratos.update_one({"_id": ObjectId(contrato_id)}, {"$set": contrato_dict})
    contrato_atualizado = await buscar_contrato_por_id(contrato_id)

    if not contrato_atualizado:
        raise HTTPException(status_code=400, detail="Falha ao atualizar contrato")

    if contrato_antigo["projeto"] != contrato_atualizado["projeto"]:
        antigos = {projeto["_id"]: projeto for projeto in contrato_antigo["projeto"]}
        novos = {projeto["_id"]: projeto for projeto in contrato_atualizado["projeto"]}
        removidos = [antigos[_id] for _id in set(antigos) - set(novos)]
        adicionados = [novos[_id] for _id in set(novos) - set(antigos)]
        for projeto in removidos:
            await db.funcionarios.update_many(
                {},
                {"$pull": {"projetos_id": ObjectId(projeto["_id"])}}
            )
            await db.contratos.delete_one({"projeto_id": ObjectId(projeto["_id"])})
            await db.projetos.delete_one({"_id": ObjectId(projeto["_id"])})

        for projeto in adicionados:
            projeto = await db.projetos.find_one({"_id": ObjectId(projeto["_id"])})
            await db.projetos.update_one(
                {"_id": ObjectId(projeto["_id"])},
                {"$set": {"cliente_id": ObjectId(contrato_atualizado["_id"])}}
            )
            await db.clientes.update_one(
                {"_id": ObjectId(projeto["cliente_id"])},
                {"$pull": {"projetos_id": ObjectId(projeto["_id"])}}
            )

    contrato_atualizado = await buscar_contrato_por_id(contrato_id)
    return contrato_atualizado

@router.delete("/{contrato_id}", response_model=ContratoDetalhadoDTO)
async def delete_contrato(contrato_id: str) -> ContratoDetalhadoDTO:
    contrato = await buscar_contrato_por_id(contrato_id)

    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    contrato_deletado = await db_contratos.delete_one({"_id": ObjectId(contrato_id)})
    if not contrato_deletado:
        raise HTTPException(status_code=400, detail="Erro ao deletar contrato")

    await db.projetos.update_one(
        {"_id": ObjectId(contrato["projeto_id"])},
        {"$set": {"contrato_id": None}}
    )

    return contrato