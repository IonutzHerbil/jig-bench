"""Which parts of Jig's syntax models get right: is Jig easy to predict?

A model writes code one token at a time, so a language is easy for a model when each next token is the obvious
one. Two measurements, both broken down by the kind of line (a plain Python line, or one of Jig's own constructs):

    python -m bench.syntax mistakes                       # free: the errors in every past run, by kind of line
    python -m bench.syntax predict --model gemini-flash-lite-latest --tasks 01,02,08
                                                          # next-line prediction on the reference solutions
    python -m bench.syntax report results/<predict>.jsonl

`predict` shows a model each reference solution up to a line and asks for the next line. A line counts as right
when it matches exactly, and as the right shape when it matches with names and literal values masked
(`parse_amount("10") -> Ok(10)` is `x(S) -> Ok(N)`): shape is what syntax decides, the values are the task's. In a
Jig file the plain Python lines are the baseline for its Jig constructs: same model, same file, same context. Jig
files are predicted with the short manual agents get in the benchmark.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import time
from pathlib import Path

from .run import MANUALS, ROOT

RESULTS = ROOT / "results"
TASKS = ROOT / "tasks"

# Jig's own constructs, most specific first; anything else is a plain Python line.
JIG_LINES = [
    ("module line", re.compile(r"^module \w")),
    ("std import", re.compile(r"^from std\.")),
    ("newtype", re.compile(r"^type \w+ = \w+\(")),
    ("record/enum header", re.compile(r"^(record|enum) \w+:")),
    ("contract clause", re.compile(r"^\s+(effects|requires|ensures|examples):")),
    ("? operator", re.compile(r"[\w)\]]\?(?![\w=?])")),
    ("Result/Option", re.compile(r"\b(Ok|Err|Some)\(|\bNothing\b|\b(Result|Option)\[")),
]
KEYWORDS = {"def", "return", "if", "elif", "else", "for", "in", "while", "not", "and", "or", "is", "None", "True",
            "False", "match", "case", "with", "as", "from", "import", "class", "lambda", "yield", "raise", "try",
            "except", "finally", "pass", "break", "continue", "module", "record", "enum", "type", "effects",
            "requires", "ensures", "examples", "Ok", "Err", "Some", "Nothing", "Result", "Option", "await", "async"}


def kinds(lines: list[str], jig: bool) -> list[str]:
    """The kind of each line. In a Jig file, lines inside a record or enum body and under `examples:` are kinds of
    their own, since they look like nothing in Python."""
    out, block, examples_indent = [], None, None
    for line in lines:
        indent = len(line) - len(line.lstrip())
        if examples_indent is not None and (not line.strip() or indent > examples_indent):
            out.append("example line" if line.strip() else "blank")
            continue
        examples_indent = None
        if not line.strip():
            out.append("blank")
            continue
        if indent == 0:
            block = None
        kind = "plain Python"
        if jig:
            for name, rx in JIG_LINES:
                if rx.search(line):
                    kind = name
                    break
            if kind == "plain Python" and block and indent > 0 and not line.strip().startswith(('"""', "def ")):
                kind = "record field / enum variant"
            if kind == "record/enum header":
                block = line
            if kind == "contract clause" and line.strip().startswith("examples:"):
                examples_indent = indent
        out.append(kind)
    return out


def shape(line: str) -> str:
    """A line with its names and literal values masked: what syntax decides."""
    line = re.sub(r'"[^"]*"|\'[^\']*\'', '""', line.strip())
    line = re.sub(r"\b\d+(\.\d+)?\b", "0", line)
    return re.sub(r"\b[A-Za-z_]\w*\b", lambda m: m.group(0) if m.group(0) in KEYWORDS else "x", line)


# ---------------------------------------------------------------- mistakes in past runs

ERROR_RE = re.compile(r"^error (\w+) \([^)]*\): (.*)\n(?:    \d+ \| (.*)\n)?", re.M)
RESULT_NAMES = {"Ok", "Err", "Result", "Some", "Nothing", "Option"}
FIRST_CURRENT_RUN = "20261007"  # from here on, jig fix adds missing imports: the toolchain models use today


def subject(code: str, message: str, source: str) -> str:
    """What an error is about: the construct a model got wrong, not merely the line it was on."""
    if code == "R001":
        name = (re.findall(r"unknown name '(\w+)'", message) or [""])[0]
        return "Result/Option" if name in RESULT_NAMES else "names and imports"
    if code == "R003":
        return "names and imports"
    if code == "R002":
        return "Result/Option" if message.startswith(("Result has", "Option has")) else "fields, methods, arguments"
    if code in ("T006", "T005", "T010", "T014", "T013"):
        return "fields, methods, arguments"
    if code in ("T007", "T009"):
        return "? operator" if "'?'" in message else "Result/Option"
    if code in ("T002", "T001"):
        return "newtype"
    if code == "T003":
        return "match coverage"
    if code.startswith("E"):
        return "contract clause"  # effects
    if code.startswith("C"):
        return "example line" if code in ("C001", "C002", "C003", "C005") else "contract clause"
    if code == "S001" and source:
        return kinds([source], jig=True)[0] if not source.startswith(" ") else _kind_in_body(source)
    return code


def _kind_in_body(source: str) -> str:
    """A line from inside a function, seen alone: an example line, a clause, or a plain line with Jig in it."""
    kind = kinds(["def f():", source], jig=True)[1]
    if kind == "plain Python" and re.match(r"^\s+\w+\(.*\) -> ", source):
        return "example line"
    return kind


def mistakes(files: list[Path]) -> None:
    """Every error the checker reported to a model writing Jig, by what it was about, in runs with the current
    toolchain: which constructs models get wrong, and what share of all their mistakes each causes."""
    errors: collections.Counter = collections.Counter()
    samples = 0
    for f in files:
        if f.name[:8] < FIRST_CURRENT_RUN:
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            r = json.loads(line) if line.strip() else {}
            if not str(r.get("cond", "")).startswith("jig"):
                continue
            samples += 1
            for feedback in r.get("feedback") or []:
                for code, message, source in ERROR_RE.findall(feedback + "\n"):
                    if code[0] in "SRTECFDM":
                        errors[subject(code, message, source)] += 1
    total = sum(errors.values())
    print(f"{total} errors over {samples} samples writing Jig (runs from {FIRST_CURRENT_RUN} on)\n")
    print(f"{'what the error was about':30} {'errors':>7} {'share':>7}")
    for kind, n in errors.most_common():
        print(f"{kind:30} {n:7} {n / max(total, 1):7.1%}")


# ---------------------------------------------------------------- next-line prediction

SYSTEM = """You continue source files. Reply with exactly the next line of the file: the whole line with its
indentation, nothing before or after it, no code fences, no explanation. If the next line is empty, reply EMPTY."""


def predict(model_name: str, tasks: list[str] | None, out: Path, rpm: int, max_lines: int) -> None:
    from jig.llm import Gemini

    llm = Gemini(model_name, temperature=0.0, rpm=rpm)
    done = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.add((r["task"], r["lang"], r["index"]))
    dirs = sorted(d for d in TASKS.iterdir() if (d / "reference.jig").is_file() and (d / "reference.py").is_file())
    if tasks:
        dirs = [d for d in dirs if any(d.name.startswith(t) for t in tasks)]
    with out.open("a", encoding="utf-8") as sink:
        for d in dirs:
            for lang in ("jig", "python"):
                lines = (d / f"reference.{'jig' if lang == 'jig' else 'py'}").read_text(encoding="utf-8").rstrip("\n").split("\n")
                line_kinds = kinds(lines, jig=lang == "jig")
                system = SYSTEM + (f"\n\nThe file is in Jig. Its reference:\n\n{MANUALS['jig-short']}" if lang == "jig" else
                                   "\n\nThe file is in Python.")
                for i in range(1, min(len(lines), max_lines)):
                    if (d.name, lang, i) in done or line_kinds[i] == "blank":
                        continue
                    prefix = "\n".join(lines[:i])
                    t0 = time.time()
                    reply = llm(system, [f"The file so far:\n\n{prefix}\n\nThe next line:"])
                    guess = _first_line(reply.text)
                    record = {"task": d.name, "lang": lang, "index": i, "kind": line_kinds[i], "actual": lines[i],
                              "predicted": guess, "exact": guess.strip() == lines[i].strip(),
                              "shape": shape(guess) == shape(lines[i]), "tokens": reply.tokens,
                              "seconds": round(time.time() - t0, 2)}
                    sink.write(json.dumps(record) + "\n")
                    sink.flush()
                    print(f"{d.name:22} {lang:6} {i:3} {line_kinds[i]:28} {'exact' if record['exact'] else 'shape' if record['shape'] else '-'}")


def _first_line(text: str) -> str:
    text = re.sub(r"^```\w*\n|```\s*$", "", text.strip("\n"))
    first = text.split("\n")[0] if text else ""
    return "" if first.strip() == "EMPTY" else first.rstrip()


def report(files: list[Path]) -> None:
    rows: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
    for f in files:
        for line in f.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            rows[(r["lang"], r["kind"])].append(r)
    print(f"{'language':8} {'kind of line':30} {'lines':>6} {'exact':>7} {'shape':>7}")
    for (lang, kind), rs in sorted(rows.items(), key=lambda kv: (kv[0][0], -len(kv[1]))):
        exact = sum(r["exact"] for r in rs) / len(rs)
        right_shape = sum(r["shape"] for r in rs) / len(rs)
        print(f"{lang:8} {kind:30} {len(rs):6} {exact:7.0%} {right_shape:7.0%}")
    print("\nIn Jig files, compare each construct's shape score with 'plain Python': a construct well below it is one")
    print("models cannot predict, so a candidate to change.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m bench.syntax", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("mistakes", help="errors in past runs, by kind of line")
    m.add_argument("results", nargs="*", help="result files (default: every run in results/)")
    pr = sub.add_parser("predict", help="next-line prediction on the reference solutions")
    pr.add_argument("--model", required=True)
    pr.add_argument("--tasks", help="comma-separated task id prefixes (default: all)")
    pr.add_argument("--rpm", type=int, default=30)
    pr.add_argument("--max-lines", type=int, default=200, help="lines per file at most")
    pr.add_argument("--out", help="results file to write or resume")
    rp = sub.add_parser("report", help="summarise prediction results")
    rp.add_argument("results", nargs="+")
    args = ap.parse_args(argv)
    if args.cmd == "mistakes":
        files = [Path(f) for f in args.results] or sorted(p for p in RESULTS.glob("*.jsonl") if "agent" not in p.name)
        mistakes(files)
    elif args.cmd == "predict":
        out = Path(args.out) if args.out else RESULTS / f"{time.strftime('%Y%m%d-%H%M%S')}-syntax-{args.model}.jsonl"
        predict(args.model, args.tasks.split(",") if args.tasks else None, out, args.rpm, args.max_lines)
        print(f"\nwrote {out}")
        report([out])
    else:
        report([Path(f) for f in args.results])
    return 0


if __name__ == "__main__":
    sys.exit(main())
