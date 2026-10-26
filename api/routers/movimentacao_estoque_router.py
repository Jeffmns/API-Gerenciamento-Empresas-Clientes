from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.models import Movimentacao_Estoque, Produto
from api.schemas import MovimentacaoEstoqueSchema

movimentacao_estoque_router = APIRouter(
    prefix="/movimentacoes-estoque",
    tags=["Movimentações de Estoque"],
)


@movimentacao_estoque_router.get("/")
async def listar_movimentacoes_estoque(
    session: AsyncSession = Depends(get_session),
):
    resultado = await session.execute(
        select(Movimentacao_Estoque).order_by(Movimentacao_Estoque.id)
    )
    return resultado.scalars().all()


@movimentacao_estoque_router.get("/{movimentacao_id}")
async def buscar_movimentacao_estoque(
    movimentacao_id: int,
    session: AsyncSession = Depends(get_session),
):
    movimentacao = await session.get(Movimentacao_Estoque, movimentacao_id)
    if movimentacao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimentação de estoque não encontrada",
        )
    return movimentacao


@movimentacao_estoque_router.post("/", status_code=status.HTTP_201_CREATED)
async def criar_movimentacao_estoque(
    movimentacao_schema: MovimentacaoEstoqueSchema,
    session: AsyncSession = Depends(get_session),
):
    produto = await session.get(Produto, movimentacao_schema.id_produto)
    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )

    movimentacao = Movimentacao_Estoque(**movimentacao_schema.model_dump())
    session.add(movimentacao)
    await session.commit()
    await session.refresh(movimentacao)
    return movimentacao


@movimentacao_estoque_router.put("/{movimentacao_id}")
async def atualizar_movimentacao_estoque(
    movimentacao_id: int,
    movimentacao_schema: MovimentacaoEstoqueSchema,
    session: AsyncSession = Depends(get_session),
):
    movimentacao = await session.get(Movimentacao_Estoque, movimentacao_id)
    if movimentacao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimentação de estoque não encontrada",
        )

    produto = await session.get(Produto, movimentacao_schema.id_produto)
    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )

    for campo, valor in movimentacao_schema.model_dump().items():
        setattr(movimentacao, campo, valor)

    await session.commit()
    await session.refresh(movimentacao)
    return movimentacao


@movimentacao_estoque_router.delete(
    "/{movimentacao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def excluir_movimentacao_estoque(
    movimentacao_id: int,
    session: AsyncSession = Depends(get_session),
):
    movimentacao = await session.get(Movimentacao_Estoque, movimentacao_id)
    if movimentacao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimentação de estoque não encontrada",
        )

    await session.delete(movimentacao)
    await session.commit()
