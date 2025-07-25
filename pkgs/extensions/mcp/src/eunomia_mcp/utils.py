import inspect
from pathlib import Path
from typing import Optional

from eunomia_core import schemas
from eunomia_sdk import EunomiaClient

from eunomia.config import settings
from eunomia.server import EunomiaServer
from eunomia_mcp.bridge import EunomiaMode
from eunomia_mcp.middleware import EunomiaMcpMiddleware


def load_policy_config(policy_file: str) -> schemas.Policy:
    """
    Load policy configuration from a JSON file.

    Args:
        policy_file: Path to policy configuration JSON file

    Returns:
        Policy configuration dictionary
    """
    policy_path = get_filepath(policy_file)

    with open(policy_path, "r") as f:
        return schemas.Policy.model_validate_json(f.read())


def get_filepath(path_str: str) -> Path:
    path = Path(path_str)

    # Strategy 1: Try the provided path as-is (works for absolute paths and correct relative paths)
    if path.exists():
        resolved_path = path.resolve()
    else:
        # Strategy 2: Try relative to current working directory
        cwd_success = False
        try:
            cwd_path = Path.cwd() / path_str
            if cwd_path.exists():
                resolved_path = cwd_path.resolve()
                cwd_success = True
        except (OSError, FileNotFoundError):
            # Current working directory doesn't exist, skip this strategy
            pass

        if not cwd_success:
            # Strategy 3: Try relative to external caller's directory
            caller_dir = _get_external_caller_directory()
            caller_path = caller_dir / path_str
            if caller_path.exists():
                resolved_path = caller_path.resolve()

            else:
                # Strategy 4: None of the strategies worked, raise error
                # Build error message with paths that were actually tried
                error_parts = ["Policy file not found. Tried:"]
                error_parts.append(f"  - As provided: {path.resolve()}")
                try:
                    cwd_resolved = Path.cwd() / path_str
                    error_parts.append(f"  - Relative to CWD: {cwd_resolved.resolve()}")
                except (OSError, FileNotFoundError):
                    error_parts.append(
                        "  - Relative to CWD: (current directory not available)"
                    )
                error_parts.append(f"  - Relative to caller: {caller_path.resolve()}")

                raise FileNotFoundError("\n".join(error_parts))

    return resolved_path


def _get_external_caller_directory() -> Path:
    """
    Get the directory of the first caller outside of the eunomia_mcp package.

    Returns:
        Path to the external caller's directory
    """
    frame = inspect.currentframe()

    while frame is not None:
        frame = frame.f_back
        if frame is None:
            break

        frame_filename = frame.f_code.co_filename
        # Skip frames within the eunomia_mcp package to find the original external caller
        if "eunomia_mcp" not in frame_filename:
            return Path(frame_filename).parent

    # Fallback to immediate caller if no external caller found
    caller_frame = inspect.currentframe().f_back
    return Path(caller_frame.f_code.co_filename).parent


def create_eunomia_middleware(
    policy_file: Optional[str] = None,
    use_remote_eunomia: bool = False,
    eunomia_endpoint: Optional[str] = None,
    enable_audit_logging: bool = True,
) -> EunomiaMcpMiddleware:
    """
    Create Eunomia authorization middleware for FastMCP servers.

    Parameters
    ----------
    policy_file : str, optional
        Path to policy configuration JSON file (defaults to "mcp_policies.json")
    use_remote_eunomia : bool, optional
        Whether to use a remote Eunomia server (defaults to False)
    eunomia_endpoint : str, optional
        Eunomia server endpoint when using a remote server (defaults to http://localhost:8421)
    enable_audit_logging : bool, optional
        Whether to enable audit logging

    Returns
    -------
    Middleware
        FastMCP Middleware instance
    """
    client, server = None, None

    if use_remote_eunomia:
        mode = EunomiaMode.CLIENT

        if policy_file is not None:
            raise ValueError(
                "policy_file is not supported when using a remote Eunomia server, use the CLI to push the policy to the server"
            )

        client = EunomiaClient(endpoint=eunomia_endpoint)

    else:
        mode = EunomiaMode.SERVER

        # enforce no database persistence and no dynamic fetchers
        settings.ENGINE_SQL_DATABASE = False
        settings.FETCHERS = {}
        server = EunomiaServer()

        # load policy from file
        policy = load_policy_config(policy_file or "mcp_policies.json")
        server.engine.add_policy(policy)

    return EunomiaMcpMiddleware(
        mode=mode,
        eunomia_client=client,
        eunomia_server=server,
        enable_audit_logging=enable_audit_logging,
    )
