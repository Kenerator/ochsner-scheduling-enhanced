# Getting started

Use the [scheduling README](../../README.md#run) for Python3.11+, public clone,
installation and CLI/Marimo setup. The [normal Ochsner launcher](../../README.md#normal-ochsner-launcher)
starts its own synthetic API and model host, explicitly selecting own Secure Note
`[Env] OPENAI_API_KEY` and resolving its scalar notes field privately. The
Ochsner-supplied key is paused until explicit resumption; no fallback selects it.
`--doctor` is key-free and makes no model
request; use free ports and Ctrl-C to stop only this launch's children.

The default model remains `gpt-5.4-mini`; `OPENAI_MODEL` configures it and
`--model MODEL` overrides it explicitly. Missing credentials/configuration never
select offline mode. There is no interactive Enhanced offline app; the
[deterministic demos](../../README.md#verify) are explicitly scripted and no-call.
[Direct reviewer commands](../../README.md#direct-reviewer-entrypoints) remain
available without a vault dependency. Historical launcher checks were on Mac ARM;
the [current credential binding](../internal/model-qualification-binding.json)
separately records own-key-policy adaptation and its qualification limits.

The application interprets public text with a real model and keeps synthetic
identity local. Original generic poc_demo commands are retained for template
tests, not scheduling acceptance.

Choose an API-returned slot, inspect the exact proposal and separately confirm. Ordinary yes and selection alone do not book. See [recovery](recovery.md).
