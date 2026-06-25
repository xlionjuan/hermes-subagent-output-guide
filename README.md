# subagent-output-guide

A Hermes user plugin that prevents subagents from writing files to arbitrary locations by injecting output-location guidance into their first turn.

Forgets to tell the subagent where to put the report? This plugin has your back.

## Injected guidance

On every subagent's first LLM call, the following block is appended to its user message:

```
<subagent-output-guide>

## Output Location Constraint

This is an automated guidance injected by the Hermes plugin
system. It is not part of the original delegated task but is
a system-level constraint that must be followed.

When writing files, reports, or any other output as part of
your task:

- If the task **explicitly specifies** where to put the output,
  follow that instruction.
- If **no output location is specified**, write all output files
  to ``/tmp/``.
- Never write files to the home directory, project root, or other
  locations without explicit direction.

</subagent-output-guide>
```

## Installation

Clone to the Hermes user plugins directory:

```bash
git clone https://github.com/xlionjuan/subagent-output-guide.git \
    ~/.hermes/plugins/subagent-output-guide
```

## Enable

```bash
hermes plugins enable subagent-output-guide
```

Takes effect on the next session (`/reset` or restart Hermes).
