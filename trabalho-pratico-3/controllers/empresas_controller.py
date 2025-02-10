from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

from dtos.EmpresaDetalhadaDTO import EmpresaDetalhadaDTO
from models import Empresa, Departamento
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

@router.get("/", response_model=List[EmpresaDetalhadaDTO])
async def get_empresas(page: int = 0, limit: int = 10) -> List[EmpresaDetalhadaDTO]:
    empresas = db_empresas.aggregate([
        # {
        #     "$match": {"name": "John Doe"}
        # },
        {
            "$lookup": {
                "from": "departamentos",
                "localField": "departamentos",
                "foreignField": "_id",
                "as": "departamentos"
            }
        }
        , {"$sort": {" _id": 1}}
        , {"$skip": (0 if page < 0 else page) * limit}
        , {"$limit": limit}
    ])
    result = []
    async for empresa in empresas:
        empresa["_id"] = str(empresa["_id"])
        for departamento in empresa["departamentos"]:
            departamento["_id"] = str(departamento["_id"])

            if departamento["empresa_id"] is not None:
                departamento["empresa_id"] = str(departamento["empresa_id"])

            if departamento["funcionarios"] is not None:
                for i, funcionario_id in enumerate(departamento["funcionarios"]):
                    departamento["funcionarios"][i] = str(funcionario_id)

        result.append(empresa)
    return result


@router.get("/{empresa_id}", response_model=EmpresaDetalhadaDTO)
async def get_empresa(empresa_id: str) -> EmpresaDetalhadaDTO:
    empresa = await db_empresas.aggregate([
        {
            "$match": {"_id": ObjectId(empresa_id)}
        },
        {
            "$lookup": {
                "from": "departamentos",
                "localField": "departamentos",
                "foreignField": "_id",
                "as": "departamentos"
            }
        }
    ]).to_list()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    empresa = empresa[0]
    empresa["_id"] = str(empresa["_id"])

    if "departamentos" in empresa and isinstance(empresa["departamentos"], list):
        for departamento in empresa["departamentos"]:
            departamento["_id"] = str(departamento["_id"])

            if departamento["empresa_id"] is not None:
                departamento["empresa_id"] = str(departamento["empresa_id"])

            if departamento["funcionarios"] is not None:
                for i,funcionario_id in enumerate(departamento["funcionarios"]):
                    departamento["funcionarios"][i] = str(funcionario_id)

    return empresa


@router.post("/", response_model=EmpresaDetalhadaDTO)
async def create_empresa(empresa: Empresa) -> EmpresaDetalhadaDTO:
    empresa_dict = empresa.model_dump(by_alias=True, exclude={"id"})
    for i,departamento in enumerate(empresa_dict["departamentos"]):
        empresa_dict['departamentos'][i] = ObjectId(departamento)
    nova_empresa = await db_empresas.insert_one(empresa_dict)
    empresa_criada = await db_empresas.aggregate([{
        "$match": {"_id": nova_empresa.inserted_id}
    }, {
        "$lookup": {
            "from": "departamentos",
            "localField": "departamentos",
            "foreignField": "_id",
            "as": "departamentos"
        }
    }]).to_list()

    empresa_criada = empresa_criada[0]
    if not empresa_criada:
        raise HTTPException(status_code=400, detail="Erro ao criar empresa")

    for departamento in empresa_criada["departamentos"]:
        departamento["_id"] = str(departamento["_id"])
        if not departamento:
            raise HTTPException(status_code=404, detail=f"Departamento {departamento["_id"]} não encontrado")
        if departamento["empresa_id"] is not None:
            departamento["empresa_id"] = str(departamento["empresa_id"])
        if departamento["funcionarios"] is not None:
            for i, funcionario_id in enumerate(departamento["funcionarios"]):
                departamento["funcionarios"][i] = str(funcionario_id)
            await db.empresas.update_one(
                {"_id": ObjectId(departamento["empresa_id"])},
                {"$pull": {"departamentos": ObjectId(departamento["_id"])}}
            )

            await db.departamentos.update_one(
                {"_id": ObjectId(departamento["_id"])},
                {"$set": {"empresa_id": ObjectId(empresa_criada["_id"])}}
            )


    empresa_criada["_id"] = str(empresa_criada["_id"])
    return empresa_criada


@router.put("/{empresa_id}", response_model=EmpresaDetalhadaDTO)
async def update_empresa(empresa_id: str, empresa: Empresa) -> EmpresaDetalhadaDTO:
    empresa_dict = empresa.model_dump(by_alias=True, exclude={"id"})
    for i,departamento in enumerate(empresa_dict["departamentos"]):
        empresa_dict['departamentos'][i] = ObjectId(departamento)

    empresa_antiga = await db_empresas.aggregate([
        {
            "$match": {"_id": ObjectId(empresa_id)}
        },
        {
            "$lookup": {
                "from": "departamentos",
                "localField": "departamentos",
                "foreignField": "_id",
                "as": "departamentos"
            }
        }
    ]).to_list()
    empresa_antiga = empresa_antiga[0]
    if not empresa_antiga:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    await db_empresas.update_one(
        {"_id": ObjectId(empresa_id)},
        {"$set": empresa_dict}
    )

    empresa_atualizada = await db_empresas.aggregate([
        {
            "$match": {"_id": ObjectId(empresa_id)}
        },
        {
            "$lookup": {
                "from": "departamentos",
                "localField": "departamentos",
                "foreignField": "_id",
                "as": "departamentos"
            }
        }
    ]).to_list()
    empresa_atualizada = empresa_atualizada[0]

    if not empresa_atualizada:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    if empresa_antiga["departamentos"] != empresa_dict["departamentos"]:
        departamentos_antigos = {departamento["_id"]: departamento for departamento in empresa_antiga["departamentos"]}
        departamentos_novos = {departamento["_id"]: departamento for departamento in empresa_atualizada["departamentos"]}

        departamentos_removidos = [departamentos_antigos[_id] for _id in set(departamentos_antigos) - set(departamentos_novos)]
        departamentos_adicionados = [departamentos_novos[_id] for _id in set(departamentos_novos) - set(departamentos_antigos)]

        for departamento in departamentos_removidos:
            await db.departamentos.delete_one({"_id": ObjectId(departamento["_id"])})
            for funcionario_id in departamento["funcionarios"]:
                await db.projetos.update_many(
                    {},
                    {"$pull": {"funcionarios": ObjectId(funcionario_id)}}
                )
                await db.funcionarios.delete_one({"_id": ObjectId(funcionario_id)})

        for departamento in departamentos_adicionados:
            print(departamento)
            if departamento["empresa_id"] is not None:
                await db.empresas.update_one(
                    {"_id": ObjectId(departamento["empresa_id"])},
                    {"$pull": {"departamentos": ObjectId(departamento["_id"])}}
                )
                await db.departamentos.update_one(
                    {"_id": ObjectId(departamento["_id"])},
                    {"$set": {"empresa_id": ObjectId(empresa_id)}}
                )

    for departamento in empresa_atualizada["departamentos"]:
        departamento["empresa_id"] = str(empresa_id)
        departamento["_id"] = str(departamento["_id"])
        for i, funcionario_id in enumerate(departamento["funcionarios"]):
            departamento["funcionarios"][i] = str(funcionario_id)


    empresa_atualizada["_id"] = str(empresa_atualizada["_id"])
    return empresa_atualizada


@router.delete("/{empresa_id}", response_model=EmpresaDetalhadaDTO)
async def delete_empresa(empresa_id: str) -> EmpresaDetalhadaDTO:
    empresa = await db_empresas.aggregate([
        {
            "$match": {"_id": ObjectId(empresa_id)}
        },
        {
            "$lookup": {
                "from": "departamentos",
                "localField": "departamentos",
                "foreignField": "_id",
                "as": "departamentos"
            }
        }
    ]).to_list()
    empresa = empresa[0]

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    empresa_deletada = await db_empresas.delete_one({"_id": ObjectId(empresa_id)})

    if not empresa_deletada:
        raise HTTPException(status_code=400, detail="Erro ao deletar empresa")

    empresa["_id"] = str(empresa["_id"])
    departamentos = empresa["departamentos"]
    for departamento in departamentos:
        db.departamentos.delete_one({"_id": ObjectId(departamento["_id"])})
        departamento["_id"] = str(departamento["_id"])
        departamento["empresa_id"] = str(departamento["empresa_id"])
        for i, funcionario_id in enumerate(departamento["funcionarios"]):
            departamento["funcionarios"][i] = str(funcionario_id)
            await db.projetos.update_many(
                {},
                {"$pull": {"funcionarios": ObjectId(funcionario_id)}}
            )
            await db.funcionarios.delete_one({"_id": ObjectId(funcionario_id)})

    return empresa