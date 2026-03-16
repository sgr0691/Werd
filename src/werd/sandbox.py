"""Sandbox policy for WASM module execution."""

from typing import Any, Dict, List, Optional


class SandboxPolicy:
    """Defines restrictions and capabilities for WASM module execution."""

    def __init__(
        self,
        max_memory_mb: int = 32,
        timeout_ms: int = 200,
        allow_network: bool = False,
        allow_filesystem: bool = False,
        allowed_paths: Optional[List[str]] = None,
    ):
        """Initialize sandbox policy.

        Args:
            max_memory_mb: Maximum memory in MB for WASM module
            timeout_ms: Timeout in milliseconds for execution
            allow_network: Whether to allow network access
            allow_filesystem: Whether to allow filesystem access
            allowed_paths: List of allowed filesystem paths
        """
        self.max_memory_mb = max_memory_mb
        self.timeout_ms = timeout_ms
        self.allow_network = allow_network
        self.allow_filesystem = allow_filesystem
        self.allowed_paths = allowed_paths or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary representation."""
        return {
            "max_memory_mb": self.max_memory_mb,
            "timeout_ms": self.timeout_ms,
            "allow_network": self.allow_network,
            "allow_filesystem": self.allow_filesystem,
            "allowed_paths": self.allowed_paths,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SandboxPolicy":
        """Create policy from dictionary representation."""
        return cls(
            max_memory_mb=data.get("max_memory_mb", 32),
            timeout_ms=data.get("timeout_ms", 200),
            allow_network=data.get("allow_network", False),
            allow_filesystem=data.get("allow_filesystem", False),
            allowed_paths=data.get("allowed_paths", []),
        )


# Default sandbox policies
DEFAULT_POLICY = SandboxPolicy()

# Strict policy - no network, no filesystem access
STRICT_POLICY = SandboxPolicy(
    max_memory_mb=16, timeout_ms=100, allow_network=False, allow_filesystem=False
)

# Permissive policy - allows some resources
PERMISSIVE_POLICY = SandboxPolicy(
    max_memory_mb=64, timeout_ms=500, allow_network=True, allow_filesystem=True
)
