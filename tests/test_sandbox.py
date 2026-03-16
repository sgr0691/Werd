"""Tests for the Werd sandbox policy."""

import pytest
from werd.sandbox import SandboxPolicy, DEFAULT_POLICY, STRICT_POLICY, PERMISSIVE_POLICY


def test_sandbox_policy_default():
    """Test that default SandboxPolicy has expected values."""
    policy = SandboxPolicy()

    assert policy.max_memory_mb == 32
    assert policy.timeout_ms == 200
    assert policy.allow_network is False
    assert policy.allow_filesystem is False
    assert policy.allowed_paths == []


def test_sandbox_policy_custom():
    """Test that SandboxPolicy accepts custom values."""
    policy = SandboxPolicy(
        max_memory_mb=64,
        timeout_ms=500,
        allow_network=True,
        allow_filesystem=True,
        allowed_paths=["/tmp", "/home"],
    )

    assert policy.max_memory_mb == 64
    assert policy.timeout_ms == 500
    assert policy.allow_network is True
    assert policy.allow_filesystem is True
    assert policy.allowed_paths == ["/tmp", "/home"]


def test_sandbox_policy_to_dict():
    """Test that SandboxPolicy can be converted to dictionary."""
    policy = SandboxPolicy(max_memory_mb=16, timeout_ms=100)
    result = policy.to_dict()

    assert isinstance(result, dict)
    assert result["max_memory_mb"] == 16
    assert result["timeout_ms"] == 100
    assert result["allow_network"] is False
    assert result["allow_filesystem"] is False
    assert result["allowed_paths"] == []


def test_sandbox_policy_from_dict():
    """Test that SandboxPolicy can be created from dictionary."""
    data = {
        "max_memory_mb": 128,
        "timeout_ms": 1000,
        "allow_network": True,
        "allow_filesystem": True,
        "allowed_paths": ["/data"],
    }

    policy = SandboxPolicy.from_dict(data)

    assert policy.max_memory_mb == 128
    assert policy.timeout_ms == 1000
    assert policy.allow_network is True
    assert policy.allow_filesystem is True
    assert policy.allowed_paths == ["/data"]


def test_default_policy():
    """Test that DEFAULT_POLICY has expected values."""
    assert DEFAULT_POLICY.max_memory_mb == 32
    assert DEFAULT_POLICY.timeout_ms == 200
    assert DEFAULT_POLICY.allow_network is False
    assert DEFAULT_POLICY.allow_filesystem is False


def test_strict_policy():
    """Test that STRICT_POLICY has expected values."""
    assert STRICT_POLICY.max_memory_mb == 16
    assert STRICT_POLICY.timeout_ms == 100
    assert STRICT_POLICY.allow_network is False
    assert STRICT_POLICY.allow_filesystem is False


def test_permissive_policy():
    """Test that PERMISSIVE_POLICY has expected values."""
    assert PERMISSIVE_POLICY.max_memory_mb == 64
    assert PERMISSIVE_POLICY.timeout_ms == 500
    assert PERMISSIVE_POLICY.allow_network is True
    assert PERMISSIVE_POLICY.allow_filesystem is True
