"""Small command-line surface for durable state and current observations."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from general_os.acceptance import (
    VerificationResult,
    apply_task_transition,
    evaluate_acceptance,
)
from general_os.deployment import DeploymentError, deploy
from general_os.git import inspect_git
from general_os.orca import OrcaCliStatusObserver
from general_os.profiles import load_profiles, project_profile, resolve_profile
from general_os.state import BLOCKER_CATEGORIES, StateError, load_state, save_state


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def run_state_validate(args: argparse.Namespace) -> int:
    state = load_state(args.path)
    _print({"status": "valid", "goal": state.goal, "task_count": len(state.tasks)})
    return 0


def run_accept(args: argparse.Namespace) -> int:
    if args.status == "pass":
        raise StateError("PASS requires verifier-produced evidence")
    if args.status != "blocked" and (
        args.blocker_category is not None or args.blocker_reason is not None
    ):
        raise StateError("blocker category and reason are only valid for blocked status")
    state = load_state(args.state)
    task = next((item for item in state.tasks if item.id == args.task_id), None)
    if task is None:
        raise StateError(f"unknown task: {args.task_id}")
    snapshot = inspect_git(args.repo)
    verification = VerificationResult(
        status=args.status,
        blocker_category=args.blocker_category,
        blocker_reason=args.blocker_reason,
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
            "probe_ok": observation.reachable is True,
        }
    )
    return 0 if observation.status == "ready" else 1


def run_profile_resolve(args: argparse.Namespace) -> int:
    profile = resolve_profile(args.name, load_profiles(args.directory))
    projection = project_profile(profile)
    _print({"profile": profile.name, **asdict(projection)})
    return 0


def run_deploy(args: argparse.Namespace) -> int:
    code, report = deploy(
        args.repo,
        adapter=args.adapter,
        dry_run=args.dry_run,
        check=args.check,
        prune=args.prune,
        strict_migration=args.strict_migration,
    )
    _print(report)
    return code


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
    accept.add_argument("--status", choices=("fail", "blocked"), required=True)
    accept.add_argument("--blocker-category", choices=sorted(BLOCKER_CATEGORIES))
    accept.add_argument("--blocker-reason")
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

    deploy_command = commands.add_parser("deploy")
    deploy_command.add_argument("--repo", default=".")
    deploy_command.add_argument("--adapter", default="codex")
    deploy_command.add_argument("--dry-run", action="store_true")
    deploy_command.add_argument("--check", action="store_true")
    deploy_command.add_argument("--prune", action="store_true")
    deploy_command.add_argument("--strict-migration", action="store_true")
    deploy_command.set_defaults(handler=run_deploy)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (DeploymentError, StateError, ValueError, OSError) as exc:
        parser.error(str(exc))
    return 2
