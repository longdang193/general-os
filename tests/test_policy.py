import pytest
from datetime import datetime, timedelta, timezone

from general_os.policy import (
    PolicyError,
    RuntimeConfig,
    load_runtime_config,
    resolve_policy,
)


def test_policy_uses_safe_defaults():
    policy = resolve_policy()

    assert policy.native_subagents_enabled is True
    assert policy.orca_enabled is False
    assert policy.remote_side_effects == "ask"


def test_policy_applies_material_side_effect_exception():
    policy = resolve_policy(
        {
            "remote_side_effects": "allow",
            "scope": "github:general-os",
            "provenance": "user-approval",
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
        },
        requested_scope="github:general-os",
    )

    assert policy.remote_side_effects == "allow"
    assert policy.orca_enabled is False


def test_policy_rejects_unscoped_or_mismatched_allow():
    with pytest.raises(PolicyError, match="requested scope"):
        resolve_policy({"remote_side_effects": "allow"})

    with pytest.raises(PolicyError, match="does not match"):
        resolve_policy(
            {
                "remote_side_effects": "allow",
                "scope": "github:general-os",
                "provenance": "user-approval",
                "expires_at": "2099-01-01T00:00:00+00:00",
            },
            requested_scope="github:other",
        )


def test_expired_allow_falls_back_to_safe_config():
    policy = resolve_policy(
        {
            "remote_side_effects": "allow",
            "scope": "github:general-os",
            "provenance": "user-approval",
            "expires_at": "2000-01-01T00:00:00+00:00",
        },
        requested_scope="github:general-os",
    )

    assert policy.remote_side_effects == "ask"


def test_configured_allow_does_not_require_exception_metadata():
    policy = resolve_policy(config=RuntimeConfig(remote_side_effects="allow"))

    assert policy.remote_side_effects == "allow"


def test_local_deny_is_a_hard_policy_ceiling():
    policy = resolve_policy(
        {"remote_side_effects": "allow"},
        RuntimeConfig(remote_side_effects="deny"),
    )

    assert policy.remote_side_effects == "deny"


def test_policy_rejects_unknown_exception():
    with pytest.raises(PolicyError, match="unknown policy exception"):
        resolve_policy({"orca": "allow"})


def test_runtime_config_reads_toggles(tmp_path):
    path = tmp_path / "runtime-policy.toml"
    path.write_text(
        "[runtime]\nnative_subagents_enabled = false\norca_enabled = true\n"
        "[policy]\nremote_side_effects = \"deny\"\n",
        encoding="utf-8",
    )

    config = load_runtime_config(path)

    assert config == RuntimeConfig(
        native_subagents_enabled=False,
        orca_enabled=True,
        remote_side_effects="deny",
    )
