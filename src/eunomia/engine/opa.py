import logging
import platform
import shutil
import subprocess
import sys
import time

from eunomia.config import settings


class OpaPolicyEngine:
    """
    Interface to the Open Policy Agent (OPA) engine.

    This class manages the lifecycle of an OPA server instance and provides
    an interface for interacting with it. It handles the installation check,
    server startup, and shutdown operations.
    """

    def __init__(self) -> None:
        self._server_address = f"{settings.OPA_SERVER_HOST}:{settings.OPA_SERVER_PORT}"
        self.policy_folder = settings.OPA_POLICY_FOLDER
        # Global variable to store the OPA process
        self._process: subprocess.Popen[bytes] | None = None
        self.url = f"http://{self._server_address}/v1/data/eunomia"

    def _check_installation(self) -> str:
        # Check if the OPA binary is available; if not, attempt to install it.
        # Returns the absolute path of the OPA binary.

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
            logging.info(
                "Failed to install OPA automatically. Please install it manually."
            )
            sys.exit(1)

        opa_path = shutil.which("opa")
        if not opa_path:
            logging.info(
                "OPA installation succeeded, but the binary is still not found in PATH."
            )
            sys.exit(1)

        logging.info("OPA is now installed at:", opa_path)
        return opa_path

    def start(self) -> None:
        """
        Start the OPA server.

        This method first checks the installation of OPA and tries to install it
        if it is not found. Then it launches the OPA server as a subprocess using
        the configured address and policy path. It waits briefly to ensure the
        server has started before returning.

        Raises
        ------
        SystemExit
            If OPA binary cannot be found or installed.
        """
        opa_binary = self._check_installation()
        opa_cmd = [
            opa_binary,
            "run",
            "--server",
            "--addr",
            self._server_address,
            self.policy_folder,
        ]

        # Start the OPA server as a subprocess, and wait to ensure it's running
        self._process = subprocess.Popen(opa_cmd, stdout=sys.stdout, stderr=sys.stderr)
        time.sleep(2)

    def stop(self) -> None:
        """
        Stop the OPA server.

        This method terminates the OPA server subprocess if it is running
        and waits for it to exit.
        """
        if self._process:
            self._process.terminate()
            self._process.wait()
