from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.models import Movimentacao_Estoque, Produto, produto_fornecedor
from api.schemas import MovimentacaoEstoqueSchema

movimentacao_estoque_router = APIRouter(
    prefix="/movimentacoes",
    tags=["Movimentações de Estoque"],
)


@movimentacao_estoque_router.get("/")
async def listar_movimentacoes(
    data_inicio: date | None = Query(default=None),
    data_fim: date | None = Query(default=None),
    id_fornecedor: int | None = Query(default=None, gt=0),
    session: AsyncSession = Depends(get_session),
):
    if data_inicio and data_fim and data_inicio > data_fim:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="data_inicio não pode ser posterior a data_fim",
        )

    consulta = select(Movimentacao_Estoque)
    if data_inicio:
        consulta = consulta.where(
            Movimentacao_Estoque.data_movimentacao >= data_inicio.isoformat()
        )
    if data_fim:
        consulta = consulta.where(
            Movimentacao_Estoque.data_movimentacao <= data_fim.isoformat()
        )
    if id_fornecedor is not None:
        consulta = (
            consulta.join(
                Produto,
                Movimentacao_Estoque.id_produto == Produto.id,
            )
            .join(
                produto_fornecedor,
                Produto.id == produto_fornecedor.c.id_produto,
            )
            .where(produto_fornecedor.c.id_fornecedor == id_fornecedor)
        )

    resultado = await session.execute(
        consulta.order_by(Movimentacao_Estoque.id).distinct()
    )
    return resultado.scalars().all()


@movimentacao_estoque_router.get("/{movimentacao_id}")
async def buscar_movimentacao(
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
async def criar_movimentacao(
    movimentacao_schema: MovimentacaoEstoqueSchema,
    session: AsyncSession = Depends(get_session),
):
    resultado = await session.execute(
        select(Produto)
        .where(Produto.id == movimentacao_schema.id_produto)
        .with_for_update()
    )
    produto = resultado.scalar_one_or_none()
    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )

    tipo_movimentacao = movimentacao_schema.tipo_movimentacao
    if tipo_movimentacao in ("saida", "saída"):
        if produto.quantidade_estoque < movimentacao_schema.quantidade:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Estoque insuficiente para realizar a saída",
            )
        produto.quantidade_estoque -= movimentacao_schema.quantidade
        tipo_movimentacao = "saida"
    else:
        produto.quantidade_estoque += movimentacao_schema.quantidade

    movimentacao = Movimentacao_Estoque(
        tipo_movimentacao=tipo_movimentacao,
        quantidade=movimentacao_schema.quantidade,
        data_movimentacao=movimentacao_schema.data_movimentacao.isoformat(),
        id_produto=movimentacao_schema.id_produto,
    )
    session.add(movimentacao)
    await session.commit()
    await session.refresh(movimentacao)
    return movimentacao
