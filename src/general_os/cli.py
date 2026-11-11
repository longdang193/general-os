"""Small command-line surface for durable state and current observations."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from general_os.acceptance import VerificationResult, apply_task_transition, evaluate_acceptance
from general_os.codex import CodexClient
from general_os.cos import ChiefOfStaff
from general_os.git import inspect_git
from general_os.orca import OrcaCliStatusObserver, OrcaClient
from general_os.policy import load_runtime_config, resolve_policy
from general_os.profiles import load_profiles
from general_os.recovery import next_unfinished_task
from general_os.state import StateError, load_state, save_state


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _build_cos(state_path: str, repo: str) -> tuple[ChiefOfStaff, object]:
    state = load_state(state_path)
    snapshot = inspect_git(repo)
    config = load_runtime_config("repo_config/runtime-policy.toml")
    policy = resolve_policy(state.policy_exceptions, config)
    profiles = load_profiles("agents")
    return (
        ChiefOfStaff(
            state=state,
            policy=policy,
            profiles=profiles,
            codex=CodexClient(),
            orca=OrcaClient(enabled=policy.orca_enabled),
        ),
        snapshot,
    )


def run_state_validate(args: argparse.Namespace) -> int:
    state = load_state(args.path)
    _print({"status": "valid", "goal": state.goal, "task_count": len(state.tasks)})
    return 0


def run_cos_next(args: argparse.Namespace) -> int:
    chief, snapshot = _build_cos(args.state, args.repo)
    _print(asdict(chief.next_decision(snapshot)))
    return 0


def run_runtime_inspect(args: argparse.Namespace) -> int:
    if args.runtime == "codex":
        observation = CodexClient().inspect(args.runtime_id)
    else:
        observation = OrcaClient().inspect(args.runtime_id)
    _print(asdict(observation))
    return 0


def run_accept(args: argparse.Namespace) -> int:
    state = load_state(args.state)
    task = next((item for item in state.tasks if item.id == args.task_id), None)
    if task is None:
        raise StateError(f"unknown task: {args.task_id}")
    snapshot = inspect_git(args.repo)
    verification = VerificationResult(
        status=args.status,
        passed=tuple(args.check),
        evidence_revision=args.revision or snapshot.revision,
    )
    decision = evaluate_acceptance(task, snapshot, verification)
    if decision.status in {"PASS", "BLOCKED"}:
        save_state(args.state, apply_task_transition(state, task.id, decision))
    _print(asdict(decision))
    return 0


def run_recover(args: argparse.Namespace) -> int:
    state = load_state(args.state)
    snapshot = inspect_git(args.repo)
    task = next_unfinished_task(state, snapshot)
    _print({"status": "ready" if task else "none", "task_id": task.id if task else None})
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="general-os")
    commands = parser.add_subparsers(dest="command", required=True)

    state = commands.add_parser("state")
    state_commands = state.add_subparsers(dest="state_command", required=True)
    validate = state_commands.add_parser("validate")
    validate.add_argument("path")
    validate.set_defaults(handler=run_state_validate)

    cos = commands.add_parser("cos")
    cos_commands = cos.add_subparsers(dest="cos_command", required=True)
    cos_next = cos_commands.add_parser("next")
    cos_next.add_argument("--state", required=True)
    cos_next.add_argument("--repo", required=True)
    cos_next.add_argument("--json", action="store_true")
    cos_next.set_defaults(handler=run_cos_next)

    runtime = commands.add_parser("runtime")
    runtime_commands = runtime.add_subparsers(dest="runtime_command", required=True)
    inspect = runtime_commands.add_parser("inspect")
    inspect.add_argument("--runtime", choices=("codex", "orca"), required=True)
    inspect.add_argument("--runtime-id", required=True)
    inspect.set_defaults(handler=run_runtime_inspect)

    accept = commands.add_parser("accept")
    accept.add_argument("--state", required=True)
    accept.add_argument("--repo", required=True)
    accept.add_argument("--task-id", required=True)
    accept.add_argument("--status", choices=("pass", "fail", "blocked"), required=True)
    accept.add_argument("--check", action="append", default=[])
    accept.add_argument("--revision")
    accept.set_defaults(handler=run_accept)

    recover = commands.add_parser("recover")
    recover.add_argument("--state", required=True)
    recover.add_argument("--repo", required=True)
    recover.set_defaults(handler=run_recover)

    orca = commands.add_parser("orca")
    orca_commands = orca.add_subparsers(dest="orca_command", required=True)
    smoke = orca_commands.add_parser("smoke")
    smoke.add_argument("--json", action="store_true")
    smoke.set_defaults(handler=run_orca_smoke)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (StateError, ValueError, OSError) as exc:
        parser.error(str(exc))
    return 2
