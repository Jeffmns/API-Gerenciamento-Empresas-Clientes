from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.errors import ERROR_RESPONSES
from api.models import Fornecedor
from api.schemas import FornecedorSchema

fornecedor_router = APIRouter(
    prefix="/fornecedores",
    tags=["Fornecedores"],
    responses=ERROR_RESPONSES,
)


@fornecedor_router.get("/")
async def listar_fornecedores(session: AsyncSession = Depends(get_session)):
    """Lista todos os fornecedores cadastrados, ordenados pelo identificador."""
    resultado = await session.execute(select(Fornecedor).order_by(Fornecedor.id))
    return resultado.scalars().all()


@fornecedor_router.get("/{fornecedor_id}")
async def buscar_fornecedor(
    fornecedor_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Busca um fornecedor pelo ID; retorna 404 quando ele não existe."""
    fornecedor = await session.get(Fornecedor, fornecedor_id)
    if fornecedor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado",
        )
    return fornecedor


@fornecedor_router.post("/", status_code=status.HTTP_201_CREATED)
async def criar_fornecedor(
    fornecedor_schema: FornecedorSchema,
    session: AsyncSession = Depends(get_session),
):
    """Cadastra um fornecedor e retorna o registro criado."""
    fornecedor = Fornecedor(**fornecedor_schema.model_dump())
    session.add(fornecedor)
    await session.commit()
    await session.refresh(fornecedor)
    return fornecedor


@fornecedor_router.put("/{fornecedor_id}")
async def atualizar_fornecedor(
    fornecedor_id: int,
    fornecedor_schema: FornecedorSchema,
    session: AsyncSession = Depends(get_session),
):
    """Atualiza os dados do fornecedor identificado pelo ID."""
    fornecedor = await session.get(Fornecedor, fornecedor_id)
    if fornecedor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado",
        )

    for campo, valor in fornecedor_schema.model_dump().items():
        setattr(fornecedor, campo, valor)

    await session.commit()
    await session.refresh(fornecedor)
    return fornecedor


@fornecedor_router.delete(
    "/{fornecedor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def excluir_fornecedor(
    fornecedor_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Exclui o fornecedor identificado pelo ID."""
    fornecedor = await session.get(Fornecedor, fornecedor_id)
    if fornecedor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado",
        )

    await session.delete(fornecedor)
    await session.commit()
