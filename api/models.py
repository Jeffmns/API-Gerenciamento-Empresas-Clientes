from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

db = create_engine('postgresql+psycopg://app:local_dev_password@localhost:5432/empresas')
Base = declarative_base()

produto_fornecedor = Table(
    'produtos_fornecedores',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('id_produto', Integer, ForeignKey('produtos.id'), nullable=False),
    Column('id_fornecedor', Integer, ForeignKey('fornecedores.id'), nullable=False),
)

class Produto (Base):

    __tablename__ = 'produtos'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    preco_custo = Column(Float, nullable=False)
    preco_venda = Column(Float, nullable=False)
    codigo = Column(Integer, nullable=False)
    quantidade_estoque = Column(Integer, nullable=False)
    data_cadastro = Column(String(10), nullable=False)
    id_categoria = Column(Integer, ForeignKey('categorias.id'), nullable=False)
    fornecedores = relationship('Fornecedor', secondary=produto_fornecedor, back_populates='produtos')

    def __init__(self, nome, preco_custo, preco_venda, codigo, quantidade_estoque, data_cadastro, id_categoria):
        self.nome = nome
        self.preco_custo = preco_custo
        self.preco_venda = preco_venda
        self.codigo = codigo
        self.quantidade_estoque = quantidade_estoque
        self.data_cadastro = data_cadastro
        self.id_categoria = id_categoria

class Categoria (Base):

    __tablename__ = 'categorias'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    def __init__(self, nome):
        self.nome = nome

class Fornecedor (Base):

    __tablename__ = 'fornecedores'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    cnpj = Column(String(14), nullable=False)
    telefone = Column(String(15), nullable=False)
    produtos = relationship('Produto', secondary=produto_fornecedor, back_populates='fornecedores')

    def __init__(self, nome, email, cnpj, telefone):
        self.nome = nome
        self.email = email
        self.cnpj = cnpj
        self.telefone = telefone

class Movimentacao_Estoque (Base):

    __tablename__ = 'movimentacoes_estoques'

    id = Column(Integer, primary_key=True)
    tipo_movimentacao = Column(String(10), nullable=False)
    quantidade = Column(Integer, nullable=False)
    data_movimentacao = Column(String(10), nullable=False)
    id_produto = Column(Integer, ForeignKey('produtos.id'), nullable=False)

    def __init__(self, tipo_movimentacao, quantidade, data_movimentacao, id_produto):
        self.tipo_movimentacao = tipo_movimentacao
        self.quantidade = quantidade
        self.data_movimentacao = data_movimentacao
        self.id_produto = id_produto

