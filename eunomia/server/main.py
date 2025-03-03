import logging
import platform
import shutil
import subprocess
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

from eunomia.config import settings
from eunomia.server.api import routers


def ensure_opa_installed() -> str:
    """
    Check if the OPA binary is available; if not, attempt to install it.
    Returns the absolute path of the OPA binary.
    """
    opa_path = shutil.which("opa")
    if opa_path:
        logging.info("OPA is installed at:", opa_path)
        return opa_path

    logging.info("OPA not found. Attempting to install OPA...")
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["brew", "install", "opa"], check=True)
        elif system == "Linux":
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "opa"], check=True)
        else:
            logging.info(f"Automatic installation not supported on {system}.")
            sys.exit(1)
    except subprocess.CalledProcessError:
        logging.info("Failed to install OPA automatically. Please install it manually.")
        sys.exit(1)

    opa_path = shutil.which("opa")
    if not opa_path:
        logging.info(
            "OPA installation succeeded, but the binary is still not found in PATH."
        )
        sys.exit(1)

    logging.info("OPA is now installed at:", opa_path)
    return opa_path


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure OPA is installed before starting the API gateway.
    opa_binary = ensure_opa_installed()

    # Build the OPA command using settings from config.
    opa_cmd = [
        opa_binary,
        "run",
        "--server",
        "--addr",
        f"{settings.OPA_SERVER_HOST}:{settings.OPA_SERVER_PORT}",
        settings.OPA_POLICY_PATH,
    ]

    # Start the OPA server as a subprocess.
    opa_process = subprocess.Popen(opa_cmd, stdout=sys.stdout, stderr=sys.stderr)

    # Wait a short period for OPA to initialize.
    time.sleep(2)

    try:
        yield
    finally:
        # Terminate the OPA process on shutdown.
        opa_process.terminate()
        opa_process.wait()


app = FastAPI(lifespan=lifespan)

app.include_router(routers.router)
