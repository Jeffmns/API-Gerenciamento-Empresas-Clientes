from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.models import Categoria
from api.schemas import CategoriaSchema

categoria_router = APIRouter(prefix="/categorias", tags=["Categorias"])


@categoria_router.get("/")
async def listar_categorias(session: AsyncSession = Depends(get_session)):
    resultado = await session.execute(select(Categoria).order_by(Categoria.id))
    return resultado.scalars().all()


@categoria_router.get("/{categoria_id}")
async def buscar_categoria(
    categoria_id: int,
    session: AsyncSession = Depends(get_session),
):
    categoria = await session.get(Categoria, categoria_id)
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada",
        )
    return categoria


@categoria_router.post("/", status_code=status.HTTP_201_CREATED)
async def criar_categoria(
    categoria_schema: CategoriaSchema,
    session: AsyncSession = Depends(get_session),
):
    categoria = Categoria(nome=categoria_schema.nome)
    session.add(categoria)
    await session.commit()
    await session.refresh(categoria)
    return categoria


@categoria_router.put("/{categoria_id}")
async def atualizar_categoria(
    categoria_id: int,
    categoria_schema: CategoriaSchema,
    session: AsyncSession = Depends(get_session),
):
    categoria = await session.get(Categoria, categoria_id)
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada",
        )

    categoria.nome = categoria_schema.nome
    await session.commit()
    await session.refresh(categoria)
    return categoria


@categoria_router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def excluir_categoria(
    categoria_id: int,
    session: AsyncSession = Depends(get_session),
):
    categoria = await session.get(Categoria, categoria_id)
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada",
        )

    await session.delete(categoria)
    try:
        await session.commit()
    except IntegrityError as erro:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir uma categoria vinculada a produtos",
        ) from erro
