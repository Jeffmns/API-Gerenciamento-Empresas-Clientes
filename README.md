# API de Gerenciamento de Empresas e Clientes

API REST desenvolvida com FastAPI, SQLAlchemy assíncrono e PostgreSQL para
gerenciamento de produtos, categorias, fornecedores e movimentações de estoque.

## Requisitos

- Python 3.10 ou superior
- Docker Desktop com Docker Compose

## Instalação e execução

No PowerShell, a partir da raiz do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker compose up -d db
alembic upgrade head
uvicorn main:app --reload
```

O servidor fica disponível em `http://127.0.0.1:8000`. A configuração local do
banco PostgreSQL está no `compose.yaml`; a aplicação e o Alembic devem apontar
para o mesmo banco configurado em `api/database.py` e `alembic.ini`.

## Documentação interativa

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Especificação OpenAPI: `http://127.0.0.1:8000/openapi.json`

## Endpoints

As rotas de coleção aceitam tanto a URL com barra final quanto o redirecionamento
automático sem ela.

| Método | Caminho | Descrição |
|---|---|---|
| `POST` | `/categorias/` | Criar categoria |
| `GET` | `/categorias/` | Listar categorias |
| `GET` | `/categorias/{categoria_id}` | Consultar categoria |
| `PUT` | `/categorias/{categoria_id}` | Atualizar categoria |
| `DELETE` | `/categorias/{categoria_id}` | Excluir categoria; retorna `409` se houver produtos vinculados |
| `POST` | `/fornecedores/` | Criar fornecedor |
| `GET` | `/fornecedores/` | Listar fornecedores |
| `GET` | `/fornecedores/{fornecedor_id}` | Consultar fornecedor |
| `PUT` | `/fornecedores/{fornecedor_id}` | Atualizar fornecedor |
| `DELETE` | `/fornecedores/{fornecedor_id}` | Excluir fornecedor |
| `POST` | `/produtos/` | Criar produto |
| `GET` | `/produtos/` | Listar produtos |
| `GET` | `/produtos/estoque-minimo` | Listar produtos com saldo menor ou igual ao limite mínimo |
| `GET` | `/produtos/{produto_id}` | Consultar produto |
| `PUT` | `/produtos/{produto_id}` | Atualizar produto |
| `DELETE` | `/produtos/{produto_id}` | Excluir produto; retorna `409` se houver movimentações |
| `POST` | `/movimentacoes/` | Registrar entrada ou saída imutável |
| `GET` | `/movimentacoes/` | Consultar histórico, com filtros opcionais |
| `GET` | `/movimentacoes/{movimentacao_id}` | Consultar movimentação |

### Filtros do histórico

`GET /movimentacoes/` aceita:

- `data_inicio` e `data_fim` no formato `AAAA-MM-DD`, inclusive.
- `id_fornecedor` para filtrar movimentações dos produtos associados ao fornecedor.

Os filtros podem ser combinados. Exemplo:

```text
GET /movimentacoes/?data_inicio=2026-01-01&data_fim=2026-01-31&id_fornecedor=3
```

Uma data inicial posterior à data final retorna `400`.

### Regras de estoque

- O produto tem um `estoque_minimo`, opcional no cadastro e com padrão `0`.
- A consulta de estoque mínimo inclui produtos com saldo igual ou inferior ao limite.
- Uma movimentação exige tipo `entrada` ou `saida`, quantidade positiva, data e produto existente.
- Entradas aumentam o saldo; saídas reduzem o saldo e são rejeitadas com `409` se não houver quantidade suficiente.
- O saldo e o registro de auditoria são persistidos na mesma transação.
- Movimentações não podem ser atualizadas nem excluídas pela API.

Exemplo de criação de movimentação:

```json
{
  "tipo_movimentacao": "entrada",
  "quantidade": 10,
  "data_movimentacao": "2026-01-15",
  "id_produto": 1
}
```

## Respostas de erro

Erros seguem um formato uniforme e não incluem detalhes internos do servidor:

```json
{
  "error": {
    "code": 404,
    "message": "Produto não encontrado"
  }
}
```

Erros de validação retornam `400` e incluem `details` com os campos inválidos.
Recursos inexistentes retornam `404`, conflitos de regras ou integridade retornam
`409`, e falhas inesperadas retornam `500` com mensagem genérica. Os detalhes
técnicos de falhas inesperadas são registrados no log do servidor, não enviados
ao cliente.
