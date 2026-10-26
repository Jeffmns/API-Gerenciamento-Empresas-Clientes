from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from api.errors import register_exception_handlers

from api.routers.produto_router import produto_router
from api.routers.categoria_router import categoria_router
from api.routers.fornecedor_router import fornecedor_router
from api.routers.movimentacao_estoque_router import movimentacao_estoque_router

app = FastAPI(
    title="API de Gerenciamento de Empresas e Clientes",
    description=(
        "API REST para gerenciamento de produtos, categorias, fornecedores "
        "e movimentações imutáveis de estoque."
    ),
    version="1.0.0",
    openapi_tags=[
        {"name": "Produtos", "description": "Cadastro e consulta de produtos."},
        {"name": "Categorias", "description": "Cadastro e consulta de categorias."},
        {"name": "Fornecedores", "description": "Cadastro e consulta de fornecedores."},
        {
            "name": "Movimentações de Estoque",
            "description": (
                "Registro imutável de entradas e saídas, com atualização do saldo "
                "do produto e filtros por data e fornecedor."
            ),
        },
    ],
)

app.include_router(produto_router)
app.include_router(categoria_router)
app.include_router(fornecedor_router)
app.include_router(movimentacao_estoque_router)

register_exception_handlers(app)


def gerar_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    for caminho in schema["paths"].values():
        for operacao in caminho.values():
            respostas = operacao.get("responses")
            if respostas:
                respostas.pop("422", None)

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = gerar_openapi