from typing import List, Dict, Optional
from http import HTTPStatus
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import logging
import persistUtils
from persistUtils import Personagem
import zipfile 
import os
import hashlib 

app = FastAPI()
CONFIG_FILE = "config.yaml"
CSV_FILE = persistUtils.configuracaoInicialServidor(CONFIG_FILE)


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
    logging.info("Endpoint de exemplo chamado")
    return {
        "quantidade": 0,
        "status": "ok",
        "mensagem": "",
        "erro": {"status": False, "mensagem": ""},
    }


@app.post(
    "/personagens",
    response_model=Personagem,
    status_code=HTTPStatus.CREATED,
    description="Recebe um json para inserer um persoangem no csv",
    summary="Criar personagem",
)
def criarPersonagem(personagem: Personagem):
    proximoId = persistUtils.obterProximoId(CONFIG_FILE)
    personagem.id = proximoId
    persistUtils.inserirPersonagemNoCSV(personagem)
    persistUtils.incrementarProximoId(CONFIG_FILE)
    return personagem


@app.get(
    "/personagens/listar",
    response_model=List[Personagem],
    description="Listar todos os personagens do csv utilizando filtros e ordenação",
    summary="Listar personagens com filtros e odrenação",
)
def listarPersonagensComFiltrosEOrdenacao(
    id: Optional[int] = None,
    nome: Optional[str] = None,
    classe: Optional[str] = None,
    hp: Optional[int] = None,
    hpMax: Optional[int] = None,
    mp: Optional[int] = None,
    mpMax: Optional[int] = None,
    status: Optional[str] = None,
    campoOrdenacao: Optional[str] = None,
    direcaoOrdenacao: Optional[persistUtils.DirecoesDeOrdenacao] = None,
) -> List[Personagem]:
    filtros = {
        k: v
        for k, v in locals().items()
        if k in ["id", "nome", "classe", "hp", "hpMax", "mp", "mpMax", "status"]
        and v is not None
    }

    request = {
        "filtros": filtros or {},
        "campoOrdenacao": campoOrdenacao or "id",
        "direcaoOrdenacao": direcaoOrdenacao
        or persistUtils.DirecoesDeOrdenacao.ASCENDENTE,
    }

    return persistUtils.listarPersonagensDoCSVComFiltrosEOrdenacao(
        request["filtros"], request["campoOrdenacao"], request["direcaoOrdenacao"]
    )


@app.get(
    "/personagens/details/{personagem_id}",
    status_code=HTTPStatus.OK,
    response_model=Personagem | Dict[str, int | str | Dict[str, int | str]],
    description="Utilizar o id do personagem para resgatar ele do csv",
    summary="Ler personagem",
)
def lerPersonagem(personagem_id: int) -> Personagem:
    try:
        personagem = persistUtils.lerPersonagemCSV(personagem_id)
        if personagem is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Personagem não encontrado",
            )
        return personagem
    except Exception as e:
        logging.error(f"Erro ao ler personagem de id {personagem_id}: {str(e.detail)}")
        if isinstance(e, HTTPException):
            return {
                "erro": {
                    "status": e.status_code,
                    "mensagem": str(e.detail),
                }
            }
        else:
            return {
                "erro": {
                    "status": HTTPStatus.INTERNAL_SERVER_ERROR,
                    "mensagem": "Erro interno do servidor, tente novamente",
                }
            }


@app.put(
    "/personagens/{personagem_id}",
    response_model=Personagem | Dict[str, int | str | Dict[str, int | str]],
    status_code=HTTPStatus.OK,
    description="Utilizar o id do personagem e um personagem no body para atualizar um personagem do csv",
    summary="Atualizar personagem",
)
def atualizarPersonagem(
    personagem_id: int, personagem_atualizado: Personagem
) -> Personagem:
    try:
        personagem = persistUtils.atualizarPersonagemNoCSV(
            personagem_id, personagem_atualizado
        )
        if personagem is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Personagem não encontrado",
            )
        return personagem
    except Exception as e:
        logging.error(f"Erro ao atualizar personagem de id {personagem_id}: {str(e)}")
        if isinstance(e, HTTPException):
            return {"erro": {"status": e.status_code, "mensagem": str(e.detail)}}
        else:
            return {
                "erro": {
                    "status": HTTPStatus.INTERNAL_SERVER_ERROR,
                    "mensagem": "Erro interno do servidor, tente novamente",
                }
            }


@app.delete(
    "/personagens/{personagem_id}",
    status_code=HTTPStatus.OK,
    response_model=Personagem | Dict[str, int | str | Dict[str, int | str]],
    description="Utilizar o id do personagem para remover ele do csv",
    summary="Remover personagem",
)
def removerPersonagem(
    personagem_id: int,
) -> Personagem:
    try:
        personagem = persistUtils.deletarPersonagemDoCSV(personagem_id)
        if personagem is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Personagem não encontrado",
            )
        return personagem
    except Exception as e:
        logging.error(f"Erro ao remover personagem de id {personagem_id}: {str(e)}")
        if isinstance(e, HTTPException):
            return {"erro": {"status": e.status_code, "mensagem": str(e.detail)}}
        else:
            return {
                "erro": {
                    "status": HTTPStatus.INTERNAL_SERVER_ERROR,
                    "mensagem": "Erro interno do servidor, tente novamente",
                }
            }


@app.get(
    "/personagens/count",
    status_code=HTTPStatus.OK,
    description="Retorna a quantidade de personagens",
    summary="Contar personagens",
)
def contarPersonagens() -> Dict[str, str | int | Dict]:
    resultado = persistUtils.contarPersonagensDoCSV()
    resultado = {"quantidade": resultado}
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


def compactarCSVParaZIP(caminho_csv: str, caminho_zip: str):
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(caminho_csv, os.path.basename(caminho_csv))


@app.get(
    "/personagens/download_zip",
    status_code=HTTPStatus.OK,
    description="Faz o download do csv compactado em um arquivo ZIP",
    summary="Download CSV ZIP",
)
def downloadCSVZIP() -> FileResponse:
    caminho_csv = CSV_FILE
    caminho_zip = "personagens.zip"
    
    # Adicionando logs
    logging.info(f"Compactando o arquivo CSV: {caminho_csv}")
    
    compactarCSVParaZIP(caminho_csv, caminho_zip)
    
    logging.info(f"Arquivo ZIP criado: {caminho_zip}")
    
    if os.path.exists(caminho_zip):
        logging.info(f"Arquivo ZIP encontrado: {caminho_zip}")
        return FileResponse(caminho_zip, media_type='application/zip', filename=caminho_zip)
    else:
        logging.error(f"Arquivo ZIP não encontrado: {caminho_zip}")
        raise HTTPException(status_code=404, detail="Arquivo ZIP não encontrado")


