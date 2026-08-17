"""GENERIC layout-walk checker — instantiate per project, do not edit the rules here.

Locks the four associations the layout-workspace/naming-config skills promise:
  A1  every group config's class_path imports, and the config's family subdir mirrors the module
  A2  every `_base_` chain is a name-prefix walk (assembly inheritance visible in the name)
  A3  the name carries the CLASS walk: resolve the config's class — INCLUDING owned sub-objects'
      class_paths (e.g. trainer.class_path), never just a module entry point — and require the
      name to contain the segment of any named backbone in its MRO
  A4  every launcher selector resolves to a real group config
  A5  no config inherits a BACKBONE's own constructor kwargs onto a chain that cannot accept them:
      for each named backbone, a config resolving to a NON-subclass must carry none of the
      backbone's __init__ params in its merged kwargs — MINUS the params the target class itself
      accepts (a name can be both a backbone param and a legitimate param of another trainer;
      flagging the raw intersection produced a false positive within minutes of the true positive).
      This turns constructor-kwarg drift into a pre-submit failure instead of a pod death an hour
      of queueing later.

INSTANTIATE by writing a thin project adapter that supplies:
  paths_of(group)   -> iterable of the group's yaml paths (the project's ONE resolver — see
                       "One resolver owns a group's paths" in the skill)
  GROUP_KEYS        -> {group: top-level yaml key}
  BACKBONES         -> {class name: required name segment}
  KNOWN_DEBTS       -> tuple of name prefixes that predate a rule: reported every run, failing
                       only under --strict. A debt list is a decision queue; silencing is a
                       blindfold. The goal state is the empty tuple.
Example instantiation: AutoRSI scripts/checks/layout_walk.py (found the harness family's hidden
DualRole inheritance as 41 declared debts on first run — after a first draft that read only the
module entry point and reported zero, which is a checker asserting nothing).
"""
# The rule bodies are identical to the instantiation; copy this file and wire the adapter.
