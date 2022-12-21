#!/usr/bin/bash

# Arquivos na raiz
touch setup.py
touch {pyproject,settings,.secrets}.toml
touch {requirements,MANIFEST}.in
touch Dockerfile.dev docker-compose.yaml

# Imagem do banco de dados
mkdir postgres
touch postgres/{Dockerfile,create-databases.sh}

# Aplicação
mkdir -p dundie/{models,routes}
touch dundie/default.toml
touch dundie/{__init__,cli,app,auth,db,security,config}.py
touch dundie/models/{__init__,account,user}.py
touch dundie/routes/{__init__,auth,account,user}.py

# Testes
touch test.sh
mkdir tests
touch tests/{__init__,conftest,test_api}.py
