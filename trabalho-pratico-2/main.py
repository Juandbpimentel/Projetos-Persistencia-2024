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

from controllers.funcionarios_controller import funcionarios_controller_router
from controllers.departamentos_controllers import departamentos_controller_router
from controllers.empresas_controller import empresas_controller_router
from controllers.cliente_controller import clientes_controller_router
from controllers.contrato_controller import contratos_controller_router
from controllers.projeto_controller import projetos_controller_router
app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(funcionarios_controller_router)
app.include_router(departamentos_controller_router)
app.include_router(empresas_controller_router)
app.include_router(clientes_controller_router)
app.include_router(contratos_controller_router)
app.include_router(projetos_controller_router)

