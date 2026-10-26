from fastapi import FastAPI

app = FastAPI()

from api.routers.produto_router import produto_router
from api.routers.categoria_router import categoria_router

app.include_router(produto_router)
app.include_router(categoria_router)