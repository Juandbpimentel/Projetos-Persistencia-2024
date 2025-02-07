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
import controllers.empresas_controller
from fastapi import FastAPI

from controllers import (
    departamentos_controller,
    empresas_controller,
    funcionarios_controller,
    clientes_controller,
    contratos_controller,
    projetos_controller
)
app = FastAPI()

app.include_router(departamentos_controller.router)
app.include_router(empresas_controller.router)
app.include_router(funcionarios_controller.router)
app.include_router(clientes_controller.router)
app.include_router(contratos_controller.router)
app.include_router(projetos_controller.router)

