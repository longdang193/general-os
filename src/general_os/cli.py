"""Small command-line surface for durable state and current observations."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from general_os.acceptance import (
    BoundaryEvidence,
    VerificationResult,
    apply_task_transition,
    evaluate_acceptance,
)
from general_os.git import inspect_git
from general_os.orca import OrcaCliStatusObserver
from general_os.profiles import load_profiles, project_profile, resolve_profile
from general_os.state import StateError, load_state, save_state


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def run_state_validate(args: argparse.Namespace) -> int:
    state = load_state(args.path)
    _print({"status": "valid", "goal": state.goal, "task_count": len(state.tasks)})
    return 0


def run_accept(args: argparse.Namespace) -> int:
    state = load_state(args.state)
    task = next((item for item in state.tasks if item.id == args.task_id), None)
    if task is None:
        raise StateError(f"unknown task: {args.task_id}")
    snapshot = inspect_git(args.repo)
    boundary_evidence = None
    if args.boundary_evidence:
        raw_boundary = json.loads(args.boundary_evidence)
        if not isinstance(raw_boundary, dict):
            raise ValueError("boundary evidence must be a JSON object")
        boundary_evidence = BoundaryEvidence(
            kind=raw_boundary.get("kind", ""),
            snapshot_identity=raw_boundary.get("snapshot_identity", ""),
            evidence=raw_boundary.get("evidence", ""),
        )
    verification = VerificationResult(
        status=args.status,
        passed=tuple(args.check),
        evidence_revision=args.revision or snapshot.revision,
        snapshot_identity=args.snapshot_identity,
        boundary_evidence=boundary_evidence,
    )
    decision = evaluate_acceptance(task, snapshot, verification)
    updated_state = apply_task_transition(state, task.id, decision)
    if updated_state != state:
        save_state(args.state, updated_state)
    _print(asdict(decision))
    return 0


def run_orca_smoke(args: argparse.Namespace) -> int:
    observation = OrcaCliStatusObserver().observe()
    _print(
        {
            "status": observation.status,
            "reachable": observation.reachable,
            "state": observation.state,
            "app_version": observation.app_version,
            "executable": observation.executable,
            "message": observation.message,
            "verified": observation.reachable is True,
        }
    )
    return 0


def run_profile_resolve(args: argparse.Namespace) -> int:
    profile = resolve_profile(args.name, load_profiles(args.directory))
    projection = project_profile(profile)
    _print({"profile": profile.name, **asdict(projection)})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="general-os")
    commands = parser.add_subparsers(dest="command", required=True)

    state = commands.add_parser("state")
    state_commands = state.add_subparsers(dest="state_command", required=True)
    validate = state_commands.add_parser("validate")
    validate.add_argument("path")
    validate.set_defaults(handler=run_state_validate)

    accept = commands.add_parser("accept")
    accept.add_argument("--state", required=True)
    accept.add_argument("--repo", required=True)
    accept.add_argument("--task-id", required=True)
    accept.add_argument("--status", choices=("pass", "fail", "blocked"), required=True)
    accept.add_argument("--check", action="append", default=[])
    accept.add_argument("--revision")
    accept.add_argument("--snapshot-identity")
    accept.add_argument("--boundary-evidence")
    accept.set_defaults(handler=run_accept)

    orca = commands.add_parser("orca")
    orca_commands = orca.add_subparsers(dest="orca_command", required=True)
    smoke = orca_commands.add_parser("smoke")
    smoke.add_argument("--json", action="store_true")
    smoke.set_defaults(handler=run_orca_smoke)

    profile = commands.add_parser("profile")
    profile_commands = profile.add_subparsers(dest="profile_command", required=True)
    resolve = profile_commands.add_parser("resolve")
    resolve.add_argument("--name", required=True)
    resolve.add_argument("--directory", default="agents")
    resolve.set_defaults(handler=run_profile_resolve)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (StateError, ValueError, OSError) as exc:
        parser.error(str(exc))
    return 2
