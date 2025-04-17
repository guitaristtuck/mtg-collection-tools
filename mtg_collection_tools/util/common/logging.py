import typer


def error(message: str, fail: bool = False):
    typer.secho(message=message,fg=typer.colors.RED,err=True)

    if fail:
        raise typer.Exit(code=1)
