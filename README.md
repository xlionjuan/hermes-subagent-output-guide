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
