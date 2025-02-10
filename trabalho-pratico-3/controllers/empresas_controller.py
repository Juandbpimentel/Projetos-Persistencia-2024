from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

from models import Empresa
from config import db

db_empresas = db.empresas

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

@router.get("/", response_model=List[Empresa])
async def get_empresas(skip: int = 0, limit: int = 10) -> List[Empresa]:
    empresas = await db_empresas.find().skip(skip).limit(limit).to_list(length=limit)
    for empresa in empresas:
        empresa["_id"] = str(empresa["_id"])
        if "departamentos" in empresa and isinstance(empresa["departamentos"], list):
            empresa["departamentos"] = [str(departamento_id) if isinstance(departamento_id, ObjectId) else departamento_id for departamento_id in empresa["departamentos"]]

    return empresas


@router.get("/{empresa_id}", response_model=Empresa)
async def get_empresa(empresa_id: str) -> Empresa:
    empresa = await db_empresas.find_one({"_id": ObjectId(empresa_id)})

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    empresa["_id"] = str(empresa["_id"])
    if "departamentos" in empresa and isinstance(empresa["departamentos"], list):
        empresa["departamentos"] = [str(departamento_id) if isinstance(departamento_id, ObjectId) else departamento_id for departamento_id in empresa["departamentos"]]

    return empresa


@router.post("/", response_model=Empresa)
async def create_empresa(empresa: Empresa) -> Empresa:
    empresa_dict = empresa.model_dump(by_alias=True, exclude={"id"})
    nova_empresa = await db_empresas.insert_one(empresa_dict)
    empresa_criada = await db_empresas.find_one({"_id": nova_empresa.inserted_id})

    if not empresa_criada:
        raise HTTPException(status_code=400, detail="Erro ao criar empresa")
    departamentos = []
    for departamento_id in empresa_criada["departamentos"]:
        departamento = await db.departamentos.find_one({"_id": ObjectId(departamento_id)})
        if not departamento:
            raise HTTPException(status_code=404, detail=f"Departamento {departamento_id} não encontrado")

        departamentos.append(departamento)

    for departamento in departamentos:
        if departamento["empresa_id"] is not None:
            await db.empresas.update_one(
                {"_id": ObjectId(departamento["empresa_id"])},
                {"$pull": {"departamentos": str(departamento["_id"])}}
            )

            await db.departamentos.update_one(
                {"_id": ObjectId(departamento["_id"])},
                {"$set": {"empresa_id": str(empresa_criada["_id"])}}
            )

    empresa_criada["_id"] = str(empresa_criada["_id"])
    return empresa_criada


@router.put("/{empresa_id}", response_model=Empresa)
async def update_empresa(empresa_id: str, empresa: Empresa) -> Empresa:
    empresa_dict = empresa.model_dump(by_alias=True, exclude={"id"})
    empresa_antiga = await db_empresas.find_one({"_id": ObjectId(empresa_id)})

    empresa_atualizada = await db_empresas.find_one_and_update(
        {"_id": ObjectId(empresa_id)},
        {"$set": empresa_dict},
        return_document=True
    )

    if not empresa_atualizada:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    if empresa_antiga["departamentos"] != empresa_dict["departamentos"]:
        departamentos_removidos = list(set(empresa_antiga["departamentos"]) - set(empresa_dict["departamentos"]))
        departamentos_adicionados = list(set(empresa_dict["departamentos"]) - set(empresa_antiga["departamentos"]))

        for departamento_id in departamentos_removidos:
            await db.departamentos.delete_one({"_id": ObjectId(departamento_id)})

            funcionarios = await db.funcionarios.find({"departamento_id": departamento_id}).to_list()
            for funcionario in funcionarios:
                await db.projetos.update_many(
                    {},
                    {"$pull": {"funcionarios": str(funcionario["_id"])}}
                )
                await db.funcionarios.delete_one({"_id": ObjectId(funcionario["_id"])})
        for departamento_id in departamentos_adicionados:
            departamento = await db.departamentos.find_one({"_id": ObjectId(departamento_id)})
            if not departamento:
                raise HTTPException(status_code=404, detail=f"Departamento {departamento_id} não encontrado")

            if departamento["empresa_id"] is not None:
                await db.empresas.update_one(
                    {"_id": ObjectId(departamento["empresa_id"])},
                    {"$pull": {"departamentos": str(departamento["_id"])}}
                )

            await db.departamentos.update_one(
                {"_id": ObjectId(departamento["_id"])},
                {"$set": {"empresa_id": str(empresa_atualizada["_id"])}}
            )
    empresa_atualizada["_id"] = str(empresa_atualizada["_id"])
    return empresa_atualizada


@router.delete("/{empresa_id}", response_model=Empresa)
async def delete_empresa(empresa_id: str) -> Empresa:
    empresa_deletada = await db_empresas.find_one_and_delete({"_id": ObjectId(empresa_id)})

    if not empresa_deletada:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    departamentos = empresa_deletada["departamentos"]

    funcionarios = []
    for departamento_id in departamentos:
        funcionarios.extend(
            await db.funcionarios.find(
                {"departamento_id": departamento_id}
            ).to_list()
        )
        db.departamentos.delete_one({"_id": ObjectId(departamento_id)})

    for funcionario in funcionarios:
        await db.projetos.update_many(
            {},
            {"$pull": {"funcionarios": str(funcionario["_id"])}}
        )
        await db.funcionarios.delete_one({"_id": ObjectId(funcionario["_id"])})

    empresa_deletada["_id"] = str(empresa_deletada["_id"])
    return empresa_deletada