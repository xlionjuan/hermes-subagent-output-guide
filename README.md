# hermes-subagent-output-guide

A Hermes user plugin that prevents subagents from writing files to arbitrary locations by injecting output-location guidance into their first turn.

Forgets to tell the subagent where to put the report? This plugin has your back.

## Injected guidance

On every subagent's first LLM call, the following block is appended to its user message:

```
<subagent-output-guide>
Parent task instructions take priority. Use this only as a fallback when the parent does not specify output details. If you create files, use the parent-specified path when given; otherwise use /tmp/. Use descriptive filenames and mention created file paths in your response. For large reports, write the full content to /tmp/; do not include the full report in the response. For temporary artifacts (coverage, logs, scripts, tables, generated data, debug output, etc.), save them under /tmp/ when useful. Reply with the key findings, decisions, or next steps, plus the file paths. If the task needs substantial output but you lack file tools, say so neutrally so the parent can add them next time for review.
</subagent-output-guide>
```

## Installation

Clone to the Hermes user plugins directory:

```bash
git clone https://github.com/xlionjuan/hermes-subagent-output-guide.git \
    ~/.hermes/plugins/hermes-subagent-output-guide
```

## Enable

```bash
hermes plugins enable hermes-subagent-output-guide
```

Takes effect after a gateway restart (`/restart` or restart the Hermes gateway service).

## Using in other profiles

To make this plugin available in another Hermes profile, create a symlink
under that profile's `plugins/` directory:

```bash
mkdir -p ~/.hermes/profiles/<profile>/plugins
ln -s ../../../plugins/hermes-subagent-output-guide \
    ~/.hermes/profiles/<profile>/plugins/hermes-subagent-output-guide
```

Then enable it from that profile:

```bash
hermes plugins --profile <profile> enable hermes-subagent-output-guide
```

> **Note:** The symlink target `../../../plugins/hermes-subagent-output-guide`
> is relative and resolves from `~/.hermes/profiles/<profile>/plugins/` back
> to the canonical install at `~/.hermes/plugins/`. This keeps a single copy
> of the plugin shared across profiles.
