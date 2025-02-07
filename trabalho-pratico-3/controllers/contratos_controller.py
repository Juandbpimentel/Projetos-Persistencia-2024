from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

from models.models import Contrato
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

@router.get("/", response_model=List[Contrato])
async def get_contratos(skip: int = 0, limit: int = 10) -> List[Contrato]:
    contratos = await db_contratos.find().skip(skip).limit(limit).to_list(length=limit)
    for contrato in contratos:
        contrato["_id"] = str(contrato["_id"])

    return contratos

@router.get("/{contrato_id}", response_model=Contrato)
async def get_contrato(contrato_id: str) -> Contrato:
    contrato = await db_contratos.find_one({"_id": ObjectId(contrato_id)})

    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    contrato["_id"] = str(contrato["_id"])
    return contrato

@router.put("/{contrato_id}", response_model=Contrato)
async def update_contrato(contrato_id: str, contrato: Contrato) -> Contrato:
    contrato_dict = contrato.model_dump(by_alias=True, exclude={"id"})
    contrato_atualizado = await db_contratos.find_one_and_update(
        {"_id": ObjectId(contrato_id)},
        {"$set": contrato_dict},
        return_document=True
    )

    if not contrato_atualizado:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    contrato_atualizado["_id"] = str(contrato_atualizado["_id"])
    return contrato_atualizado

@router.delete("/{contrato_id}", response_model=dict[str, str | Contrato])
async def delete_contrato(contrato_id: str) -> dict[str, str | Contrato]:
    contrato_deletado = await db_contratos.find_one({"_id": ObjectId(contrato_id)})

    if not contrato_deletado:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    await db_contratos.delete_one({"_id": ObjectId(contrato_id)})
    contrato_deletado["_id"] = str(contrato_deletado["_id"])
    return {"message": "Contrato deletado com sucesso!", "contrato": contrato_deletado}

@router.post("/", response_model=Contrato)
async def create_contrato(contrato: Contrato) -> Contrato:
    contrato_dict = contrato.model_dump(by_alias=True, exclude={"id"})
    novo_contrato = await db_contratos.insert_one(contrato_dict)
    contrato_criado = await db_contratos.find_one({"_id": novo_contrato.inserted_id})

    if not contrato_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar contrato")

    contrato_criado["_id"] = str(contrato_criado["_id"])
    return contrato_criado