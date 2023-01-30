# Estrutura de arquivos

Esta é estrutura deste repositório, os arquivos com `*` são os que você vai precisar editar ao longo deste guia.

```console
$ tree --filesfirst -L 3 -I docs
.
├── docker-compose.yaml          # Container Orchestration
├── Dockerfile.dev               # Container Dev Image
├── MANIFEST.in                  # Arquivos do projeto
├── pyproject.toml               # Metadados do projeto
├── requirements-dev.txt         # Dev tools
├── requirements.in              # Dependencies
├── settings.toml                # Config por ambiente
├── setup.py                     # Setuptools bootstrap
├── test.sh                      # CI Pipeline
├── dundie                       # Main Package
│   ├── app.py*                  # FastAPI app
│   ├── auth.py*                 # Token JWT
│   ├── cli.py*                  # CLI app
│   ├── config.py                # Config management
│   ├── db.py*                   # Database connection
│   ├── default.toml             # Default settings
│   ├── __init__.py
│   ├── security.py*             # Password Hashing
│   ├── VERSION.txt              # SCM versioning
│   ├── models
│   │   ├── __init__.py*
│   │   ├── transaction.py*      # Models for transaction
│   │   └── user.py*             # Models for User
│   ├── routes
│   │    ├── auth.py*             # Token and Auth URLs
│   │    ├── __init__.py*
│   │    ├── transaction.py*      # Transaction URLs
│   │    └── user.py*             # User URLs
│   └── tasks
│       ├── __init__.py*
│       ├── transaction.py*      # Transaction Taks
│       └── user.py*             # User Tasks
├── postgres
│   ├── create-databases.sh      # DB startup
│   └── Dockerfile               # DB image
└── tests
    ├── conftest.py*             # Pytest config
    ├── __init__.py
    └── test_api.py*             # API tests
```

```admonish info
Todos os arquivos acima já estão criados no repositório, você vai precisar apenas editar,
alguns arquivos como o `.secrets.toml` (para guardar dados sensiveis) você irá criar localmente
pois este arquivo não deverá ser comitado ao repositório.
```
