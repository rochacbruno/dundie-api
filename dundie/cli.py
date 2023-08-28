import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import Session, select

from .config import settings
from .db import SQLModel, engine
from .models import User
from .models.transaction import Balance, Transaction
from .models.user import generate_username
from .tasks.transaction import add_transaction

main = typer.Typer(name="dundie CLI", add_completion=False)


@main.command()
def shell() -> None:  # pyright: ignore
    """Opens interactive shell"""
    _vars = {
        "settings": settings,
        "engine": engine,
        "select": select,
        "session": Session(engine),
        "User": User,
        "Transaction": Transaction,
        "Balance": Balance,
        "add_transaction": add_transaction,
    }
    typer.echo(f"Auto imports: {list(_vars.keys())}")
    try:
        from IPython import start_ipython

        start_ipython(argv=["--ipython-dir=/tmp", "--no-banner"], user_ns=_vars)  # type: ignore
    except ImportError:
        import code

        code.InteractiveConsole(_vars).interact()


@main.command()
def user_list() -> None:  # pyright: ignore
    """Lists all users"""
    table = Table(title="dundie users")
    fields = ["name", "username", "dept", "email", "currency"]
    for header in fields:
        table.add_column(header, style="magenta")

    with Session(engine) as session:
        users = session.exec(select(User))
        for user in users:
            table.add_row(*[getattr(user, field) for field in fields])

    Console().print(table)


@main.command()
def create_user(
    name: str,
    email: str,
    password: str,
    dept: str,
    username: str | None = None,
    currency: str = "USD",
) -> User:
    """Create user"""
    with Session(engine) as session:
        user = User(
            name=name,
            email=email,
            password=password,  # pyright: ignore
            dept=dept,
            username=username or generate_username(name),
            currency=currency,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        typer.echo(f"created {user.username} user")
        return user  # pyright: ignore


@main.command()
def transaction(
    username: str,
    value: int,
):
    """Adds specified value to the user"""

    table = Table(title="Transaction")
    fields = ["user", "before", "after"]
    for header in fields:
        table.add_column(header, style="magenta")

    with Session(engine) as session:
        from_user = session.exec(select(User).where(User.username == "admin")).first()
        if not from_user:
            typer.echo("admin user not found")
            exit(1)
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            typer.echo(f"user {username} not found")
            exit(1)

        from_user_before = from_user.balance
        user_before = user.balance
        add_transaction(user=user, from_user=from_user, session=session, value=value)
        table.add_row(from_user.username, str(from_user_before), str(from_user.balance))
        table.add_row(user.username, str(user_before), str(user.balance))

        Console().print(table)


@main.command()
def reset_db(
    force: bool = typer.Option(
        False, "--force", "-f", help="Run with no confirmation"
    )
):
    """Resets the database tables"""
    force = force or typer.confirm("Are you sure?")
    if force:
        SQLModel.metadata.drop_all(engine)
