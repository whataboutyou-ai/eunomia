import logging
import platform
import shutil
import subprocess
import sys
import time

from eunomia.config import settings


class OpaPolicyEngine:
    def __init__(self) -> None:
        self._opa_binary = self._check_installation()
        self._server_address = f"{settings.OPA_SERVER_HOST}:{settings.OPA_SERVER_PORT}"
        self._policy_path = settings.OPA_POLICY_PATH

        # Global variable to store the OPA process
        self.process: subprocess.Popen[bytes] | None = None

    def _check_installation(self) -> str:
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
        opa_cmd = [
            self._opa_binary,
            "run",
            "--server",
            "--addr",
            self._server_address,
            self._policy_path,
        ]

        # Start the OPA server as a subprocess, and wait to ensure it's running
        self.process = subprocess.Popen(opa_cmd, stdout=sys.stdout, stderr=sys.stderr)
        time.sleep(2)

    def stop(self) -> None:
        if self.process:
            self.process.terminate()
            self.process.wait()
