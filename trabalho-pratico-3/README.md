# Projeto 3 Persistência de Dados

## Como Executar o Projeto?

Para executar o projeto, siga os passos abaixo:
- Clone o repositório
```shell
    git clone https://github.com/Juandbpimentel/Projetos-Persistencia-2024.git
```
- Abra o projeto no PyCharm
- Instale as dependências do projeto executando o seguinte comando:
```shell
  pip install pymongo motor fastapi uvicorn pydantic python-dotenv
```
- Execute o arquivo `main.py` usando o seguinte comando: 
```shell
  python -m fastapi dev main:app --reload --port 8000
```
- Acesse o endereço `http://localhost:8000/docs` no seu navegador para acessar a documentação da API
- Pronto! Agora você pode testar a API