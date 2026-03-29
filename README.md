# {{ project-name }}

{{ project_description }}

## Quick start

```bash
cargo run
```

## Useful commands

These commands apply after you generate a project from the template.

```bash
cargo fmt
cargo clippy --all-targets --all-features -- -D warnings
cargo test
```

## Included by default

- `src/main.rs` with a minimal binary entrypoint
- GitHub Actions CI for `fmt`, `check`, `clippy`, and `test`
- `pre-commit` hooks for the same local quality checks
- Optional engineering configs for `cargo-deny`, `typos`, and `git-cliff`
- Dual-license files for `MIT OR Apache-2.0`

## Optional tool setup

```bash
python -m pip install pre-commit
cargo install --locked cargo-deny
cargo install typos-cli
cargo install git-cliff
cargo install cargo-generate
```

## Generate from this template

```bash
cargo generate --path . --name my-app
```

After you publish this fixed template to your own GitHub repository:

```bash
cargo generate gh:<owner>/<repo> --name my-app
```

## Notes

- Replace the sample code in `src/main.rs` with your project logic.
- Review the generated package metadata in `Cargo.toml` before your first release.
- If you use `pre-commit` in the template repository, install `pre-commit`, `cargo-generate`, `cargo-deny`, and `typos-cli` first.
- Generated projects only need the regular Rust tooling and any hooks you keep enabled.
- Update `cliff.toml` with your own repository URL before generating changelogs.
