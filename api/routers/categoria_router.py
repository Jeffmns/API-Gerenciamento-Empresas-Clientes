from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas import CategoriaSchema
from api.models import Categoria
from api.database import get_session

categoria_router = APIRouter(prefix="/categorias", tags=["Categorias"])

@categoria_router.get("/")
async def listar_categorias(session: AsyncSession = Depends(get_session)):
    return {"message": "List of categories"}

@categoria_router.post("/")
async def criar_categoria(categoria_schema: CategoriaSchema, session: AsyncSession = Depends(get_session)):
    categoria = Categoria(
        nome=categoria_schema.nome
    )

    session.add(categoria)
    await session.commit()
    await session.refresh(categoria)

    return categoria