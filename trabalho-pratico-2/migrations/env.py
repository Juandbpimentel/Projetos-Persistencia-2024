from logging.config import fileConfig

from database import Base
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Importar o modelo FuncionarioModel
from models.funcionario_model import FuncionarioModel
from models.cliente_model import ClienteModel
from models.projeto_model import ProjetoModel
from models.departamento_model import DepartamentoModel
from models.contrato_model import ContratoModel
from models.empresa_model import EmpresaModel

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()