from fastapi import APIRouter, HTTPException
from typing import List

from fastapi.params import Depends
from motor.motor_asyncio import AsyncIOMotorCollection

from models.models import DepartamentoSchema
from config import db

def get_database():
    return db.empresas

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

@router.get("/", response_model=List[DepartamentoSchema])
async def get_departamentos(database: AsyncIOMotorCollection =Depends(get_database)):
    departamentos = []
    async for departamento in database.find():
        departamentos.append(DepartamentoSchema(**departamento))
    return departamentos

@router.post("/", response_model=DepartamentoSchema, dependencies=[db])
async def create_departamento(departamento: DepartamentoSchema, database: AsyncIOMotorCollection =Depends(get_database)) -> DepartamentoSchema:
    departamento = await database.insert_one(departamento.model_dump())
    new_departamento = await database.find_one({"_id": departamento.inserted_id})
    return new_departamento