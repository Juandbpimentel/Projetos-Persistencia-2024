#TODO: FUNCIONARIO
#       - TODO: MODELO
#       - TODO: CONTROLLER
#       - TODO: CRUD_ROUTER
#TODO: FUNCIONARIOPROJETO
#TODO: CLIENTE
#TODO: DEPARTAMENTO
#TODO: PROJETO
#TODO: CLIENTE
#TODO: CONTRATO

from fastapi import FastAPI
from database import Base,engine
from models.funcionario_model import funcionario_routes

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(funcionario_routes)
