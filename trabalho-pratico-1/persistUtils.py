import csv
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import yaml
from enum import Enum


class Personagem(BaseModel):
    id: Optional[int] = Field(default=None)
    nome: str
    classe: str
    hp: int
    hpMax: int
    mp: int
    mpMax: int
    status: str


class DirecoesDeOrdenacao(Enum):
    ASCENDENTE = "ASCENDENTE"
    DESCENTENDE = "DESCENDENTE"


def carregarYaml(nomeDoArquivo: str):
    print("Carregando dados de configuração")
    with open(nomeDoArquivo, "r") as file:
        dadosCarregados = yaml.safe_load(file)
        print("Dados de configuração carregados")
        return dadosCarregados


def salvarYaml(nomeDoArquivo: str, dados: Dict):
    print("Salvando dados de configuração")
    with open(nomeDoArquivo, "w") as file:
        yaml.safe_dump(dados, file)
        print("Dados de configuração salvos")


def configurarLog(configuracao):
    print("Configurando log")
    logging.basicConfig(
        level=configuracao["level"],
        filename=configuracao["file"],
        format=configuracao["format"],
    )
    print("Log configurado com sucesso!")
    logging.info(
        "____________________________________ Log iniciado ____________________________________"
    )


def configuracaoInicialServidor(arquivoDeConfiguracao: str) -> str:
    dadosDeConfiguracao = carregarYaml(arquivoDeConfiguracao)
    nomeArquivoCSV = dadosDeConfiguracao["data"]["file"]
    configurarLog(dadosDeConfiguracao["logging"])
    return nomeArquivoCSV


# TODO: Implementar médotos auxiliares para manipulação do CSV
def listarPersonagensDoCSV() -> List[Personagem]:
    personagens = []
    with open("personagens.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            personagens.append(Personagem(**row))
    return personagens


def lerPersonagemCSV(idPersonagem: int):
    with open("personagens.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(row)
            if int(int(row["id"])) == idPersonagem:
                return Personagem(**row)
    return None


def inserirPersonagemNoCSV(personagem: Personagem):
    with open("personagens.csv", mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=personagem.model_dump().keys())
        writer.writerow(personagem.model_dump())
    return personagem


def atualizarPersonagemNoCSV(idPersonagem: int, personagem: Personagem):
    linhas = []
    with open("personagens.csv", mode="r") as file:
        reader = csv.DictReader(file)
        achouPersonagem = False
        for row in reader:
            if int(row["id"]) == idPersonagem:
                row = personagem.model_dump()
                achouPersonagem = True
            linhas.append(row)
        if not achouPersonagem:
            return None

    with open("personagens.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=personagem.model_dump().keys())
        writer.writeheader()
        writer.writerows(linhas)
    return personagem


def deletarPersonagemDoCSV(idPersonagem: int):
    linhas = []
    personagemDeletado = None
    with open("personagens.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row["id"]) != idPersonagem:
                linhas.append(row)
            else:
                personagemDeletado = Personagem(**row)
    if len(linhas) == 0:
        return None
    with open("personagens.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=linhas[0].keys())
        writer.writeheader()
        writer.writerows(linhas)
    return personagemDeletado


# TODO: Implementar métodos específicos para filtrar os dados de personagens
def listarPersonagensDoCSVComFiltrosEOrdenacao(
    filtros: Dict[str, int | str] = {},
    ordenacao: str = "id",
    direcao: DirecoesDeOrdenacao = DirecoesDeOrdenacao.ASCENDENTE,
):
    personagens = listarPersonagensDoCSV()
    print(filtros)
    for chave, valor in filtros.items():
        personagens = [
            personagem
            for personagem in personagens
            if getattr(personagem, chave) == valor
        ]

    personagens.sort(
        key=lambda personagem: getattr(personagem, ordenacao),
        reverse=direcao == DirecoesDeOrdenacao.DESCENTENDE,
    )
    return personagens


def contarPersonagensDoCSV() -> int:
    return len(listarPersonagensDoCSV())


def obterProximoId(config_file: str) -> str:
    config = carregarYaml(config_file)
    proximo_id = config["data"]["proximoId"]
    return proximo_id


def incrementarProximoId(config_file: str):
    config = carregarYaml(config_file)
    config["data"]["proximoId"] += 1
    salvarYaml(config_file, config)
