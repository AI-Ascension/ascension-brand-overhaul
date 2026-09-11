# Tested developer quickstart

Ascension's flagship repository is currently named
[AI-Ascension/sts2-harness](https://github.com/AI-Ascension/sts2-harness).
The public display name is **Ascension**; the repository/package/binary names
remain unchanged until a separately approved rename. This path runs the
existing offline Runtime-v2 fake record workflow. It does not launch Slay the
Spire 2, read a save, call a model provider, or require credentials.

## Prerequisites

Use Git, `rustup`, and a working Rust toolchain. The repository pins Rust
`1.97.1` in `rust-toolchain.toml`; the verification below used:

```text
rustup show active-toolchain
1.97.1-x86_64-unknown-linux-gnu (overridden by .../sts2-harness/rust-toolchain.toml)
cargo --version
cargo 1.97.1 (c980f4866 2026-06-30)
rustc --version
rustc 1.97.1 (8bab26f4f 2026-07-14)
```

No game installation, provider key, MCP server or gateway process is required.
Fetching source and locked Cargo dependencies needs network access. After that
preparation, `--offline` prevents dependency network access during the fake run.

## Fetch the exact source

```sh
git clone --branch main --single-branch https://github.com/AI-Ascension/sts2-harness.git
cd sts2-harness
git checkout cb17b6c15262ce9356f1e85fd475af997aedc445
cargo fetch --locked
```

The commands below were run at that exact commit. Give every parallel
worktree its own target directory; this verification used
`/tmp/ai-ascension-brand-w04-harness-target`.

## Run the bounded record workflow

```sh
CARGO_TARGET_DIR=/tmp/ai-ascension-brand-w04-harness-target \
  cargo run --locked --offline --package sts2-harness \
  --bin sts2-harness-runtime-v2-fake
```

Observed result on 2026-09-07: exit `0`, with
`schema_bytes_verified: true`, `mutation_count: 1`,
`duplicate_replay_without_second_application: true`,
`stale_epoch_rejected: true`, and
`no_blind_retry_after_disconnect: true`. The ordered fake record contains
`requested`, `accepted`, `unknown`, `reconciled`, and `settled` outcomes and
ends at generation 5. This is deterministic offline component evidence, not a
host, provider, deployment, autonomous-play, or win claim.

Run the focused regression test as an optional second check:

```sh
CARGO_TARGET_DIR=/tmp/ai-ascension-brand-w04-harness-target \
  cargo test --locked --offline --package sts2-harness --test runtime_v2
```

Observed result on 2026-09-07: exit `0`; 3 tests passed. The test covers the
copied Runtime-v2 artifact, the fake reconciliation/replay/fencing trace, and
rejection of an omitted envelope field.

For the complete target gate, use the commands in the repository's
`docs/TESTING.md`. Those gates remain source/build/test evidence and do not
promote this quickstart to host or release compatibility.
