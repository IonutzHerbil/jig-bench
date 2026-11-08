# Jig benchmark results

Measured with `bench/` in October 2026. Raw per-sample results (code, errors, tokens, hidden-test outputs)
are in `bench/results/` (not committed); `python -m bench.report <file>` reproduces every table here.

## Method

A model gets a plain-language feature request and the function signature. It writes code, its toolchain
checks it, and errors go back to it for up to 4 attempts. The final code is then graded on **hidden tests the
model never sees**. Each sample ends in one of four outcomes:

| outcome | meaning |
| --- | --- |
| delivered | passed its own checks and every hidden test |
| false alarm | the code was correct, but its own checks blocked it, so nothing was delivered |
| silent bug | passed its own checks, but fails hidden tests: a bug that would ship |
| failed | wrong and blocked |

Toolchains compared:

| condition | the model writes | feedback before delivery |
| --- | --- | --- |
| `python` | Python plus its own pytest tests | crashes and failing tests (pytest) |
| `python-plain` | Python only | only whether the module imports |
| `jig` / `jig-short` | Jig, with the full (LANGUAGE.md) or short manual | `jig fix` + `jig check` (closed world, effects, newtypes, examples) |

Suites: 12 standalone functions (strings, parsing, data, business rules, interpreter, algorithms, state
machine, graphs), 8 feature requests in a store app (payments library, tiers, tax), 5 in a clinic app (calendar
and SMS libraries, time arithmetic). Hidden tests check exact results and the exact error kind; reference
solutions in both languages pass all of them. 3 samples per task and condition, temperature 1.

## Results

### Jig v0.1 (restrictive) lost to Python

On standalone tasks (gemini-flash-lite) v0.1 delivered 83-90% vs Python's 94-97%, needed ~2 attempts vs ~1.3,
and cost 5x the tokens. Its bans (while, try, None, comments) pushed models into hand-rolled code that misread
specs. This led to v0.2: correct idiomatic Python is valid Jig.

### Jig v0.2 vs Python with its own tests

| suite (gemini-flash-lite) | Jig delivered | Python delivered | Python false alarms | Jig tokens | Python tokens |
| --- | --- | --- | --- | --- | --- |
| standalone, 36 each | 94-100% | 97% | 0 | 1.3-4.3k | 1.2k |
| store project, 24 each | 96-100% | 75% | 6 | 4.1-9.0k | 6.5k |
| clinic project, 15 each | 93% | 67% | 5 | 5.3k | 9.2k |

| suite (gemini-flash-latest) | Jig delivered | Python delivered | Jig tokens | Python tokens |
| --- | --- | --- | --- | --- |
| store project, 24 each | 100% | 100% | 7.0k | 11.3k |

On project tasks Jig delivered more and cost less. But Python's **code** was as correct as Jig's every time:
its losses were false alarms, correct code blocked by wrong AI-written tests.

### Jig v0.2 vs Python with no verification at all

| suite (gemini-flash-lite, 3 samples per task) | Jig delivered | plain Python delivered | Jig tokens | plain Python tokens |
| --- | --- | --- | --- | --- |
| standalone, 36 each | 94% | 97% | 1.3k | 0.5k |
| store + clinic projects, 39 each | 100% | 100% | 4.3k | 2.2k |

**With the whole project visible in the prompt, unchecked Python was as correct as Jig at half the cost.**
The models made almost none of the mistakes Jig checks for, because every name they needed was in front of
them.

### Partial context: an agent that cannot see the whole codebase

The model sees the request, the shared types module, and only the *names* of the other modules and libraries,
like an agent in a codebase larger than its context. Same information for both languages.

| store + clinic projects (gemini-flash-lite, 39 samples each) | Jig | plain Python |
| --- | --- | --- |
| delivered correct | **64%** (25/39) | 15% (6/39) |
| silent bugs | 12 | 24 |
| store | 22/24 | 6/24 |
| clinic | 3/15 | 0/15 |

Both guessed wrong constantly (Jig 91 unknown imports, Python 86 import errors). Python's feedback was
"cannot import name X"; Jig's lists what exists ("it exports: charge, refund, ..."), and models converged on
the real API. Of Jig's 12 silent bugs, 10 were type errors the checker then learned to catch: looping over a
dict, which gives keys (6); an unused `ctx` parameter (2); a field missing from a library record (1); a library's
error type leaking out (1). The other 2 were spec misreadings.

## What this means so far

- When everything is visible, today's models rarely make the mistakes Jig checks for: unchecked Python was as
  correct as Jig at half the cost.
- When the model cannot see everything, the usual case in real codebases, Jig delivered correct code 4x as
  often and shipped half the bugs, because its errors carry the ground truth.
- Verification by AI-written tests is unreliable: on project tasks it blocked 25-33% of correct solutions.
  Jig's mechanical checks blocked correct code once in all v0.2 runs.
- Changes driven by these measurements: v0.2 (Python plus guarantees), `jig fix` and auto-imports, C006,
  Result/Option methods models expect, argument checks on library calls, errors that list what exists, and
  type flow through loops, containers, Result payloads and library records (T008, T009).

## Open

- Partial context after the type-flow checks (a re-run is pending), an ablation that switches the "lists what exists" feedback off.
- Interfaces context with the fixed (valid Jig) view: the header errors should disappear.
- Stub requests (`--request stub`): does a developer's stub with two examples beat the prose request alone, in
  delivered results and silent bugs, and does it help Jig (examples run by the checker) more than Python (a pytest
  function)? c04 has no stub: its only inputs are the three specialties, all of them hidden tests.
- Jig views now include the library fakes (`lib/*.fake.py`, bodies elided) that examples run against, as Python's
  library stubs always showed their module data: in earlier runs, 5 of 8 example-only repairs came from fake data
  the model could not see. Runs before 2026-11-08 lack them.
- Other model families, larger projects, multi-file features (`jig do`).
- Sample sizes are small (3 per task); differences under ~10 points are within noise.

## Is Jig easy to predict? (2026-10-19, gemini-flash-lite)

A model writes one token at a time, so a construct it cannot predict is a construct it gets wrong or leaves out.
`python -m bench.syntax predict` showed the model every reference solution up to a line and asked for the next
line: 622 lines of Jig and 294 of Python, scored by shape (names and values masked).

| Kind of line | Lines | Shape right |
| --- | --- | --- |
| Plain Python, in Python files | 294 | 39% |
| Plain Python, in Jig files | 287 | 38% |
| `Result` / `Ok` / `Err` | 117 | 63% |
| `?` | 26 | 38% |
| Examples | 80 | 28% |
| `effects:` / `examples:` clauses | 63 | 19% |
| `from std.result import ...` | 22 | 0% |

Errors in runs with the current toolchain (`python -m bench.syntax mistakes`), by what the model saw of the
project:

| | Full project | Partial (types module and module names) |
| --- | --- | --- |
| Samples | 75 | 42 |
| Errors per sample | 0.28 | 3.2 |
| Most common | examples (0.16 per sample), names (0.08) | names and imports (2.5 per sample), fields and arguments (0.4) |

A first reading pooled the two and reported 70% of errors as names; nearly all of those come from the partial
setting, where the model is never shown the names and has to guess (`find_doctor` became `get_doctor`, constants
were imported from the wrong module). With the project in view, models rarely get names wrong, and examples are
the most common mistake.

What it changed: Jig code is no harder to predict than Python, and its error handling is the most predictable part
of a file. The `std.result` import line was never predicted, so `Result`, `Ok`, `Err`, `Option`, `Some` and
`Nothing` became built in (jig-lang 0.3). Optional clauses are a fork models skip after a docstring: they are
rarely written unless something asks for them. For code bases too big to show whole, `--context interfaces` shows
every module without bodies (`jig interface`, which also lists inferred effects and examples, against Python
stubs).

## Interfaces context (2026-10-20, gemini-flash-lite, project tasks, 3 samples)

| | Python | Jig |
| --- | --- | --- |
| Delivered | 31 / 39 | 38 / 39 |
| False alarms (correct code the toolchain rejected) | 8 | 1 |
| Silent bugs | 0 | 0 |
| Mean attempts | 2.2 | 1.9 |

Name errors writing Jig fell from 2.5 per sample (partial) to 0.23: showing signatures removes nearly all the
guessing. Python's false alarms are its own tests asserting the wrong thing.

The run also found a defect in the view itself: `jig interface` printed `def f(x: int) -> T` without a colon and
`effects: net  (inferred)`, and models copied both (26 syntax errors on function headers, 0.67 per sample, and
two unknown-effect errors). The view is now valid Jig, like a `.pyi` stub (`def f(x: int) -> T:`, `...` bodies,
`# inferred` as a comment), which also changes the project map the Claude Code hook shows and `jig do` on large
projects. A re-run with the fixed view is pending.
