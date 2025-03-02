from contextlib import asynccontextmanager
import subprocess
import time
import shutil
import sys
import platform

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.routers import public

def ensure_opa_installed() -> str:
    """
    Check if the OPA binary is available; if not, attempt to install it.
    Returns the absolute path of the OPA binary.
    """
    opa_path = shutil.which("opa")
    if opa_path:
        print("OPA is installed at:", opa_path)
        return opa_path

    print("OPA not found. Attempting to install OPA...")
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["brew", "install", "opa"], check=True)
        elif system == "Linux":
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "opa"], check=True)
        else:
            print(f"Automatic installation not supported on {system}.")
            sys.exit(1)
    except subprocess.CalledProcessError:
        print("Failed to install OPA automatically. Please install it manually.")
        sys.exit(1)

    opa_path = shutil.which("opa")
    if not opa_path:
        print("OPA installation succeeded, but the binary is still not found in PATH.")
        sys.exit(1)

    print("OPA is now installed at:", opa_path)
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
        "--addr", f"{settings.OPA_SERVER_URL}:{settings.OPA_SERVER_PORT}",
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

app.include_router(public.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("eunomia.server.api.main:app", host=settings.SERVER_HOST, port=settings.SERVER_PORT, reload=True)
    


