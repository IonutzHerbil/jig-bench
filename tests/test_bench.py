"""The benchmark's own correctness: every reference solution passes its hidden tests in every toolchain."""

import json

import pytest

from bench import agent, run
from bench.model import Reference

TASKS = sorted(p.parent for p in (run.ROOT / "tasks").glob("*/task.json"))


@pytest.mark.parametrize("task_dir", TASKS, ids=lambda p: p.name)
@pytest.mark.parametrize("cond", ["python", "jig-short"])
def test_reference_delivers(task_dir, cond):
    task = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    rec = run.run_sample(Reference(), task_dir, task, cond, 1)
    assert rec["checked_ok"], rec["feedback"]
    assert rec["hidden_passed"] == rec["hidden_total"], rec["outputs"]


@pytest.mark.parametrize("task_dir", sorted(p.parent for p in (agent.TASKS).glob("*/task.json")), ids=lambda p: p.name)
@pytest.mark.parametrize("cond", ["python", "jig"])
def test_engineering_reference_delivers(task_dir, cond):
    """Each scenario's reference fix delivers in both repositories: the Jig port behaves like the Python original."""
    rec = agent.run_sample(agent.ReferenceAgent(), task_dir, cond, budget=12)
    assert rec["outcome"] == "delivered", (rec["outcome"], rec["final_errors"], rec["transcript"][-1])


@pytest.mark.parametrize("task_dir", [d for d in TASKS if (d / "stub.jig").exists()], ids=lambda p: p.name)
@pytest.mark.parametrize("lang", ["jig", "python"])
def test_stub_examples_hold_for_the_reference(task_dir, lang, tmp_path):
    """A stub's examples are right: the reference solution, given them, still passes its toolchain."""
    import re
    import shutil

    task = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    stub = (task_dir / f"stub.{'jig' if lang == 'jig' else 'py'}").read_text(encoding="utf-8")
    reference = (task_dir / f"reference.{'jig' if lang == 'jig' else 'py'}").read_text(encoding="utf-8")
    if lang == "jig":
        examples = stub[stub.index("    examples:\n") : stub.rindex("    ...")]
        head = re.search(rf"def {task['entry']}\(.*\n(    \"\"\".*\"\"\"\n)?", reference)
        rest = re.sub(r"^    examples:\n(        .*\n)+", "", reference[head.end() :])
        code = reference[: head.end()] + examples + rest
    else:
        test = stub[stub.index("def test_examples") :]
        code = "import pytest\n" + reference + "\n\n" + stub[: stub.index("def ")].replace("import pytest", "") + test
    if task.get("project"):
        shutil.copytree(run.ROOT / "projects" / task["project"] / lang, tmp_path / ("src" if lang == "jig" else "build"))
    ok, _, feedback, _ = run.check(lang, code, tmp_path, task.get("module", "solution"))
    assert ok, feedback


@pytest.mark.parametrize("lang", ["jig", "python"])
def test_interfaces_view(lang):
    """The interfaces view shows every module's names and signatures, and the types module whole, but no bodies."""
    full = run.project_context("clinic", lang, "full")
    view = run.project_context("clinic", lang, "interfaces")
    assert "def find_doctor(doctor: DoctorId)" in view and "def overlaps(" in view and "reserve(" in view
    assert run.project_context("clinic", lang, "partial").split("\n\n")[0] in view  # the types module, unchanged
    before_types = "### clinic/types"
    assert "return " in full.split(before_types)[0] and "return " not in view.split(before_types)[0]


def test_syntax_kinds_and_shapes():
    """The predictability study's line classifier and shape masking, on a Jig snippet."""
    from bench.syntax import kinds, shape

    lines = ["module m", "", "from std.result import Err, Ok, Result", "", "", "record R:", "    a: int", "",
             "", "def f(x: int) -> Result[int, str]:", '    """."""', "    effects: none", "    examples:",
             "        f(1) -> Ok(1)", "    y = g(x)?", "    return Ok(y)"]
    assert kinds(lines, jig=True) == ["module line", "blank", "std import", "blank", "blank", "record/enum header",
                                     "record field / enum variant", "blank", "blank", "Result/Option", "plain Python",
                                     "contract clause", "contract clause", "example line", "? operator", "Result/Option"]
    assert shape('        parse_amount("10") -> Ok(10)') == 'x("") -> Ok(0)'
