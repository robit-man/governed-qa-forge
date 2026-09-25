from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from qaforge.errors import ForgeError
from qaforge.fixtures import scaffold_workspace
from qaforge.io import read_jsonl
from qaforge.models import CandidateRecord, GateStatus
from qaforge.pilot import run_calibration_pilot
from qaforge.pipeline import approve_all, export_review, generate_run, import_reviews, load_state
from qaforge.release import build_release, release_anchor, verify_release
from qaforge.service import ServiceSettings, create_agent_app, create_control_app
from qaforge.workspace import Workspace

app = typer.Typer(
    name="qaforge",
    help="Compile governed synthetic Q/A candidates into auditable fine-tuning releases.",
    no_args_is_help=True,
)


def _fail(exc: Exception) -> None:
    typer.secho(f"error: {exc}", fg=typer.colors.RED, err=True)
    raise typer.Exit(1)


@app.command("init")
def init_command(path: Path) -> None:
    """Create a production workspace whose remote teacher is deny-by-default."""
    try:
        created = scaffold_workspace(path, demo=False)
        typer.echo(f"initialized {created}")
        typer.echo("teacher authorization is unclear by design; edit registry/teachers.yaml")
    except (ForgeError, OSError, ValueError) as exc:
        _fail(exc)


@app.command("doctor")
def doctor_command(
    path: Annotated[Path, typer.Argument(help="Corpus workspace path.")] = Path("."),
    provider: str | None = None,
) -> None:
    """Validate configuration, taxonomy, seeds, authorization, and depth."""
    try:
        report = Workspace(path).doctor(provider)
        for item in report.checks:
            marker = "PASS" if item.status is GateStatus.PASS else "FAIL"
            typer.echo(f"{marker:4} {item.gate}: {item.detail}")
        if not report.passed:
            raise typer.Exit(1)
    except typer.Exit:
        raise
    except (ForgeError, OSError, ValueError) as exc:
        _fail(exc)


@app.command("generate")
def generate_command(
    path: Annotated[Path, typer.Argument(help="Corpus workspace path.")] = Path("."),
    run_id: str = typer.Option("run-001", help="New immutable run identifier."),
    provider: str | None = typer.Option(None, help="Teacher registry ID override."),
) -> None:
    """Generate, verify, decontaminate, and select candidates."""
    try:
        state = generate_run(Workspace(path), run_id, provider)
        typer.echo(json.dumps(state.model_dump(mode="json"), indent=2))
    except (ForgeError, OSError, ValueError) as exc:
        _fail(exc)


@app.command("review-export")
def review_export_command(path: Path, run_id: str, destination: Path) -> None:
    """Export every selected candidate as a required review decision packet."""
    try:
        typer.echo(str(export_review(Workspace(path), run_id, destination)))
    except (ForgeError, OSError, ValueError) as exc:
        _fail(exc)


@app.command("review-import")
def review_import_command(path: Path, run_id: str, decisions: Path) -> None:
    """Import complete, explicit review decisions."""
    try:
        state = import_reviews(Workspace(path), run_id, decisions)
        typer.echo(json.dumps(state.model_dump(mode="json"), indent=2))
    except (ForgeError, OSError, ValueError) as exc:
        _fail(exc)


@app.command("review-all")
def review_all_command(
    path: Path,
    run_id: str,
    reviewer: str = typer.Option(...),
    rationale: str = typer.Option(...),
    acknowledge_manual_review: bool = typer.Option(
        False,
        "--acknowledge-manual-review",
        help="Confirm every selected row was manually reviewed.",
    ),
) -> None:
    """Record one explicit decision for every selected row."""
    try:
        state = approve_all(Workspace(path), run_id, reviewer, rationale, acknowledge_manual_review)
        typer.echo(json.dumps(state.model_dump(mode="json"), indent=2))
    except (ForgeError, OSError, ValueError) as exc:
        _fail(exc)


@app.command("release")
def release_command(path: Path, run_id: str) -> None:
    """Re-run mandatory gates and build an immutable release evidence bundle."""
    try:
        release_path = build_release(Workspace(path), run_id)
        typer.echo(
            json.dumps(
                {"release": str(release_path), "anchor_sha256": release_anchor(release_path)},
                indent=2,
            )
        )
    except (ForgeError, OSError, ValueError) as exc:
        _fail(exc)


@app.command("verify-release")
def verify_release_command(
    path: Path,
    version: str,
    expected_sha256: Annotated[
        str | None,
        typer.Option(help="Trusted SHA-256 of the release SHA256SUMS file."),
    ] = None,
    allow_unanchored: Annotated[
        bool,
        typer.Option(help="Allow fixity-only verification; intended for local demos."),
    ] = False,
) -> None:
    """Verify release fixity, counts, content hashes, and lineage isolation."""
    try:
        result = verify_release(
            Workspace(path), version, expected_sha256, allow_unanchored=allow_unanchored
        )
        typer.echo(json.dumps(result, indent=2))
        if not result["passed"]:
            raise typer.Exit(1)
    except typer.Exit:
        raise
    except (ForgeError, OSError, ValueError) as exc:
        _fail(exc)


@app.command("status")
def status_command(
    path: Annotated[Path, typer.Argument(help="Corpus workspace path.")] = Path("."),
) -> None:
    """Show run and release state."""
    try:
        workspace = Workspace(path)
        runs_dir = workspace.root / "runs"
        states = []
        if runs_dir.exists():
            states = [
                load_state(workspace, child.name).model_dump(mode="json")
                for child in sorted(runs_dir.iterdir())
                if child.is_dir() and (child / "state.json").exists()
            ]
        releases_dir = workspace.root / "releases"
        releases = (
            sorted(child.name for child in releases_dir.iterdir() if child.is_dir())
            if releases_dir.exists()
            else []
        )
        typer.echo(json.dumps({"runs": states, "releases": releases}, indent=2))
    except (ForgeError, OSError, ValueError) as exc:
        _fail(exc)


@app.command("serve-agent")
def serve_agent_command(
    path: Annotated[Path, typer.Argument(help="Corpus workspace path.")],
    database: Annotated[Path, typer.Option("--database", help="Private SQLite broker path.")],
    host: Annotated[str, typer.Option(help="Worker-plane bind address.")] = "127.0.0.1",
    port: Annotated[int, typer.Option(min=1, max=65535)] = 8411,
    lease_seconds: Annotated[int, typer.Option(min=30, max=86_400)] = 900,
) -> None:
    """Run the opaque worker plane (health, lease, and submit only)."""
    try:
        import uvicorn

        settings = ServiceSettings.from_agent_env(path, database, lease_seconds)
        uvicorn.run(
            create_agent_app(settings),
            host=host,
            port=port,
            access_log=True,
            server_header=False,
            date_header=False,
            proxy_headers=False,
            limit_concurrency=128,
            backlog=128,
            timeout_keep_alive=5,
        )
    except (ForgeError, OSError, ValueError) as exc:
        _fail(exc)


@app.command("serve-control")
def serve_control_command(
    path: Annotated[Path, typer.Argument(help="Corpus workspace path.")],
    database: Annotated[Path, typer.Option("--database", help="Private SQLite broker path.")],
    host: Annotated[str, typer.Option(help="Control-plane bind address.")] = "127.0.0.1",
    port: Annotated[int, typer.Option(min=1, max=65535)] = 8412,
    lease_seconds: Annotated[int, typer.Option(min=30, max=86_400)] = 900,
) -> None:
    """Run the private collection control plane; bind it to a trusted interface."""
    try:
        import uvicorn

        settings = ServiceSettings.from_control_env(path, database, lease_seconds)
        uvicorn.run(
            create_control_app(settings),
            host=host,
            port=port,
            access_log=True,
            server_header=False,
            date_header=False,
            proxy_headers=False,
            limit_concurrency=128,
            backlog=128,
            timeout_keep_alive=5,
        )
    except (ForgeError, OSError, ValueError) as exc:
        _fail(exc)


@app.command("calibration-pilot")
def calibration_pilot_command(
    path: Annotated[Path, typer.Argument(help="New calibration workspace path.")],
    size: Annotated[int, typer.Option(min=10, help="Selected-record target.")] = 1000,
    run_id: Annotated[str, typer.Option(help="Immutable pilot run ID.")] = (
        "opaque-calibration-1000"
    ),
) -> None:
    """Run the deterministic blind-service calibration and stop before review."""
    try:
        result = run_calibration_pilot(path, size=size, run_id=run_id)
        typer.echo(json.dumps(result, indent=2, sort_keys=True))
    except (ForgeError, OSError, ValueError) as exc:
        _fail(exc)


@app.command("demo")
def demo_command(path: Path) -> None:
    """Run the complete offline fixture journey, including a marked demo review."""
    try:
        scaffold_workspace(path, demo=True)
        workspace = Workspace(path)
        generate_run(workspace, "demo-run")
        approve_all(
            workspace,
            "demo-run",
            reviewer="demo-fixture",
            rationale="deterministic fixture approval for end-to-end demonstration",
            acknowledged_manual_review=False,
        )
        release_path = build_release(workspace, "demo-run")
        result = verify_release(workspace, "0.1.0", allow_unanchored=True)
        selected = read_jsonl(workspace.run_dir("demo-run") / "selected.jsonl", CandidateRecord)
        typer.echo(
            json.dumps(
                {
                    "workspace": str(workspace.root),
                    "release": str(release_path),
                    "anchor_sha256": release_anchor(release_path),
                    "selected": len(selected),
                    "verification": result,
                },
                indent=2,
            )
        )
        if not result["passed"]:
            raise typer.Exit(1)
    except typer.Exit:
        raise
    except (ForgeError, OSError, ValueError) as exc:
        _fail(exc)
