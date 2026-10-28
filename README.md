# {{ project-name }}

{{ project_description }}

## Quick start

```bash
cargo run
```

## Repository checks

Every check lives in `scripts/validate_repo.py`, and both GitHub Actions and
pre-commit call that one file, so CI and local hooks cannot drift apart.

| Command | What it does |
| --- | --- |
| `python scripts/validate_repo.py all` | fmt, check, clippy, test, `cargo deny`, `typos` |
| `python scripts/validate_repo.py template-smoke` | generate a scratch project from the template and validate it |
| `python scripts/validate_repo.py fmt` | `cargo fmt --all -- --check` |

The script detects its own mode. While `Cargo.toml` still contains
cargo-generate placeholders it validates a throw-away generated project; once
the manifest is rendered it validates the project in place.

## Included by default

- `src/main.rs` with a minimal binary entrypoint
- `scripts/validate_repo.py` as the single source of truth for all checks
- a GitHub Actions `ci` workflow with a template smoke test, the quality checks
  and a minimum-supported-Rust-version job
- pre-commit hooks: file hygiene plus the same checks CI runs
- `cargo-deny`, `typos` and `git-cliff` configuration, ready for optional use
- dual license files for `MIT OR Apache-2.0`
- `.gitattributes` normalizing text files to LF

## CI behaviour

- Template repository: the `template-smoke` job generates a project from the
  template and validates the generated code. The `quality` and `msrv` jobs skip.
- Generated project: the `quality` and `msrv` jobs run, the smoke job skips.

## Local tool setup

```bash
python -m pip install pre-commit
cargo install --locked cargo-generate
cargo install --locked cargo-deny
cargo install --locked typos-cli
cargo install --locked git-cliff
```

## Generate from this template

```bash
cargo generate --path . --destination .. --name my-app
```

After you publish the template to your own GitHub repository:

```bash
cargo generate gh:<owner>/<repo> --name my-app
```

The `authors` placeholder is taken from your git config, so set it first:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## Changelog

```bash
git-cliff --unreleased --output CHANGELOG.md
```

`cargo-generate` fills the repository URLs in `cliff.toml` in automatically, so
no manual editing is needed after generating a project.

## Notes

- Replace the sample code in `src/main.rs` with your project logic.
- Review the optional package metadata (`homepage`, `documentation`, `keywords`,
  `categories`) in `Cargo.toml` before your first release.
- `rust-version = "1.85"` is the floor implied by `edition = "2024"`, and the
  `msrv` CI job enforces it.
- `.github/` and `scripts/` are listed under `exclude` in `cargo-generate.toml`:
  they are copied byte for byte instead of being rendered, so keep template
  syntax out of them.
