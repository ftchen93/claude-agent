"""Unit tests for the deterministic scripts in qe-workflow and dev-workflow.

Run from the repo root:  python3 -m unittest discover -s tests -v
Standard library only. No API key or network needed.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QE = ROOT / "qe-workflow"
DEV = ROOT / "dev-workflow"
QE_EX = QE / "examples" / "qe-artifacts" / "PAY-101"
DEV_EX = DEV / "examples" / "sdlc" / "PAY-101"


def run(script, *args, env=None, stdin=None, cwd=None):
    p = subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True,
                       text=True, env=env, input=stdin, cwd=cwd)
    return p.returncode, p.stdout + p.stderr


class TmpMixin:
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_json(self, name, data):
        p = self.tmp / name
        p.write_text(json.dumps(data))
        return p


class ScoreGate(TmpMixin, unittest.TestCase):
    script = QE / "skills/us-quality-gate/scripts/score_gate.py"

    def base(self):
        return json.loads((QE_EX / "01-quality-report.json").read_text())

    def set_score(self, report, cid, score):
        for c in report["criteria"]:
            if c["id"] == cid:
                c["score"] = score
        return report

    def test_example_passes(self):
        code, out = run(self.script, QE_EX / "01-quality-report.json")
        self.assertEqual(code, 0, out)

    def test_hard_fail_on_acceptance_criteria(self):
        p = self.write_json("r.json", self.set_score(self.base(), "acceptance_criteria", 1))
        code, out = run(self.script, p)
        self.assertEqual(code, 1)
        self.assertIn("hard fail", out)

    def test_na_not_allowed(self):
        p = self.write_json("r.json", self.set_score(self.base(), "testability", None))
        self.assertEqual(run(self.script, p)[0], 2)

    def test_na_allowed_drops_weight(self):
        p = self.write_json("r.json", self.set_score(self.base(), "ux_reference", None))
        code, out = run(self.script, p)
        self.assertEqual(code, 0, out)

    def test_out_of_range(self):
        p = self.write_json("r.json", self.set_score(self.base(), "role_and_value", 7))
        self.assertEqual(run(self.script, p)[0], 2)


class CheckDor(TmpMixin, unittest.TestCase):
    script = QE / "skills/definition-of-ready/scripts/check_dor.py"

    def test_example_blocks_on_unknown(self):
        code, out = run(self.script, QE_EX / "02-dor-result.json")
        self.assertEqual(code, 1)
        self.assertIn("test_data_identified", out)

    def test_all_met_is_ready(self):
        d = json.loads((QE_EX / "02-dor-result.json").read_text())
        for c in d["conditions"]:
            c["status"] = "met"
        self.assertEqual(run(self.script, self.write_json("d.json", d))[0], 0)


class CheckDod(TmpMixin, unittest.TestCase):
    script = QE / "skills/definition-of-done/scripts/check_dod.py"

    def dod(self, covered=5, passed=20, high=0):
        return {"story_id": "X", "metrics": {"ac_total": 5, "ac_covered_executed": covered, "tests_executed": 20,
                                             "tests_passed": passed, "open_defects": {"High": high}},
                "conditions": [{"id": i, "status": "met", "evidence": "e"} for i in
                               ["all_ac_covered", "pass_rate_met", "no_blocking_defects", "regression_executed",
                                "test_summary_published"]]}

    def test_done(self):
        self.assertEqual(run(self.script, self.write_json("d.json", self.dod()))[0], 0)

    def test_not_done_on_metrics(self):
        code, out = run(self.script, self.write_json("d.json", self.dod(covered=4, passed=18, high=1)))
        self.assertEqual(code, 1)
        for s in ("coverage", "pass rate", "high"):
            self.assertIn(s, out)


class Feasibility(TmpMixin, unittest.TestCase):
    script = QE / "skills/automation-feasibility/scripts/score_feasibility.py"

    def row(self, rec, rationale, f):
        keys = ["repeatability", "stability", "technical_feasibility", "business_risk", "effort"]
        return {"tc_id": "TC-001", "factors": dict(zip(keys, f)), "recommendation": rec, "rationale": rationale}

    def test_consistent(self):
        d = {"story_id": "X", "assessments": [self.row("automate", "core", [5, 4, 5, 5, 2])]}
        self.assertEqual(run(self.script, self.write_json("f.json", d))[0], 0)

    def test_unjustified_override_flagged(self):
        d = {"story_id": "X", "assessments": [self.row("automate", "nice", [2, 2, 2, 2, 4])]}
        self.assertEqual(run(self.script, self.write_json("f.json", d))[0], 1)

    def test_justified_override_ok(self):
        d = {"story_id": "X", "assessments": [self.row("automate", "OVERRIDE: regulatory", [2, 2, 2, 2, 4])]}
        self.assertEqual(run(self.script, self.write_json("f.json", d))[0], 0)


class TriageSummary(TmpMixin, unittest.TestCase):
    script = QE / "shared/scripts/triage_summary.py"

    def triage(self, confidence="high", sub_type="locator_drift"):
        return {"run_id": "1", "failures": [
            {"test": "a", "category": "test_bug", "sub_type": sub_type, "confidence": confidence,
             "evidence": "e", "route": "pipeline-self-heal"},
            {"test": "b", "category": "product_bug", "sub_type": "none", "confidence": "high",
             "evidence": "e", "route": "defect-raising"}]}

    def outputs(self, data):
        out_file = self.tmp / "gh_out"
        env = dict(os.environ, GITHUB_OUTPUT=str(out_file))
        code, _ = run(self.script, self.write_json("t.json", data), env=env)
        self.assertEqual(code, 0)
        return dict(l.split("=", 1) for l in out_file.read_text().split())

    def test_eligible(self):
        o = self.outputs(self.triage())
        self.assertEqual(o["heal_eligible"], "true")
        self.assertEqual(o["product_bugs"], "1")

    def test_low_confidence_downgraded(self):
        o = self.outputs(self.triage(confidence="low"))
        self.assertEqual(o["heal_eligible"], "false")
        self.assertEqual(o["needs_human"], "1")

    def test_disallowed_subtype_downgraded(self):
        self.assertEqual(self.outputs(self.triage(sub_type="assertion_outdated"))["heal_eligible"], "false")


class HealDiff(TmpMixin, unittest.TestCase):
    script = QE / "skills/pipeline-self-heal/scripts/check_heal_diff.py"

    def setUp(self):
        super().setUp()
        g = lambda *a: subprocess.run(["git", *a], cwd=self.tmp, check=True, capture_output=True)
        self.g = g
        g("init", "-q")
        g("config", "user.email", "t@example.com")
        g("config", "user.name", "t")
        (self.tmp / "tests/pages").mkdir(parents=True)
        (self.tmp / "src").mkdir()
        (self.tmp / "tests/pages/checkout.ts").write_text('export const promo = "#promo-input";\n')
        (self.tmp / "tests/promo.spec.ts").write_text('expect(total).toBe("18.00");\n')
        (self.tmp / "src/app.ts").write_text("export const x = 1;\n")
        g("add", "-A")
        g("commit", "-qm", "init")

    def check(self):
        self.g("add", "-A")
        return run(self.script, cwd=self.tmp)

    def test_locator_fix_ok(self):
        (self.tmp / "tests/pages/checkout.ts").write_text('export const promo = "[data-testid=promo]";\n')
        self.assertEqual(self.check()[0], 0)

    def test_assertion_change_rejected(self):
        (self.tmp / "tests/promo.spec.ts").write_text('expect(total).toBe("20.00");\n')
        self.assertEqual(self.check()[0], 1)

    def test_product_code_rejected(self):
        (self.tmp / "src/app.ts").write_text("export const x = 2;\n")
        self.assertEqual(self.check()[0], 1)


class CheckSdlc(TmpMixin, unittest.TestCase):
    script = DEV / "scripts/check_sdlc.py"
    tc = QE_EX / "03-test-cases.json"

    def test_example_chain_ok(self):
        self.assertEqual(run(self.script, "intent", DEV_EX / "intent.md")[0], 0)
        self.assertEqual(run(self.script, "spec", DEV_EX / "spec.md", "--intent", DEV_EX / "intent.md")[0], 0)
        code, out = run(self.script, "plan", DEV_EX / "plan.md", "--test-cases", self.tc, "--spec", DEV_EX / "spec.md")
        self.assertEqual(code, 0, out)

    def test_labelled_and_withdrawn_acs(self):
        p = self.tmp / "spec.md"
        text = (DEV_EX / "spec.md").read_text().replace("- AC-5: Only", "- AC-5 (withdrawn, PO 2026-11-21): Only")
        text = text.replace("- AC-6: Given", "- AC-6 (new): Given")
        p.write_text(text)
        self.assertEqual(run(self.script, "spec", p, "--intent", DEV_EX / "intent.md")[0], 0)
        plan = self.tmp / "plan.md"
        plan.write_text((DEV_EX / "plan.md").read_text().replace("- TC-007 (AC-6): PromoApiIT::TC-007\n", ""))
        code, out = run(self.script, "plan", plan, "--test-cases", self.tc, "--spec", p)
        self.assertEqual(code, 1)
        self.assertIn("AC-6", out)          # labelled AC is still recognised
        self.assertNotIn("AC-5 is not", out)  # withdrawn AC needs no coverage

    def test_template_intent_fails(self):
        self.assertEqual(run(self.script, "intent", DEV / "templates/intent.md")[0], 1)

    def test_dropped_ac_in_spec(self):
        p = self.tmp / "spec.md"
        p.write_text("\n".join(l for l in (DEV_EX / "spec.md").read_text().splitlines() if not l.startswith("- AC-5")))
        code, out = run(self.script, "spec", p, "--intent", DEV_EX / "intent.md")
        self.assertEqual(code, 1)
        self.assertIn("AC-5", out)

    def test_uncited_p1_and_uncovered_ac(self):
        p = self.tmp / "plan.md"
        p.write_text("\n".join(l for l in (DEV_EX / "plan.md").read_text().splitlines() if "TC-007" not in l))
        code, out = run(self.script, "plan", p, "--test-cases", self.tc, "--spec", DEV_EX / "spec.md")
        self.assertEqual(code, 1)
        self.assertIn("TC-007", out)
        self.assertIn("AC-6", out)

    def test_unknown_tc_cited(self):
        p = self.tmp / "plan.md"
        p.write_text((DEV_EX / "plan.md").read_text().replace("## Deviations", "- TC-999 (AC-1): ghost\n\n## Deviations"))
        code, out = run(self.script, "plan", p, "--test-cases", self.tc)
        self.assertEqual(code, 1)
        self.assertIn("TC-999", out)


class GuardEdits(TmpMixin, unittest.TestCase):
    script = DEV / "hooks/guard_edits.py"

    def setUp(self):
        super().setUp()
        (self.tmp / ".claude").mkdir()
        (self.tmp / "tests").mkdir()
        (self.tmp / "tests/a.spec.ts").write_text('expect(t).toBe("18.00");\nconst x = 1;\n')
        (self.tmp / ".claude/protected-paths").write_text("src/gen/**\n")

    def hook(self, tool, **ti):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(self.tmp))
        env.pop("CLAUDE_FIX_MODE", None)
        return run(self.script, env=env, stdin=json.dumps({"tool_name": tool, "tool_input": ti}))[0]

    def test_product_edit_allowed(self):
        self.assertEqual(self.hook("Edit", file_path="src/app.ts", old_string="a", new_string="b"), 0)

    def test_protected_path_blocked(self):
        self.assertEqual(self.hook("Write", file_path="src/gen/M.java", content="x"), 2)

    def test_new_assertion_allowed(self):
        self.assertEqual(self.hook("Edit", file_path="tests/a.spec.ts", old_string="const x = 1;",
                                   new_string="const x = 1;\nexpect(x).toBe(1);"), 0)

    def test_assertion_change_blocked(self):
        self.assertEqual(self.hook("Edit", file_path="tests/a.spec.ts", old_string='expect(t).toBe("18.00");',
                                   new_string='expect(t).toBe("20.00");'), 2)

    def test_write_dropping_assertion_blocked(self):
        self.assertEqual(self.hook("Write", file_path="tests/a.spec.ts", content="const x = 1;\n"), 2)

    def test_fix_mode_blocks_any_test_edit(self):
        (self.tmp / ".claude/fix-mode").touch()
        self.assertEqual(self.hook("Edit", file_path="tests/a.spec.ts", old_string="const x = 1;",
                                   new_string="const x = 2;"), 2)

    def test_allow_marker(self):
        (self.tmp / ".claude/allow-assertion-edits").touch()
        self.assertEqual(self.hook("Edit", file_path="tests/a.spec.ts", old_string='expect(t).toBe("18.00");',
                                   new_string='expect(t).toBe("20.00");'), 0)


class SchemasValidate(unittest.TestCase):
    script = QE / "shared/scripts/validate.py"

    def test_examples_valid(self):
        for schema, f in [("quality-report", "01-quality-report.json"), ("dor-result", "02-dor-result.json"),
                          ("test-cases", "03-test-cases.json")]:
            code, out = run(self.script, schema, QE_EX / f)
            self.assertEqual(code, 0, f"{f}: {out}")


if __name__ == "__main__":
    unittest.main()
