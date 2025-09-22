import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp
from eunomia_core import schemas

logger = logging.getLogger(__name__)


class OPAException(Exception):
    """Exception raised when OPA communication fails."""

    pass


class OPAClient:
    """HTTP client for communicating with OPA."""

    def __init__(self, base_url: str, timeout: int):
        self.base_url = base_url.rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self._session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def evaluate_policy(
        self, policy_path: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a policy in OPA by sending input data to the specified policy path.

        Args:
            policy_path: The policy path (e.g., "eunomia/authz")
            input_data: The input data to send to OPA

        Returns:
            The OPA response data

        Raises:
            OPAException: If OPA communication fails or returns an error
        """
        session = await self._get_session()
        url = f"{self.base_url}/v1/data/{policy_path}"

        payload = {"input": input_data}

        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                elif response.status == 404:
                    raise OPAException(f"Policy path '{policy_path}' not found in OPA")
                else:
                    error_text = await response.text()
                    raise OPAException(
                        f"OPA request failed with status {response.status}: {error_text}"
                    )
        except aiohttp.ClientError as e:
            raise OPAException(f"Failed to communicate with OPA: {str(e)}") from e
        except asyncio.TimeoutError as e:
            raise OPAException("OPA request timed out") from e


class OPAPolicyEngine:
    """
    OPA-based policy engine that communicates with an OPA sidecar to evaluate policies.
    """

    def __init__(self, base_url: str, policy_path: str, timeout: int):
        self.opa_client = OPAClient(base_url=base_url, timeout=timeout)
        self.policy_path = policy_path

    async def close(self) -> None:
        """Close the OPA client connection."""
        await self.opa_client.close()

    def _prepare_opa_input(self, request: schemas.CheckRequest) -> Dict[str, Any]:
        """
        Convert a CheckRequest to OPA input format.

        Args:
            request: The Eunomia check request

        Returns:
            Dictionary in OPA input format
        """
        return {
            "principal": {
                "uri": request.principal.uri,
                "attributes": request.principal.attributes or {},
                "type": request.principal.type.value,
            },
            "resource": {
                "uri": request.resource.uri,
                "attributes": request.resource.attributes or {},
                "type": request.resource.type.value,
            },
            "action": request.action,
        }

    def _parse_opa_response(
        self, opa_response: Dict[str, Any]
    ) -> schemas.CheckResponse:
        """
        Parse OPA response and convert to CheckResponse.

        Args:
            opa_response: The response from OPA

        Returns:
            CheckResponse object

        Raises:
            OPAException: If the OPA response format is invalid
        """
        try:
            # OPA returns the result under the "result" key
            result = opa_response.get("result")

            if result is None:
                # If no result, policy didn't match - default deny
                return schemas.CheckResponse(
                    allowed=False,
                    reason="No policy evaluation result returned from OPA",
                )

            # Handle different response formats
            if isinstance(result, bool):
                # Simple boolean response
                return schemas.CheckResponse(
                    allowed=result, reason=f"OPA policy evaluation result: {result}"
                )
            elif isinstance(result, dict):
                # Structured response with allow and optional reason
                allowed = result.get("allow", False)
                reason = result.get(
                    "reason", f"OPA policy evaluation result: {allowed}"
                )

                return schemas.CheckResponse(allowed=bool(allowed), reason=reason)
            else:
                # Unexpected format - default deny with explanation
                return schemas.CheckResponse(
                    allowed=False,
                    reason=f"Unexpected OPA response format: {type(result)}",
                )

        except Exception as e:
            logger.error(f"Failed to parse OPA response: {e}")
            raise OPAException(f"Failed to parse OPA response: {str(e)}") from e

    async def evaluate_all(
        self, request: schemas.CheckRequest
    ) -> schemas.CheckResponse:
        """
        Evaluate the request using OPA and return a CheckResponse.

        This method prepares the input for OPA, sends it to the policy engine,
        and parses the response back into Eunomia format.

        Args:
            request: The check request to evaluate

        Returns:
            CheckResponse indicating whether the action is allowed

        Raises:
            OPAException: If OPA communication or evaluation fails
        """
        try:
            # Prepare input for OPA
            opa_input = self._prepare_opa_input(request)

            logger.debug(f"Sending request to OPA: {opa_input}")

            # Send to OPA for evaluation
            opa_response = await self.opa_client.evaluate_policy(
                policy_path=self.policy_path, input_data=opa_input
            )

            logger.debug(f"Received response from OPA: {opa_response}")

            # Parse response and return
            return self._parse_opa_response(opa_response)

        except OPAException:
            # Re-raise OPA exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error during policy evaluation: {e}")
            raise OPAException(f"Policy evaluation failed: {str(e)}") from e

    # Legacy methods for compatibility with the existing interface
    def add_policy(self, policy: schemas.Policy) -> None:
        """
        Legacy method for compatibility. OPA policies are managed externally.
        This method logs a warning and does nothing.
        """
        logger.warning(
            "add_policy called on OPAPolicyEngine - policies should be managed directly in OPA"
        )

    def remove_policy(self, policy_name: str) -> bool:
        """
        Legacy method for compatibility. OPA policies are managed externally.
        This method logs a warning and returns False.
        """
        logger.warning(
            "remove_policy called on OPAPolicyEngine - policies should be managed directly in OPA"
        )
        return False

    def get_policies(self) -> list[schemas.Policy]:
        """
        Legacy method for compatibility. OPA policies are managed externally.
        This method logs a warning and returns an empty list.
        """
        logger.warning(
            "get_policies called on OPAPolicyEngine - policies should be retrieved directly from OPA"
        )
        return []

    def get_policy(self, policy_name: str) -> Optional[schemas.Policy]:
        """
        Legacy method for compatibility. OPA policies are managed externally.
        This method logs a warning and returns None.
        """
        logger.warning(
            "get_policy called on OPAPolicyEngine - policies should be retrieved directly from OPA"
        )
        return None
