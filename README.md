# hermes-subagent-output-guide

A Hermes user plugin that prevents subagents from writing files to arbitrary locations by injecting output-location guidance into their first turn.

Forgets to tell the subagent where to put the report? This plugin has your back.

## Injected guidance

On every subagent's first LLM call, the following block is appended to its user message:

```
<subagent-output-guide>

## File Output Location

This guidance only applies if your delegated task requires you
to create output files. It does not require you to create a
file. If the task can be completed by replying in chat, reply
in chat.

If you do create output files:

- If the task **explicitly specifies** an output location, use
  that location.
- If **no output location is specified**, write output files
  to ``/tmp/``.
- Do not write output files to the home directory, project
  root, or other locations unless explicitly directed.

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
