from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

class ProdutoSchema(BaseModel):
    nome: str
    preco_custo: float
    preco_venda: float
    codigo: int
    quantidade_estoque: int
    estoque_minimo: int = Field(default=0, ge=0)
    id_categoria: int
    data_cadastro: str

    class Config:
        from_attributes= True

class CategoriaSchema(BaseModel):
    nome: str

    class Config:
        from_attributes= True

class FornecedorSchema(BaseModel):
    nome: str
    email: str
    cnpj: str
    telefone: str

    class Config:
        from_attributes= True

class MovimentacaoEstoqueSchema(BaseModel):
    tipo_movimentacao: Literal["entrada", "saida", "saída"]
    quantidade: int = Field(gt=0)
    data_movimentacao: date
    id_produto: int

    class Config:
        from_attributes= True