import pytest

from general_os.profiles import ProfileError, load_profiles, project_profile, resolve_profile


def test_load_profiles_and_resolve_named_profile(tmp_path):
    (tmp_path / "normal.toml").write_text(
        'name = "normal"\nrank = 2\nharness = "codex"\nprovider = "native"\n',
        encoding="utf-8",
    )

    profiles = load_profiles(tmp_path)

    assert resolve_profile("normal", profiles).harness == "codex"
    assert profiles["normal"].rank == 2


def test_projection_preserves_explicit_values_without_inference(tmp_path):
    (tmp_path / "reviewer.toml").write_text(
        'name = "reviewer"\nharness = "custom-review"\nmodel = "real-model"\n'
        'effort = "high"\ninstructions = "Review evidence."\n',
        encoding="utf-8",
    )

    projection = project_profile(resolve_profile("reviewer", load_profiles(tmp_path)))

    assert projection.harness == "custom-review"
    assert projection.model == "real-model"
    assert projection.effort == "high"
    assert projection.instructions == "Review evidence."


def test_projection_omits_native_defaults(tmp_path):
    (tmp_path / "normal.toml").write_text('name = "normal"\nrank = 2\n', encoding="utf-8")

    projection = project_profile(resolve_profile("normal", load_profiles(tmp_path)))

    assert projection.harness is None
    assert projection.model is None
    assert projection.effort is None


@pytest.mark.parametrize("field", ["harness", "effort"])
def test_empty_runtime_fact_fails(field, tmp_path):
    (tmp_path / "invalid.toml").write_text(
        f'name = "invalid"\n{field} = ""\n', encoding="utf-8"
    )

    with pytest.raises(ProfileError, match=field):
        load_profiles(tmp_path)


def test_resolve_profile_defaults_to_normal():
    profile = resolve_profile(None, {})

    assert profile.name == "normal"


def test_unknown_profile_fails_clearly():
    with pytest.raises(ProfileError, match="unknown profile"):
        resolve_profile("missing", {})


@pytest.mark.parametrize(
    ("name", "model", "effort"),
    [
        ("low", "combo-low", "low"),
        ("normal", "combo-normal", "medium"),
        ("high", "combo-high", "high"),
        ("xhigh", "combo-xhigh", "xhigh"),
    ],
)
def test_provided_profiles_own_verified_combo_configuration(name, model, effort):
    profile = resolve_profile(name, load_profiles("agents"))
    projection = project_profile(profile)

    assert projection.model == model
    assert projection.effort == effort
