# hermes-subagent-output-guide

A Hermes user plugin that prevents subagents from writing files to arbitrary locations by injecting output-location guidance into their first turn.

Forgets to tell the subagent where to put the report? This plugin has your back.

## Injected guidance

On every subagent's first LLM call, the following block is appended to its user message:

```
<subagent-output-guide>

## Output Location Constraint

...

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
