from importlib.metadata import version

import typer
import uvicorn

app = typer.Typer()


@app.command(name="version")
def get_version():
    """Show the installed version of Eunomia"""
    print(f"Eunomia v{version('eunomia-ai')}")


@app.command()
def server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Run the Eunomia API server"""
    uvicorn.run("eunomia.api:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
