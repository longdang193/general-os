import pytest

from general_os.profiles import ProfileError, load_profiles, resolve_profile


def test_load_profiles_and_resolve_named_profile(tmp_path):
    (tmp_path / "normal.toml").write_text(
        'name = "normal"\nrank = 2\nmodel = "codex"\nprovider = "native"\n',
        encoding="utf-8",
    )

    profiles = load_profiles(tmp_path)

    assert resolve_profile("normal", profiles).model == "codex"
    assert profiles["normal"].rank == 2


def test_resolve_profile_defaults_to_normal():
    profile = resolve_profile(None, {})

    assert profile.name == "normal"


def test_unknown_profile_fails_clearly():
    with pytest.raises(ProfileError, match="unknown profile"):
        resolve_profile("missing", {})
