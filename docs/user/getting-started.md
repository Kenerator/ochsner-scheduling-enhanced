# Getting started

Use the [scheduling README](../../README.md#run) for Python3.11+, public clone,
installation and CLI/Marimo setup. The [normal Ochsner launcher](../../README.md#normal-ochsner-launcher)
starts its own synthetic API and model host, resolving the dedicated Bitwarden
item's scalar notes field privately. `--doctor` is key-free and makes no model
request; use free ports and Ctrl-C to stop only this launch's children.

The default model remains `gpt-5.4-mini`; `OPENAI_MODEL` configures it and
`--model MODEL` overrides it explicitly. Missing credentials/configuration never
select offline mode. There is no interactive Enhanced offline app; the
[deterministic demos](../../README.md#verify) are explicitly scripted and no-call.
[Direct reviewer commands](../../README.md#direct-reviewer-entrypoints) remain
available without a vault dependency. The launcher is currently Mac ARM
qualified; no new live language or cross-platform qualification is claimed.

The application interprets public text with a real model and keeps synthetic
identity local. Original generic poc_demo commands are retained for template
tests, not scheduling acceptance.

Choose an API-returned slot, inspect the exact proposal and separately confirm. Ordinary yes and selection alone do not book. See [recovery](recovery.md).
