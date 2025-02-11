from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List

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
        400: {"description": "Requisição inválida"}},
)


@router.get("/", response_model=List[DepartamentoDetalhadoDTO])
async def get_departamentos(skip: int = 0, limit: int = 10) -> List[DepartamentoDetalhadoDTO]:
    departamentos = await buscar_departamentos_com_page_e_limit(skip, limit)
    for departamento in departamentos:
        departamento["_id"] = str(departamento["_id"])
        print(departamento)
        if departamento["empresa"] is not None:
            departamento["empresa"]["_id"] = str(departamento["empresa"]["_id"])
            departamento["empresa"]["departamentos_id"] = [str(departamento_id) for departamento_id in
                                                        departamento["empresa"]["departamentos_id"]]

        if departamento["funcionarios"] is not None:
            for funcionario in departamento["funcionarios"]:
                funcionario["_id"] = str(funcionario["_id"])
                funcionario["departamento_id"] = str(funcionario["departamento_id"])

    return departamentos

@router.get("/{departamento_id}", response_model=DepartamentoDetalhadoDTO)
async def get_departamento(departamento_id: str) -> DepartamentoDetalhadoDTO:
    if departamento_id is None or not ObjectId.is_valid(departamento_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    departamento = await buscar_departamento_por_id(departamento_id)

    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    departamento["_id"] = str(departamento["_id"])
    if departamento["empresa"] is not None:
        departamento["empresa"]["_id"] = str(departamento["empresa"]["_id"])
        departamento["empresa"]["departamentos_id"] = [str(departamento_id) for departamento_id in departamento["empresa"]["departamentos_id"]]
    if departamento["funcionarios"] is not None:
        for funcionario in departamento["funcionarios"]:
            funcionario["_id"] = str(funcionario["_id"])
            funcionario["departamento_id"] = str(funcionario["departamento_id"])
            funcionario["projetos_id"] = [str(projeto_id) for projeto_id in funcionario["projetos_id"]]

    return departamento


@router.post("/", response_model=DepartamentoDetalhadoDTO, status_code=201)
async def create_departamento(departamento: Departamento) -> DepartamentoDetalhadoDTO:
    departamento_dict = departamento.model_dump(by_alias=True, exclude={"id"})
    for i,funcionario in enumerate(departamento_dict["funcionarios_id"]):
        funcionario = await db.departamentos.find_one({"_id": ObjectId(funcionario)})
        if not departamento:
            departamento_dict['funcionarios_id'].pop(i)
            continue
        departamento_dict['funcionarios_id'][i] = ObjectId(funcionario)
    empresa = await db.empresas.find_one({"_id": ObjectId(departamento_dict["empresa_id"])})
    if empresa is not None:
        departamento_dict["empresa_id"] = ObjectId(departamento_dict["empresa_id"])
    else:
        raise HTTPException(status_code=400, detail="Empresa não encontrada")

    novo_departamento = await db_departamentos.insert_one(departamento_dict)

    departamento_criado = await buscar_departamento_por_id(str(novo_departamento.inserted_id))
    if not departamento_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar departamento")

    departamento_criado["_id"] = str(departamento_criado["_id"])

    if departamento_criado["empresa"] is not None:
        departamento_criado["empresa"]["_id"] = str(empresa["_id"])
        departamento_criado["empresa"]["departamentos_id"] = [str(departamento_id) for departamento_id in departamento_criado["empresa"]["departamentos_id"]]
        await db.empresas.update_one(
            {"_id": ObjectId(departamento_criado["empresa_id"])},
            {"$push": {"departamentos_id": ObjectId(departamento_criado["_id"])}}
        )


    if departamento_criado["funcionarios"] is not None:
        for funcionario in departamento_criado["funcionarios"]:
            funcionario["_id"] = str(funcionario["_id"])
            funcionario["projetos_id"] = [str(projeto_id) for projeto_id in funcionario["projetos_id"]]

            if funcionario["departamento_id"] is not None:
                await db_departamentos.update_one(
                    {"_id": ObjectId(funcionario["departamento_id"])},
                    {"$pull": {"funcionarios_id": ObjectId(funcionario["_id"])}}
                )

            await db.funcionarios.update_one(
                {"_id": ObjectId(funcionario["_id"])},
                {"$set": {"departamento_id": ObjectId(departamento_criado["_id"])}}
            )
            funcionario["departamento_id"] = str(departamento_criado["_id"])

    return departamento_criado

@router.put("/{departamento_id}", response_model=DepartamentoDetalhadoDTO)
async def update_departamento(departamento_id: str, departamento: Departamento) -> DepartamentoDetalhadoDTO:
    departamento_dict = departamento.model_dump(by_alias=True, exclude={"id"})
    for i,funcionario_id in enumerate(departamento_dict["funcionarios_id"]):
        funcionario = await db.funcionarios.find_one({"_id": ObjectId(funcionario_id)})
        if not funcionario:
            departamento_dict['funcionarios_id'].pop(i)
            continue
        departamento_dict['funcionarios_id'][i] = ObjectId(funcionario_id)
    empresa = await db.empresas.find_one({"_id": ObjectId(departamento_dict["empresa_id"])})
    if empresa is not None:
        departamento_dict["empresa_id"] = ObjectId(departamento_dict["empresa_id"])
    else:
        raise HTTPException(status_code=400, detail="Empresa não encontrada")

    departamento_antigo = await buscar_departamento_por_id(departamento_id)

    await db_departamentos.update_one(
        {"_id": ObjectId(departamento_id)},
        {"$set": departamento_dict}
    )

    departamento_atualizado = await buscar_departamento_por_id(departamento_id)
    if not departamento_atualizado:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")


    if departamento_antigo["funcionarios"] != departamento_atualizado["funcionarios"]:
        funcionarios_antigos = {funcionario["_id"]: funcionario for funcionario in departamento_antigo["funcionarios"]}
        funcionarios_novos = {funcionario["_id"]: funcionario for funcionario in departamento_atualizado["funcionarios"]}

        funcionarios_removidos = [funcionarios_antigos[_id] for _id in set(funcionarios_antigos) - set(funcionarios_novos)]
        funcionarios_adicionados = [funcionarios_novos[_id] for _id in set(funcionarios_novos) - set(funcionarios_antigos)]

        for funcionario in funcionarios_removidos:
            await db.funcionarios.delete_one({"_id": ObjectId(funcionario["_id"])})
            for projeto_id in funcionario["projetos_id"]:
                await db.projetos.update_many(
                    {},
                    {"$pull": {"funcionarios_id": ObjectId(funcionario["_id"])}}
                )

        for funcionario in funcionarios_adicionados:
            if funcionario["departamento_id"] is not None:
                await db_departamentos.update_one(
                    {"_id": ObjectId(funcionario["departamento_id"])},
                    {"$pull": {"funcionarios_id": ObjectId(funcionario["_id"])}}
                )
            await db.funcionarios.update_one(
                {"_id": ObjectId(funcionario["_id"])},
                {"$set": {"departamento_id": ObjectId(departamento_atualizado["_id"])}}
            )

    for funcionario in departamento_atualizado["funcionarios"]:
            funcionario["_id"] = str(funcionario["_id"])
            funcionario["projetos_id"] = [str(projeto_id) for projeto_id in funcionario["projetos_id"]]
            funcionario["departamento_id"] = str(departamento_atualizado["_id"])

    departamento_atualizado["empresa"]['_id'] = str(empresa['_id'])
    departamento_atualizado["empresa"]["departamentos_id"] = [str(departamento_id) for departamento_id in departamento_atualizado["empresa"]["departamentos_id"]]
    departamento_atualizado["_id"] = str(departamento_atualizado["_id"])
    return departamento_atualizado

@router.delete("/{departamento_id}", response_model=DepartamentoDetalhadoDTO)
async def delete_departamento(departamento_id: str) -> DepartamentoDetalhadoDTO:
    departamento = await buscar_departamento_por_id(departamento_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    resultado_delecao = await db_departamentos.delete_one({"_id": ObjectId(departamento_id)})
    if not resultado_delecao:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    await db.empresas.update_one(
        {"_id": ObjectId(departamento["empresa_id"])},
        {"$pull": {"departamentos": departamento_id}}
    )


    for funcionario in departamento["funcionarios"]:
        await db.projetos.update_many(
            {},
            {"$pull": {"funcionarios": funcionario["_id"]}}
        )
        await db.funcionarios.delete_one({"_id": funcionario["_id"]})
        funcionario["_id"] = str(funcionario["_id"])
        funcionario["departamento_id"] = str(funcionario["departamento_id"])
        funcionario["projetos_id"] = [str(projeto_id) for projeto_id in funcionario["projetos_id"]]

    departamento["_id"] = str(departamento["_id"])
    departamento["empresa"]["_id"] = str(departamento["empresa"]["_id"])
    for i, departamento_id in enumerate(departamento["empresa"]["departamentos_id"]):
        departamento["empresa"]["departamentos_id"][i] = str(departamento_id)

    return departamento


async def buscar_departamento_por_id(departamento_id: str) -> DepartamentoDetalhadoDTO:
    departamento = await db_departamentos.aggregate([
        {
            "$match": {"_id": ObjectId(departamento_id)}
        },
        {
            "$lookup": {
                "from": "funcionarios",
                "localField": "funcionarios_id",
                "foreignField": "_id",
                "as": "funcionarios"
            }
        }, {
            "$lookup": {
                "from": "empresas",
                "localField": "empresa_id",
                "foreignField": "_id",
                "as": "empresa"
            }
        }
    ]).to_list()
    departamento = departamento[0] if departamento else None
    departamento["empresa"] = departamento["empresa"][0] if departamento["empresa"] else None
    return departamento

async def buscar_departamentos_com_page_e_limit(page: int, limit:int) -> List[DepartamentoDetalhadoDTO]:
    departamentos = await db_departamentos.aggregate([
        {
            "$lookup": {
                "from": "funcionarios",
                "localField": "funcionarios_id",
                "foreignField": "_id",
                "as": "funcionarios"
            }
        },{
            "$lookup": {
                "from": "empresas",
                "localField": "empresa_id",
                "foreignField": "_id",
                "as": "empresa"
            }
        }, {"$sort": {" _id": 1}}
        , {"$skip": (0 if page < 0 else page) * limit}
        , {"$limit": limit}
    ]).to_list()
    for departamento in departamentos:
        departamento["empresa"] = departamento["empresa"][0]
        departamento["funcionarios"] = departamento["funcionarios"] if departamento["funcionarios"] else []
    return departamentos if departamentos else []
