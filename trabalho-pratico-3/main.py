from traceback import print_stack, print_exception

import controllers.empresas_controller
from fastapi import FastAPI, HTTPException
from models import( funcionario_models, departamento_models, empresa_models, cliente_models, contrato_models, projeto_models)
funcionario_models.FuncionarioDetalhadoDTO.resolve_refs()
departamento_models.DepartamentoDetalhadoDTO.resolve_refs()
empresa_models.EmpresaDetalhadaDTO.resolve_refs()
cliente_models.ClienteDetalhadoDTO.resolve_refs()
contrato_models.ContratoDetalhadoDTO.resolve_refs()
projeto_models.ProjetoDetalhadoDTO.resolve_refs()

from controllers import (
    departamentos_controller,
    empresas_controller,
    funcionarios_controller,
    clientes_controller,
    contratos_controller,
    projetos_controller
)
app = FastAPI()

try:
    app.include_router(departamentos_controller.router)
    app.include_router(empresas_controller.router)
    app.include_router(funcionarios_controller.router)
    app.include_router(clientes_controller.router)
    app.include_router(contratos_controller.router)
    app.include_router(projetos_controller.router)
except  Exception as e:
    if object.__class__.__name__ == 'HTTPException':
        print_exception(e)
        raise e
    else:
        print_exception(e)
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


