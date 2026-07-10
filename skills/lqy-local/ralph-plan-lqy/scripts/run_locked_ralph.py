#!/usr/bin/env python3
"""Run Ralph while holding the current worktree's OS file lock."""
from __future__ import annotations

import argparse
import fcntl
import os
import signal
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from types import FrameType


def git_worktree_root(path: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise OSError(f"cannot resolve Git worktree: {detail}")
    return Path(result.stdout.strip()).resolve()


def run_locked(worktree: Path, command: Sequence[str]) -> int:
    root = git_worktree_root(worktree)
    state_dir = root / ".ralph"
    state_dir.mkdir(exist_ok=True)
    lock_path = state_dir / "worker.lock"

    with lock_path.open("a+", encoding="utf-8") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(f"LOCK BUSY: another Ralph worker holds `{lock_path}`", file=sys.stderr)
            return 2

        lock_file.seek(0)
        lock_file.truncate()
        lock_file.write(f"pid={os.getpid()}\n")
        lock_file.flush()

        child = subprocess.Popen(command, cwd=root, start_new_session=True)
        previous_handlers: dict[int, signal.Handlers] = {}

        def forward(signum: int, _frame: FrameType | None) -> None:
            if child.poll() is None:
                os.killpg(child.pid, signum)

        for signum in (signal.SIGINT, signal.SIGTERM):
            previous_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, forward)
        try:
            return child.wait()
        finally:
            for signum, handler in previous_handlers.items():
                signal.signal(signum, handler)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a command while holding `.ralph/worker.lock`.")
    parser.add_argument("--worktree", default=".", help="Target Git worktree path.")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after `--`.")
    args = parser.parse_args(argv)
    if args.command[:1] == ["--"]:
        args.command = args.command[1:]
    if not args.command:
        parser.error("a command is required after `--`")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        return run_locked(Path(args.worktree), args.command)
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
