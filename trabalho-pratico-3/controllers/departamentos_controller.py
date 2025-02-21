from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

from logger import logger

from models.departamento_models import Departamento, DepartamentoDetalhadoDTO
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
        400: {"description": "Requisição inválida"},
    },
)


async def buscar_departamento_por_id(departamento_id: str) -> DepartamentoDetalhadoDTO:
    departamento = await db_departamentos.aggregate(
        [
            {"$match": {"_id": ObjectId(departamento_id)}},
            {
                "$lookup": {
                    "from": "funcionarios",
                    "localField": "funcionarios_id",
                    "foreignField": "_id",
                    "as": "funcionarios",
                }
            },
            {
                "$lookup": {
                    "from": "empresas",
                    "localField": "empresa_id",
                    "foreignField": "_id",
                    "as": "empresa",
                }
            },
        ]
    ).to_list()
    if departamento:
        departamento = departamento[0]
        converte_ids_para_string(departamento)
    return departamento


async def buscar_departamentos_com_page_e_limit(
    page: int, limit: int
) -> List[DepartamentoDetalhadoDTO]:
    departamentos = await db_departamentos.aggregate(
        [
            {
                "$lookup": {
                    "from": "funcionarios",
                    "localField": "funcionarios_id",
                    "foreignField": "_id",
                    "as": "funcionarios",
                }
            },
            {
                "$lookup": {
                    "from": "empresas",
                    "localField": "empresa_id",
                    "foreignField": "_id",
                    "as": "empresa",
                }
            },
            {"$sort": {"_id": 1}},
            {"$skip": max(0, page) * limit},
            {"$limit": limit},
        ]
    ).to_list()
    for departamento in departamentos:
        converte_ids_para_string(departamento)
    return departamentos


def converte_ids_para_string(departamento: DepartamentoDetalhadoDTO):
    departamento["_id"] = str(departamento["_id"])
    if departamento["empresa"]:
        empresa = departamento["empresa"][0]
        empresa["_id"] = str(empresa["_id"])
        empresa["departamentos_id"] = [
            str(dep_id) for dep_id in empresa["departamentos_id"]
        ]
        departamento["empresa"] = empresa
    if departamento["funcionarios"]:
        for funcionario in departamento["funcionarios"]:
            funcionario["_id"] = str(funcionario["_id"])
            funcionario["departamento_id"] = str(funcionario["departamento_id"])
            funcionario["projetos_id"] = [
                str(projeto_id) for projeto_id in funcionario["projetos_id"]
            ]


async def trata_departamento_dict(departamento: Departamento):
    departamento_dict = departamento.model_dump(by_alias=True, exclude={"id"})
    departamento_dict["funcionarios_id"] = [
        ObjectId(funcionario)
        for funcionario in departamento_dict["funcionarios_id"]
        if await db.funcionarios.find_one({"_id": ObjectId(funcionario)})
    ]
    empresa = await db.empresas.find_one(
        {"_id": ObjectId(departamento_dict["empresa_id"])}
    )
    if not empresa:
        raise HTTPException(status_code=400, detail="Empresa não encontrada")
    departamento_dict["empresa_id"] = ObjectId(departamento_dict["empresa_id"])
    return departamento_dict


@router.get("/", response_model=List[DepartamentoDetalhadoDTO])
async def get_departamentos(
    page: int = 0, limit: int = 10
) -> List[DepartamentoDetalhadoDTO]:
    return await buscar_departamentos_com_page_e_limit(page, limit)


@router.get("/{departamento_id}", response_model=DepartamentoDetalhadoDTO)
async def get_departamento(departamento_id: str) -> DepartamentoDetalhadoDTO:
    if not ObjectId.is_valid(departamento_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    departamento = await buscar_departamento_por_id(departamento_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    return departamento


@router.post("/", response_model=DepartamentoDetalhadoDTO, status_code=201)
async def create_departamento(departamento: Departamento) -> DepartamentoDetalhadoDTO:
    departamento_dict = await trata_departamento_dict(departamento)
    novo_departamento = await db_departamentos.insert_one(departamento_dict)
    departamento_criado = await buscar_departamento_por_id(
        str(novo_departamento.inserted_id)
    )
    if not departamento_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar departamento")
    if departamento_criado["empresa"]:
        await db.empresas.update_one(
            {"_id": ObjectId(departamento_criado["empresa_id"])},
            {"$push": {"departamentos_id": ObjectId(departamento_criado["_id"])}},
        )
    if departamento_criado["funcionarios"]:
        for funcionario in departamento_criado["funcionarios"]:
            if funcionario["departamento_id"]:
                await db.departamentos.update_one(
                    {"_id": ObjectId(funcionario["departamento_id"])},
                    {"$pull": {"funcionarios_id": ObjectId(funcionario["_id"])}},
                )
            await db.funcionarios.update_one(
                {"_id": ObjectId(funcionario["_id"])},
                {"$set": {"departamento_id": ObjectId(departamento_criado["_id"])}},
            )
    departamento_criado = await buscar_departamento_por_id(
        str(novo_departamento.inserted_id)
    )
    return departamento_criado


@router.put("/{departamento_id}", response_model=DepartamentoDetalhadoDTO)
async def update_departamento(
    departamento_id: str, departamento: Departamento
) -> DepartamentoDetalhadoDTO:
    departamento_dict = await trata_departamento_dict(departamento)
    departamento_antigo = await buscar_departamento_por_id(departamento_id)
    await db_departamentos.update_one(
        {"_id": ObjectId(departamento_id)}, {"$set": departamento_dict}
    )
    departamento_atualizado = await buscar_departamento_por_id(departamento_id)
    if not departamento_atualizado:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    if departamento_antigo["funcionarios"] != departamento_atualizado["funcionarios"]:
        antigos = {func["_id"]: func for func in departamento_antigo["funcionarios"]}
        novos = {func["_id"]: func for func in departamento_atualizado["funcionarios"]}
        removidos = [antigos[_id] for _id in set(antigos) - set(novos)]
        adicionados = [novos[_id] for _id in set(novos) - set(antigos)]
        for funcionario in removidos:
            await db.funcionarios.delete_one({"_id": ObjectId(funcionario["_id"])})
            await db.projetos.update_many(
                {}, {"$pull": {"funcionarios_id": ObjectId(funcionario["_id"])}}
            )
        for funcionario in adicionados:
            if funcionario["departamento_id"]:
                await db.departamentos.update_one(
                    {"_id": ObjectId(funcionario["departamento_id"])},
                    {"$pull": {"funcionarios_id": ObjectId(funcionario["_id"])}},
                )
            await db.funcionarios.update_one(
                {"_id": ObjectId(funcionario["_id"])},
                {"$set": {"departamento_id": ObjectId(departamento_atualizado["_id"])}},
            )
    departamento_atualizado = await buscar_departamento_por_id(departamento_id)
    return departamento_atualizado


@router.delete("/{departamento_id}", response_model=DepartamentoDetalhadoDTO)
async def delete_departamento(departamento_id: str) -> DepartamentoDetalhadoDTO:
    departamento = await buscar_departamento_por_id(departamento_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    await db_departamentos.delete_one({"_id": ObjectId(departamento_id)})
    await db.empresas.update_one(
        {"_id": ObjectId(departamento["empresa_id"])},
        {"$pull": {"departamentos_id": ObjectId(departamento_id)}},
    )
    for funcionario in departamento["funcionarios"]:
        await db.projetos.update_many(
            {}, {"$pull": {"funcionarios_id": ObjectId(funcionario["_id"])}}
        )
        await db.funcionarios.delete_one({"_id": ObjectId(funcionario["_id"])})
    return departamento


@router.get("/utils/contar_departamentos", response_model=int)
async def count_departamentos() -> int:
    try:
        count = await db_departamentos.count_documents({})
        return count
    except Exception as e:
        logger.error(f"Erro ao contar projetos: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao contar projetos")


@router.get("/filtro/{nome}", response_model=List[DepartamentoDetalhadoDTO])
async def buscar_departamentos_por_nome(nome: str) -> List[DepartamentoDetalhadoDTO]:
    departamentos = await db_departamentos.aggregate(
        [
            {"$match": {"nome": {"$regex": nome, "$options": "i"}}},
            {
                "$lookup": {
                    "from": "funcionarios",
                    "localField": "funcionarios_id",
                    "foreignField": "_id",
                    "as": "funcionarios",
                }
            },
            {
                "$lookup": {
                    "from": "empresas",
                    "localField": "empresa_id",
                    "foreignField": "_id",
                    "as": "empresa",
                }
            },
        ]
    ).to_list()
    print(f"Aaaaaaaaaaaaaaa {nome}")
    for departamento in departamentos:
        converte_ids_para_string(departamento)
    return departamentos


@router.get(
    "/filtro/buscar_por_empresa/{empresa_id}",
    response_model=List[DepartamentoDetalhadoDTO],
)
async def buscar_departamentos_por_empresa(
    empresa_id: str,
) -> List[DepartamentoDetalhadoDTO]:
    departamentos = await db_departamentos.aggregate(
        [
            {"$match": {"empresa_id": ObjectId(empresa_id)}},
            {
                "$lookup": {
                    "from": "funcionarios",
                    "localField": "funcionarios_id",
                    "foreignField": "_id",
                    "as": "funcionarios",
                }
            },
            {
                "$lookup": {
                    "from": "empresas",
                    "localField": "empresa_id",
                    "foreignField": "_id",
                    "as": "empresa",
                }
            },
        ]
    ).to_list()
    for departamento in departamentos:
        converte_ids_para_string(departamento)
    return departamentos
