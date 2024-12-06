from typing import List, Dict
import json
import pandas as pd
from http import HTTPStatus
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os


app = FastAPI()
CSV_FILE = "personagens.csv"


# Modelo de dados para o personagem
class Personagem(BaseModel):
    id: str
    nome: str
    classe: str
    hp: int
    hpMax: int
    mp: int
    mpMax: int
    status: str


# TODO: Implementar médotos auxiliares para manipulação do CSV
def lerDadosCSV():
    pass


def lerPersonagemCSV(idPersonagem: str):
    pass


def inserirPersonagemNoCSV(personagem: Personagem):
    pass


def atualizarPersonagemNoCSV(idPersonagem: str, personagem: Personagem):
    pass


def deletarPersonagemDoCSV(idPersonagem: str):
    pass


# TODO: Implementar métodos específicos para filtrar os dados de personagens
# exemplo: def getPersonagensPorClasse(classe: str):
# exemplo: def getPErsonagemPorParametros(parametros: dict):


@app.get(
    "/",
    responses={
        201: {
            "description": "Criado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "quantidade": 0,
                        "status": "ok",
                        "mensagem": "",
                        "erro": {"status": False, "mensagem": ""},
                    }
                }
            },
        },
        400: {
            "description": "Requisição inválida",
            "content": {
                "application/json": {
                    "example": {
                        "quantidade": 0,
                        "status": "erro",
                        "mensagem": "Requisição inválida",
                        "erro": {"status": True, "mensagem": "Detalhes do erro"},
                    }
                }
            },
        },
    },
    response_model=Dict[str, int | str | Dict[str, bool | str]],
    status_code=HTTPStatus.CREATED,
    description="Endpoint de exemplo",
    summary="Exemplo",
)
async def exemplo_endpoint() -> Dict[str, int | str | Dict[str, bool | str]]:
    return {
        "quantidade": 0,
        "status": "ok",
        "mensagem": "",
        "erro": {"status": False, "mensagem": ""},
    }


@app.post(
    "/personagem/",
    response_model=Personagem,
    status_code=HTTPStatus.CREATED,
    description="Recebe um json para inserer um persoangem no csv",
    summary="Criar personagem",
)
def criarPersonagem(personagem: Personagem):
    pass


@app.get(
    "/personagens/",
    response_model=List[Personagem],
    description="Listar todos os personagens do csv",
    summary="Listar personagens",
)
def listarPersonagems() -> List[Personagem]:
    return lerDadosCSV()


@app.get(
    "/personagens/{personagem_id}",
    status_code=HTTPStatus.OK,
    response_model=Personagem,
    description="Utilizar o id do personagem para resgatar ele do csv",
    summary="Ler personagem",
)
def lerPersonagem(personagem_id: int) -> Personagem:
    pass


@app.put(
    "/personagens/{personagem_id}",
    response_model=Personagem,
    status_code=HTTPStatus.OK,
    description="Utilizar o id do personagem e um personagem no body para atualizar um personagem do csv",
    summary="Atualizar personagem",
)
def atualizarPersonagem(
    personagem_id: int, personagem_atualizado: Personagem
) -> Personagem:
    pass


@app.delete(
    "/personagens/{personagem_id}",
    status_code=HTTPStatus.OK,
    description="Utilizar o id do personagem para remover ele do csv",
    summary="Remover personagem",
)
def removerPersonagem(personagem_id: int) -> Personagem:
    pass


@app.get(
    "/personagens/count",
    status_code=HTTPStatus.OK,
    description="Retorna a quantidade de personagens",
    summary="Contar personagens",
)
def contarPersonagens() -> Dict[str, str | int | Dict]:
    resultado = {
        "quantidade": 0,
        "status": "ok",
        "mensagem": "",
        "erro": {"status": False, "mensagem": ""},
    }
    return resultado


@app.get(
    "/personagens/download",
    status_code=HTTPStatus.OK,
    description="Faz o download do csv",
    summary="Download CSV",
)
def downloadCSV() -> FileResponse:
    pass


@app.get(
    "/personagens/hash",
    status_code=HTTPStatus.OK,
    description="Retorna o hash do csv",
    summary="Hash CSV",
)
def hashCSV() -> Dict[str, str]:
    pass
