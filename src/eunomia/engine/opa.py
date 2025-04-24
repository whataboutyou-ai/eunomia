import logging
import os
import platform
import shutil
import subprocess
import sys
import time

import httpx
from eunomia_core import schemas

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
        self._url = f"http://{self._server_address}/v1/data/eunomia"
        self._policy_folder = settings.OPA_POLICY_FOLDER

        # Global variable to store the OPA process
        self._process: subprocess.Popen[bytes] | None = None

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
            self._policy_folder,
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

    async def check_access(self, request: schemas.AccessRequest) -> bool:
        input_data = {
            "input": {
                "principal": {
                    "uri": request.principal.uri,
                    "attributes": request.principal.attributes,
                },
                "resource": {
                    "uri": request.resource.uri,
                    "attributes": request.resource.attributes,
                },
            }
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._url}/{request.action}", json=input_data
            )
            response.raise_for_status()
            result = response.json()
            decision = result.get("result", False)
            return bool(decision)

    def _entity_to_rego(self, entity: schemas.EntityAccess) -> str:
        EQUAL_URI_STMNT = '	input.{type}.uri == "{uri}"'
        EQUAL_ATTRIBUTE_STMNT = '	input.{type}.attributes.{key} == "{value}"'

        uri_stmt = (
            [EQUAL_URI_STMNT.format(type=entity.type.value, uri=entity.uri)]
            if entity.uri
            else []
        )
        attribute_stmts = [
            EQUAL_ATTRIBUTE_STMNT.format(
                type=entity.type.value, key=attribute.key, value=attribute.value
            )
            for attribute in entity.attributes
        ]
        return "\n".join(uri_stmt + attribute_stmts)

    def _access_rule_to_rego(self, rule: schemas.AccessRequest) -> str:
        ALLOW_RULE_STMNT = "allow if {{\n{entity_stmts}\n}}"

        rego_items = "\n".join(
            [self._entity_to_rego(rule.principal), self._entity_to_rego(rule.resource)]
        )
        return ALLOW_RULE_STMNT.format(entity_stmts=rego_items)

    def _policy_to_rego(self, policy: schemas.Policy) -> str:
        ALLOW_POLICY_STMNT = "package eunomia\n\ndefault allow := false\n\n{rules}\n"

        rego_rules = "\n\n".join(
            [self._access_rule_to_rego(rule) for rule in policy.rules]
        )
        return ALLOW_POLICY_STMNT.format(rules=rego_rules)

    def create_policy(self, policy: schemas.Policy, filename: str) -> str:
        """
        Create a policy from Eunomia's Policy schema object
        to a Rego (OPA's native policy language) file.
        """
        if not os.path.exists(self._policy_folder):
            os.makedirs(self._policy_folder)
            logging.info(
                f"Policy folder did not exist, created it at {self._policy_folder}"
            )

        path = os.path.join(self._policy_folder, filename)
        if os.path.exists(path):
            logging.warning(
                f"Policy file '{filename}' already exists at {self._policy_folder}, "
                "overwriting it"
            )

        policy_rego = self._policy_to_rego(policy)
        with open(path, "w") as f:
            f.write(policy_rego)
        return path
