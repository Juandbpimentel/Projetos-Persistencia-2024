from fastapi import APIRouter, HTTPException
from typing import List

from fastapi.params import Depends
from motor.motor_asyncio import AsyncIOMotorCollection

from models.models import EmpresaSchema
from config import db

def get_database():
    return db.empresas

router = APIRouter(
    prefix="/empresas",
    tags=["empresas"],
    responses={
        404: {"description": "Não encontrado"},
        200: {"description": "Sucesso"},
        201: {"description": "Criado com sucesso"},
        500: {"description": "Erro interno"},
        400: {"description": "Requisição inválida"}},
)

@router.get("/", response_model=List[EmpresaSchema])
async def get_empresas(database: AsyncIOMotorCollection =Depends(get_database)) -> List[EmpresaSchema]:
    empresas = []
    async for empresa in database.find():
        empresas.append(EmpresaSchema(**empresa))
    return empresas

@router.post("/", response_model=EmpresaSchema)
async def create_empresa(empresa: EmpresaSchema, database: AsyncIOMotorCollection =Depends(get_database)) -> EmpresaSchema:
    empresa = await database.insert_one(empresa.model_dump())
    new_empresa = await database.find_one({"_id": empresa.inserted_id})
    return new_empresa