# rs-temp

rstemp

## Quick start

```bash
cargo run
```

## Useful commands

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
cargo install --locked cargo-deny
cargo install typos-cli
cargo install git-cliff
```

## Generate from this template

```bash
cargo generate --path . --name my_app
```

After you publish this fixed template to your own GitHub repository:

```bash
cargo generate gh:<owner>/<repo> --name my_app
```

## Notes

- Replace the sample code in `src/main.rs` with your project logic.
- Adjust package metadata in `Cargo.toml` to match your release policy.
- Update `repository`, optional `homepage`, and optional `documentation` metadata after generation.
- Update `cliff.toml` with your own repository URL before generating changelogs.
