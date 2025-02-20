from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

from logger import logger

from models.empresa_models import EmpresaDetalhadaDTO, Empresa
from config import db

db_empresas = db.empresas
router = APIRouter(prefix="/empresas", tags=["empresas"], responses={
    404: {"description": "Não encontrado"},
    200: {"description": "Sucesso"},
    201: {"description": "Criado com sucesso"},
    500: {"description": "Erro interno"},
    400: {"description": "Requisição inválida"},
})

async def buscar_empresa_por_id(empresa_id: str) -> EmpresaDetalhadaDTO:
    empresa = await db_empresas.aggregate([
        {"$match": {"_id": ObjectId(empresa_id)}},
        {"$lookup": {
            "from": "departamentos",
            "localField": "departamentos_id",
            "foreignField": "_id",
            "as": "departamentos"
        }}
    ]).to_list()
    if empresa:
        empresa = empresa[0]
        converte_ids_para_string(empresa)
    return empresa

async def buscar_empresas_com_page_e_limit(page: int, limit: int) -> List[EmpresaDetalhadaDTO]:
    empresas = await db_empresas.aggregate([
        {"$lookup": {
            "from": "departamentos",
            "localField": "departamentos_id",
            "foreignField": "_id",
            "as": "departamentos"
        }},
        {"$sort": {"_id": 1}},
        {"$skip": max(0, page) * limit},
        {"$limit": limit}
    ]).to_list()
    for empresa in empresas:
        converte_ids_para_string(empresa)
    return empresas

def converte_ids_para_string(empresa: EmpresaDetalhadaDTO):
    empresa["_id"] = str(empresa["_id"])
    for departamento in empresa["departamentos"]:
        departamento["_id"] = str(departamento["_id"])
        departamento["empresa_id"] = str(departamento["empresa_id"])
        departamento["funcionarios_id"] = [str(funcionario_id) for funcionario_id in departamento["funcionarios_id"]]

async def trata_empresa_dict(empresa: Empresa):
    empresa_dict = empresa.model_dump(by_alias=True, exclude={"id"})
    empresa_dict["departamentos_id"] = [
        ObjectId(departamento["_id"]) for departamento in
        await db.departamentos.find({"_id": {"$in": [ObjectId(d) for d in empresa_dict["departamentos_id"]]}}).to_list()
    ]
    return empresa_dict

@router.get("/", response_model=List[EmpresaDetalhadaDTO])
async def get_empresas(page: int = 0, limit: int = 10) -> List[EmpresaDetalhadaDTO]:
    return await buscar_empresas_com_page_e_limit(page, limit)

@router.get("/{empresa_id}", response_model=EmpresaDetalhadaDTO)
async def get_empresa(empresa_id: str) -> EmpresaDetalhadaDTO:
    empresa = await buscar_empresa_por_id(empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa

@router.post("/", response_model=EmpresaDetalhadaDTO)
async def create_empresa(empresa: Empresa) -> EmpresaDetalhadaDTO:
    empresa_dict = await trata_empresa_dict(empresa)
    nova_empresa = await db_empresas.insert_one(empresa_dict)
    empresa_criada = await buscar_empresa_por_id(str(nova_empresa.inserted_id))
    if not empresa_criada:
        raise HTTPException(status_code=400, detail="Erro ao criar empresa")
    for departamento in empresa_criada["departamentos"]:
        if departamento["empresa_id"]:
            await db.empresas.update_one(
                {"_id": ObjectId(departamento["empresa_id"])},
                {"$pull": {"departamentos_id": ObjectId(departamento["_id"])}}
            )
        await db.departamentos.update_one({"_id": ObjectId(departamento["_id"])}, {"$set": {"empresa_id": ObjectId(empresa_criada["_id"])}})
        empresa_criada = await buscar_empresa_por_id(str(nova_empresa.inserted_id))
    return empresa_criada

@router.put("/{empresa_id}", response_model=EmpresaDetalhadaDTO)
async def update_empresa(empresa_id: str, empresa: Empresa) -> EmpresaDetalhadaDTO:
    empresa_dict = await trata_empresa_dict(empresa)
    empresa_antiga = await buscar_empresa_por_id(empresa_id)
    if not empresa_antiga:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    await db_empresas.update_one({"_id": ObjectId(empresa_id)}, {"$set": empresa_dict})
    empresa_atualizada = await buscar_empresa_por_id(empresa_id)
    if not empresa_atualizada:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    if empresa_antiga["departamentos"] != empresa_atualizada["departamentos"]:
        antigos = {dep["_id"]: dep for dep in empresa_antiga["departamentos"]}
        novos = {dep["_id"]: dep for dep in empresa_atualizada["departamentos"]}
        removidos = [antigos[_id] for _id in set(antigos) - set(novos)]
        adicionados = [novos[_id] for _id in set(novos) - set(antigos)]
        for departamento in removidos:
            await db.departamentos.delete_one({"_id": ObjectId(departamento["_id"])})
            for funcionario_id in departamento["funcionarios_id"]:
                await db.projetos.update_many({}, {"$pull": {"funcionarios_id": ObjectId(funcionario_id)}})
                await db.funcionarios.delete_one({"_id": ObjectId(funcionario_id)})
        for departamento in adicionados:
            if departamento["empresa_id"]:
                await db.empresas.update_one(
                    {"_id": ObjectId(departamento["empresa_id"])},
                    {"$pull": {"departamentos_id": ObjectId(departamento["_id"])}}
                )
            await db.departamentos.update_one({"_id": ObjectId(departamento["_id"])}, {"$set": {"empresa_id": ObjectId(empresa_id)}})
    empresa_atualizada = await buscar_empresa_por_id(empresa_id)
    return empresa_atualizada

@router.delete("/{empresa_id}", response_model=EmpresaDetalhadaDTO)
async def delete_empresa(empresa_id: str) -> EmpresaDetalhadaDTO:
    empresa = await buscar_empresa_por_id(empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    await db_empresas.delete_one({"_id": ObjectId(empresa_id)})
    for departamento in empresa["departamentos"]:
        await db.departamentos.delete_one({"_id": ObjectId(departamento["_id"])})
        for funcionario_id in departamento["funcionarios_id"]:
            await db.projetos.update_many({}, {"$pull": {"funcionarios_id": ObjectId(funcionario_id)}})
            await db.funcionarios.delete_one({"_id": ObjectId(funcionario_id)})
    return empresa

@router.get("/empresas/count", response_model=int)
async def count_empresas() -> int:
    try:
        count = await db_empresas.count_documents({})
        return count
    except Exception as e:
        logger.error(f"Erro ao contar projetos: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao contar")
