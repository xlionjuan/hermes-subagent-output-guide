# vulture whitelist — intentionally unused parameters in hook callbacks
# Hook callbacks accept kwargs via named parameters for clarity; unused
# ones are caught by **_: Any.

_on_subagent_start  # unused function reference (register() wires it)
_on_pre_llm_call  # unused function reference (register() wires it)
