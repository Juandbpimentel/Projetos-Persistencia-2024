from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List, Any

from models.projeto_models import Projeto, ProjetoDetalhadoDTO
from config import db

db_projetos = db.projetos

router = APIRouter(
    prefix="/projetos",
    tags=["projetos"],
    responses={
        404: {"description": "Não encontrado"},
        200: {"description": "Sucesso"},
        201: {"description": "Criado com sucesso"},
        500: {"description": "Erro interno"},
        400: {"description": "Requisição inválida"}},
)

async def buscar_projeto_por_id(projeto_id: str) -> ProjetoDetalhadoDTO:
    projeto = await db_projetos.aggregate([
        {"$match": {"_id": ObjectId(projeto_id)}},
        {"$lookup": {
            "from": "clientes",
            "localField": "cliente_id",
            "foreignField": "_id",
            "as": "cliente"
        }},
        {"$lookup": {
            "from": "funcionarios",
            "localField": "funcionarios_id",
            "foreignField": "_id",
            "as": "funcionarios"
        }},
        {"$lookup": {
            "from": "contratos",
            "localField": "contrato_id",
            "foreignField": "_id",
            "as": "contrato"
        }}
    ]).to_list()
    print(projeto)
    if projeto:
        projeto = projeto[0]
        converte_ids_para_string(projeto)
    return projeto

async def buscar_projetos_com_page_e_limit(page: int, limit: int) -> List[ProjetoDetalhadoDTO]:
    projetos = await db_projetos.aggregate([
        {"$lookup": {
            "from": "clientes",
            "localField": "cliente_id",
            "foreignField": "_id",
            "as": "cliente"
        }},
        {"$lookup": {
            "from": "funcionarios",
            "localField": "funcionarios_id",
            "foreignField": "_id",
            "as": "funcionarios"
        }},
        {"$lookup": {
            "from": "contratos",
            "localField": "contrato_id",
            "foreignField": "_id",
            "as": "contrato"
        }},
        {"$sort": {"_id": 1}},
        {"$skip": max(0, page) * limit},
        {"$limit": limit}
    ]).to_list()
    print(projetos)
    for projeto in projetos:
        converte_ids_para_string(projeto)
    print(projetos)
    return projetos

def converte_ids_para_string(projeto: ProjetoDetalhadoDTO):
    projeto["_id"] = str(projeto["_id"])
    if projeto["cliente"] and len(projeto["cliente"]) > 0:
        print(projeto["cliente"])
        cliente = projeto["cliente"][0]
        cliente["_id"] = str(cliente["_id"])
        cliente["projetos_id"] = [str(pid) for pid in cliente["projetos_id"]]
        projeto["cliente"] = cliente
    else:
        projeto["cliente"] = None
    if projeto["funcionarios"]:
        for funcionario in projeto["funcionarios"]:
            funcionario["_id"] = str(funcionario["_id"])
            funcionario["projetos_id"] = [str(pid) for pid in funcionario["projetos_id"]]
            funcionario["departamento_id"] = str(funcionario["departamento_id"])
            projeto["funcionarios"] = funcionario
    if projeto["contrato"] and len(projeto["contrato"]) > 0:
        contrato = projeto["contrato"][0] if projeto["contrato"] else None
        if contrato:
            contrato["_id"] = str(contrato["_id"])
            contrato["projeto_id"] = str(contrato["projeto_id"])
            projeto["contrato"] = contrato
    else:
        projeto["contrato"] = None


async def trata_projetos_dict(projeto: Projeto) -> dict:
    projeto_dict = projeto.model_dump(by_alias=True, exclude={"id"})
    projeto_dict["funcionarios_id"] = [
        ObjectId(funcionario) for funcionario in projeto_dict["funcionarios_id"]
            if await db.funcionarios.find_one({"_id": ObjectId(funcionario)})
    ]
    projeto_dict["cliente_id"] = ObjectId(projeto_dict["cliente_id"])
    if not await db.clientes.find_one({"_id": projeto_dict["cliente_id"]}):
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    projeto_dict["contrato_id"] = ObjectId(projeto_dict["contrato_id"]) if projeto_dict["contrato_id"] else None
    if projeto_dict["contrato_id"] and not await db.contratos.find_one({"_id": projeto_dict["contrato_id"]}):
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return projeto_dict

@router.get("/", response_model=List[ProjetoDetalhadoDTO])
async def get_projetos(page: int = 0, limit: int = 10) -> List[ProjetoDetalhadoDTO]:
    return await buscar_projetos_com_page_e_limit(page, limit)

@router.get("/{projeto_id}", response_model=ProjetoDetalhadoDTO)
async def get_projeto(projeto_id: str) -> ProjetoDetalhadoDTO:
    projeto = await buscar_projeto_por_id(projeto_id)
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return projeto

@router.post("/", response_model=ProjetoDetalhadoDTO)
async def create_projeto(projeto: Projeto) -> ProjetoDetalhadoDTO:
    projeto_dict = await trata_projetos_dict(projeto)
    novo_projeto = await db_projetos.insert_one(projeto_dict)
    projeto_criado = await buscar_projeto_por_id(str(novo_projeto.inserted_id))

    if not projeto_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar projeto")

    await db.clientes.update_one(
        {"_id": ObjectId(projeto_criado["cliente_id"])},
        {"$push": {"projetos_id": ObjectId(projeto_criado["_id"])}}
    )
    for funcionario in projeto_criado["funcionarios"]:
        if not funcionario:
            raise HTTPException(status_code=404, detail=f"Funcionario {funcionario['_id']} não encontrado")
        await db.funcionarios.update_one(
            {"_id": ObjectId(funcionario["_id"])},
            {"$push": {"projetos_id": ObjectId(projeto_criado["_id"])}}
        )
    projeto_criado = await buscar_projeto_por_id(str(projeto_criado["_id"]))
    return projeto_criado

@router.put("/{projeto_id}", response_model=ProjetoDetalhadoDTO)
async def update_projeto(projeto_id: str, projeto: Projeto) -> ProjetoDetalhadoDTO:
    projeto_dict = await trata_projetos_dict(projeto)
    projeto_antigo = await buscar_projeto_por_id(projeto_id)
    await db_projetos.update_one(
        {"_id": ObjectId(projeto_id)},
        {"$set": projeto_dict}
    )
    projeto_atualizado = await buscar_projeto_por_id(projeto_id)
    if not projeto_atualizado:
        raise HTTPException(status_code=404, detail="Falha ao atualizar projeto")
    if projeto_atualizado["cliente"] != projeto_antigo["cliente"]:
        await db.clientes.update_one(
            {"_id": ObjectId(projeto_antigo["cliente"]["_id"])},
            {"$pull": {"projetos_id": ObjectId(projeto_antigo["_id"])}}
        )
        await db.clientes.update_one(
            {"_id": ObjectId(projeto_atualizado["cliente"]["_id"])},
            {"$push": {"projetos_id": ObjectId(projeto_atualizado["_id"])}}
        )

    if projeto_atualizado["contrato"] is None and projeto_antigo["contrato"] is not None:
            await db.contratos.delete_one({"_id": ObjectId(projeto_antigo["contrato"]["_id"])})

    if projeto_atualizado["funcionarios"] != projeto_antigo["funcionarios"]:
        antigos = {func["_id"]: func for func in projeto_antigo["funcionarios"]}
        novos = {func["_id"]: func for func in projeto_atualizado["funcionarios"]}
        removidos = [antigos[_id] for _id in set(antigos) - set(novos)]
        adicionados = [novos[_id] for _id in set(novos) - set(antigos)]
        for funcionario in removidos:
            await db.funcionarios.update_one(
                {"_id": ObjectId(funcionario["_id"])},
                {"$pull": {"projetos_id": ObjectId(projeto_atualizado["_id"])}}
            )
        for funcionario in adicionados:
            await db.funcionarios.update_one(
                {"_id": ObjectId(funcionario["_id"])},
                {"$push": {"projetos_id": ObjectId(projeto_atualizado["_id"])}}
            )
    projeto_atualizado = await buscar_projeto_por_id(projeto_id)
    return projeto_atualizado

@router.delete("/{projeto_id}", response_model=ProjetoDetalhadoDTO)
async def delete_projeto(projeto_id: str) -> ProjetoDetalhadoDTO:
    projeto = await buscar_projeto_por_id(projeto_id)
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    await db_projetos.delete_one({"_id": ObjectId(projeto_id)})

    await db.clientes.update_one(
        {"_id": ObjectId(projeto["cliente_id"])},
        {"$pull": {"projetos_id": ObjectId(projeto["_id"])}}
    )
    if projeto["contrato"] is not None:
        await db.contratos.delete_one({"_id": ObjectId(projeto["contrato"]["_id"])})
    for funcionario in projeto["funcionarios"]:
        await db.funcionarios.update_one(
            {"_id": ObjectId(funcionario["_id"])},
            {"$pull": {"projetos_id": ObjectId(projeto["_id"])}}
        )
    return projeto