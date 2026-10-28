#!/usr/bin/env python3
"""Repository checks for the ``rs-temp`` cargo-generate template.

GitHub Actions and pre-commit both call this file, so the template repository
and the projects generated from it cannot drift apart.

Two modes are detected automatically:

``template``
    ``Cargo.toml`` still holds cargo-generate placeholders, so the manifest is
    not valid cargo metadata. The checks run against a throw-away project that
    is generated into a temporary directory.

``project``
    ``Cargo.toml`` is already rendered, so every check runs in the repository
    itself.

Examples::

    python scripts/validate_repo.py all
    python scripts/validate_repo.py template-smoke
    python scripts/validate_repo.py fmt

Exit code is 0 only when every requested check passed.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parent.parent

# Builtin cargo-generate placeholders plus the ones declared in
# cargo-generate.toml. None of them may survive rendering.
PLACEHOLDER_TOKENS = (
    "project-name",
    "crate_name",
    "project_description",
    "github_user",
)

# Copied verbatim by cargo-generate (see ``exclude`` in cargo-generate.toml), so
# they legitimately keep their braces. cliff.toml keeps its Tera braces because
# git-cliff, not cargo-generate, expands them.
AUDIT_SKIP_DIRS = {".git", "target", ".github", "scripts"}
AUDIT_SKIP_FILES = {"cliff.toml"}

SMOKE_DEFINES = (
    "project_description=Template smoke test project",
    "github_user=template-smoke",
)

CARGO_CHECKS = {
    "fmt": ["cargo", "fmt", "--all", "--", "--check"],
    "check": ["cargo", "check", "--all-targets", "--locked"],
    "clippy": [
        "cargo",
        "clippy",
        "--all-targets",
        "--all-features",
        "--locked",
        "--",
        "-D",
        "warnings",
    ],
    "test": ["cargo", "test", "--all-targets", "--all-features", "--locked"],
    "deny": ["cargo", "deny", "check"],
}

CHECK_ORDER = ("fmt", "check", "clippy", "test", "deny", "typos")


def run(argv: Sequence[str], cwd: Path) -> None:
    """Run one command in ``cwd``, streaming its output; abort on failure."""
    printable = " ".join(argv)
    print(f"==> {printable}  (cwd: {cwd})", flush=True)
    completed = subprocess.run(list(argv), cwd=str(cwd))
    if completed.returncode != 0:
        raise SystemExit(f"FAILED with exit code {completed.returncode}: {printable}")


def require(tool: str, hint: str) -> None:
    if shutil.which(tool) is None:
        raise SystemExit(f"missing required tool `{tool}`: {hint}")


def is_template_repo() -> bool:
    """True while Cargo.toml is still an unrendered template manifest."""
    manifest = ROOT / "Cargo.toml"
    if not manifest.is_file():
        raise SystemExit(f"no Cargo.toml found in {ROOT}")
    text = manifest.read_text(encoding="utf-8")
    return any(token in text for token in PLACEHOLDER_TOKENS)


def audit_rendered_tree(tree: Path) -> None:
    """Fail when cargo-generate placeholders survived the rendering step."""
    leftovers: list[str] = []
    for path in sorted(tree.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(tree)
        if AUDIT_SKIP_DIRS.intersection(relative.parts):
            continue
        if relative.name in AUDIT_SKIP_FILES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        leftovers.extend(
            f"{relative}: {token}" for token in PLACEHOLDER_TOKENS if token in text
        )
    if leftovers:
        raise SystemExit(
            "unrendered placeholders in the generated project:\n  "
            + "\n  ".join(leftovers)
        )
    print("==> placeholder audit: clean", flush=True)


def generate_scratch_project() -> Path:
    """Generate the template into a temporary directory and return its path."""
    require("cargo", "install cargo-generate: cargo install cargo-generate")
    probe = subprocess.run(
        ["cargo", "generate", "--version"],
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0:
        raise SystemExit("the cargo-generate subcommand is not installed")

    scratch = Path(tempfile.mkdtemp(prefix="rs-temp-smoke-"))
    argv: list[str] = [
        "cargo",
        "generate",
        "--path",
        str(ROOT),
        "--name",
        "template-smoke",
        "--destination",
        str(scratch),
        "--vcs",
        "none",
    ]
    for define in SMOKE_DEFINES:
        argv.extend(["--define", define])
    run(argv, cwd=ROOT)

    project = scratch / "template-smoke"
    if not (project / "Cargo.toml").is_file():
        raise SystemExit(f"generation produced no project at {project}")
    return project


def run_named_check(name: str, project: Path) -> None:
    if name in CARGO_CHECKS:
        if name == "deny":
            require("cargo-deny", "cargo install --locked cargo-deny")
        run(CARGO_CHECKS[name], cwd=project)
        return
    if name == "typos":
        require("typos", "cargo install typos-cli")
        run(["typos"], cwd=project)
        return
    raise SystemExit(f"unknown check: {name}")


def unknown_commands(commands: Sequence[str]) -> list[str]:
    valid = {"all", "template-smoke", *CARGO_CHECKS, "typos"}
    return [name for name in commands if name not in valid]


def expand(commands: Sequence[str]) -> list[str]:
    """Expand ``all`` and drop duplicates while keeping the requested order."""
    expanded: list[str] = []
    for name in commands:
        for item in CHECK_ORDER if name == "all" else (name,):
            if item not in expanded:
                expanded.append(item)
    return expanded


def main(argv: list[str]) -> int:
    requested = argv[1:] or ["all"]
    unknown = unknown_commands(requested)
    if unknown:
        raise SystemExit(
            "unknown command(s): {} (valid: all, template-smoke, {})".format(
                ", ".join(unknown), ", ".join([*CARGO_CHECKS, "typos"])
            )
        )

    template_mode = is_template_repo()
    print(f"==> mode: {'template' if template_mode else 'project'} ({ROOT})", flush=True)

    workdir = ROOT
    scratch: Path | None = None
    if template_mode:
        # The template manifest is not valid cargo metadata, so generate a
        # scratch project and validate that instead.
        workdir = generate_scratch_project()
        scratch = workdir.parent
        audit_rendered_tree(workdir)

    try:
        for name in expand(requested):
            if name == "template-smoke":
                if template_mode:
                    print(f"==> template-smoke OK ({workdir})", flush=True)
                else:
                    print("==> template-smoke skipped: already a generated project")
                continue
            run_named_check(name, workdir)
    finally:
        if scratch is not None:
            if os.environ.get("VALIDATE_REPO_KEEP") == "1":
                print(f"==> kept scratch project: {scratch}", flush=True)
            else:
                shutil.rmtree(scratch, ignore_errors=True)

    print("==> all requested checks passed", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
