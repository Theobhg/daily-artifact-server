# Daily Artifact API

> **One day. One artifact.**

API do **Daily Artifact**: cada dia é representado por um único artefato
(frase, pensamento, foto, música ou link).

O frontend está em
[`daily-artifact-client`](https://github.com/Theobhg/daily-artifact-client).

**Stack:** Python 3.12+, FastAPI, SQLAlchemy e SQLite.

> O uso de FastAPI no lugar de Flask foi autorizado como exceção para este
> trabalho.

## Como executar

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API sobe em `http://127.0.0.1:8000`, e o banco SQLite é criado
automaticamente.

Para popular com dados de exemplo (opcional):

```bash
python seed.py
```

## Documentação

Swagger em <http://127.0.0.1:8000/docs>.

## Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/artifacts` | Cria um artefato |
| `GET` | `/artifacts` | Lista, com filtros `type`, `year`, `month` e `tag` |
| `GET` | `/artifacts/random` | Retorna um artefato aleatório |
| `GET` | `/artifacts/by-date/{date}` | Busca pela data (`YYYY-MM-DD`) |
| `GET` | `/artifacts/{id}` | Busca pelo id |
| `PUT` | `/artifacts/{id}` | Atualiza um artefato |
| `DELETE` | `/artifacts/{id}` | Remove um artefato |

## Regras de negócio

- Um artefato por data (`409` se repetir).
- Datas futuras não são aceitas (`400`).
- `text` e `quote` exigem `content`; `photo`, `link` e `music` exigem `url`
  (`422` se faltar).
- Tags são normalizadas para minúsculas e sem duplicatas.
