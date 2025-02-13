from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

from logger import logger

from models.funcionario_models import Funcionario, FuncionarioDetalhadoDTO
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

async def buscar_funcionario_por_id(funcionario_id: str) -> FuncionarioDetalhadoDTO:
    funcionario = await db_funcionarios.aggregate([
        {"$match": {"_id": ObjectId(funcionario_id)}},
        {"$lookup": {
            "from": "departamentos",
            "localField": "departamento_id",
            "foreignField": "_id",
            "as": "departamento"
        }},
        {"$lookup": {
            "from": "projetos",
            "localField": "projetos_id",
            "foreignField": "_id",
            "as": "projetos"
        }}
    ]).to_list()
    if funcionario:
        funcionario = funcionario[0]
        converte_ids_em_string(funcionario)
    return funcionario

async def buscar_funcionarios_com_page_e_limit(page: int, limit: int) -> List[FuncionarioDetalhadoDTO]:
    funcionarios = await db_funcionarios.aggregate([
        {"$lookup": {
            "from": "departamentos",
            "localField": "departamento_id",
            "foreignField": "_id",
            "as": "departamento"
        }},
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
    for funcionario in funcionarios:
        converte_ids_em_string(funcionario)
    return funcionarios

def converte_ids_em_string(funcionario: FuncionarioDetalhadoDTO):
    funcionario["_id"] = str(funcionario["_id"])
    if funcionario["departamento"]:
        departamento = funcionario["departamento"][0]
        departamento["_id"] = str(departamento["_id"])
        departamento["empresa_id"] = str(departamento["empresa_id"])
        departamento["funcionarios_id"] = [str(fid) for fid in departamento["funcionarios_id"]]
        funcionario["departamento"] = departamento
    if funcionario["projetos"]:
        for projeto in funcionario["projetos"]:
            projeto["_id"] = str(projeto["_id"])
            projeto["funcionarios_id"] = [str(fid) for fid in projeto["funcionarios_id"]]
            projeto["contrato_id"] = str(projeto["contrato_id"])
            projeto["cliente_id"] = str(projeto["cliente_id"])

async def trata_funcionario_dict(funcionario: Funcionario) -> dict:
    funcionario_dict = funcionario.model_dump(by_alias=True, exclude={"id"})
    funcionario_dict["projetos_id"] = [
        ObjectId(projeto) for projeto in funcionario_dict["projetos_id"]
        if await db.projetos.find_one({"_id": ObjectId(projeto)})
    ]
    funcionario_dict["departamento_id"] = ObjectId(funcionario_dict["departamento_id"])
    if not await db.departamentos.find_one({"_id": funcionario_dict["departamento_id"]}):
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    return funcionario_dict

@router.get("/", response_model=List[FuncionarioDetalhadoDTO])
async def get_funcionarios(page: int = 0, limit: int = 10) -> List[FuncionarioDetalhadoDTO]:
    return await buscar_funcionarios_com_page_e_limit(page, limit)

@router.get("/{funcionario_id}", response_model=FuncionarioDetalhadoDTO)
async def get_funcionario(funcionario_id: str) -> FuncionarioDetalhadoDTO:
    funcionario = await buscar_funcionario_por_id(funcionario_id)
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionario não encontrado")
    return funcionario

@router.post("/", response_model=FuncionarioDetalhadoDTO)
async def create_funcionario(funcionario: Funcionario) -> FuncionarioDetalhadoDTO:
    funcionario_dict = await trata_funcionario_dict(funcionario)
    novo_funcionario = await db_funcionarios.insert_one(funcionario_dict)
    funcionario_criado = await buscar_funcionario_por_id(str(novo_funcionario.inserted_id))
    if not funcionario_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar funcionario")
    for projeto in funcionario_criado["projetos"]:
        await db.projetos.update_one({"_id": ObjectId(projeto["_id"])}, {"$push": {"funcionarios_id": ObjectId(funcionario_criado["_id"])}})
    await db.departamentos.update_one({"_id": ObjectId(funcionario_criado["departamento"]["_id"])}, {"$push": {"funcionarios_id": ObjectId(funcionario_criado["_id"])}})
    funcionario_criado = await buscar_funcionario_por_id(str(novo_funcionario.inserted_id))
    return funcionario_criado

@router.put("/{funcionario_id}", response_model=FuncionarioDetalhadoDTO)
async def update_funcionario(funcionario_id: str, funcionario: Funcionario) -> FuncionarioDetalhadoDTO:
    funcionario_dict = await trata_funcionario_dict(funcionario)
    funcionario_antigo = await buscar_funcionario_por_id(funcionario_id)
    if not funcionario_antigo:
        raise HTTPException(status_code=404, detail="Funcionario não encontrado")
    await db_funcionarios.update_one({"_id": ObjectId(funcionario_id)}, {"$set": funcionario_dict})
    funcionario_atualizado = await buscar_funcionario_por_id(funcionario_id)
    if not funcionario_atualizado:
        raise HTTPException(status_code=400, detail="Falha ao atualizar funcionario")
    if funcionario_antigo["projetos"] != funcionario_atualizado["projetos"]:
        antigos = set(funcionario_antigo["projetos"])
        novos = set(funcionario_atualizado["projetos"])
        for projeto_id in antigos - novos:
            await db.projetos.update_one({"_id": ObjectId(projeto_id)}, {"$pull": {"funcionarios_id": ObjectId(funcionario_id)}})
        for projeto_id in novos - antigos:
            await db.projetos.update_one({"_id": ObjectId(projeto_id)}, {"$push": {"funcionarios_id": ObjectId(funcionario_id)}})
    if funcionario_antigo["departamento"] != funcionario_atualizado["departamento"]:
        await db.departamentos.update_one({"_id": ObjectId(funcionario_antigo["departamento"]["_id"])}, {"$pull": {"funcionarios_id": ObjectId(funcionario_id)}})
        await db.departamentos.update_one({"_id": ObjectId(funcionario_atualizado["departamento"]["_id"])}, {"$push": {"funcionarios_id": ObjectId(funcionario_id)}})
    funcionario_atualizado = await buscar_funcionario_por_id(funcionario_id)
    return funcionario_atualizado

@router.delete("/{funcionario_id}", response_model=FuncionarioDetalhadoDTO)
async def delete_funcionario(funcionario_id: str) -> FuncionarioDetalhadoDTO:
    funcionario = await buscar_funcionario_por_id(funcionario_id)
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionario não encontrado")
    await db_funcionarios.delete_one({"_id": ObjectId(funcionario_id)})
    for projeto in funcionario["projetos"]:
        await db.projetos.update_one({"_id": ObjectId(projeto["_id"])}, {"$pull": {"funcionarios_id": ObjectId(funcionario_id)}})
    await db.departamentos.update_one({"_id": ObjectId(funcionario["departamento"]["_id"])}, {"$pull": {"funcionarios_id": ObjectId(funcionario_id)}})
    return funcionario

@router.get("/funcionarios/count", response_model=int)
async def count_funcionarios() -> int:
    try:
        count = await db_funcionarios.count_documents({})
        return count
    except Exception as e:
        logger.error(f"Erro ao contar projetos: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao contar funcionarios")
