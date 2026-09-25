from pathlib import Path

import pytest
import yaml

from qaforge.errors import ConfigurationError
from qaforge.fixtures import scaffold_workspace
from qaforge.workspace import Workspace


def test_fr001_demo_workspace_doctor_passes(demo_workspace: Workspace) -> None:
    report = demo_workspace.doctor()
    assert report.passed
    assert report.seed_count == 8
    assert all(check.status.value == "pass" for check in report.checks)


def test_fr002_production_teacher_is_deny_by_default(tmp_path: Path) -> None:
    workspace = Workspace(scaffold_workspace(tmp_path / "production", demo=False))
    report = workspace.doctor()
    assert not report.passed
    assert any(
        check.gate == "teacher_authorized" and check.status.value == "fail"
        for check in report.checks
    )


def test_fr002_unauthorized_seed_source_blocks(demo_workspace: Workspace) -> None:
    path = demo_workspace.registry_dir / "sources.yaml"
    data = yaml.safe_load(path.read_text())
    data["sources"][0]["authorization_status"] = "blocked"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    report = demo_workspace.doctor()
    assert not report.passed
    assert any(check.gate == "seed_sources_authorized" for check in report.checks)


def test_fr002_incompatible_source_license_blocks(demo_workspace: Workspace) -> None:
    path = demo_workspace.registry_dir / "sources.yaml"
    data = yaml.safe_load(path.read_text())
    data["sources"][0]["compatible_release_licenses"] = ["Apache-2.0"]
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    report = demo_workspace.doctor()
    assert not report.passed
    assert any(
        check.gate == "source_release_license_compatible" and check.status.value == "fail"
        for check in report.checks
    )


def test_fr002_incompatible_teacher_target_use_blocks(demo_workspace: Workspace) -> None:
    path = demo_workspace.registry_dir / "teachers.yaml"
    data = yaml.safe_load(path.read_text())
    data["teachers"][0]["allowed_target_uses"] = ["unrelated use"]
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    report = demo_workspace.doctor()
    assert not report.passed
    assert any(
        check.gate == "teacher_target_use_compatible" and check.status.value == "fail"
        for check in report.checks
    )


def test_nfr006_run_id_cannot_escape_runs_directory(demo_workspace: Workspace) -> None:
    with pytest.raises(ConfigurationError, match="invalid run ID"):
        demo_workspace.run_dir("../outside-runs")
