# hermes-subagent-output-guide

A Hermes user plugin that guides subagents to keep concise text reports in the
response and save long reports to a specified location or `/tmp/`.

Forgets to tell the subagent where to put the report? This plugin has your back.

## Injected guidance

On every subagent's first LLM call, the following block is appended to its user message:

```
<subagent-output-guide>

## Text Report Delivery

This guidance applies only to text reports. It does not apply to source
code, tests, project documentation, scripts, data, logs, build outputs,
or any other non-report files.

Follow any explicit delivery instructions in the delegated task.

- For a concise report, respond directly unless the task requests a file.
- If the report would make the final response long, proactively save the
  detailed report to a text file instead of placing most of it in the
  final response.
- Use the report location specified by the delegated task. If none is
  specified, save the report under ``/tmp/``.
- When a report file is created, keep the final response concise and include
  the key findings, decisions, or next steps together with the report's
  absolute path.

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
