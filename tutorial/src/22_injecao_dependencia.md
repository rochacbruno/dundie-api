# Injeção de dependência

O FastAPI tem um excelente sistema de injeção de dependêcias, isto é util por 
exemplo para quando quisermos que um endpoint seja acessivel apenas por usuários
administradores, ao invés de colocarmos lógica para verificar o nivel de permissão
do usuário diretamente em cada view, podemos criar uma dependência.

Outro exemplo (que vamos aplicar agora) é precisarmos garantir que cada endpoint,
ao ter sua função view invocada, uma sessão de conexão com o banco de dados já esteja
disponível.

Vamos criar uma dependência chamada `ActiveSession` que posteriormente será usada
na definição das views.


No topo de `dundie/db.py` nas linhas 2 e 3
```python
from fastapi import Depends
from sqlmodel import Session, create_engine
```

No final de `dundie/db.py` após a linha 13

```python
def get_session():
    with Session(engine) as session:
        yield session


ActiveSession = Depends(get_session)
```

O objeto que `ActiveSession` é uma dependência para rotas do FastAPI
quando usarmos este objeto como parâmetro de uma view o FastAPI
vai executar de forma **lazy** este objeto e passar o retorno da função
atrelada a ele como argumento da nossa view.

Neste caso teremos sempre uma conexão com o banco de dados dentro de cada
view que marcarmos com `session: Session = ActiveSession`.

Veremos a seguir como usar esta dependência -->
