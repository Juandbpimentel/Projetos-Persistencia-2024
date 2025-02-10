from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

from models import Projeto
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

@router.get("/", response_model=List[Projeto])
async def get_projetos(skip: int = 0, limit: int = 10) -> List[Projeto]:
    projetos = await db_projetos.find().skip(skip).limit(limit).to_list(length=limit)
    for projeto in projetos:
        projeto["_id"] = str(projeto["_id"])

    return projetos

@router.get("/{projeto_id}", response_model=Projeto)
async def get_projeto(projeto_id: str) -> Projeto:
    projeto = await db_projetos.find_one({"_id": ObjectId(projeto_id)})

    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    projeto["_id"] = str(projeto["_id"])
    return projeto


@router.post("/", response_model=Projeto)
async def create_projeto(projeto: Projeto) -> Projeto:
    projeto_dict = projeto.model_dump(by_alias=True, exclude={"id"})
    novo_projeto = await db_projetos.insert_one(projeto_dict)
    projeto_criado = await db_projetos.find_one({"_id": novo_projeto.inserted_id})

    if not projeto_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar projeto")

    await db.clientes.update_one(
        {"_id": ObjectId(projeto_criado["cliente_id"])},
        {"$push": {"projetos": str(projeto_criado["_id"])}}
    )

    funcionarios=[]
    for funcionario_id in projeto_criado["funcionarios"]:
        funcionario = await db.funcionarios.find_one({"_id": ObjectId(funcionario_id)})
        if not funcionario:
            raise HTTPException(status_code=404, detail=f"Funcionario {funcionario_id} não encontrado")
        funcionarios.append(funcionario)

    for funcionario in funcionarios:
        await db.funcionarios.update_one(
            {"_id": ObjectId(funcionario["_id"])},
            {"$push": {"projetos": str(projeto_criado["_id"])}}
        )


    projeto_criado["_id"] = str(projeto_criado["_id"])
    return projeto_criado


@router.put("/{projeto_id}", response_model=Projeto)
async def update_projeto(projeto_id: str, projeto: Projeto) -> Projeto:
    projeto_dict = projeto.model_dump(by_alias=True, exclude={"id"})
    projeto_antigo = await db_projetos.find_one({"_id": ObjectId(projeto_id)})

    projeto_atualizado = await db_projetos.find_one_and_update(
        {"_id": ObjectId(projeto_id)},
        {"$set": projeto_dict},
        return_document=True
    )

    if not projeto_atualizado:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    if projeto_atualizado["cliente_id"] != projeto_antigo["cliente_id"]:
        await db.clientes.update_one(
            {"_id": ObjectId(projeto_atualizado["cliente_id"])},
            {"$push": {"projetos": str(projeto_atualizado["_id"])}}
        )

        await db.clientes.update_one(
            {"_id": ObjectId(projeto_antigo["cliente_id"])},
            {"$pull": {"projetos": str(projeto_antigo["_id"])}}
        )

    if projeto_atualizado["contrato_id"] is None and projeto_antigo["contrato_id"] is not None:
        await db.contratos.delete_one({"_id": ObjectId(projeto_antigo["contrato_id"])})


    if projeto_atualizado["funcionarios"] != projeto_antigo["funcionarios"]:
        funcionarios_removidos = list(set(projeto_antigo["funcionarios"]) - set(projeto_atualizado["funcionarios"]))
        funcionarios_novos = list(set(projeto_atualizado["funcionarios"]) - set(projeto_antigo["funcionarios"]))
        for funcionario_id in funcionarios_removidos:
            await db.funcionarios.update_one(
                {"_id": ObjectId(funcionario_id)},
                {"$pull": {"projetos": str(projeto_atualizado["_id"])}
            }
        )
        for funcionario_id in funcionarios_novos:
            await db.funcionarios.update_one(
                {"_id": ObjectId(funcionario_id)},
                {"$push": {"projetos": str(projeto_atualizado["_id"])}
            }
        )


    projeto_atualizado["_id"] = str(projeto_atualizado["_id"])
    return projeto_atualizado

@router.delete("/{projeto_id}", response_model=dict[str, str | Projeto])
async def delete_projeto(projeto_id: str) -> dict[str, str | Projeto]:
    projeto = await db_projetos.find_one_and_delete({"_id": ObjectId(projeto_id)})

    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    await db.clientes.update_one(
        {"_id": ObjectId(projeto["cliente_id"])},
        {"$pull": {"projetos": str(projeto["_id"])}}
    )

    if projeto["contrato_id"] is not None:
        await db.contratos.delete_one({"_id": ObjectId(projeto["contrato_id"])})

    funcionarios = projeto["funcionarios"] if "funcionarios" in projeto else []

    for funcionario_id in funcionarios:
        await db.funcionarios.update_one(
            {"_id": ObjectId(funcionario_id)},
            {"$pull": {"projetos": str(projeto["_id"])}}
        )

    await db_projetos.delete_one({"_id": ObjectId(projeto_id)})
    projeto["_id"] = str(projeto["_id"])
    return {"message": "Projeto deletado com sucesso!", "projeto": projeto}