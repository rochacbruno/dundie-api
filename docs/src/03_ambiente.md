# Ambiente de Desenvolvimento

Ambiente Dev é para fins de programação o conjunto de ferramentas, bibliotecas e variáveis que precisam estar disponíveis para desenvolver, testar e manter o projeto.

## Preparando o Ambiente

### Opção 1: Rodando no seu computador local 

Dentro da pasta `dundie-api` e crie um ambiente virtual.

```console
$ python -m venv .venv
```

E ative a virtualenv

No Linux/Mac ou Windows WSL
```console
$ source .venv/bin/activate
```

No Windows Power Shell
```console
$ .\venv\Scripts\activate.ps1
```

```admonish success
O ambiente virtual ativado fará com que seu terminal exiba `(.venv)` juntamente do prompt, você ainda pode digitar no terminal `which python` para confirmar se o ambiente está mesmo ativado, o output deverá ser `[...]/.venv/bin/python`
```

### Opção 2: Rodando online com o gitpod

> No gitpod.io não é preciso criar um abiente virtual, o ambiente já vem configurado isoladamente.

## Instalando as dependências

Com o ambiente pronto podemos agora instalar as dependências básicas do projeto que estão contidas no arquivo `requirements-dev.txt`.

Confirme que o arquivo já contém a lista de todas as ferramentas que usaremos para fins de desenvolvimento e debugging, confira o conteúdo do arquivo abrindo em seu editor ou através do comando `cat` no terminal Linux.

```console 
$ cat requirements-dev.txt

ipython         # terminal
ipdb            # debugger
sdb             # debugger remoto
pip-tools       # lock de dependencias
pytest          # execução de testes
pytest-order    # ordenação de testes
httpx==0.26.0   # requests async para testes
black           # auto formatação
flake8          # linter
```

Instalaremos as dependencias com a ferramenta `pip` que é um módulo do Python.

1. Atualizamos o pip
    ```console
    $ python -m pip install --upgrade pip
    ```
2. Instalamos as dependencias de desenvolvimento
    ```console
    $ python -m pip install -r requirements-dev.txt
    ```
3. Instalamos o projeto em modo de desenvolvimento.

    Esta instalação permite maior facilidade nos testes e auto-complete
do editor de código
    ```console
    $ python -m pip install -e ".[dev]"
    ```

```admonish info
Os metadados de instalação estão definidos no arquivo `pyproject.toml`, neste arquivo estão listados os atributos do projeto, os arquivos e módulos que fazem parte, a versão e as dependencias.
```

