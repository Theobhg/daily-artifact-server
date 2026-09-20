# Daily Artifact API

> **One day. One artifact.**

API do **Daily Artifact**: uma aplicação onde cada dia é representado por um
único artefato — uma frase que marcou o dia, um pequeno pensamento, uma foto,
uma música ou um link interessante. Ao longo do ano, essa coleção vira uma
representação visual das próprias memórias.

Este repositório contém apenas o backend. O frontend vive em
[`daily-artifact-client`](https://github.com/Theobhg/daily-artifact-client).

---

## Tecnologias

| Tecnologia | Papel |
|---|---|
| Python 3.12+ | Linguagem |
| FastAPI | Framework web e geração automática do OpenAPI |
| Uvicorn | Servidor ASGI |
| SQLAlchemy 2 | ORM e construção das queries |
| SQLite | Banco de dados (arquivo local, sem instalação) |
| Pydantic v2 | Validação e serialização |
| pydantic-settings | Carregamento das configurações a partir do `.env` |

> **Nota acadêmica:** o uso de FastAPI no lugar de Flask foi autorizado
> como exceção para este trabalho.

---

## Pré-requisitos

- Python 3.12 ou superior
- `pip`

Nada além disso. O SQLite é um arquivo criado automaticamente na primeira
execução — não há banco para instalar nem migração para rodar.

---

## Configuração

### 1. Criar o arquivo `.env`

```bash
cp .env.example .env
```

No Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

O `.env` não é versionado; o `.env.example` é, e serve como documentação dos
valores esperados. Os padrões do `.env.example` já funcionam para
desenvolvimento local.

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

Ativar:

```bash
source .venv/bin/activate
```

No Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Executar

```bash
uvicorn app.main:app --reload
```

A API sobe em `http://127.0.0.1:8000`. Na primeira execução o arquivo
`daily_artifact.db` é criado automaticamente na raiz do projeto.

### 5. (Opcional) Popular com dados de exemplo

```bash
python seed.py
```

Cria cerca de 30 artefatos distribuídos ao longo do ano, úteis para ver o
calendário e a listagem com conteúdo. O script é idempotente: datas já
ocupadas são ignoradas, então pode ser executado mais de uma vez.

---

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `APP_NAME` | `Daily Artifact API` | Título exibido no Swagger e no OpenAPI. |
| `APP_VERSION` | `1.0.0` | Versão da API publicada no OpenAPI. |
| `DATABASE_URL` | `sqlite:///./daily_artifact.db` | String de conexão do SQLAlchemy. O arquivo é criado automaticamente. |
| `CORS_ORIGINS` | `*` | Origens permitidas pelo CORS, separadas por vírgula. |

Todas são carregadas pela classe `Settings` (`app/config.py`) via
pydantic-settings. Nenhum segredo real é versionado.

### Por que `CORS_ORIGINS=*`

O frontend é aberto diretamente do sistema de arquivos (`file://`), e nesse
caso o navegador envia `Origin: null`. O wildcard cobre esse cenário. Por isso
também o CORS é configurado **sem credenciais** — habilitá-las invalidaria o
uso de `*`.

Além disso, a aplicação responde ao preflight com
`Access-Control-Allow-Private-Network: true`. Navegadores baseados em Chromium
aplicam a política de *Private Network Access*, que bloqueia chamadas de uma
página `file://` para `127.0.0.1` sem esse cabeçalho.

---

## Swagger / OpenAPI

Com a API rodando:

- **Swagger UI:** <http://127.0.0.1:8000/docs>
- **ReDoc:** <http://127.0.0.1:8000/redoc>
- **OpenAPI JSON:** <http://127.0.0.1:8000/openapi.json>

Abrir a raiz (<http://127.0.0.1:8000>) redireciona para o Swagger.

Todas as rotas estão documentadas com resumo, descrição, modelo de requisição,
modelo de resposta e os códigos de erro que podem retornar.

---

## Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/artifacts` | Registra o artefato de um dia. Retorna `201`. |
| `GET` | `/artifacts` | Lista os artefatos, do mais recente para o mais antigo. Aceita os filtros `type`, `year`, `month` e `tag`. |
| `GET` | `/artifacts/random` | Sorteia um artefato da coleção (funcionalidade *Me surpreenda*). |
| `GET` | `/artifacts/by-date/{artifact_date}` | Busca o artefato de uma data (`YYYY-MM-DD`). |
| `GET` | `/artifacts/{artifact_id}` | Busca um artefato pelo identificador. |
| `PUT` | `/artifacts/{artifact_id}` | Substitui por completo um artefato, incluindo suas tags. |
| `DELETE` | `/artifacts/{artifact_id}` | Remove um artefato. Retorna `204`. |

### Exemplos

Criar um artefato:

```bash
curl -X POST http://127.0.0.1:8000/artifacts \
  -H 'Content-Type: application/json' \
  -d '{
    "artifact_date": "2026-09-20",
    "type": "quote",
    "title": "Anotado no fim da tarde",
    "content": "O dia inteiro cabe em uma frase, se a frase for a certa.",
    "tags": ["memoria", "leitura"]
  }'
```

Filtrar a coleção:

```bash
curl "http://127.0.0.1:8000/artifacts?year=2026&type=photo"
curl "http://127.0.0.1:8000/artifacts?tag=memoria"
```

### Códigos de resposta

| Código | Quando acontece |
|---|---|
| `200` | Consulta ou atualização bem-sucedida. |
| `201` | Artefato criado. |
| `204` | Artefato excluído. |
| `400` | Data no futuro. |
| `404` | Artefato inexistente, ou `/random` com a coleção vazia. |
| `409` | Já existe um artefato na data informada. |
| `422` | Payload inválido para o tipo de artefato (ex.: `photo` sem `url`). |

---

## Regras de negócio

1. **Um artefato por dia.** É a regra central do produto. Ela é garantida em
   dois níveis: por uma *unique constraint* na coluna `artifact_date` e pela
   validação do `ArtifactService` antes de gravar. Uma data repetida responde
   `409 Conflict`.

2. **Datas futuras não são aceitas.** Hoje e qualquer dia passado são válidos;
   amanhã não. Um dia só pode ser registrado depois de ter acontecido. Retorna
   `400 Bad Request`.

3. **Campo obrigatório varia conforme o tipo:**

   | Tipo | Campo obrigatório | Observação |
   |---|---|---|
   | `text` | `content` | |
   | `quote` | `content` | |
   | `photo` | `url` | `content` funciona como legenda |
   | `link` | `url` | `content` funciona como comentário |
   | `music` | `url` | `content` funciona como comentário |

   `title` é sempre opcional. A violação retorna `422`.

4. **Tags.** Chegam à API como lista de strings (`["viagem", "família"]`).
   Antes de gravar são normalizadas: espaços nas bordas são removidos, strings
   vazias descartadas, nomes convertidos para minúsculas e duplicatas
   eliminadas. Tags já existentes são reaproveitadas em vez de recriadas —
   daí o relacionamento N:N. A normalização em minúsculas é o que torna o
   controle de duplicidade naturalmente *case-insensitive*: `Viagem` e
   `viagem` são a mesma tag.

5. **Datas em formato ISO.** Entrada e saída sempre em `YYYY-MM-DD`.

6. **`PUT` substitui por completo.** Campos omitidos no corpo voltam a ficar
   vazios. As regras de data futura e de data única continuam valendo, mas
   manter o artefato na própria data não gera conflito.

---

## Estrutura do projeto

```
server/
├── app/
│   ├── main.py                       # App FastAPI, CORS, handlers, startup
│   ├── config.py                     # Settings (pydantic-settings)
│   ├── database.py                   # Engine, sessão, Base, init_db
│   ├── exceptions.py                 # Exceções de domínio
│   ├── models/
│   │   ├── artifact.py               # Artifact + enum ArtifactType
│   │   └── tag.py                    # Tag + tabela associativa artifact_tags
│   ├── schemas/
│   │   └── artifact.py               # Create / Update / Response
│   ├── repositories/
│   │   ├── artifact_repository.py    # Queries de artefatos
│   │   └── tag_repository.py         # Reaproveitamento de tags
│   ├── services/
│   │   └── artifact_service.py       # Regras de negócio
│   └── routers/
│       └── artifacts.py              # Rotas HTTP
├── seed.py                           # Dados de exemplo (opcional)
├── requirements.txt
├── .env.example
└── README.md
```

### Arquitetura

```
Router  →  Service  →  Repository  →  SQLAlchemy / SQLite
```

- **Router** cuida de HTTP: parâmetros, status codes, schemas e documentação.
- **Service** concentra as regras de negócio e coordena as operações.
- **Repository** traduz intenções em queries, sem conhecer regra de negócio.

A divisão de validação segue essa mesma linha, evitando checagens duplicadas:
o **Pydantic** cuida da forma dos dados e da exigência por tipo (`422`), e o
**Service** cuida das regras do domínio — data futura (`400`) e data já
ocupada (`409`).

As exceções de domínio (`app/exceptions.py`) são traduzidas para respostas
HTTP por um único *exception handler* registrado em `main.py`. Isso mantém o
service independente de HTTP e os routers enxutos.

### Modelo de dados

```
┌────────────────────┐        ┌────────────────┐        ┌──────────┐
│     artifacts      │        │ artifact_tags  │        │   tags   │
├────────────────────┤        ├────────────────┤        ├──────────┤
│ id            PK   │───┐    │ artifact_id FK │    ┌───│ id    PK │
│ artifact_date UQ   │   └───>│ tag_id      FK │<───┘   │ name  UQ │
│ type               │        └────────────────┘        └──────────┘
│ title              │
│ content            │              N : N
│ url                │
│ created_at         │
│ updated_at         │
└────────────────────┘
```

O carregamento das tags usa a estratégia `selectin`, que evita o problema de
N+1 consultas ao listar artefatos.
