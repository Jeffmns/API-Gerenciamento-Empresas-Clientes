from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.errors import ERROR_RESPONSES
from api.models import Produto
from api.schemas import ProdutoSchema

produto_router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"],
    responses=ERROR_RESPONSES,
)


@produto_router.get("/")
async def listar_produtos(session: AsyncSession = Depends(get_session)):
    """Lista todos os produtos cadastrados, ordenados pelo identificador."""
    resultado = await session.execute(select(Produto).order_by(Produto.id))
    return resultado.scalars().all()


@produto_router.get("/estoque-minimo")
async def listar_produtos_estoque_minimo(
    session: AsyncSession = Depends(get_session),
):
    """Lista produtos cujo estoque está igual ou abaixo do limite mínimo."""
    resultado = await session.execute(
        select(Produto)
        .where(Produto.quantidade_estoque <= Produto.estoque_minimo)
        .order_by(Produto.id)
    )
    return resultado.scalars().all()


@produto_router.get("/{produto_id}")
async def buscar_produto(
    produto_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Busca um produto pelo ID; retorna 404 quando ele não existe."""
    produto = await session.get(Produto, produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@produto_router.post("/", status_code=status.HTTP_201_CREATED)
async def criar_produto(
    produto_schema: ProdutoSchema,
    session: AsyncSession = Depends(get_session),
):
    """Cadastra um produto; estoque_minimo assume 0 se não for informado."""
    produto = Produto(**produto_schema.model_dump())
    session.add(produto)
    await session.commit()
    await session.refresh(produto)
    return produto


@produto_router.put("/{produto_id}")
async def atualizar_produto(
    produto_id: int,
    produto_schema: ProdutoSchema,
    session: AsyncSession = Depends(get_session),
):
    """Substitui os dados do produto identificado pelo ID."""
    produto = await session.get(Produto, produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    for campo, valor in produto_schema.model_dump().items():
        setattr(produto, campo, valor)

    await session.commit()
    await session.refresh(produto)
    return produto


@produto_router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def excluir_produto(
    produto_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Exclui um produto; retorna 409 se houver movimentações vinculadas."""
    produto = await session.get(Produto, produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    await session.delete(produto)
    try:
        await session.commit()
    except IntegrityError as erro:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir um produto com movimentações de estoque",
        ) from erro