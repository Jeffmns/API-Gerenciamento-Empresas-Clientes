from pydantic import BaseModel

class ProdutoSchema(BaseModel):
    nome: str
    preco_custo: float
    preco_venda: float
    codigo: int
    quantidade_estoque: int
    id_categoria: int
    data_cadastro: str

    class Config:
        from_attributes= True

class CategoriaSchema(BaseModel):
    nome: str

    class Config:
        from_attributes= True