# Configurações

Agora que temos pelo menos uma tabela mapeada para uma classe precisamos
estabelecer conexão com o banco de dados e para isso precisamos carregar
configurações

Verifique o arquivo `dundie/default.toml`
```toml
[default]

[default.db]
uri = ""
connect_args = {check_same_thread=false}
echo = false
```

Lembra que no `docker-compose.yaml` passamos as variáveis `DUNDIE_DB...`
aquelas variáveis vão sobrescrever os valores definidos no `default.toml`, por exemplo, `DUNDIE_DB__uri=...` irá preencher o valor `uri` na seção `[default.db]` do arquivo `default.toml`

Para carregar as configurações vamos usar o plugin `dynaconf` que já está instalado e só precisamos carregar criando uma instancia de `settings` que será o objeto usado durante toda a aplicação para acessar as configurações:

Veja em `dundie/config.py` como estamos inicializando o plugin de configurações.
```python
"""Settings module"""
import os

from dynaconf import Dynaconf

HERE = os.path.dirname(os.path.abspath(__file__))

settings = Dynaconf(
    envvar_prefix="dundie",
    preload=[os.path.join(HERE, "default.toml")],
    settings_files=["settings.toml", ".secrets.toml"],
    environments=["development", "production", "testing"],
    env_switcher="dundie_env",
    load_dotenv=False,
)
```

No arquivo acima estamos definindo que o objeto `settings` irá
carregar variáveis do arquivo `default.toml` e em seguida dos arquivos
`settings.toml` e `.secrets.toml` e que será possivel usar `DUNDIE_` como
prefixo nas variáveis de ambiente para sobrescrever os valores.

Agora já podemos acessar esses valores e criar a conexão com o banco de dados --> 
