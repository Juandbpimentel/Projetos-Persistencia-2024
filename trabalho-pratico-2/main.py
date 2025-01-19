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
from models.crud_router_models import funcionarios_routes,clientes_routes,departamentos_routes,projetos_routes,contratos_routes,empresas_routes

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(funcionarios_routes)
app.include_router(clientes_routes)
app.include_router(departamentos_routes)
app.include_router(projetos_routes)
app.include_router(contratos_routes)
app.include_router(empresas_routes)

