# Jig benchmark

Measures whether AI models build correct software more reliably with Jig than with Python, and decides which
of Jig's rules stay: a rule has to catch more bugs than it costs. The language itself is
[jig-lang](https://github.com/IonutzHerbil/jig-lang); this repository is the research behind it.

```bash
pip install -e ../jig-lang        # the language, from a clone next to this one (or: pip install jig-lang)
pip install -e .[dev]             # add [xai] for the SHAP and LIME analysis
pytest                            # every reference solution delivers; no model needed
```

Models are Gemini, through `GEMINI_API_KEY`. Results and their caveats: [RESULTS.md](RESULTS.md).

## Feature requests (`run.py`)

A model gets a plain-language request and a function signature, repairs its code against its toolchain for up
to 4 attempts, and is graded on hidden tests it never sees.

```bash
python -m bench.run --model gemini-flash-lite-latest --samples 3 --conditions python,python-plain,jig-short
python -m bench.run --model reference          # no model: every reference solution must deliver
```

| Option | Meaning |
| --- | --- |
| `--conditions` | `python` (writes its own pytest tests), `python-plain` (no checks), `jig` (full manual), `jig-short` (short manual), `jig-probe`, `jig-learned` |
| `--tasks` | id prefixes: `0`/`1` standalone functions, `p` store app, `c` clinic app |
| `--context partial` | app tasks show only the types module and the names of other modules |
| `--resume <file>` | continue an interrupted run |

Tasks live in `bench/tasks/<id>/` (request, signatures, hidden tests, reference solutions in both languages); the
apps they extend live in `bench/projects/`.

## Engineering scenarios (`agent.py`)

An agent works in a real repository with LIST, READ, SEARCH, WRITE, EDIT, CHECK and DONE on a step budget, and is
graded on hidden tests plus the repository's own suite. `python` works in `bench/repos/billing/python` and checks
with the tests; `jig` works in `bench/repos/billing/jig`, the same code ported to Jig, and checks with `jig check`
and then the tests against the compiled program. Tests confirm each scenario's reference fix delivers in both.

```bash
python -m bench.agent --model gemini-flash-lite-latest --samples 2
python -m bench.agent --model reference        # every reference fix must deliver
```

Scenarios live in `bench/se_tasks/<id>/`: the request, an optional `start/` overlay (a planted bug, an upgraded
library), hidden tests, and a `reference/` fix.

## Is Jig easy to predict? (`syntax.py`)

A model writes one token at a time, so a language is easy for models when each next line is the obvious one.

```bash
python -m bench.syntax mistakes          # free: every error in past runs, by what it was about
python -m bench.syntax predict --model gemini-flash-lite-latest   # next-line prediction on every reference solution
python -m bench.syntax report bench/results/<file>.jsonl
```

`predict` shows the model each reference solution, in Jig and in Python, up to a line and asks for the next one;
a line is scored exactly and by shape (names and values masked). In Jig files, plain Python lines are the baseline
for each of Jig's own constructs.

## Reading results

| Command | Gives |
| --- | --- |
| `python -m bench.report <results.jsonl>...` | delivered, false alarms, silent bugs, attempts and tokens per condition |
| `python -m bench.explain <results.jsonl>... --xai -o page.html` | an explorer page: every sample's attempts and feedback, plus SHAP and LIME explanations |
| `python -m bench.regrade <results.jsonl>` | re-grade results recorded before blocked code was graded |
| `python -m bench.learn <results.jsonl>...` | mistakes models keep making, as hints (`jig/cards/learned.md` in the jig-lang checkout) |

Raw results go to `bench/results/` (not committed).
