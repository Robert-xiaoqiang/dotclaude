---
name: code-abstraction
description: "Find the concept several implementations share and consolidate them behind one contract as a codebase grows: name the role by its job, type the data that crosses the boundary, give each axis of variation its own interface, choose an interface, a base class, a capability interface or a plain function by what the variants actually share, select variants by name in config, and migrate without changing behaviour. Worked through a multi-environment RL mix: one rollout loop over single-turn, dialogue and tool-use environments, and one feedback contract over rubric judges, verifiers, unit tests and metrics."
when_to_use: "Use when a third implementation of one job arrives, when callers branch on a variant's type or kind, when parallel factories return the same kind of thing with different signatures, when a function keeps gaining mode flags, or when reviewing a base class, a registry or a plugin seam. Not for whether an input may default (code-no-fallbacks) or where a module lives (layout-workspace)."
---
# Skill: code-abstraction

## Purpose
A research codebase grows by addition: a second environment, a third scorer, a fourth reward. Each
arrives as a copy of its nearest neighbour with one step changed. A few months later the same job has
four names and four signatures, and a caller tells them apart with `if`. This skill is how to see the
one concept under the copies and give it a skeleton: a contract every variant honours, a loop written
once, and variants that plug in through config. Existing code is evidence of what the variants are,
never a model of how to structure them. Most repos, ours included, break the rules below in places,
and those places are where the work is.

## Contents
- [When to Use](#when-to-use)
- [The questions, in order](#the-questions-in-order)
- [Choosing the mechanism](#choosing-the-mechanism)
- [Worked example: a multi-environment RL mix](#worked-example-a-multi-environment-rl-mix)
- [Consolidating a family that already exists](#consolidating-a-family-that-already-exists)
- [What drift looks like](#what-drift-looks-like)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- A third implementation of one job is about to land, or just did.
- A caller branches on a variant: `isinstance`, `if kind == "rubric"`, `hasattr(x, "write_group")`.
- Several factories or classes return the same kind of thing under different names or signatures.
- One function keeps gaining mode flags such as `multi_turn=`, `tools=` or `judge=`.
- Adding a variant means editing files that are not about that variant.
- Reviewing a base class, a registry, a plugin seam or a `Protocol`.

Not for whether an input may carry a default (`code-no-fallbacks`), where an interface module or a
config file lives (`layout-workspace`, `naming-config`), or a one-off script that will not grow.

## The questions, in order
Each answer constrains the next, so the order matters.

1. **What job does it do in the loop?** Name the role by that job: rollout, environment, feedback,
   reducer, critic. A role named after its first implementation, such as a `RubricJudge` base for
   every scorer, cannot hold the second variant without lying. Every later reader takes the name as a
   claim about all of them.
2. **What crosses the boundary?** Write the values first, as dataclasses: what goes in, what comes out,
   and in which units. Two implementations that look different often agree completely once their
   inputs and outputs are typed. Two that look alike often disagree on what they return, a score in
   [0, 1] against a raw count. The data types are more of the contract than the method names are.
3. **What does every caller use?** The interface is the intersection of what callers call, never the
   union of what variants offer. Whatever one variant needs beyond that, a judge client, a sandbox, a
   timeout, an answer extractor, is a constructor argument fixed when the variant is built. A method
   signature that carries one variant's knob makes every variant accept it and every caller supply it.
4. **How many independent axes vary?** Interaction protocol, task domain, feedback kind and reduction
   change independently. Each axis gets its own interface, and a combination is a row of
   configuration. Classes per combination grow as the product of the axes. Interfaces grow as the sum.
5. **Which variant is the general case?** Build the skeleton on the general case and let the special
   case fall out as a parameter. Single-turn generation is a one-turn episode, and an accuracy metric
   is a feedback with one part. Built the other way round, the general case gets bolted on as flags.
6. **What do the variants share: a call shape, an algorithm, or a capability?** That decides the
   mechanism, in the next section.
7. **Where is the variant chosen?** In one place, from config, by name. Callers receive a built object
   and call its method, and never learn which variant they hold.

## Choosing the mechanism
Inheritance is one tool among several, and the most expensive to undo. Pick by what the variants share.

| the variants share | mechanism | in Python |
|---|---|---|
| a call shape and no code | an interface | `abc.ABC` whose methods are all abstract, for a family we own. `typing.Protocol` for objects we do not own |
| a fixed algorithm whose steps vary | a template method | a concrete method on the base that calls abstract hooks |
| a capability only some variants have | a second, small interface | its own ABC, inherited by the variants that have it |
| a stateless transformation | a function | a typed `Callable` alias, no class |
| a combination of parts | composition | an object holding one instance per axis |
| a set of fields | a record | a frozen `dataclass` |

**Inheritance, when it is the answer, stays narrow.** A subclass must work anywhere its base is
expected, so a subclass that stubs a base method out is evidence that the interface is too wide, and
the fix is to split the interface. Borrowing a helper is a function call, never a reason to inherit.
At most one level of behaviour sits between an interface and a concrete class, because each further
level is a base whose change breaks children nobody is looking at. An abstract method has no body
that returns a value. A base `score` that returns 0.0 turns a forgotten implementation into a zero
reward that trains.

Three Python details, each a failure seen in practice:

- **An ABC fails at construction, a Protocol fails at call time.** A class that misses an abstract
  method cannot be instantiated, so the gap shows at startup. The same gap under a `Protocol` shows
  when the method is first called, which may be step 900. Prefer the ABC for a family we own.
- **`@runtime_checkable` checks names, never signatures.** `isinstance(x, SomeProtocol)` passes for
  any object with methods of the right names, whatever arguments they take. It cannot stand in for a
  declared base.
- **A framework's calling convention stays at the edge.** TRL calls a reward function as
  `f(prompts=..., completions=..., **columns)`. Write one adapter from that shape to the family's own
  contract, rather than letting every reward take TRL's shape and its open `**columns`.

## Worked example: a multi-environment RL mix
One policy trains on a mixture: math with a checkable answer, health dialogue graded by rubric, and
code repair graded by unit tests. Each domain tends to arrive with its own rollout function and its
own reward factory. The questions above give one loop and three interfaces instead.

**The values that cross every boundary:**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Task:
    source: str              # the mixture entry it was drawn from
    prompt: tuple            # chat messages
    reference: dict          # what its feedback reads: an answer, rubric items, unit tests

@dataclass(frozen=True)
class Turn:
    role: str                # "policy", "user" or "tool"
    content: str
    tool_calls: tuple = ()

@dataclass
class Episode:
    task: Task
    turns: list = field(default_factory=list)
    truncated: bool = False

@dataclass(frozen=True)
class Feedback:
    score: float             # in [0, 1], whatever produced it
    parts: dict              # per rubric item, per test, per check
    evidence: str            # judge rationale, test log, extracted answer
```

**One interface per axis, and the loop written once:**

```python
class Environment(ABC):
    """Who answers the policy. Single-turn, dialogue and tool use differ only here."""
    @abstractmethod
    def reply(self, episode: Episode) -> Turn | None: ...      # None ends the episode

class FeedbackSource(ABC):
    """How an episode is judged. Rubrics, verifiers, unit tests and metrics differ only here."""
    @abstractmethod
    def score(self, episodes: list[Episode]) -> list[Feedback]: ...

def rollout(policy, env: Environment, task: Task, max_turns: int) -> Episode:
    ep = Episode(task)
    for _ in range(max_turns):
        ep.turns.append(policy.act(ep))
        reply = env.reply(ep)
        if reply is None:
            return ep
        ep.turns.append(reply)
    ep.truncated = True
    return ep
```

A base rollout with single-turn, dialogue and tool-call kinds is therefore not three rollout
subclasses. The loop is the same in all three. What varies is who answers the policy, so the
environment is the polymorphic part:

| environment | `reply` returns | constructor takes |
|---|---|---|
| `SingleTurn` | `None`, always | nothing |
| `SimulatedUser` | the user model's next message, `None` once it is satisfied | a user model |
| `ToolSandbox` | the results of the last turn's tool calls, `None` when it made none | a sandbox |

Feedback works the same way. Each source needs something different, and that goes to its constructor,
so `score` keeps one signature:

| feedback source | reads from `task.reference` | constructor takes |
|---|---|---|
| `RubricJudge` | the rubric items | a judge client |
| `AnswerVerifier` | the answer | an extractor and an equivalence check |
| `UnitTests` | the tests | a sandbox and a timeout |
| `ExactMatch` and other metrics | the answer | nothing |

`score` takes a batch because judges and sandboxes are batched. A per-episode method would push the
batching into every caller.

**A reward is a reduction over feedback, which is a separate axis.** Training wants one scalar per
episode, perhaps a weighted sum of parts minus a length penalty. Evaluation wants accuracy or pass@k
over many episodes. One `UnitTests` source serves both, and only the reducer differs. Fusing the two
produces a unit-test reward and a unit-test metric that drift apart.

**The mixture is configuration.** Each entry names its source, weight, environment and feedback:

```yaml
mixture:
  - {source: gsm8k,       weight: 0.3, env: single_turn,    feedback: answer_verifier}
  - {source: healthbench, weight: 0.3, env: simulated_user, feedback: rubric_judge}
  - {source: swe_lite,    weight: 0.4, env: tool_sandbox,   feedback: unit_tests}
```

The composition root builds one environment and one feedback source per entry, keyed by `source`. At
load it checks that every task carries the reference keys its feedback reads, so a missing rubric
fails before the first step. The trainer looks each task up in that table and names no domain. A
fourth domain is one config row plus at most one new class.

## Consolidating a family that already exists
Most consolidation happens to code that already runs and already has results attached, so the
procedure protects behaviour first.

1. **Inventory.** List every implementation of the role in a table: name, inputs, outputs and their
   units, dependencies, side effects, callers. Grep for the role's synonyms as well (scorer, judge,
   grader, reward_fn, verifier), because a family is usually spread across several names.
2. **Record golden outputs.** Run each variant on a small fixed input and save what it returns. This
   is the test that the consolidation changed nothing.
3. **Write the contract** from the questions above: the data types, one interface per axis, the
   mechanism.
4. **Move one variant per commit** behind the contract, and compare its golden output each time. When
   something differs, one move did it.
5. **Keep every persisted name.** A class path in a config, a pickled object, a checkpoint and a
   run-identity hash all name code from outside it. Leave an alias at the old import path until every
   persisted reference has moved. A repo that hashes its resolved config, as AutoRSI does with every
   `class_path` in it, otherwise gives each old run a new identity, and resume starts from step zero.
6. **Delete the caller branches last**, once every variant answers the contract.
7. **Accept on the next variant.** Adding one should take a new file and a config entry, with no edit
   to any caller. If it takes more, the skeleton is not done.

## What drift looks like
Found in AutoRSI at `53d19e9`, recorded as symptoms to fix, not patterns to copy:

- **A contract held by convention alone.** Four scorers answer `__call__(records, max_workers)` and
  four critics answer `value` and `update`, and no base declares either. Drift has already started:
  two critics take `value(state=None)` and two take `value(state)`.
- **Capabilities probed by name.** The GRPO loop calls `write_group` only when
  `hasattr(self.critic, "write_group")`, and the trainer reads `getattr(rubric, "schedule", None)`. A
  misspelt method there raises nothing. The feature switches off without a word.
- **One role, several shapes.** Each reward factory takes its own keyword set, and one takes only
  `**kw`, so a misspelt knob is accepted and ignored.

## Rules
1. **A role is named by its job in the loop, never after its first implementation.** The name is read
   as a claim about every variant.
2. **Abstract at the third variant, or at the first caller that branches on type.** Two variants do
   not show which differences are essential, and a wrong abstraction costs more to unwind than
   duplication costs to keep.
3. **The data that crosses a boundary is typed before any interface is written.** Most apparent
   disagreements between variants are untyped data, and most hidden ones are units.
4. **An interface is the intersection of what callers call.** What one variant needs beyond that is a
   constructor argument.
5. **One interface per independent axis of variation. A combination is a config row, never a class.**
   Classes per combination grow as the product of the axes.
6. **The skeleton is built on the general case.** A special case that is a parameter of the general
   one, one turn or one part, is not a subclass of it.
7. **Inheritance carries a shared algorithm or a substitutable kind, nothing else.** Reusing a helper
   is a function call, and at most one level of behaviour sits between an interface and a concrete class.
8. **A subclass that stubs out a base method means the interface is too wide.** Split the interface
   rather than adding the stub.
9. **An optional capability is its own declared interface, checked once where the object is built.**
   Probing for a method by name at the call site lets a typo disable a feature without an error.
10. **Callers never branch on a variant.** No `isinstance`, no `if kind ==`, no `hasattr`. Dispatch is
    the variant's own method, or one table at the composition root.
11. **A variant is selected in one place, from config, by name, and an unknown name fails loudly.** A
    registry that falls back to a default class is the silent relocation `code-no-fallbacks` forbids.
12. **An abstract method has no body that returns a value.** A neutral return value turns a missing
    implementation into a plausible result.
13. **A consolidation changes no behaviour.** Golden outputs are recorded before it starts and compared
    after each moved variant.
14. **A name persisted outside the code is public.** Config class paths, pickles, checkpoints and run
    hashes keep an alias at the old path until every reference has moved.
15. **The skeleton is done when the next variant edits no caller.** That is the acceptance test, and
    the only one that measures what the work was for.

## Anti-patterns
- **The pair abstraction.** Two similar classes merged into a base on sight, tempting because the
  duplication is visible now. The third variant then differs on the axis the base fixed, and the base
  grows a flag.
- **The flag-accreting function.** `generate(..., multi_turn=False, tools=None, user=None)`. Each flag
  was a one-line change. Together they form a class hierarchy that no type checker can see.
- **The kwargs sponge.** `make_reward(**kw)` accepts every variant's knobs and so declares none of
  them. It ends arguments about the signature, and it ends the error on a misspelt name too.
- **The combination class.** `MultiTurnToolRubricRollout` feels specific and safe. It is one cell of a
  product, and no other cell can reuse it.
- **The god base.** A base class collecting helpers that one subclass each uses, tempting because the
  base is imported everywhere already. Every subclass now depends on all of it.
- **The convention-only contract.** Variants agree on a method shape because each was copied from the
  last, and nothing declares it. The next copy drifts and nothing notices.
- **The big-bang consolidation.** Every variant rewritten in one change. When an output moves, nobody
  can say which edit moved it, and the whole change gets reverted.
- **The default variant.** A registry or factory that returns some reasonable class for an unknown
  name. The run proceeds with the wrong component and reports success.

## Companions
`code-no-fallbacks` (the loud-failure rule for inputs, which rules 11 and 12 apply to variants) ·
`layout-workspace` (where the contract module and each implementation live, and why an interface
lives with its consumer) · `config-composition` (`class_path` as the only seam, the config half of
rule 10) · `naming-config` (how a config names a variant) · `config-variants` (the launcher selects,
the config specifies) · `docs-arch` (where a project records its roles and their contracts) ·
`conventions` (the family index).
