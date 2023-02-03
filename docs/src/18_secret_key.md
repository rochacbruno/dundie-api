# Configurando SECRET_KEY

Precisamos ser capazes de encryptar tokens e gerar hash para as senhas dos usuários 
e para isso temos alguns requisitos, primeiro precisamos de uma chave secreta em nosso 
arquivo de settings, esta chave será usada em nosso algoritmo de criptografia quando
começarmos a gerar tokens.

**EDITE** `dundie/default.toml` e adicione ao final

`dundie/default.toml`
```toml
[default.security]
# Set secret key in .secrets.toml
# SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 600
```

Como explicado no próprio comentário do arquivo `default.toml`, vamos colocar uma secret key separada 
no arquivo `.secrets.toml` na raiz do repositório, isso é recomendável pois podemos adicionar o 
arquivo `.secrets.toml` ao `.gitignore` para que ele não seja enviado para o repositório e desta 
maneira evitamos expor a chave secreta.

**CRIE** o arquivo `.secrets.toml` (na raiz do repositório)
```toml
[development]
dynaconf_merge = true

[development.security]
# openssl rand -hex 32
SECRET_KEY = "ONLYFORDEVELOPMENT"
```

```admonish note "NOTA"
Repare que estamos agora usando a seção `environment` e isso tem a ver
com o modo como o dynaconf gerencia os settings, esses valores serão
carregados apenas durante a execução em fase de desenvolvimento, em produção 
o dynaconf carrega apenas valores das variáveis de ambiente (recomendado) ou
de uma seção similar nomeada `[production]`.
```

```admonish tip "DICA"

Você pode gerar uma secret key mais segura se quiser usando:

    $ python -c "print(__import__('secrets').token_hex(32))"
    b9483cc8a0bad1c2fe31e6d9d6a36c4a96ac23859a264b69a0badb4b32c538f8

    # OU no Linux

    $ openssl rand -hex 32
    b9483cc8a0bad1c2fe31e6d9d6a36c4a96ac23859a264b69a0badb4b32c538f8
```

## Garantindo que os settings sempre tenham uma SECRET_KEY

Como a secret key será de extrema importância para o funcionamento da API precisamos garantir que esta chave de configuração
esteja sempre presente antes do sistema inicializar.

**EDITE** `dundie/config.py`

```python
# No topo faça o import de `Validator`
from dynaconf import Dynaconf, Validator  

# No final adicione a validação

settings.validators.register(  # pyright: ignore
    Validator("security.SECRET_KEY", must_exist=True, is_type_of=str),
)

settings.validators.validate()  # pyright: ignore
```

A partir de agora caso a **SECRET_KEY** não esteja disponível a aplicação não irá inicializar.


Agora sim podemos adicionar o código para geração de hash do password -->
